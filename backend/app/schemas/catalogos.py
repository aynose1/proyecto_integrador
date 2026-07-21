from pydantic import BaseModel, ConfigDict


class TipoUsuarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tipo: str


class EstadoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    estado: str


class MotivoIncidenciaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    motivo: str


class TipoNotificacionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tipo: str
