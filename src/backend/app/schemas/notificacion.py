from pydantic import BaseModel, ConfigDict, Field

from app.schemas.catalogos import TipoNotificacionRead


class NotificacionCreate(BaseModel):
    contenido: str = Field(max_length=2000)
    id_contenedor: int
    id_tipo_notificacion: int
    id_usuario: int


class NotificacionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    contenido: str
    id_contenedor: int
    tipo_notificacion: TipoNotificacionRead
    id_usuario: int
