import { useCallback, useState } from 'react';
import { View, SafeAreaView, Text, FlatList, Pressable, ActivityIndicator, RefreshControl, StyleSheet } from 'react-native';
import { useFocusEffect } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

import { colors, typography } from '../theme';
import Header from '../components/Header';
import EmptyState from '../components/EmptyState';
import { getMisIncidencias } from '../services/incidenciasService';

const ICONOS_MOTIVO = {
  'sensor dañado': 'hardware-chip-outline',
  'contenedor dañado': 'trash-outline',
  'lectura errónea': 'warning-outline',
  otro: 'information-circle-outline',
};

function iconoMotivo(motivo) {
  return ICONOS_MOTIVO[(motivo || '').toLowerCase()] || 'information-circle-outline';
}

function tiempoRelativo(fechaHoraStr) {
  if (!fechaHoraStr) return '—';
  const momento = new Date(fechaHoraStr);
  const segundos = Math.max(0, (Date.now() - momento.getTime()) / 1000);
  if (segundos < 60) return 'Justo ahora';
  const minutos = Math.floor(segundos / 60);
  if (minutos < 60) return `Hace ${minutos} min`;
  const horas = Math.floor(minutos / 60);
  if (horas < 24) return `Hace ${horas} h`;
  const dias = Math.floor(horas / 24);
  if (dias === 1) return 'Ayer';
  if (dias < 7) return `Hace ${dias} días`;
  return momento.toLocaleDateString('es-MX');
}

function mismoDiaCalendario(a, b) {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();
}

// Agrupa igual que el centro de notificaciones de la web: Hoy / Ayer /
// Esta semana / Más antiguo -- mismo criterio, para que la experiencia
// se sienta consistente entre web y móvil.
function agruparPorFecha(incidencias) {
  const hoy = new Date();
  const ayer = new Date(hoy);
  ayer.setDate(hoy.getDate() - 1);
  const limiteSemana = new Date(hoy);
  limiteSemana.setDate(hoy.getDate() - 7);

  const franjas = { Hoy: [], Ayer: [], 'Esta semana': [], 'Más antiguo': [] };
  incidencias.forEach((inc) => {
    const fecha = new Date(inc.fecha_hora);
    if (mismoDiaCalendario(fecha, hoy)) franjas.Hoy.push(inc);
    else if (mismoDiaCalendario(fecha, ayer)) franjas.Ayer.push(inc);
    else if (fecha > limiteSemana) franjas['Esta semana'].push(inc);
    else franjas['Más antiguo'].push(inc);
  });

  return Object.entries(franjas)
    .filter(([, items]) => items.length > 0)
    .map(([titulo, items]) => ({ titulo, items }));
}

const FILTROS = [
  { clave: 'todos', etiqueta: 'Todos' },
  { clave: 'hoy', etiqueta: 'Hoy' },
  { clave: 'semana', etiqueta: 'Esta semana' },
];

