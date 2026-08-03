import { useCallback, useState } from 'react';
import { SafeAreaView, View, FlatList, Text, Pressable, ActivityIndicator, RefreshControl, StyleSheet } from 'react-native';
import { useRouter, useFocusEffect } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

import { colors, typography } from '../theme';
import Header from '../components/Header';
import EmptyState from '../components/EmptyState';
import { getMisRutas, hoyISO } from '../services/rutasService';

// Ordena por hora_inicio ascendente -- las rutas sin hora capturada
// (opcional) van al final, no se intercalan al azar entre las que sí
// tienen horario definido.
function ordenarPorHora(rutas) {
  return [...rutas].sort((a, b) => {
    if (!a.hora_inicio && !b.hora_inicio) return 0;
    if (!a.hora_inicio) return 1;
    if (!b.hora_inicio) return -1;
    return a.hora_inicio.localeCompare(b.hora_inicio);
  });
}

export default function RutasScreen() {
  const router = useRouter();
  const [rutas, setRutas] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [refrescando, setRefrescando] = useState(false);

  const cargar = useCallback(async () => {
    try {
      const data = await getMisRutas(hoyISO());
      setRutas(ordenarPorHora(data));
    } catch {
      setRutas([]);
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

  if (cargando) {
    return (
      <SafeAreaView style={styles.center}>
        <ActivityIndicator size="large" color={colors.brandTeal700} />
      </SafeAreaView>
    );
  }

  return (
    <View style={styles.safe}>
      <Header title="Rutas" />
      <FlatList
        data={rutas.length > 0 ? [rutas] : []}
        keyExtractor={() => 'lista-rutas'}
        ListHeaderComponent={<Text style={styles.leyenda}>Rutas asignadas para hoy</Text>}
        contentContainerStyle={rutas.length === 0 ? styles.emptyContainer : styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refrescando} onRefresh={onRefresh} tintColor={colors.brandTeal700} />
        }
        ListEmptyComponent={
          <EmptyState
            icon="map-outline"
            title="Sin rutas para hoy"
            subtitle="Cuando el administrador te asigne una ruta, aparecerá aquí."
          />
        }
        renderItem={() => (
          <View style={styles.listaCard}>
            {rutas.map((item, idx) => (
              <Pressable
                key={item.id}
                style={({ pressed }) => [
                  styles.fila,
                  idx < rutas.length - 1 && styles.filaBorde,
                  pressed && styles.filaPressed,
                ]}
                onPress={() => router.push(`/(tabs)/rutas/${item.id}`)}
              >
                <View style={styles.filaCuerpo}>
                  <Text style={styles.nombre}>{item.nombre}</Text>
                  <View style={styles.filaMetaRow}>
                    <Text style={styles.meta}>
                      {item.hora_inicio ? item.hora_inicio.slice(0, 5) : '—'} – {item.hora_fin ? item.hora_fin.slice(0, 5) : '—'}
                    </Text>
                    <Text style={[styles.estado, item.completada ? styles.estadoCompletada : styles.estadoProgreso]}>
                      {item.completada ? 'Completada' : 'En progreso'}
                    </Text>
                  </View>
                </View>
                <Ionicons name="chevron-forward" size={18} color={colors.ink400} />
              </Pressable>
            ))}
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.pageBg },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.pageBg },
  leyenda: {
    fontFamily: typography.regular,
    fontSize: 13,
    color: colors.ink600,
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 8,
  },
  listContainer: { paddingBottom: 24 },
  emptyContainer: { flexGrow: 1 },

  // Un solo contenedor con divisores entre filas -- estilo "Ajustes de
  // Android", en vez de una tarjeta separada por cada ruta.
  listaCard: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.borderSoft,
    borderRadius: 14,
    marginHorizontal: 16,
    overflow: 'hidden',
  },
  fila: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingHorizontal: 16, paddingVertical: 14 },
  filaBorde: { borderBottomWidth: 1, borderBottomColor: colors.borderSoft },
  filaPressed: { backgroundColor: colors.brandAqua100 },
  filaCuerpo: { flex: 1 },
  filaMetaRow: { flexDirection: 'row', alignItems: 'center', gap: 10, marginTop: 4 },

  nombre: { fontFamily: typography.semibold, fontSize: 15, color: colors.ink900 },
  meta: { fontFamily: typography.regular, fontSize: 12, color: colors.ink600 },
  estado: { fontFamily: typography.bold, fontSize: 11 },
  estadoCompletada: { color: colors.recycleGreen },
  estadoProgreso: { color: colors.warning },
});
