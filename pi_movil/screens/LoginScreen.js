import { SafeAreaView, Text, StyleSheet } from 'react-native';

import { colors } from '../theme';

export default function LoginScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>Iniciar sesión</Text>
      <Text style={styles.subtitle}>El formulario real se conecta en el siguiente paso.</Text>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.pageBg, alignItems: 'center', justifyContent: 'center', padding: 20 },
  title: { fontSize: 22, fontWeight: '700', color: colors.ink900, marginBottom: 6 },
  subtitle: { fontSize: 14, color: colors.ink600, textAlign: 'center' },
});
