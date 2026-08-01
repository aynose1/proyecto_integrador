from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.registro_nivel import OrigenRegistro


class RegistroPesoSensorCreate(BaseModel):
    """
    Payload que manda el sensor de peso (celda de carga), autenticado
    con API Key (X-API-Key), igual que el de nivel — el dispositivo no
    es un usuario del sistema.

    A diferencia de nivel, aquí se manda directo el peso del CONTENIDO
    en Kg — el sensor ya lo aísla, no hace falta ningún dato de
    calibración del contenedor (no hay equivalente a altura_cm).

    fecha_hora la puede mandar el dispositivo o, si no la manda, se usa
    la hora del servidor al recibir la petición.
    """
    codigo_contenedor: str = Field(max_length=50)
    peso_kg: Decimal = Field(ge=0, description="Peso del contenido medido por el sensor, en Kg")
    fecha_hora: datetime | None = None


class RegistroPesoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_contenedor: int
    fecha_hora: datetime
    peso_kg: Decimal
    origen: OrigenRegistro
