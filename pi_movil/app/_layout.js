import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';

/**
 * Stack raíz de toda la app.
 * - "login" vive AFUERA de (tabs): antes de iniciar sesión no debe verse
 *   ninguna barra de tabs.
 * - "(tabs)" es el grupo con la barra de Tabs (Rutas / Escanear QR / Perfil),
 *   ver app/(tabs)/_layout.js.
 *
 * Nota: por ahora esto NO redirige solo si no hay sesión — eso se agrega
 * en el siguiente paso, cuando construyamos el login real con
 * expo-secure-store.
 */
export default function RootLayout() {
  return (
    <>
      <StatusBar style="dark" />
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="login" />
        <Stack.Screen name="(tabs)" />
      </Stack>
    </>
  );
}
