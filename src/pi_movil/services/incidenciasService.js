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
