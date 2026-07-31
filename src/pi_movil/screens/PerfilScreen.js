import { useEffect, useState } from 'react';
import { SafeAreaView, View, Text, Pressable, ActivityIndicator, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';

import { colors } from '../theme';
import { getPerfil, logout } from '../services/authService';

export default function PerfilScreen() {
  const router = useRouter();
  const [perfil, setPerfil] = useState(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    let activo = true;
    getPerfil()
      .then((data) => {
        if (activo) setPerfil(data);
      })
      .catch(() => {})
      .finally(() => {
        if (activo) setCargando(false);
      });
    return () => {
      activo = false;
    };
  }, []);

  async function handleLogout() {
    await logout();
    router.replace('/login');
  }

  if (cargando) {
    return (
      <SafeAreaView style={styles.center}>
        <ActivityIndicator size="large" color={colors.brandTeal700} />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.nombre}>
          {perfil ? `${perfil.nombre} ${perfil.apellido_paterno}` : 'Recolector'}
        </Text>
        {perfil?.codigo_usuario ? <Text style={styles.codigo}>{perfil.codigo_usuario}</Text> : null}
      </View>

      <Pressable
        style={({ pressed }) => [styles.logoutButton, pressed && styles.logoutButtonPressed]}
        onPress={handleLogout}
      >
        <Text style={styles.logoutText}>Cerrar sesión</Text>
      </Pressable>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.pageBg, padding: 20 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.pageBg },
  card: {
    backgroundColor: colors.brandAqua100,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.borderSoft,
    padding: 18,
    marginBottom: 24,
  },
  nombre: { fontSize: 18, fontWeight: '700', color: colors.ink900 },
  codigo: { fontSize: 13, color: colors.ink600, marginTop: 4 },
  logoutButton: { borderWidth: 1, borderColor: colors.danger, borderRadius: 10, paddingVertical: 14, alignItems: 'center' },
  logoutButtonPressed: { backgroundColor: colors.danger },
  logoutText: { color: colors.danger, fontWeight: '700', fontSize: 15 },
});
