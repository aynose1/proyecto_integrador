import { SafeAreaView, Text, StyleSheet } from 'react-native';

import { colors } from '../theme';

export default function EscanearScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>Escanear QR</Text>
      <Text style={styles.subtitle}>Aquí vas a escanear el código de un contenedor.</Text>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.pageBg, padding: 20 },
  title: { fontSize: 20, fontWeight: '700', color: colors.ink900, marginBottom: 6 },
  subtitle: { fontSize: 14, color: colors.ink600 },
});
