import { View, StyleSheet } from 'react-native';
import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

import { colors, typography } from '../../theme';

// Ícono con variante "outline" (inactivo) y "sólida" (activa), más una
// píldora de fondo aqua detrás del ícono activo -- remarca cuál pestaña
// está seleccionada más fuerte que solo cambiar el color.
function IconoTab({ focused, color, size, outline, solido }) {
  return (
    <View style={focused ? styles.pildora : undefined}>
      <Ionicons name={focused ? solido : outline} size={size} color={color} />
    </View>
  );
}

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.brandTeal700,
        tabBarInactiveTintColor: colors.ink400,
        tabBarStyle: { borderTopColor: colors.borderSoft, backgroundColor: colors.surface },
        tabBarLabelStyle: { fontFamily: typography.semibold, fontSize: 11 },
      }}
    >
      <Tabs.Screen
        name="rutas"
        options={{
          title: 'Rutas',
          tabBarIcon: ({ focused, color, size }) => (
            <IconoTab focused={focused} color={color} size={size} outline="map-outline" solido="map" />
          ),
        }}
      />
      <Tabs.Screen
        name="escaneo"
        options={{
          title: 'Escaneo Rápido',
          tabBarIcon: ({ focused, color, size }) => (
            <IconoTab focused={focused} color={color} size={size} outline="qr-code-outline" solido="qr-code" />
          ),
        }}
      />
      <Tabs.Screen
        name="reportes"
        options={{
          title: 'Reportes',
          tabBarIcon: ({ focused, color, size }) => (
            <IconoTab
              focused={focused}
              color={color}
              size={size}
              outline="document-text-outline"
              solido="document-text"
            />
          ),
        }}
      />
      <Tabs.Screen
        name="perfil"
        options={{
          title: 'Perfil',
          tabBarIcon: ({ focused, color, size }) => (
            <IconoTab focused={focused} color={color} size={size} outline="person-outline" solido="person" />
          ),
        }}
      />
    </Tabs>
  );
}

const styles = StyleSheet.create({
  pildora: {
    backgroundColor: colors.brandAqua100,
    borderRadius: 14,
    paddingHorizontal: 14,
    paddingVertical: 4,
  },
});
