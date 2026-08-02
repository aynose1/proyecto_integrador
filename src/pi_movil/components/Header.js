import { useEffect, useState } from 'react';
import { View, Text, Pressable, Modal, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

import { colors } from '../theme';
import { getPerfil, logout } from '../services/authService';

/**
 * Barra superior fija de cada pestaña (tipo Google Classroom): título +
 * un avatar circular arriba a la izquierda que abre un menú con
 * "Cambiar de cuenta" y "Cerrar sesión".
 *
 * NOTA: esta app no guarda varias cuentas en el dispositivo (solo hay
 * una sesión activa a la vez), así que "Cambiar de cuenta" hace
 * exactamente lo mismo que "Cerrar sesión" -- cierra la sesión actual y
 * manda a la pantalla de login para volver a entrar. Se dejan como dos
 * opciones separadas solo por ser el patrón que la gente ya conoce de
 * apps como Gmail/Classroom, no porque haya una diferencia real hoy.
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
    <View style={styles.header}>
      <Pressable style={styles.avatarButton} onPress={() => setMenuVisible(true)}>
        <Text style={styles.avatarTexto}>{iniciales}</Text>
      </Pressable>
      <Text style={styles.titulo} numberOfLines={1}>
        {title}
      </Text>
      <View style={styles.spacer} />

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
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.borderSoft,
  },
  avatarButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.brandTeal700,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarTexto: { color: '#ffffff', fontWeight: '700', fontSize: 13 },
  titulo: { flex: 1, textAlign: 'center', fontSize: 16, fontWeight: '700', color: colors.ink900 },
  spacer: { width: 36 },
  backdrop: { flex: 1, backgroundColor: 'rgba(7, 33, 30, 0.4)' },
  menu: {
    position: 'absolute',
    top: 60,
    left: 16,
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
  menuNombre: { fontSize: 15, fontWeight: '700', color: colors.ink900, paddingHorizontal: 16, paddingTop: 8 },
  menuCodigo: { fontSize: 12, color: colors.ink600, paddingHorizontal: 16, paddingBottom: 8 },
  menuDivider: { height: 1, backgroundColor: colors.borderSoft, marginVertical: 4 },
  menuItem: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingHorizontal: 16, paddingVertical: 12 },
  menuItemPressed: { backgroundColor: colors.brandAqua100 },
  menuItemTexto: { fontSize: 14, fontWeight: '600', color: colors.ink900 },
});
