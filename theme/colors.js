/**
 * Paleta de marca — los mismos tokens que web/app/static/css/main.css,
 * para que la app móvil se sienta parte del mismo sistema que la web.
 */
export const colors = {
  brandTeal950: '#07211e',
  brandTeal900: '#0b3b38',
  brandTeal800: '#0e4d47',
  brandTeal700: '#127a6c', // primario: botones, tabs activos
  brandTeal600: '#18917f',
  brandAqua500: '#17b8a6', // acento vivo
  brandAqua300: '#74e0d1',
  brandAqua100: '#e3f8f5', // fondos suaves, tarjetas de header

  // Acento "literal del sector": el verde real del símbolo universal de
  // reciclaje (no el teal/aqua de marca, que es más genérico-tech).
  // Uso deliberadamente restringido a estados de "ya se resolvió" --
  // ruta completada, reporte atendido -- para que funcione como un
  // acento con significado, no como un color más de fondo.
  recycleGreen: '#2e7d32',
  recycleGreenSoft: '#e6f2e6',

  ink900: '#13221f', // texto principal
  ink600: '#4c6360',
  ink400: '#7d928e', // texto muted / iconos inactivos

  pageBg: '#f1f8f7',
  surface: '#ffffff',
  borderSoft: 'rgba(11, 59, 56, 0.12)',

  danger: '#bf4a40',
  warning: '#dfa524',
};
