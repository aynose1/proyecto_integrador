import { SafeAreaView, Text, StyleSheet } from 'react-native';

import { colors } from '../theme';

export default function RutasScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>Mis rutas</Text>
      <Text style={styles.subtitle}>Aquí vas a ver tus rutas asignadas.</Text>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.pageBg, padding: 20 },
  title: { fontSize: 20, fontWeight: '700', color: colors.ink900, marginBottom: 6 },
  subtitle: { fontSize: 14, color: colors.ink600 },
});
