/**
 * Nombres de fuente de Inter (la misma familia que usa la web) --
 * se cargan una sola vez en app/_layout.js vía useFonts(), y estos
 * strings son los que hay que usar en cualquier fontFamily de la app.
 * Centralizarlos aquí evita escribir "Inter_700Bold" a mano en cada
 * StyleSheet y facilita cambiar de fuente en un solo lugar a futuro.
 */
export const typography = {
  regular: 'Inter_400Regular',
  semibold: 'Inter_600SemiBold',
  bold: 'Inter_700Bold',
};
