import { useCallback, useState } from 'react';
import {
  SafeAreaView,
  ScrollView,
  View,
  Text,
  Pressable,
  Modal,
  TextInput,
  Alert,
  ActivityIndicator,
  StyleSheet,
} from 'react-native';
import { useFocusEffect } from 'expo-router';

import { colors } from '../theme';
import NivelBar from '../components/NivelBar';
import { getContenedor } from '../services/contenedoresService';
import { getMotivosIncidencia, reportarIncidencia } from '../services/incidenciasService';

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

  const [modalVisible, setModalVisible] = useState(false);
  const [motivos, setMotivos] = useState([]);
  const [motivoId, setMotivoId] = useState(null);
  const [comentario, setComentario] = useState('');
  const [enviando, setEnviando] = useState(false);

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

  async function abrirModalReportar() {
    setModalVisible(true);
    setMotivoId(null);
    setComentario('');
    try {
      const data = await getMotivosIncidencia();
      setMotivos(data);
    } catch (error) {
      Alert.alert('Error', 'No se pudieron cargar los motivos. Intenta de nuevo.');
      setModalVisible(false);
    }
  }

  async function enviarReporte() {
    if (!motivoId) {
      Alert.alert('Falta el motivo', 'Elige qué está pasando con este contenedor.');
      return;
    }
    setEnviando(true);
    try {
      await reportarIncidencia(Number(contenedorId), motivoId, comentario.trim());
      setModalVisible(false);
      Alert.alert('Listo', 'Se reportó la incidencia. Un administrador la va a revisar.');
    } catch (error) {
      Alert.alert('Error', error.message || 'No se pudo enviar el reporte.');
    } finally {
      setEnviando(false);
    }
  }

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

        <Pressable
          style={({ pressed }) => [styles.reportarButton, pressed && styles.reportarButtonPressed]}
          onPress={abrirModalReportar}
        >
          <Text style={styles.reportarButtonText}>Reportar incidencia</Text>
        </Pressable>
      </ScrollView>

      {/* Bottom sheet (Modal): reportar incidencia */}
      <Modal visible={modalVisible} transparent animationType="slide" onRequestClose={() => setModalVisible(false)}>
        <View style={styles.modalBackdrop}>
          <View style={styles.sheet}>
            <Text style={styles.sheetTitle}>Reportar incidencia</Text>
            <Text style={styles.sheetSubtitle}>{contenedor.nombre}</Text>

            {motivos.length === 0 ? (
              <ActivityIndicator color={colors.brandTeal700} style={{ marginVertical: 20 }} />
            ) : (
              <View style={styles.motivosLista}>
                {motivos.map((m) => (
                  <Pressable
                    key={m.id}
                    style={[styles.motivoItem, motivoId === m.id && styles.motivoItemSeleccionado]}
                    onPress={() => setMotivoId(m.id)}
                  >
                    <Text style={[styles.motivoTexto, motivoId === m.id && styles.motivoTextoSeleccionado]}>
                      {m.motivo}
                    </Text>
                  </Pressable>
                ))}
              </View>
            )}

            <Text style={styles.comentarioLabel}>Comentario (opcional)</Text>
            <TextInput
              style={styles.comentarioInput}
              value={comentario}
              onChangeText={setComentario}
              placeholder="Describe lo que observaste..."
              placeholderTextColor={colors.ink400}
              multiline
              numberOfLines={3}
              editable={!enviando}
            />

            <Pressable
              style={({ pressed }) => [
                styles.confirmButton,
                (!motivoId || enviando) && styles.confirmButtonDisabled,
                pressed && motivoId && !enviando && styles.confirmButtonPressed,
              ]}
              onPress={enviarReporte}
              disabled={!motivoId || enviando}
            >
              {enviando ? (
                <ActivityIndicator color="#ffffff" />
              ) : (
                <Text style={styles.confirmButtonText}>Enviar reporte</Text>
              )}
            </Pressable>
            <Pressable style={styles.cancelButton} onPress={() => setModalVisible(false)} disabled={enviando}>
              <Text style={styles.cancelButtonText}>Cancelar</Text>
            </Pressable>
          </View>
        </View>
      </Modal>
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
  reportarButton: {
    borderWidth: 1,
    borderColor: colors.danger,
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: 4,
    marginBottom: 24,
  },
  reportarButtonPressed: { backgroundColor: colors.danger },
  reportarButtonText: { color: colors.danger, fontWeight: '700', fontSize: 15 },
  modalBackdrop: { flex: 1, backgroundColor: 'rgba(7, 33, 30, 0.5)', justifyContent: 'flex-end' },
  sheet: { backgroundColor: colors.surface, borderTopLeftRadius: 20, borderTopRightRadius: 20, padding: 24 },
  sheetTitle: { fontSize: 18, fontWeight: '700', color: colors.ink900 },
  sheetSubtitle: { fontSize: 13, color: colors.ink600, marginTop: 4, marginBottom: 16 },
  motivosLista: { marginBottom: 16 },
  motivoItem: {
    borderWidth: 1,
    borderColor: colors.borderSoft,
    borderRadius: 10,
    padding: 14,
    marginBottom: 8,
  },
  motivoItemSeleccionado: { borderColor: colors.brandTeal700, backgroundColor: colors.brandAqua100 },
  motivoTexto: { fontSize: 15, color: colors.ink900 },
  motivoTextoSeleccionado: { fontWeight: '700', color: colors.brandTeal900 },
  comentarioLabel: { fontSize: 13, fontWeight: '600', color: colors.ink600, marginBottom: 6 },
  comentarioInput: {
    backgroundColor: colors.pageBg,
    borderWidth: 1,
    borderColor: colors.borderSoft,
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 14,
    color: colors.ink900,
    textAlignVertical: 'top',
    minHeight: 80,
    marginBottom: 20,
  },
  confirmButton: { backgroundColor: colors.brandTeal700, borderRadius: 10, paddingVertical: 14, alignItems: 'center' },
  confirmButtonPressed: { backgroundColor: colors.brandTeal900 },
  confirmButtonDisabled: { backgroundColor: colors.ink400 },
  confirmButtonText: { color: '#fff', fontWeight: '700', fontSize: 15 },
  cancelButton: { alignItems: 'center', paddingVertical: 14 },
  cancelButtonText: { color: colors.ink600, fontWeight: '600' },
});
