import { apiFetch } from './apiClient';

export async function getContenedor(contenedorId) {
  return apiFetch(`/contenedores/${contenedorId}`);
}
