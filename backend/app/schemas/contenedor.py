from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.catalogos import EstadoRead
from app.schemas.ubicacion import UbicacionRead


class ContenedorBase(BaseModel):
    nombre: str = Field(max_length=100)
    codigo_contenedor: str = Field(max_length=50)
    capacidad_max: Decimal = Field(gt=0)
    id_ubicacion: int
    id_estado: int


class ContenedorCreate(ContenedorBase):
    # nivel_actual no se recibe en creación: inicia en 0 y solo lo
    # actualiza el flujo de lecturas (sensor o vaciado manual).
    pass


class ContenedorUpdate(BaseModel):
    nombre: str | None = Field(default=None, max_length=100)
    capacidad_max: Decimal | None = Field(default=None, gt=0)
    id_ubicacion: int | None = None
    id_estado: int | None = None


class ContenedorRead(ContenedorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nivel_actual: Decimal
    ubicacion: UbicacionRead
    estado: EstadoRead


class ContenedorSummary(BaseModel):
    """Versión ligera para listados dentro de una ruta (sin anidar ubicación completa)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    codigo_contenedor: str
    nivel_actual: Decimal
    capacidad_max: Decimal
