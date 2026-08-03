import { apiFetch } from './apiClient';

const ESTADO_PENDIENTE = 'pendiente';

export function hoyISO() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

export async function getMisRutas(fecha) {
  const query = fecha ? `?fecha=${fecha}` : '';
  return apiFetch(`/rutas/me${query}`);
}

export async function getRutaDetalle(rutaId) {
  return apiFetch(`/rutas/${rutaId}`);
}

/**
 * Solo los contenedores pendientes de recolectar dentro de una ruta —
 * los ya recolectados no deben aparecer en la lista que ve el recolector.
 */
export function contenedoresPendientes(ruta) {
  return (ruta?.detalles || []).filter((d) => d.estado?.estado === ESTADO_PENDIENTE);
}

export async function marcarRecolectado(rutaId, codigoContenedor) {
  return apiFetch(`/rutas/${rutaId}/recolectar`, {
    method: 'POST',
    body: JSON.stringify({ codigo_contenedor: codigoContenedor }),
  });
}

/**
 * Busca, entre las rutas de HOY del recolector (no en su histórico
 * completo — una ruta vieja no debería seguir siendo accionable), en
 * cuál está pendiente el contenedor con ese código. Devuelve un arreglo
 * de coincidencias { ruta, detalle } — normalmente 0 o 1, pero puede
 * haber más de una si el mismo contenedor está en más de una ruta hoy.
 */
export async function buscarRutaPorContenedor(codigoContenedor) {
  const rutasHoy = await getMisRutas(hoyISO());
  const coincidencias = [];

  for (const resumen of rutasHoy) {
    const detalleRuta = await getRutaDetalle(resumen.id);
    const match = contenedoresPendientes(detalleRuta).find(
      (d) => d.contenedor.codigo_contenedor === codigoContenedor
    );
    if (match) {
      coincidencias.push({ ruta: detalleRuta, detalle: match });
    }
  }

  return coincidencias;
}
