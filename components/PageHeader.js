import { View, Text, StyleSheet } from 'react-native';

import { colors } from '../theme';

/**
 * Misma idea que .page-header de la web: tarjeta con fondo aqua suave
 * que envuelve título + descripción, a todo el ancho.
 */
export default function PageHeader({ title, subtitle }) {
  return (
    <View style={styles.card}>
      <Text style={styles.title}>{title}</Text>
      {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.brandAqua100,
    borderWidth: 1,
    borderColor: colors.borderSoft,
    borderRadius: 12,
    padding: 16,
    margin: 16,
    marginBottom: 8,
  },
  title: { fontSize: 18, fontWeight: '700', color: colors.ink900 },
  subtitle: { fontSize: 13, color: colors.ink600, marginTop: 2 },
});
