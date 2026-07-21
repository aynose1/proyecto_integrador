from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.registro_nivel import OrigenRegistro


class RegistroNivelSensorCreate(BaseModel):
    """
    Payload que manda el sistema embebido (autenticado con API Key, no JWT).
    Se identifica con codigo_contenedor (el mismo código impreso/QR del
    contenedor), no con el id interno autoincremental de la base de
    datos, que el firmware del dispositivo no tiene por qué conocer.
    fecha_hora la puede mandar el dispositivo o, si no la manda, se usa
    la hora del servidor al recibir la petición.
    """
    codigo_contenedor: str = Field(max_length=50)
    nivel_porcentaje: Decimal = Field(ge=0, le=100)
    fecha_hora: datetime | None = None


class RegistroNivelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_contenedor: int
    fecha_hora: datetime
    nivel_porcentaje: Decimal
    origen: OrigenRegistro
