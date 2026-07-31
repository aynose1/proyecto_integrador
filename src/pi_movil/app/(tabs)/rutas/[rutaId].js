import { useLocalSearchParams } from 'expo-router';

import RutaDetalleScreen from '../../../screens/RutaDetalleScreen';

export default function RutaDetalleTab() {
  const { rutaId } = useLocalSearchParams();
  return <RutaDetalleScreen rutaId={rutaId} />;
}
