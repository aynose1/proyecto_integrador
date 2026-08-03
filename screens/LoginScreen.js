import { useState } from 'react';
import {
  SafeAreaView,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Image,
  View,
  Text,
  TextInput,
  Pressable,
  ActivityIndicator,
  Alert,
  StyleSheet,
} from 'react-native';
import { useRouter } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';

import { colors, typography } from '../theme';
import { login } from '../services/authService';

export default function LoginScreen() {
  const router = useRouter();
  const [codigoUsuario, setCodigoUsuario] = useState('');
  const [contrasena, setContrasena] = useState('');
  const [verContrasena, setVerContrasena] = useState(false);
  const [cargando, setCargando] = useState(false);

  const puedeEnviar = codigoUsuario.trim().length > 0 && contrasena.length > 0 && !cargando;

  async function handleLogin() {
    if (!puedeEnviar) return;
    setCargando(true);
    try {
      await login(codigoUsuario.trim(), contrasena);
      router.replace('/(tabs)/rutas');
    } catch (error) {
      Alert.alert('No se pudo iniciar sesión', error.message || 'Intenta de nuevo.');
    } finally {
      setCargando(false);
    }
  }

  return (
    <View style={styles.safe}>
      {/* Fondo claro en el cuerpo -- sobreescribe el "light" (íconos
          claros) que es el global en app/_layout.js para las pestañas
          con header oscuro. Aquí el panel superior SÍ es oscuro, pero
          el resto de la pantalla es clara. */}
      <StatusBar style="light" />
      <KeyboardAvoidingView style={styles.flex} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
          {/* ---------- Panel de marca ---------- */}
          <SafeAreaView style={styles.panelMarca}>
            <Image source={require('../assets/icon.png')} style={styles.logo} resizeMode="contain" />
            <Text style={styles.marcaNombre}>Echo-Bin</Text>
            <Text style={styles.marcaTagline}>Gestión de recolección de residuos</Text>
          </SafeAreaView>

          {/* ---------- Formulario ---------- */}
          <View style={styles.formulario}>
            <Text style={styles.title}>Iniciar sesión</Text>
            <Text style={styles.subtitle}>Acceso exclusivo para recolectores.</Text>

            <Text style={styles.label}>Código de usuario</Text>
            <TextInput
              style={styles.input}
              value={codigoUsuario}
              onChangeText={setCodigoUsuario}
              autoCapitalize="none"
              autoCorrect={false}
              placeholder="Ej. REC001"
              placeholderTextColor={colors.ink400}
              editable={!cargando}
            />

            <Text style={styles.label}>Contraseña</Text>
            <View style={styles.inputConIcono}>
              <TextInput
                style={styles.inputInterno}
                value={contrasena}
                onChangeText={setContrasena}
                secureTextEntry={!verContrasena}
                autoCapitalize="none"
                placeholder="••••••••"
                placeholderTextColor={colors.ink400}
                editable={!cargando}
                onSubmitEditing={handleLogin}
              />
              <Pressable onPress={() => setVerContrasena((v) => !v)} style={styles.iconoOjo} hitSlop={10}>
                <Ionicons name={verContrasena ? 'eye-off-outline' : 'eye-outline'} size={20} color={colors.ink600} />
              </Pressable>
            </View>

            <Pressable
              style={({ pressed }) => [
                styles.button,
                !puedeEnviar && styles.buttonDisabled,
                pressed && puedeEnviar && styles.buttonPressed,
              ]}
              onPress={handleLogin}
              disabled={!puedeEnviar}
            >
              {cargando ? <ActivityIndicator color="#ffffff" /> : <Text style={styles.buttonText}>Entrar</Text>}
            </Pressable>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.brandTeal900 },
  flex: { flex: 1 },
  scroll: { flexGrow: 1 },

  // Panel superior de marca: mismo teal oscuro que el header del resto
  // de la app, para que el login se sienta parte del mismo sistema
  // desde el primer segundo, no una pantalla aparte genérica.
  panelMarca: {
    backgroundColor: colors.brandTeal900,
    alignItems: 'center',
    paddingTop: 32,
    paddingBottom: 40,
    borderBottomLeftRadius: 28,
    borderBottomRightRadius: 28,
  },
  logo: { width: 84, height: 84, marginBottom: 12 },
  marcaNombre: { fontFamily: typography.bold, fontSize: 24, color: '#ffffff', letterSpacing: 0.3 },
  marcaTagline: { fontFamily: typography.regular, fontSize: 13, color: colors.brandAqua300, marginTop: 4 },

  formulario: { flex: 1, backgroundColor: colors.pageBg, padding: 24, paddingTop: 32 },
  title: { fontFamily: typography.bold, fontSize: 20, color: colors.ink900 },
  subtitle: { fontFamily: typography.regular, fontSize: 13, color: colors.ink600, marginTop: 4, marginBottom: 24 },
  label: { fontFamily: typography.semibold, fontSize: 13, color: colors.ink600, marginBottom: 6, marginTop: 14 },
  input: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.borderSoft,
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontFamily: typography.regular,
    fontSize: 15,
    color: colors.ink900,
  },
  inputConIcono: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.borderSoft,
    borderRadius: 10,
    paddingHorizontal: 14,
  },
  inputInterno: {
    flex: 1,
    paddingVertical: 12,
    fontFamily: typography.regular,
    fontSize: 15,
    color: colors.ink900,
  },
  iconoOjo: { paddingLeft: 10, paddingVertical: 4 },
  button: {
    marginTop: 28,
    backgroundColor: colors.brandTeal700,
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonPressed: { backgroundColor: colors.brandTeal900 },
  buttonDisabled: { backgroundColor: colors.ink400 },
  buttonText: { fontFamily: typography.bold, fontSize: 16, color: '#ffffff' },
});
