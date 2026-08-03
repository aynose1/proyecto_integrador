import { View, Text, StyleSheet } from 'react-native';

import { colors } from '../theme';

/**
 * Barra de nivel de llenado, mismos umbrales de color que el dashboard
 * web: <50% aqua, 50-80% ámbar, >=80% rojo.
 */
export default function NivelBar({ nivel }) {
  const pct = Math.max(0, Math.min(100, Number(nivel) || 0));
  const color = pct >= 80 ? colors.danger : pct >= 50 ? colors.warning : colors.brandAqua500;

  return (
    <View>
      <View style={styles.track}>
        <View style={[styles.fill, { width: `${pct}%`, backgroundColor: color }]} />
      </View>
      <Text style={styles.label}>{pct}%</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  track: { height: 10, borderRadius: 6, backgroundColor: colors.borderSoft, overflow: 'hidden' },
  fill: { height: '100%', borderRadius: 6 },
  label: { marginTop: 6, fontSize: 13, fontWeight: '700', color: colors.ink900 },
});
