
export const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL;

if (!API_BASE_URL) {
  console.warn(
    '[config/api.js] Falta EXPO_PUBLIC_API_BASE_URL. Crea un archivo ".env" ' +
      'en la raíz del proyecto (puedes copiar ".env.example") y reinicia "npx expo start".'
  );
}

export const PLATFORM_API_KEY = process.env.EXPO_PUBLIC_PLATFORM_API_KEY;

if (!PLATFORM_API_KEY) {
  console.warn(
    '[config/api.js] Falta EXPO_PUBLIC_PLATFORM_API_KEY en tu ".env". ' +
      'Sin ella, TODAS las peticiones a la API van a fallar (401).'
  );
}
