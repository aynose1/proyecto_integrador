from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.catalogos import EstadoRead, MotivoIncidenciaRead


class IncidenciaCreate(BaseModel):
    """Reporte que levanta el recolector desde la vista de escaneo QR."""
    id_contenedor: int
    id_motivo: int
    comentario: str | None = Field(default=None, max_length=1000)


class IncidenciaUpdate(BaseModel):
    """Usado por el administrador para atender la incidencia."""
    id_estado: int


class IncidenciaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_contenedor: int
    id_usuario: int
    fecha_hora: datetime
    motivo: MotivoIncidenciaRead
    comentario: str | None
    estado: EstadoRead


class ContenedorVaciadoRequest(BaseModel):
    """Body vacío intencional: la acción 'marcar como vaciado' solo necesita
    el id_contenedor (en la ruta) y el usuario autenticado (del token)."""
    pass
