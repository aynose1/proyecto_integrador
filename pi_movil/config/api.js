/**
 * URL base de la API. Se lee de la variable de entorno
 * EXPO_PUBLIC_API_BASE_URL (definida en tu archivo .env, en la raíz del
 * proyecto — junto a package.json).
 *
 * Para cambiarla (IP local, ngrok, etc.):
 *   1. Edita el archivo ".env" en la raíz del proyecto.
 *   2. Reinicia "npx expo start" (las variables de entorno solo se leen
 *      al arrancar Metro, un cambio en caliente no se refleja solo).
 *
 * No importes process.env.EXPO_PUBLIC_API_BASE_URL directamente en otros
 * archivos — importa API_BASE_URL desde aquí, así hay un solo lugar que
 * sabe de dónde sale el valor.
 */
export const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL;

if (!API_BASE_URL) {
  // No se lanza un error para no tronar la app en desarrollo, pero es
  // imposible que funcione ninguna pantalla sin esto configurado.
  console.warn(
    '[config/api.js] Falta EXPO_PUBLIC_API_BASE_URL. Crea un archivo ".env" ' +
      'en la raíz del proyecto (puedes copiar ".env.example") y reinicia "npx expo start".'
  );
}
