import { useState, useCallback } from 'react';
import {
  View,
  SafeAreaView,
  Text,
  Pressable,
  ActivityIndicator,
  Alert,
  Modal,
  TextInput,
  StyleSheet,
} from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { useFocusEffect } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

import { colors, typography } from '../theme';
import Header from '../components/Header';
import NivelBar from '../components/NivelBar';
import { buscarRutaPorContenedor, marcarRecolectado } from '../services/rutasService';
import { getContenedorPorCodigo } from '../services/contenedoresService';
import { getMotivosIncidencia, reportarIncidencia } from '../services/incidenciasService';

// modo del bottom sheet: null (cerrado) | 'eleccion' | 'elegirRuta' | 'confirmarRecoleccion' | 'reportar'
export default function EscaneoRapidoScreen() {
  const [permission, requestPermission] = useCameraPermissions();
  const [activo, setActivo] = useState(true);
  const [buscando, setBuscando] = useState(false);
  const [modo, setModo] = useState(null);

  const [contenedorInfo, setContenedorInfo] = useState(null);
  const [coincidenciasRuta, setCoincidenciasRuta] = useState([]);
  const [seleccionRuta, setSeleccionRuta] = useState(null);
  const [confirmando, setConfirmando] = useState(false);

  const [motivos, setMotivos] = useState([]);
  const [motivoId, setMotivoId] = useState(null);
  const [comentario, setComentario] = useState('');
  const [enviando, setEnviando] = useState(false);

  useFocusEffect(
    useCallback(() => {
      resetTodo();
      return () => setActivo(false);
    }, [])
  );

  function resetTodo() {
    setActivo(true);
    setModo(null);
    setContenedorInfo(null);
    setCoincidenciasRuta([]);
    setSeleccionRuta(null);
    setMotivoId(null);
    setComentario('');
  }

  async function handleScanned({ data }) {
    if (!activo || buscando) return;
    setActivo(false);
    setBuscando(true);
    try {
      const [cont, coincidencias] = await Promise.all([
        getContenedorPorCodigo(data),
        buscarRutaPorContenedor(data),
      ]);
      setContenedorInfo(cont);
      setCoincidenciasRuta(coincidencias);
      setModo('eleccion');
    } catch (error) {
      Alert.alert('No encontrado', 'No se encontró ningún contenedor con ese código.', [
        { text: 'Entendido', onPress: () => setActivo(true) },
      ]);
    } finally {
      setBuscando(false);
    }
  }

  function elegirMarcarRecolectado() {
    if (coincidenciasRuta.length === 0) return;
    if (coincidenciasRuta.length === 1) {
      setSeleccionRuta(coincidenciasRuta[0]);
      setModo('confirmarRecoleccion');
    } else {
      setModo('elegirRuta');
    }
  }

  async function elegirReportar() {
    setModo('reportar');
    if (motivos.length === 0) {
      try {
        const lista = await getMotivosIncidencia();
        setMotivos(lista);
      } catch {
        // si falla, el picker de motivos se queda vacío -- el usuario puede reintentar
      }
    }
  }

  async function confirmarRecoleccion() {
    if (!seleccionRuta) return;
    setConfirmando(true);
    try {
      await marcarRecolectado(seleccionRuta.ruta.id, seleccionRuta.detalle.contenedor.codigo_contenedor);
      Alert.alert('Listo', 'Contenedor marcado como recolectado.');
      resetTodo();
    } catch (error) {
      Alert.alert('Error', error.message || 'No se pudo confirmar la recolección.');
    } finally {
      setConfirmando(false);
    }
  }

  async function enviarReporte() {
    if (!motivoId) {
      Alert.alert('Falta el motivo', 'Elige qué está pasando con este contenedor.');
      return;
    }
    setEnviando(true);
    try {
      await reportarIncidencia(contenedorInfo.id, motivoId, comentario.trim());
      Alert.alert('Listo', 'Se reportó la incidencia. Un administrador la va a revisar.');
      resetTodo();
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
      <Header title="Escaneo Rápido" />

      <View style={styles.cameraWrapper}>
        <CameraView
          style={StyleSheet.absoluteFillObject}
          facing="back"
          barcodeScannerSettings={{ barcodeTypes: ['qr'] }}
          onBarcodeScanned={activo ? handleScanned : undefined}
        />
        <View style={styles.overlay} pointerEvents="none">
          <View style={styles.frame} />
          <Text style={styles.overlayText}>Apunta al código QR del contenedor</Text>
        </View>
        {buscando ? (
          <View style={styles.buscandoOverlay}>
            <ActivityIndicator size="large" color="#ffffff" />
          </View>
        ) : null}
      </View>

      <Modal visible={modo !== null} transparent animationType="slide" onRequestClose={resetTodo}>
        <View style={styles.modalBackdrop}>
          <View style={styles.sheet}>
            {/* ---------- Elegir qué hacer ---------- */}
            {modo === 'eleccion' && contenedorInfo && (
              <>
                <Text style={styles.sheetTitle}>{contenedorInfo.nombre}</Text>
                <Text style={styles.sheetSubtitle}>¿Qué quieres hacer con este contenedor?</Text>

                <Pressable
                  style={({ pressed }) => [
                    styles.opcionCard,
                    coincidenciasRuta.length === 0 && styles.opcionCardDisabled,
                    pressed && coincidenciasRuta.length > 0 && styles.opcionCardPressed,
                  ]}
                  onPress={elegirMarcarRecolectado}
                  disabled={coincidenciasRuta.length === 0}
                >
                  <View style={[styles.opcionIcono, { backgroundColor: colors.brandAqua100 }]}>
                    <Ionicons name="checkmark-circle-outline" size={22} color={colors.brandTeal700} />
                  </View>
                  <View style={styles.opcionTexto}>
                    <Text style={styles.opcionTitulo}>Marcar recolectado</Text>
                    <Text style={styles.opcionDescripcion}>
                      {coincidenciasRuta.length > 0
                        ? 'Está pendiente en tu ruta de hoy.'
                        : 'No está pendiente en ninguna ruta de hoy.'}
                    </Text>
                  </View>
                  <Ionicons name="chevron-forward" size={20} color={colors.ink400} />
                </Pressable>

                <Pressable
                  style={({ pressed }) => [styles.opcionCard, pressed && styles.opcionCardPressed]}
                  onPress={elegirReportar}
                >
                  <View style={[styles.opcionIcono, { backgroundColor: '#fbeee0' }]}>
                    <Ionicons name="warning-outline" size={22} color={colors.warning} />
                  </View>
                  <View style={styles.opcionTexto}>
                    <Text style={styles.opcionTitulo}>Reportar un problema</Text>
                    <Text style={styles.opcionDescripcion}>Sensor dañado, lectura errónea, etc.</Text>
                  </View>
                  <Ionicons name="chevron-forward" size={20} color={colors.ink400} />
                </Pressable>

                <Pressable style={styles.cancelButton} onPress={resetTodo}>
                  <Text style={styles.cancelButtonText}>Cancelar</Text>
                </Pressable>
              </>
            )}

            {/* ---------- Elegir en cuál ruta (si hay varias coincidencias) ---------- */}
            {modo === 'elegirRuta' && (
              <>
                <Text style={styles.sheetTitle}>Está pendiente en más de una ruta</Text>
                <Text style={styles.sheetSubtitle}>Elige en cuál confirmarlo:</Text>
                {coincidenciasRuta.map((c) => (
                  <Pressable
                    key={c.ruta.id}
                    style={({ pressed }) => [styles.opcionRuta, pressed && styles.opcionRutaPressed]}
                    onPress={() => {
                      setSeleccionRuta(c);
                      setModo('confirmarRecoleccion');
                    }}
                  >
                    <Text style={styles.opcionRutaTexto}>{c.ruta.nombre}</Text>
                  </Pressable>
                ))}
                <Pressable style={styles.cancelButton} onPress={() => setModo('eleccion')}>
                  <Text style={styles.cancelButtonText}>Regresar</Text>
                </Pressable>
              </>
            )}

            {/* ---------- Confirmar recolección ---------- */}
            {modo === 'confirmarRecoleccion' && seleccionRuta && (
              <>
                <Text style={styles.sheetTitle}>{seleccionRuta.detalle.contenedor.nombre}</Text>
                <Text style={styles.sheetSubtitle}>Ruta: {seleccionRuta.ruta.nombre}</Text>
                <View style={styles.sheetNivel}>
                  <NivelBar nivel={seleccionRuta.detalle.contenedor.nivel_actual} />
                </View>
                <Pressable
                  style={({ pressed }) => [styles.confirmButton, pressed && styles.confirmButtonPressed]}
                  onPress={confirmarRecoleccion}
                  disabled={confirmando}
                >
                  {confirmando ? (
                    <ActivityIndicator color="#ffffff" />
                  ) : (
                    <Text style={styles.confirmButtonText}>Marcar como recolectado</Text>
                  )}
                </Pressable>
                <Pressable style={styles.cancelButton} onPress={resetTodo} disabled={confirmando}>
                  <Text style={styles.cancelButtonText}>Cancelar</Text>
                </Pressable>
              </>
            )}

            {/* ---------- Reportar un problema ---------- */}
            {modo === 'reportar' && contenedorInfo && (
              <>
                <Text style={styles.sheetTitle}>Reportar incidencia</Text>
                <Text style={styles.sheetSubtitle}>{contenedorInfo.nombre}</Text>

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
                  {enviando ? <ActivityIndicator color="#ffffff" /> : <Text style={styles.confirmButtonText}>Enviar reporte</Text>}
                </Pressable>
                <Pressable style={styles.cancelButton} onPress={() => setModo('eleccion')} disabled={enviando}>
                  <Text style={styles.cancelButtonText}>Regresar</Text>
                </Pressable>
              </>
            )}
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.surface },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.pageBg, padding: 24 },
  permisoTexto: { fontFamily: typography.regular, fontSize: 15, color: colors.ink900, textAlign: 'center', marginBottom: 16 },
  permisoBoton: { backgroundColor: colors.brandTeal700, borderRadius: 10, paddingVertical: 12, paddingHorizontal: 24 },
  permisoBotonTexto: { fontFamily: typography.bold, color: '#fff' },
  cameraWrapper: { flex: 1, backgroundColor: '#000000' },
  overlay: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  frame: { width: 240, height: 240, borderWidth: 3, borderColor: colors.brandAqua500, borderRadius: 16 },
  overlayText: { fontFamily: typography.semibold, color: '#ffffff', marginTop: 16, fontSize: 14, textAlign: 'center', paddingHorizontal: 32 },
  buscandoOverlay: { ...StyleSheet.absoluteFillObject, backgroundColor: 'rgba(0,0,0,0.5)', alignItems: 'center', justifyContent: 'center' },
  modalBackdrop: { flex: 1, backgroundColor: 'rgba(7, 33, 30, 0.5)', justifyContent: 'flex-end' },
  sheet: { backgroundColor: colors.surface, borderTopLeftRadius: 22, borderTopRightRadius: 22, padding: 24, maxHeight: '85%' },
  sheetTitle: { fontFamily: typography.bold, fontSize: 18, color: colors.ink900 },
  sheetSubtitle: { fontFamily: typography.regular, fontSize: 13, color: colors.ink600, marginTop: 4, marginBottom: 18 },
  sheetNivel: { marginBottom: 20 },

  opcionCard: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    borderWidth: 1,
    borderColor: colors.borderSoft,
    borderRadius: 14,
    padding: 14,
    marginBottom: 10,
  },
  opcionCardPressed: { backgroundColor: colors.brandAqua100 },
  opcionCardDisabled: { opacity: 0.45 },
  opcionIcono: { width: 40, height: 40, borderRadius: 20, alignItems: 'center', justifyContent: 'center' },
  opcionTexto: { flex: 1 },
  opcionTitulo: { fontFamily: typography.semibold, fontSize: 15, color: colors.ink900 },
  opcionDescripcion: { fontFamily: typography.regular, fontSize: 12, color: colors.ink600, marginTop: 2 },

  confirmButton: { backgroundColor: colors.brandTeal700, borderRadius: 10, paddingVertical: 14, alignItems: 'center' },
  confirmButtonPressed: { backgroundColor: colors.brandTeal900 },
  confirmButtonDisabled: { backgroundColor: colors.ink400 },
  confirmButtonText: { fontFamily: typography.bold, color: '#fff', fontSize: 15 },
  cancelButton: { alignItems: 'center', paddingVertical: 14 },
  cancelButtonText: { fontFamily: typography.semibold, color: colors.ink600 },
  opcionRuta: { borderWidth: 1, borderColor: colors.borderSoft, borderRadius: 10, padding: 14, marginBottom: 10 },
  opcionRutaPressed: { backgroundColor: colors.brandAqua100 },
  opcionRutaTexto: { fontFamily: typography.semibold, fontSize: 15, color: colors.ink900 },

  motivosLista: { marginBottom: 16 },
  motivoItem: { borderWidth: 1, borderColor: colors.borderSoft, borderRadius: 10, padding: 14, marginBottom: 8 },
  motivoItemSeleccionado: { borderColor: colors.brandTeal700, backgroundColor: colors.brandAqua100 },
  motivoTexto: { fontFamily: typography.regular, fontSize: 15, color: colors.ink900 },
  motivoTextoSeleccionado: { fontFamily: typography.semibold, color: colors.brandTeal900 },
  comentarioLabel: { fontFamily: typography.semibold, fontSize: 13, color: colors.ink600, marginBottom: 6 },
  comentarioInput: {
    backgroundColor: colors.pageBg,
    borderWidth: 1,
    borderColor: colors.borderSoft,
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontFamily: typography.regular,
    fontSize: 14,
    color: colors.ink900,
    textAlignVertical: 'top',
    minHeight: 80,
    marginBottom: 20,
  },
});
