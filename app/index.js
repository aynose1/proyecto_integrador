import { useEffect } from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';

import { colors } from '../theme';
import { hasSession } from '../services/authService';

/**
 * Pantalla "puerta": decide a dónde mandar al usuario apenas abre la
 * app (login si no hay sesión guardada, o directo a Rutas si ya la
 * hay), antes de mostrar cualquier otra pantalla.
 */
export default function Index() {
  const router = useRouter();

  useEffect(() => {
    let activo = true;
    hasSession().then((logueado) => {
      if (!activo) return;
      router.replace(logueado ? '/(tabs)/rutas' : '/login');
    });
    return () => {
      activo = false;
    };
  }, []);

  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color={colors.brandTeal700} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.pageBg },
});
