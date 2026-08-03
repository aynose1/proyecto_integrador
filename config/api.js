/**
 * URL base de la API. Se lee de la variable de entorno
 * EXPO_PUBLIC_API_BASE_URL (definida en tu archivo .env, en la raíz del
 * proyecto — junto a package.json).
 *
 * Para cambiarla (IP local, ngrok, etc.):
 *   1. Edita el archivo ".env" en la raíz del proyecto.
 *   2. Reinicia "npx expo start" (las variables de entorno solo se leen
 *      al arrancar Metro, un cambio en caliente no se refleja solo).
 */
export const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL;

if (!API_BASE_URL) {
  console.warn(
    '[config/api.js] Falta EXPO_PUBLIC_API_BASE_URL. Crea un archivo ".env" ' +
      'en la raíz del proyecto (puedes copiar ".env.example") y reinicia "npx expo start".'
  );
}

/**
 * API Key de plataforma -- capa extra junto al JWT (defensa en
 * profundidad), la misma llave compartida que usa la web (ver
 * web/app/config.py::PLATFORM_API_KEY). Debe coincidir EXACTO con
 * PLATFORM_API_KEY en el .env del backend.
 *
 * AVISO: esta llave viaja embebida en el bundle de la app compilada --
 * cualquiera que descompile el .apk podría extraerla. Es una capa de
 * "defensa en profundidad" (una más, no la única), no un secreto
 * verdaderamente inviolable.
 */
export const PLATFORM_API_KEY = process.env.EXPO_PUBLIC_PLATFORM_API_KEY;

if (!PLATFORM_API_KEY) {
  console.warn(
    '[config/api.js] Falta EXPO_PUBLIC_PLATFORM_API_KEY en tu ".env". ' +
      'Sin ella, TODAS las peticiones a la API van a fallar (401).'
  );
}
