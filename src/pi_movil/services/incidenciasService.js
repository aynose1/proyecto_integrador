import { apiFetch } from './apiClient';

export async function getMotivosIncidencia() {
  return apiFetch('/catalogos/motivos-incidencia');
}

export async function reportarIncidencia(idContenedor, idMotivo, comentario) {
  return apiFetch('/incidencias', {
    method: 'POST',
    body: JSON.stringify({
      id_contenedor: idContenedor,
      id_motivo: idMotivo,
      comentario: comentario || null,
    }),
  });
}

/**
 * Usado por la pestaña "Reportes": solo los reportes que levantó el
 * recolector que inició sesión (GET /incidencias/me, protegido contra
 * BOLA en el backend -- no puede ver los de nadie más).
 */
export async function getMisIncidencias() {
  return apiFetch('/incidencias/me');
}
