import { Stack } from 'expo-router';

import { colors } from '../../../theme';

/**
 * Stack propio de la tab "Rutas": permite navegar
 * Lista de rutas -> Detalle de ruta -> Detalle de contenedor
 * sin salir de esta tab ni perder la barra inferior.
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
      <Stack.Screen name="index" options={{ title: 'Mis rutas' }} />
    </Stack>
  );
}
