import { View, ActivityIndicator } from 'react-native';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { useFonts, Inter_400Regular, Inter_600SemiBold, Inter_700Bold } from '@expo-google-fonts/inter';

import { colors } from '../theme';

/**
 * Stack raíz de toda la app:
 * - "index"  → puerta de entrada, decide login vs (tabs) (ver app/index.js)
 * - "login"  → fuera de (tabs): antes de iniciar sesión no debe verse
 *              ninguna barra de tabs
 * - "(tabs)" → grupo con la barra de Tabs una vez logueado
 *
 * useFonts() carga Inter (la misma familia que ya usa la web) UNA sola
 * vez aquí, antes de renderizar nada más -- si algún texto usara
 * fontFamily: 'Inter_700Bold' antes de que termine de cargar, React
 * Native simplemente ignoraría esa fuente (sin tronar), pero se vería
 * con la fuente del sistema por un instante y luego "saltaría" a Inter.
 * Bloquear el render hasta que esté lista evita ese salto visual.
 */
export default function RootLayout() {
  const [fontsLoaded] = useFonts({ Inter_400Regular, Inter_600SemiBold, Inter_700Bold });

  if (!fontsLoaded) {
    return (
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.pageBg }}>
        <ActivityIndicator size="large" color={colors.brandTeal700} />
      </View>
    );
  }

  return (
    <>
      <StatusBar style="light" />
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="index" />
        <Stack.Screen name="login" />
        <Stack.Screen name="(tabs)" />
      </Stack>
    </>
  );
}
