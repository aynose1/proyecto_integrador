import { useState } from 'react';
import {
  SafeAreaView,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Text,
  TextInput,
  Pressable,
  ActivityIndicator,
  Alert,
  StyleSheet,
} from 'react-native';
import { useRouter } from 'expo-router';

import { colors } from '../theme';
import { login } from '../services/authService';

export default function LoginScreen() {
  const router = useRouter();
  const [codigoUsuario, setCodigoUsuario] = useState('');
  const [contrasena, setContrasena] = useState('');
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
    <SafeAreaView style={styles.safe}>
      <KeyboardAvoidingView style={styles.flex} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
          <Text style={styles.brand}>Echo-Bin</Text>
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
          <TextInput
            style={styles.input}
            value={contrasena}
            onChangeText={setContrasena}
            secureTextEntry
            autoCapitalize="none"
            placeholder="••••••••"
            placeholderTextColor={colors.ink400}
            editable={!cargando}
            onSubmitEditing={handleLogin}
          />

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
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.pageBg },
  flex: { flex: 1 },
  scroll: { flexGrow: 1, justifyContent: 'center', padding: 24 },
  brand: {
    fontSize: 15,
    fontWeight: '700',
    color: colors.brandTeal700,
    textAlign: 'center',
    marginBottom: 4,
    letterSpacing: 0.5,
  },
  title: { fontSize: 24, fontWeight: '700', color: colors.ink900, textAlign: 'center', marginBottom: 4 },
  subtitle: { fontSize: 14, color: colors.ink600, textAlign: 'center', marginBottom: 28 },
  label: { fontSize: 13, fontWeight: '600', color: colors.ink600, marginBottom: 6, marginTop: 14 },
  input: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.borderSoft,
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 15,
    color: colors.ink900,
  },
  button: {
    marginTop: 26,
    backgroundColor: colors.brandTeal700,
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonPressed: { backgroundColor: colors.brandTeal900 },
  buttonDisabled: { backgroundColor: colors.ink400 },
  buttonText: { color: '#ffffff', fontSize: 16, fontWeight: '700' },
});
