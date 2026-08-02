import { useCallback, useState } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  Pressable,
  Modal,
  TextInput,
  Alert,
  ActivityIndicator,
  StyleSheet,
} from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { useFocusEffect } from 'expo-router';

import { colors } from '../theme';
import Header from '../components/Header';
import { getContenedorPorCodigo } from '../services/contenedoresService';
import { getMotivosIncidencia, reportarIncidencia } from '../services/incidenciasService';

export default function ReportarScreen() {
  const [permission, requestPermission] = useCameraPermissions();
  const [activo, setActivo] = useState(true);
  const [buscando, setBuscando] = useState(false);
  const [contenedor, setContenedor] = useState(null);

  const [motivos, setMotivos] = useState([]);
  const [motivoId, setMotivoId] = useState(null);
  const [comentario, setComentario] = useState('');
  const [enviando, setEnviando] = useState(false);

  useFocusEffect(
    useCallback(() => {
      setActivo(true);
      setContenedor(null);
      return () => setActivo(false);
    }, [])
  );

  async function handleScanned({ data }) {
    if (!activo || buscando) return;
    setActivo(false);
    setBuscando(true);
    try {
      const cont = await getContenedorPorCodigo(data);
      setContenedor(cont);
      setMotivoId(null);
      setComentario('');
      const listaMotivos = await getMotivosIncidencia();
      setMotivos(listaMotivos);
    } catch (error) {
      Alert.alert('No encontrado', 'No se encontró ningún contenedor con ese código.', [
        { text: 'Entendido', onPress: () => setActivo(true) },
      ]);
    } finally {
      setBuscando(false);
    }
  }

  function cancelar() {
    setContenedor(null);
    setActivo(true);
  }

  async function enviarReporte() {
    if (!motivoId) {
      Alert.alert('Falta el motivo', 'Elige qué está pasando con este contenedor.');
      return;
    }
    setEnviando(true);
    try {
      await reportarIncidencia(contenedor.id, motivoId, comentario.trim());
      Alert.alert('Listo', 'Se reportó la incidencia. Un administrador la va a revisar.');
      cancelar();
    } catch (error) {
      Alert.alert('Error', error.message || 'No se pudo enviar el reporte.');
    } finally {
      setEnviando(false);
    }
  }

  if (!permission) {
    return (
      <SafeAreaView style={styles.center}>
        <ActivityIndicator size="large" color={colors.brandTeal700} />
      </SafeAreaView>
    );
  }

  if (!permission.granted) {
    return (
      <SafeAreaView style={styles.center}>
        <Text style={styles.permisoTexto}>Necesitamos acceso a tu cámara para escanear códigos QR.</Text>
        <Pressable style={styles.permisoBoton} onPress={requestPermission}>
          <Text style={styles.permisoBotonTexto}>Dar permiso</Text>
        </Pressable>
      </SafeAreaView>
    );
  }

  return (
    <View style={styles.safe}>
      <Header title="Reportar" />

      <View style={styles.cameraWrapper}>
        <CameraView
          style={StyleSheet.absoluteFillObject}
          facing="back"
          barcodeScannerSettings={{ barcodeTypes: ['qr'] }}
          onBarcodeScanned={activo ? handleScanned : undefined}
        />
        <View style={styles.overlay} pointerEvents="none">
          <View style={styles.frame} />
          <Text style={styles.overlayText}>Apunta al código QR del contenedor a reportar</Text>
        </View>
        {buscando ? (
          <View style={styles.buscandoOverlay}>
            <ActivityIndicator size="large" color="#ffffff" />
          </View>
        ) : null}
      </View>

      {/* Bottom sheet: motivo + comentario, una vez identificado el contenedor */}
      <Modal visible={Boolean(contenedor)} transparent animationType="slide" onRequestClose={cancelar}>
        <View style={styles.modalBackdrop}>
          <View style={styles.sheet}>
            {contenedor ? (
              <>
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
                <Pressable style={styles.cancelButton} onPress={cancelar} disabled={enviando}>
                  <Text style={styles.cancelButtonText}>Cancelar</Text>
                </Pressable>
              </>
            ) : null}
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.surface },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.pageBg, padding: 24 },
  permisoTexto: { fontSize: 15, color: colors.ink900, textAlign: 'center', marginBottom: 16 },
  permisoBoton: { backgroundColor: colors.brandTeal700, borderRadius: 10, paddingVertical: 12, paddingHorizontal: 24 },
  permisoBotonTexto: { color: '#fff', fontWeight: '700' },
  cameraWrapper: { flex: 1, backgroundColor: '#000000' },
  overlay: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  frame: { width: 240, height: 240, borderWidth: 3, borderColor: colors.brandAqua500, borderRadius: 16 },
  overlayText: {
    color: '#ffffff',
    marginTop: 16,
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
    paddingHorizontal: 32,
  },
  buscandoOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.5)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  modalBackdrop: { flex: 1, backgroundColor: 'rgba(7, 33, 30, 0.5)', justifyContent: 'flex-end' },
  sheet: { backgroundColor: colors.surface, borderTopLeftRadius: 20, borderTopRightRadius: 20, padding: 24, maxHeight: '85%' },
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
