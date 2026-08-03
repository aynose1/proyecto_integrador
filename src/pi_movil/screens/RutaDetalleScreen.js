import { useCallback, useState } from 'react';
import { SafeAreaView, View, FlatList, Text, Pressable, ActivityIndicator, StyleSheet } from 'react-native';
import { useRouter, useFocusEffect } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

import { colors, typography } from '../theme';
import EmptyState from '../components/EmptyState';
import { getRutaDetalle, contenedoresPendientes } from '../services/rutasService';

// Mismos umbrales que ya usa la web (bajo/medio/crítico) para colorear
// el punto de nivel de cada fila.
function colorPorNivel(nivel) {
  const n = Number(nivel);
  if (n >= 80) return colors.danger;
  if (n >= 50) return colors.warning;
  return colors.brandTeal600;
}

/**
 * Detalle de una ruta: solo muestra los contenedores PENDIENTES
 * (los ya recolectados no aparecen aquí — ver contenedoresPendientes).
 */
export default function RutaDetalleScreen({ rutaId }) {
  const router = useRouter();
  const [ruta, setRuta] = useState(null);
  const [cargando, setCargando] = useState(true);

  useFocusEffect(
    useCallback(() => {
      let activo = true;
      setCargando(true);
      getRutaDetalle(rutaId)
        .then((data) => {
          if (activo) setRuta(data);
        })
        .catch(() => {
          if (activo) setRuta(null);
        })
        .finally(() => {
          if (activo) setCargando(false);
        });
      return () => {
        activo = false;
      };
    }, [rutaId])
  );

  if (cargando) {
    return (
      <SafeAreaView style={styles.center}>
        <ActivityIndicator size="large" color={colors.brandTeal700} />
      </SafeAreaView>
    );
  }

  const pendientes = ruta ? contenedoresPendientes(ruta) : [];

  return (
    <SafeAreaView style={styles.safe}>
      <FlatList
        data={pendientes.length > 0 ? [pendientes] : []}
        keyExtractor={() => 'lista-contenedores'}
        ListHeaderComponent={
          <View style={styles.encabezado}>
            <Text style={styles.tituloRuta}>{ruta?.nombre || 'Ruta'}</Text>
            <Text style={styles.leyenda}>
              {pendientes.length} contenedor{pendientes.length === 1 ? '' : 'es'} pendiente
              {pendientes.length === 1 ? '' : 's'} de recolectar
            </Text>
          </View>
        }
        contentContainerStyle={pendientes.length === 0 ? styles.emptyContainer : styles.listContainer}
        ListEmptyComponent={
          <EmptyState
            icon="checkmark-done-outline"
            title="Todo recolectado"
            subtitle="Ya no hay contenedores pendientes en esta ruta."
          />
        }
        renderItem={() => (
          <View style={styles.listaCard}>
            {pendientes.map((item, idx) => (
              <Pressable
                key={item.id}
                style={({ pressed }) => [
                  styles.fila,
                  idx < pendientes.length - 1 && styles.filaBorde,
                  pressed && styles.filaPressed,
                ]}
                onPress={() => router.push(`/(tabs)/rutas/contenedor/${item.contenedor.id}`)}
              >
                <View style={[styles.puntoNivel, { backgroundColor: colorPorNivel(item.contenedor.nivel_actual) }]} />
                <View style={styles.filaCuerpo}>
                  <Text style={styles.nombre}>{item.contenedor.nombre}</Text>
                  <Text style={styles.codigo}>{item.contenedor.codigo_contenedor}</Text>
                </View>
                <Text style={styles.nivelTexto}>{item.contenedor.nivel_actual}%</Text>
                <Ionicons name="chevron-forward" size={18} color={colors.ink400} />
              </Pressable>
            ))}
          </View>
        )}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.pageBg },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.pageBg },
  listContainer: { paddingBottom: 24 },
  emptyContainer: { flexGrow: 1 },

  encabezado: { paddingHorizontal: 16, paddingTop: 16, paddingBottom: 8 },
  tituloRuta: { fontFamily: typography.bold, fontSize: 20, color: colors.ink900 },
  leyenda: { fontFamily: typography.regular, fontSize: 13, color: colors.ink600, marginTop: 2 },

  // Un solo contenedor con divisores entre filas -- estilo "Ajustes de
  // Android", en vez de una tarjeta separada por cada contenedor.
  listaCard: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.borderSoft,
    borderRadius: 14,
    marginHorizontal: 16,
    overflow: 'hidden',
  },
  fila: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingHorizontal: 16, paddingVertical: 14 },
  filaBorde: { borderBottomWidth: 1, borderBottomColor: colors.borderSoft },
  filaPressed: { backgroundColor: colors.brandAqua100 },
  puntoNivel: { width: 10, height: 10, borderRadius: 5 },
  filaCuerpo: { flex: 1 },
  nombre: { fontFamily: typography.semibold, fontSize: 15, color: colors.ink900 },
  codigo: { fontFamily: typography.regular, fontSize: 12, color: colors.ink600, marginTop: 2 },
  nivelTexto: { fontFamily: typography.bold, fontSize: 13, color: colors.ink900 },
});
