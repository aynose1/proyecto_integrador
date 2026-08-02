import { useCallback, useState } from 'react';
import { SafeAreaView, FlatList, Text, Pressable, ActivityIndicator, RefreshControl, StyleSheet } from 'react-native';
import { useRouter, useFocusEffect } from 'expo-router';

import { colors } from '../theme';
import Header from '../components/Header';
import PageHeader from '../components/PageHeader';
import EmptyState from '../components/EmptyState';
import { getMisRutas, hoyISO } from '../services/rutasService';

export default function RutasScreen() {
  const router = useRouter();
  const [rutas, setRutas] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [refrescando, setRefrescando] = useState(false);

  const cargar = useCallback(async () => {
    try {
      const data = await getMisRutas(hoyISO());
      setRutas(data);
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
    <SafeAreaView style={styles.safe}>
      <Header title="Rutas" />
      <FlatList
        data={rutas}
        keyExtractor={(item) => String(item.id)}
        ListHeaderComponent={<PageHeader title="Mis rutas" subtitle="Rutas asignadas para hoy." />}
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
        renderItem={({ item }) => (
          <Pressable
            style={({ pressed }) => [styles.card, pressed && styles.cardPressed]}
            onPress={() => router.push(`/(tabs)/rutas/${item.id}`)}
          >
            <Text style={styles.nombre}>{item.nombre}</Text>
            <Text style={styles.meta}>
              {item.hora_inicio ? item.hora_inicio.slice(0, 5) : '—'} – {item.hora_fin ? item.hora_fin.slice(0, 5) : '—'}
            </Text>
            <Text style={[styles.estado, item.completada ? styles.estadoCompletada : styles.estadoProgreso]}>
              {item.completada ? 'Completada' : 'En progreso'}
            </Text>
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
  meta: { fontSize: 13, color: colors.ink600, marginTop: 4 },
  estado: { fontSize: 12, fontWeight: '700', marginTop: 8, alignSelf: 'flex-start' },
  estadoCompletada: { color: colors.brandAqua500 },
  estadoProgreso: { color: colors.warning },
});
