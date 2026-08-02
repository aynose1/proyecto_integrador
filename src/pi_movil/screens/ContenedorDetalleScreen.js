import { useCallback, useState } from 'react';
import { SafeAreaView, ScrollView, View, Text, ActivityIndicator, StyleSheet } from 'react-native';
import { useFocusEffect } from 'expo-router';

import { colors } from '../theme';
import NivelBar from '../components/NivelBar';
import { getContenedor } from '../services/contenedoresService';

function Row({ label, value }) {
  return (
    <View style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <Text style={styles.rowValue}>{value}</Text>
    </View>
  );
}

export default function ContenedorDetalleScreen({ contenedorId }) {
  const [contenedor, setContenedor] = useState(null);
  const [cargando, setCargando] = useState(true);

  useFocusEffect(
    useCallback(() => {
      let activo = true;
      setCargando(true);
      getContenedor(contenedorId)
        .then((data) => {
          if (activo) setContenedor(data);
        })
        .catch(() => {
          if (activo) setContenedor(null);
        })
        .finally(() => {
          if (activo) setCargando(false);
        });
      return () => {
        activo = false;
      };
    }, [contenedorId])
  );

  if (cargando) {
    return (
      <SafeAreaView style={styles.center}>
        <ActivityIndicator size="large" color={colors.brandTeal700} />
      </SafeAreaView>
    );
  }

  if (!contenedor) {
    return (
      <SafeAreaView style={styles.center}>
        <Text style={styles.errorText}>No se pudo cargar la información del contenedor.</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={styles.nombre}>{contenedor.nombre}</Text>
        <Text style={styles.codigo}>{contenedor.codigo_contenedor}</Text>

        <View style={styles.card}>
          <Text style={styles.label}>Nivel de llenado</Text>
          <NivelBar nivel={contenedor.nivel_actual} />
        </View>

        <View style={styles.card}>
          <Row
            label="Ubicación"
            value={`${contenedor.sector?.zona?.nombre ?? '—'} / ${contenedor.sector?.nombre ?? '—'}`}
          />
          <Row label="Capacidad máxima" value={`${contenedor.capacidad_max} Kg`} />
          <Row label="Peso actual" value={`${contenedor.peso_actual} Kg`} />
          <Row label="Estado" value={contenedor.estado?.estado === 'activo' ? 'Activo' : 'Inactivo'} />
        </View>

        <Text style={styles.nota}>
          ¿Este contenedor tiene un problema (sensor dañado, lectura errónea, etc.)? Repórtalo desde la pestaña
          "Reportar".
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.pageBg },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.pageBg, padding: 20 },
  scroll: { padding: 16 },
  nombre: { fontSize: 20, fontWeight: '700', color: colors.ink900 },
  codigo: { fontSize: 13, color: colors.ink600, marginTop: 2, marginBottom: 16 },
  card: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.borderSoft,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  label: { fontSize: 13, fontWeight: '600', color: colors.ink600, marginBottom: 8 },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: colors.borderSoft,
  },
  rowLabel: { fontSize: 14, color: colors.ink600 },
  rowValue: { fontSize: 14, fontWeight: '600', color: colors.ink900 },
  errorText: { color: colors.ink600, textAlign: 'center' },
  nota: { fontSize: 13, color: colors.ink600, textAlign: 'center', marginTop: 8, marginBottom: 24 },
});
