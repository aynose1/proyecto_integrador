import { useCallback, useState } from 'react';
import { SafeAreaView, FlatList, Text, Pressable, ActivityIndicator, StyleSheet } from 'react-native';
import { useRouter, useFocusEffect } from 'expo-router';

import { colors } from '../theme';
import PageHeader from '../components/PageHeader';
import EmptyState from '../components/EmptyState';
import { getRutaDetalle, contenedoresPendientes } from '../services/rutasService';

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
        data={pendientes}
        keyExtractor={(item) => String(item.id)}
        ListHeaderComponent={
          <PageHeader
            title={ruta?.nombre || 'Ruta'}
            subtitle={`${pendientes.length} contenedor${pendientes.length === 1 ? '' : 'es'} pendiente${
              pendientes.length === 1 ? '' : 's'
            } de recolectar`}
          />
        }
        contentContainerStyle={pendientes.length === 0 ? styles.emptyContainer : styles.listContainer}
        ListEmptyComponent={
          <EmptyState
            icon="checkmark-done-outline"
            title="Todo recolectado"
            subtitle="Ya no hay contenedores pendientes en esta ruta."
          />
        }
        renderItem={({ item }) => (
          <Pressable
            style={({ pressed }) => [styles.card, pressed && styles.cardPressed]}
            onPress={() => router.push(`/(tabs)/rutas/contenedor/${item.contenedor.id}`)}
          >
            <Text style={styles.nombre}>{item.contenedor.nombre}</Text>
            <Text style={styles.codigo}>{item.contenedor.codigo_contenedor}</Text>
            <Text style={styles.nivel}>{item.contenedor.nivel_actual}% de llenado</Text>
          </Pressable>
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
  card: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.borderSoft,
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 16,
    marginBottom: 12,
  },
  cardPressed: { backgroundColor: colors.brandAqua100 },
  nombre: { fontSize: 16, fontWeight: '700', color: colors.ink900 },
  codigo: { fontSize: 12, color: colors.ink600, marginTop: 2 },
  nivel: { fontSize: 13, fontWeight: '600', color: colors.brandTeal700, marginTop: 8 },
});
