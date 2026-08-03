from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.catalogos import EstadoRead
from app.schemas.zona_sector import SectorRead


class ContenedorBase(BaseModel):
    nombre: str = Field(max_length=100)
    codigo_contenedor: str = Field(max_length=50)
    capacidad_max: Decimal = Field(gt=0)
    id_sector: int
    id_estado: int


class ContenedorCreate(ContenedorBase):
    # altura_cm es obligatoria al crear: sin ella el endpoint del sensor
    # no puede convertir la distancia medida en un porcentaje de llenado.
    altura_cm: Decimal = Field(gt=0, description="Distancia en cm del sensor al fondo del contenedor vacío")


class ContenedorUpdate(BaseModel):
    nombre: str | None = Field(default=None, max_length=100)
    capacidad_max: Decimal | None = Field(default=None, gt=0)
    altura_cm: Decimal | None = Field(default=None, gt=0)
    id_sector: int | None = None
    id_estado: int | None = None


class ContenedorRead(ContenedorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nivel_actual: Decimal
    # Puede ser None en contenedores creados antes de este cambio, hasta
    # que el administrador la capture desde la web.
    altura_cm: Decimal | None
    # Última lectura del sensor de peso (Kg). No requiere calibración
    # previa como altura_cm — arranca en 0 hasta la primera lectura real.
    peso_actual: Decimal
    sector: SectorRead
    estado: EstadoRead


class ContenedorSummary(BaseModel):
    """Versión ligera para listados dentro de una ruta (sin anidar sector completa)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    codigo_contenedor: str
    nivel_actual: Decimal
    peso_actual: Decimal
    capacidad_max: Decimal
    # Agregado a propósito: la app móvil necesita saber si el contenedor
    # quedó Inactivo (ej. por un reporte de incidencia) para poder
    # ocultarlo de la lista de pendientes de una ruta -- antes este
    # campo no viajaba aquí, solo en ContenedorRead (la vista completa).
    estado: EstadoRead
