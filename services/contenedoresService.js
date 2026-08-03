import { apiFetch } from './apiClient';

export async function getContenedor(contenedorId) {
  return apiFetch(`/contenedores/${contenedorId}`);
}

/**
 * Usado por la pestaña "Reportar": el recolector escanea el QR de
 * cualquier contenedor (no tiene que estar en una ruta de hoy, a
 * diferencia de "Escaneo Rápido") para poder reportarle una incidencia.
 */
export async function getContenedorPorCodigo(codigoContenedor) {
  return apiFetch(`/contenedores/qr/${encodeURIComponent(codigoContenedor)}`);
}
