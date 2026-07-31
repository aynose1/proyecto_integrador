import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';

/**
 * Stack raíz de toda la app:
 * - "index"  → puerta de entrada, decide login vs (tabs) (ver app/index.js)
 * - "login"  → fuera de (tabs): antes de iniciar sesión no debe verse
 *              ninguna barra de tabs
 * - "(tabs)" → grupo con la barra de Tabs una vez logueado
 */
export default function RootLayout() {
  return (
    <>
      <StatusBar style="dark" />
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="index" />
        <Stack.Screen name="login" />
        <Stack.Screen name="(tabs)" />
      </Stack>
    </>
  );
}
