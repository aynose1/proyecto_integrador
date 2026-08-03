import { API_BASE_URL } from '../config/api';
import { apiFetch, saveTokens, clearTokens, getAccessToken, ApiError } from './apiClient';

/**
 * Inicia sesión y valida que la cuenta sea de un RECOLECTOR — esta app
 * es solo para ellos. Si el login es válido pero la cuenta es de
 * administrador (u otro tipo), se descartan los tokens y se rechaza.
 */
export async function login(codigoUsuario, contrasena) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ codigo_usuario: codigoUsuario, contrasena }),
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new ApiError('Código de usuario o contraseña incorrectos.', 401);
    }
    throw new ApiError('No se pudo iniciar sesión. Intenta de nuevo.', response.status);
  }

  const tokens = await response.json();
  await saveTokens(tokens);

  try {
    const perfil = await apiFetch('/usuarios/me');
    if (perfil?.tipo_usuario?.tipo !== 'recolector') {
      await clearTokens();
      throw new ApiError('Esta aplicación es solo para recolectores.', 403);
    }
    return perfil;
  } catch (error) {
    await clearTokens();
    throw error;
  }
}

export async function logout() {
  await clearTokens();
}

export async function hasSession() {
  const token = await getAccessToken();
  return Boolean(token);
}

export async function getPerfil() {
  return apiFetch('/usuarios/me');
}
