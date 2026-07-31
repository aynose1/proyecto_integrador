import * as SecureStore from 'expo-secure-store';

import { API_BASE_URL } from '../config/api';

const ACCESS_TOKEN_KEY = 'pi_access_token';
const REFRESH_TOKEN_KEY = 'pi_refresh_token';

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

export async function getAccessToken() {
  return SecureStore.getItemAsync(ACCESS_TOKEN_KEY);
}

export async function getRefreshToken() {
  return SecureStore.getItemAsync(REFRESH_TOKEN_KEY);
}

export async function saveTokens(tokens) {
  await SecureStore.setItemAsync(ACCESS_TOKEN_KEY, tokens.access_token);
  await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, tokens.refresh_token);
}

export async function clearTokens() {
  await SecureStore.deleteItemAsync(ACCESS_TOKEN_KEY);
  await SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY);
}

async function parseErrorMessage(response) {
  try {
    const data = await response.json();
    return data.detail || 'Ocurrió un error inesperado.';
  } catch {
    return 'Ocurrió un error inesperado.';
  }
}

async function refreshAccessToken() {
  const refreshToken = await getRefreshToken();
  if (!refreshToken) return null;

  const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!response.ok) {
    await clearTokens();
    return null;
  }

  const data = await response.json();
  await saveTokens(data);
  return data.access_token;
}

/**
 * Fetch autenticado hacia la API: agrega el header Authorization,
 * intenta refrescar el token UNA vez si la respuesta es 401 (por si
 * expiró), y lanza ApiError con el mensaje que manda el backend si algo
 * falla, para que las pantallas solo tengan que mostrar error.message.
 */
export async function apiFetch(path, options = {}) {
  const token = await getAccessToken();

  const doFetch = async (accessToken) =>
    fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
        ...options.headers,
      },
    });

  let response = await doFetch(token);

  if (response.status === 401 && token) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      response = await doFetch(newToken);
    }
  }

  if (!response.ok) {
    throw new ApiError(await parseErrorMessage(response), response.status);
  }

  if (response.status === 204) return null;
  return response.json();
}
