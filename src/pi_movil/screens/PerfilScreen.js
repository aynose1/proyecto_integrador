import { useEffect, useState } from 'react';
import { View, SafeAreaView, Text, Pressable, ActivityIndicator, Alert, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

import { colors, typography } from '../theme';
import Header from '../components/Header';
import { getPerfil, logout } from '../services/authService';

function Fila({ icono, label, valor }) {
  return (
    <View style={styles.fila}>
      <Ionicons name={icono} size={18} color={colors.ink600} />
      <View style={styles.filaTexto}>
        <Text style={styles.filaLabel}>{label}</Text>
        <Text style={styles.filaValor}>{valor}</Text>
      </View>
    </View>
  );
}

export default function PerfilScreen() {
  const router = useRouter();
  const [perfil, setPerfil] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [saliendo, setSaliendo] = useState(false);

  useEffect(() => {
    let activo = true;
    getPerfil()
      .then((data) => {
        if (activo) setPerfil(data);
      })
      .catch(() => {
        if (activo) setPerfil(null);
      })
      .finally(() => {
        if (activo) setCargando(false);
      });
    return () => {
      activo = false;
    };
  }, []);

  function confirmarSalir() {
    Alert.alert('Cerrar sesión', '¿Seguro que quieres cerrar tu sesión?', [
      { text: 'Cancelar', style: 'cancel' },
      { text: 'Cerrar sesión', style: 'destructive', onPress: salir },
    ]);
  }

  async function salir() {
    setSaliendo(true);
    await logout();
    router.replace('/login');
  }

  const iniciales = perfil
    ? `${(perfil.nombre || '?')[0]}${(perfil.apellido_paterno || '?')[0]}`.toUpperCase()
    : '..';

  return (
    <View style={styles.safe}>
      <Header title="Perfil" />
      <SafeAreaView style={styles.cuerpo}>
        {cargando ? (
          <ActivityIndicator size="large" color={colors.brandTeal700} style={{ marginTop: 40 }} />
        ) : (
          <>
            <View style={styles.tarjetaAvatar}>
              <View style={styles.avatarGrande}>
                <Text style={styles.avatarGrandeTexto}>{iniciales}</Text>
              </View>
              <Text style={styles.nombreCompleto}>
                {perfil ? `${perfil.nombre} ${perfil.apellido_paterno}` : 'Recolector'}
              </Text>
              <Text style={styles.rol}>Recolector</Text>
            </View>

            <View style={styles.listaCard}>
              <Fila icono="person-outline" label="Código de usuario" valor={perfil?.codigo_usuario || '—'} />
            </View>

            <Pressable
              style={({ pressed }) => [styles.salirButton, pressed && styles.salirButtonPressed]}
              onPress={confirmarSalir}
              disabled={saliendo}
            >
              {saliendo ? (
                <ActivityIndicator color={colors.danger} />
              ) : (
                <>
                  <Ionicons name="log-out-outline" size={18} color={colors.danger} />
                  <Text style={styles.salirButtonTexto}>Cerrar sesión</Text>
                </>
              )}
            </Pressable>
          </>
        )}
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.pageBg },
  cuerpo: { flex: 1, padding: 16 },

  tarjetaAvatar: { alignItems: 'center', paddingVertical: 24 },
  avatarGrande: {
    width: 76,
    height: 76,
    borderRadius: 38,
    backgroundColor: colors.brandAqua500,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  avatarGrandeTexto: { fontFamily: typography.bold, fontSize: 24, color: colors.brandTeal900 },
  nombreCompleto: { fontFamily: typography.bold, fontSize: 18, color: colors.ink900 },
  rol: { fontFamily: typography.regular, fontSize: 13, color: colors.ink600, marginTop: 2 },

  // Un solo contenedor con divisor -- mismo estilo "Ajustes de Android"
  // que ya usan Rutas y el detalle de ruta.
  listaCard: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.borderSoft,
    borderRadius: 14,
    overflow: 'hidden',
    marginBottom: 24,
  },
  fila: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingHorizontal: 16, paddingVertical: 14 },
  divisor: { height: 1, backgroundColor: colors.borderSoft, marginLeft: 46 },
  filaTexto: { flex: 1 },
  filaLabel: { fontFamily: typography.regular, fontSize: 12, color: colors.ink600 },
  filaValor: { fontFamily: typography.semibold, fontSize: 15, color: colors.ink900, marginTop: 1 },

  salirButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    borderWidth: 1,
    borderColor: colors.danger,
    borderRadius: 12,
    paddingVertical: 14,
  },
  salirButtonPressed: { backgroundColor: '#fbeceb' },
  salirButtonTexto: { fontFamily: typography.semibold, fontSize: 15, color: colors.danger },
});
