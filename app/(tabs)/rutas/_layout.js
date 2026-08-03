import { Stack } from 'expo-router';

import { colors } from '../../../theme';

/**
 * Stack propio de la tab "Rutas": permite navegar
 * Lista de rutas -> Detalle de ruta -> Detalle de contenedor
 * sin salir de esta tab ni perder la barra inferior.
 *
 * "index" (RutasScreen) ya trae su PROPIO header (componente <Header>,
 * teal oscuro, con logo/avatar) -- por eso headerShown:false ahí
 * específicamente. Sin esto, el header nativo de este Stack (fondo
 * blanco, título "Mis rutas") se queda encimado arriba del header
 * personalizado, mostrando los dos a la vez.
 *
 * Las otras 2 pantallas ([rutaId], contenedor/[contenedorId]) SÍ
 * necesitan el header nativo -- es de donde sale el botón de "regresar"
 * al navegar hacia adentro, y ninguna de esas 2 trae su propio <Header>.
 */
export default function RutasStackLayout() {
  return (
    <Stack
      screenOptions={{
        headerStyle: { backgroundColor: colors.surface },
        headerTintColor: colors.ink900,
        headerShadowVisible: false,
      }}
    >
      <Stack.Screen name="index" options={{ headerShown: false }} />
      <Stack.Screen name="[rutaId]" options={{ title: 'Detalle de ruta' }} />
      <Stack.Screen name="contenedor/[contenedorId]" options={{ title: 'Contenedor' }} />
    </Stack>
  );
}
