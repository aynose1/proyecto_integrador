import { View, Text, Image, StyleSheet, SafeAreaView } from 'react-native';

import { colors, typography } from '../theme';

/**
 * Barra superior fija de cada pestaña: logotipo real (assets/icon.png)
 * + título de la pestaña. El perfil/cerrar sesión se movieron a su
 * propia pestaña ("Perfil") -- antes vivían aquí como un botón de
 * avatar, mismo estilo que Google Classroom, pero se sentía estorboso.
 *
 * SafeAreaView vacío de abajo: pinta el inset superior (donde vive la
 * barra de notificaciones) del mismo teal oscuro que el header, para
 * que quede continuo en cualquier pantalla (incluida la de cámara, con
 * fondo negro).
 */
export default function Header({ title }) {
  return (
    <>
      <SafeAreaView style={{ backgroundColor: colors.brandTeal900 }} />
      <View style={styles.header}>
        <Image source={require('../assets/icon.png')} style={styles.logo} resizeMode="contain" />
        <Text style={styles.titulo} numberOfLines={1}>
          {title}
        </Text>
      </View>
    </>
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    gap: 12,
    backgroundColor: colors.brandTeal900,
    shadowColor: '#000',
    shadowOpacity: 0.18,
    shadowRadius: 6,
    shadowOffset: { width: 0, height: 2 },
    elevation: 4,
    zIndex: 10,
  },
  logo: { width: 46, height: 46 },
  titulo: {
    flex: 1,
    fontFamily: typography.bold,
    fontSize: 18,
    color: '#ffffff',
    letterSpacing: 0.2,
  },
});
