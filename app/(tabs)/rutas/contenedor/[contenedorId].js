import { useLocalSearchParams } from 'expo-router';

import ContenedorDetalleScreen from '../../../../screens/ContenedorDetalleScreen';

export default function ContenedorDetalleTab() {
  const { contenedorId } = useLocalSearchParams();
  return <ContenedorDetalleScreen contenedorId={contenedorId} />;
}
