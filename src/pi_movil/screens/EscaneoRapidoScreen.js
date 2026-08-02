import { useState, useCallback } from 'react';
import { SafeAreaView, View, Text, Pressable, ActivityIndicator, Alert, Modal, StyleSheet } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { useFocusEffect } from 'expo-router';

import { colors } from '../theme';
import Header from '../components/Header';
import NivelBar from '../components/NivelBar';
import { buscarRutaPorContenedor, marcarRecolectado } from '../services/rutasService';

export default function EscaneoRapidoScreen() {
  const [permission, requestPermission] = useCameraPermissions();
  const [activo, setActivo] = useState(true);
  const [buscando, setBuscando] = useState(false);
  const [coincidencias, setCoincidencias] = useState(null);
  const [seleccion, setSeleccion] = useState(null);
  const [confirmando, setConfirmando] = useState(false);

  useFocusEffect(
    useCallback(() => {
      setActivo(true);
      setCoincidencias(null);
      setSeleccion(null);
      return () => setActivo(false);
    }, [])
  );

  async function handleScanned({ data }) {
    if (!activo || buscando) return;
    setActivo(false);
    setBuscando(true);
    try {
      const resultados = await buscarRutaPorContenedor(data);
      if (resultados.length === 0) {
        Alert.alert(
          'No encontrado',
          'Este contenedor no está pendiente en ninguna de tus rutas de hoy.',
          [{ text: 'Entendido', onPress: () => setActivo(true) }]
        );
      } else if (resultados.length === 1) {
        setSeleccion(resultados[0]);
      } else {
        setCoincidencias(resultados);
      }
    } catch (error) {
      Alert.alert('Error', error.message || 'No se pudo buscar el contenedor.', [
        { text: 'Entendido', onPress: () => setActivo(true) },
      ]);
    } finally {
      setBuscando(false);
    }
  }

  async function confirmarRecoleccion() {
    if (!seleccion) return;
    setConfirmando(true);
    try {
      await marcarRecolectado(seleccion.ruta.id, seleccion.detalle.contenedor.codigo_contenedor);
      Alert.alert('Listo', 'Contenedor marcado como recolectado.');
      setSeleccion(null);
      setCoincidencias(null);
      setActivo(true);
    } catch (error) {
      Alert.alert('Error', error.message || 'No se pudo confirmar la recolección.');
    } finally {
      setConfirmando(false);
    }
  }

  function cancelarSeleccion() {
    setSeleccion(null);
    setCoincidencias(null);
    setActivo(true);
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

      {/* Bottom sheet (Modal): una sola coincidencia -> confirmar recoleccion */}
      <Modal visible={Boolean(seleccion)} transparent animationType="slide" onRequestClose={cancelarSeleccion}>
        <View style={styles.modalBackdrop}>
          <View style={styles.sheet}>
            {seleccion ? (
              <>
                <Text style={styles.sheetTitle}>{seleccion.detalle.contenedor.nombre}</Text>
                <Text style={styles.sheetSubtitle}>Ruta: {seleccion.ruta.nombre}</Text>
                <View style={styles.sheetNivel}>
                  <NivelBar nivel={seleccion.detalle.contenedor.nivel_actual} />
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
                <Pressable style={styles.cancelButton} onPress={cancelarSeleccion} disabled={confirmando}>
                  <Text style={styles.cancelButtonText}>Cancelar</Text>
                </Pressable>
              </>
            ) : null}
          </View>
        </View>
      </Modal>

      {/* Bottom sheet (Modal): varias coincidencias -> elegir ruta */}
      <Modal visible={Boolean(coincidencias)} transparent animationType="slide" onRequestClose={cancelarSeleccion}>
        <View style={styles.modalBackdrop}>
          <View style={styles.sheet}>
            <Text style={styles.sheetTitle}>Está pendiente en más de una ruta</Text>
            <Text style={styles.sheetSubtitle}>Elige en cuál confirmarlo:</Text>
            {(coincidencias || []).map((c) => (
              <Pressable
                key={c.ruta.id}
                style={({ pressed }) => [styles.opcionRuta, pressed && styles.opcionRutaPressed]}
                onPress={() => {
                  setSeleccion(c);
                  setCoincidencias(null);
                }}
              >
                <Text style={styles.opcionRutaTexto}>{c.ruta.nombre}</Text>
              </Pressable>
            ))}
            <Pressable style={styles.cancelButton} onPress={cancelarSeleccion}>
              <Text style={styles.cancelButtonText}>Cancelar</Text>
            </Pressable>
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
  overlayText: { color: '#ffffff', marginTop: 16, fontSize: 14, fontWeight: '600' },
  buscandoOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.5)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  modalBackdrop: { flex: 1, backgroundColor: 'rgba(7, 33, 30, 0.5)', justifyContent: 'flex-end' },
  sheet: { backgroundColor: colors.surface, borderTopLeftRadius: 20, borderTopRightRadius: 20, padding: 24 },
  sheetTitle: { fontSize: 18, fontWeight: '700', color: colors.ink900 },
  sheetSubtitle: { fontSize: 13, color: colors.ink600, marginTop: 4, marginBottom: 16 },
  sheetNivel: { marginBottom: 20 },
  confirmButton: { backgroundColor: colors.brandTeal700, borderRadius: 10, paddingVertical: 14, alignItems: 'center' },
  confirmButtonPressed: { backgroundColor: colors.brandTeal900 },
  confirmButtonText: { color: '#fff', fontWeight: '700', fontSize: 15 },
  cancelButton: { alignItems: 'center', paddingVertical: 14 },
  cancelButtonText: { color: colors.ink600, fontWeight: '600' },
  opcionRuta: { borderWidth: 1, borderColor: colors.borderSoft, borderRadius: 10, padding: 14, marginBottom: 10 },
  opcionRutaPressed: { backgroundColor: colors.brandAqua100 },
  opcionRutaTexto: { fontSize: 15, fontWeight: '600', color: colors.ink900 },
});
