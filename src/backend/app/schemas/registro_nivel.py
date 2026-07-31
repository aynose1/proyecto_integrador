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

    Manda la distancia cruda medida por el sensor ultrasónico (cm desde
    el sensor hasta la basura), NO un porcentaje ya calculado — el
    backend hace la conversión usando la altura_cm configurada para
    ese contenedor. Así el firmware no necesita saber nada de
    porcentajes ni de la altura instalada.

    fecha_hora la puede mandar el dispositivo o, si no la manda, se usa
    la hora del servidor al recibir la petición.
    """
    codigo_contenedor: str = Field(max_length=50)
    distancia_cm: Decimal = Field(ge=0, description="Distancia medida por el sensor, en cm")
    fecha_hora: datetime | None = None


class RegistroNivelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_contenedor: int
    fecha_hora: datetime
    nivel_porcentaje: Decimal
    distancia_cm: Decimal | None
    origen: OrigenRegistro