export default function ReportesScreen() {
  const [incidencias, setIncidencias] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [refrescando, setRefrescando] = useState(false);
  const [filtro, setFiltro] = useState('todos');

  const cargar = useCallback(async () => {
    try {
      const data = await getMisIncidencias();
      setIncidencias(data);
    } catch {
      setIncidencias([]);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      let activo = true;
      setCargando(true);
      cargar().finally(() => {
        if (activo) setCargando(false);
      });
      return () => {
        activo = false;
      };
    }, [cargar])
  );

  async function onRefresh() {
    setRefrescando(true);
    await cargar();
    setRefrescando(false);
  }

  const hoy = new Date();
  const limiteSemana = new Date(hoy);
  limiteSemana.setDate(hoy.getDate() - 7);

  const incidenciasFiltradas = incidencias.filter((inc) => {
    if (filtro === 'todos') return true;
    const fecha = new Date(inc.fecha_hora);
    if (filtro === 'hoy') return mismoDiaCalendario(fecha, hoy);
    if (filtro === 'semana') return fecha > limiteSemana;
    return true;
  });

  const grupos = agruparPorFecha(incidenciasFiltradas);

  if (cargando) {
    return (
      <SafeAreaView style={styles.center}>
        <ActivityIndicator size="large" color={colors.brandTeal700} />
      </SafeAreaView>
    );
  }

  return (
    <View style={styles.safe}>
      <Header title="Reportes" />

      <View style={styles.filtros}>
        {FILTROS.map((f) => (
          <Pressable
            key={f.clave}
            style={[styles.filtroChip, filtro === f.clave && styles.filtroChipActivo]}
            onPress={() => setFiltro(f.clave)}
          >
            <Text style={[styles.filtroChipTexto, filtro === f.clave && styles.filtroChipTextoActivo]}>
              {f.etiqueta}
            </Text>
          </Pressable>
        ))}
      </View>

      <FlatList
        data={grupos}
        keyExtractor={(g) => g.titulo}
        contentContainerStyle={grupos.length === 0 ? styles.emptyContainer : styles.listContainer}
        refreshControl={<RefreshControl refreshing={refrescando} onRefresh={onRefresh} tintColor={colors.brandTeal700} />}
        ListEmptyComponent={
          <EmptyState
            icon="document-text-outline"
            title="Sin reportes"
            subtitle="Los reportes que levantes desde Escaneo Rápido van a aparecer aquí."
          />
        }
        renderItem={({ item: grupo }) => (
          <View style={styles.grupo}>
            <Text style={styles.grupoTitulo}>{grupo.titulo}</Text>
            <View style={styles.grupoCard}>
              {grupo.items.map((inc, idx) => (
                <View key={inc.id} style={[styles.item, idx < grupo.items.length - 1 && styles.itemBorde]}>
                  <View style={styles.itemIcono}>
                    <Ionicons name={iconoMotivo(inc.motivo?.motivo)} size={18} color={colors.brandTeal700} />
                  </View>
                  <View style={styles.itemCuerpo}>
                    <View style={styles.itemFila}>
                      <Text style={styles.itemMotivo} numberOfLines={1}>
                        {inc.motivo?.motivo || 'Reporte'}
                      </Text>
                      <Text style={styles.itemTiempo}>{tiempoRelativo(inc.fecha_hora)}</Text>
                    </View>
                    {inc.comentario ? (
                      <Text style={styles.itemComentario} numberOfLines={2}>
                        {inc.comentario}
                      </Text>
                    ) : null}
                    <View
                      style={[
                        styles.estadoBadge,
                        inc.estado?.estado === 'atendido' ? styles.estadoBadgeAtendido : styles.estadoBadgePendiente,
                      ]}
                    >
                      <Text
                        style={[
                          styles.estadoBadgeTexto,
                          inc.estado?.estado === 'atendido' && styles.estadoBadgeTextoAtendido,
                        ]}
                      >
                        {inc.estado?.estado === 'atendido' ? 'Atendido' : 'Pendiente'}
                      </Text>
                    </View>
                  </View>
                </View>
              ))}
            </View>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.pageBg },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.pageBg },
  listContainer: { paddingBottom: 24, paddingTop: 4 },
  emptyContainer: { flexGrow: 1 },

  filtros: { flexDirection: 'row', gap: 8, paddingHorizontal: 16, paddingVertical: 12, backgroundColor: colors.surface },
  filtroChip: {
    paddingHorizontal: 14,
    paddingVertical: 7,
    borderRadius: 999,
    backgroundColor: colors.pageBg,
    borderWidth: 1,
    borderColor: colors.borderSoft,
  },
  filtroChipActivo: { backgroundColor: colors.brandTeal700, borderColor: colors.brandTeal700 },
  filtroChipTexto: { fontFamily: typography.semibold, fontSize: 13, color: colors.ink600 },
  filtroChipTextoActivo: { color: '#ffffff' },

  grupo: { marginTop: 16, paddingHorizontal: 16 },
  grupoTitulo: { fontFamily: typography.bold, fontSize: 13, color: colors.ink600, marginBottom: 8, textTransform: 'uppercase', letterSpacing: 0.4 },
  grupoCard: {
    backgroundColor: colors.surface,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.borderSoft,
    overflow: 'hidden',
  },
  item: { flexDirection: 'row', gap: 12, padding: 14 },
  itemBorde: { borderBottomWidth: 1, borderBottomColor: colors.borderSoft },
  itemIcono: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.brandAqua100,
    alignItems: 'center',
    justifyContent: 'center',
  },
  itemCuerpo: { flex: 1 },
  itemFila: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', gap: 8 },
  itemMotivo: { flex: 1, fontFamily: typography.semibold, fontSize: 14, color: colors.ink900 },
  itemTiempo: { fontFamily: typography.regular, fontSize: 11, color: colors.ink400 },
  itemComentario: { fontFamily: typography.regular, fontSize: 12, color: colors.ink600, marginTop: 3 },
  estadoBadge: { alignSelf: 'flex-start', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 999, marginTop: 6 },
  estadoBadgePendiente: { backgroundColor: '#fbeee0' },
  estadoBadgeAtendido: { backgroundColor: colors.pageBg },
  estadoBadgeTexto: { fontFamily: typography.semibold, fontSize: 10, color: colors.warning },
  estadoBadgeTextoAtendido: { color: colors.ink600 },
});
