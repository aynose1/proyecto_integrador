import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

import { colors } from '../theme';

export default function EmptyState({ icon = 'file-tray-outline', title, subtitle }) {
  return (
    <View style={styles.container}>
      <Ionicons name={icon} size={40} color={colors.ink400} />
      {title ? <Text style={styles.title}>{title}</Text> : null}
      {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { alignItems: 'center', justifyContent: 'center', padding: 32 },
  title: { fontSize: 16, fontWeight: '700', color: colors.ink900, marginTop: 12, textAlign: 'center' },
  subtitle: { fontSize: 13, color: colors.ink600, marginTop: 4, textAlign: 'center' },
});
