from datetime import date, time

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.catalogos import EstadoRead
from app.schemas.contenedor import ContenedorSummary


class RutaBase(BaseModel):
    nombre: str = Field(max_length=100)
    id_usuario: int  # recolector asignado
    fecha: date
    hora_inicio: time | None = None
    hora_fin: time | None = None


class RutaCreate(RutaBase):
    # Lista de contenedores a incluir en la ruta al crearla
    ids_contenedores: list[int] = Field(min_length=1)


class RutaUpdate(BaseModel):
    nombre: str | None = Field(default=None, max_length=100)
    id_usuario: int | None = None
    fecha: date | None = None
    hora_inicio: time | None = None
    hora_fin: time | None = None
    ids_contenedores: list[int] | None = None  # si se manda, reemplaza el detalle completo


class RecolectarContenedorRequest(BaseModel):
    """Body que manda la app móvil al escanear el QR de un contenedor dentro de una ruta."""
    codigo_contenedor: str = Field(max_length=50)


class DetalleRutaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    orden: int
    contenedor: ContenedorSummary
    estado: EstadoRead


class RutaRead(RutaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    detalles: list[DetalleRutaRead] = []


class RutaSummary(BaseModel):
    """Para listados (sin el detalle completo de contenedores)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    fecha: date
    hora_inicio: time | None
    hora_fin: time | None
