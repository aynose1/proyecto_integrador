import { useEffect, useState } from 'react';
import { View, Text, Image, Pressable, Modal, StyleSheet, SafeAreaView } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

import { colors, typography } from '../theme';
import { getPerfil, logout } from '../services/authService';

/**
 * Barra superior fija de cada pestaña, igual esquema que el header
 * nuevo de la web (fondo teal-900, acento aqua): logotipo arriba a la
 * izquierda, título de la pestaña en el centro, avatar arriba a la
 * derecha que abre el menú de "Cambiar de cuenta" / "Cerrar sesión".
 *
 * LOGOTIPO: por ahora usa assets/icon.png (el placeholder teal con
 * "PI" que ya existe en el proyecto) porque es el único archivo que
 * tengo garantizado que existe -- si apunto a un archivo que no
 * existe, el build de Expo truena. Para poner el logo real: agrega tu
 * archivo (ej. assets/logo.png, fondo transparente, recomendado ~200px
 * de alto) y cambia la línea del require() más abajo.
 *
 * SafeAreaView vacío de abajo: ver la nota larga que ya se dejó en
 * versiones anteriores de este archivo -- pinta el inset superior
 * (donde vive la barra de notificaciones) del mismo teal oscuro que el
 * header, para que quede continuo en cualquier pantalla (incluida la
 * de cámara, con fondo negro).
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
        {/* LOGOTIPO -- cambia este require() por tu archivo real cuando lo tengas */}
        <Image source={require('../assets/icon.png')} style={styles.logo} resizeMode="contain" />

        <Text style={styles.titulo} numberOfLines={1}>
          {title}
        </Text>

        <Pressable style={styles.avatarButton} onPress={() => setMenuVisible(true)}>
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
    paddingVertical: 10,
    gap: 12,
    backgroundColor: colors.brandTeal900,
  },
  logo: {
    width: 32,
    height: 32,
  },
  titulo: {
    flex: 1,
    fontFamily: typography.bold,
    fontSize: 17,
    color: '#ffffff',
    letterSpacing: 0.2,
  },
  avatarButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.brandAqua500,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarTexto: { fontFamily: typography.bold, color: colors.brandTeal900, fontSize: 13 },
  backdrop: { flex: 1, backgroundColor: 'rgba(7, 33, 30, 0.4)' },
  menu: {
    position: 'absolute',
    top: 60,
    right: 16,
    backgroundColor: colors.surface,
    borderRadius: 12,
    paddingVertical: 8,
    minWidth: 220,
    borderWidth: 1,
    borderColor: colors.borderSoft,
    shadowColor: '#000',
    shadowOpacity: 0.15,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 4 },
    elevation: 6,
  },
  menuNombre: { fontFamily: typography.bold, fontSize: 15, color: colors.ink900, paddingHorizontal: 16, paddingTop: 8 },
  menuCodigo: { fontFamily: typography.regular, fontSize: 12, color: colors.ink600, paddingHorizontal: 16, paddingBottom: 8 },
  menuDivider: { height: 1, backgroundColor: colors.borderSoft, marginVertical: 4 },
  menuItem: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingHorizontal: 16, paddingVertical: 12 },
  menuItemPressed: { backgroundColor: colors.brandAqua100 },
  menuItemTexto: { fontFamily: typography.semibold, fontSize: 14, color: colors.ink900 },
});
