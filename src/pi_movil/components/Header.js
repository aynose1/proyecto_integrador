import { useEffect, useState } from 'react';
import { View, Text, Image, Pressable, Modal, StyleSheet, SafeAreaView } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

import { colors, typography } from '../theme';
import { getPerfil, logout } from '../services/authService';

/**
 * Barra superior fija de cada pestaña: logotipo real arriba a la
 * izquierda (assets/logo.png), título de la pestaña al centro, avatar
 * arriba a la derecha con el menú de "Cambiar de cuenta"/"Cerrar sesión".
 *
 * SafeAreaView vacío de abajo: pinta el inset superior (donde vive la
 * barra de notificaciones) del mismo teal oscuro que el header, para
 * que quede continuo en cualquier pantalla (incluida la de cámara, con
 * fondo negro).
 *
 * NOTA sobre "Cambiar de cuenta": la app solo guarda una sesión a la
 * vez, así que hace exactamente lo mismo que "Cerrar sesión" por
 * dentro -- se dejan como 2 opciones separadas solo por ser el patrón
 * que ya conoce la gente de Gmail/Classroom.
 */
export default function Header({ title }) {
  const router = useRouter();
  const [menuVisible, setMenuVisible] = useState(false);
  const [perfil, setPerfil] = useState(null);

  useEffect(() => {
    let activo = true;
    getPerfil()
      .then((data) => {
        if (activo) setPerfil(data);
      })
      .catch(() => {});
    return () => {
      activo = false;
    };
  }, []);

  async function salir() {
    setMenuVisible(false);
    await logout();
    router.replace('/login');
  }

  const iniciales = perfil
    ? `${(perfil.nombre || '?')[0]}${(perfil.apellido_paterno || '?')[0]}`.toUpperCase()
    : '..';

  return (
    <>
      <SafeAreaView style={{ backgroundColor: colors.brandTeal900 }} />
      <View style={styles.header}>
        <Image source={require('../assets/logo.png')} style={styles.logo} resizeMode="contain" />

        <Text style={styles.titulo} numberOfLines={1}>
          {title}
        </Text>

        <Pressable
          style={({ pressed }) => [styles.avatarButton, pressed && styles.avatarButtonPressed]}
          onPress={() => setMenuVisible(true)}
        >
          <Text style={styles.avatarTexto}>{iniciales}</Text>
        </Pressable>

        <Modal visible={menuVisible} transparent animationType="fade" onRequestClose={() => setMenuVisible(false)}>
          <Pressable style={styles.backdrop} onPress={() => setMenuVisible(false)}>
            <View style={styles.menu}>
              <Text style={styles.menuNombre}>
                {perfil ? `${perfil.nombre} ${perfil.apellido_paterno}` : 'Recolector'}
              </Text>
              {perfil?.codigo_usuario ? <Text style={styles.menuCodigo}>{perfil.codigo_usuario}</Text> : null}
              <View style={styles.menuDivider} />
              <Pressable style={({ pressed }) => [styles.menuItem, pressed && styles.menuItemPressed]} onPress={salir}>
                <Ionicons name="swap-horizontal-outline" size={18} color={colors.ink900} />
                <Text style={styles.menuItemTexto}>Cambiar de cuenta</Text>
              </Pressable>
              <Pressable style={({ pressed }) => [styles.menuItem, pressed && styles.menuItemPressed]} onPress={salir}>
                <Ionicons name="log-out-outline" size={18} color={colors.danger} />
                <Text style={[styles.menuItemTexto, { color: colors.danger }]}>Cerrar sesión</Text>
              </Pressable>
            </View>
          </Pressable>
        </Modal>
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
    // Sombra suave hacia el contenido de abajo, para que el header se
    // sienta como una capa propia y no un bloque plano pegado al resto.
    shadowColor: '#000',
    shadowOpacity: 0.18,
    shadowRadius: 6,
    shadowOffset: { width: 0, height: 2 },
    elevation: 4,
    zIndex: 10,
  },
  logo: {
    width: 46,
    height: 46,
  },
  titulo: {
    flex: 1,
    fontFamily: typography.bold,
    fontSize: 18,
    color: '#ffffff',
    letterSpacing: 0.2,
  },
  avatarButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.brandAqua500,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: 'rgba(255,255,255,0.25)',
  },
  avatarButtonPressed: { opacity: 0.85 },
  avatarTexto: { fontFamily: typography.bold, color: colors.brandTeal900, fontSize: 14 },
  backdrop: { flex: 1, backgroundColor: 'rgba(7, 33, 30, 0.4)' },
  menu: {
    position: 'absolute',
    top: 66,
    right: 16,
    backgroundColor: colors.surface,
    borderRadius: 14,
    paddingVertical: 8,
    minWidth: 224,
    borderWidth: 1,
    borderColor: colors.borderSoft,
    shadowColor: '#000',
    shadowOpacity: 0.18,
    shadowRadius: 16,
    shadowOffset: { width: 0, height: 6 },
    elevation: 8,
  },
  menuNombre: { fontFamily: typography.bold, fontSize: 15, color: colors.ink900, paddingHorizontal: 16, paddingTop: 8 },
  menuCodigo: { fontFamily: typography.regular, fontSize: 12, color: colors.ink600, paddingHorizontal: 16, paddingBottom: 8 },
  menuDivider: { height: 1, backgroundColor: colors.borderSoft, marginVertical: 4 },
  menuItem: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingHorizontal: 16, paddingVertical: 12 },
  menuItemPressed: { backgroundColor: colors.brandAqua100 },
  menuItemTexto: { fontFamily: typography.semibold, fontSize: 14, color: colors.ink900 },
});
