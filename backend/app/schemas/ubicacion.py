from pydantic import BaseModel, ConfigDict

from app.schemas.zona_sector import SectorRead


class UbicacionBase(BaseModel):
    id_sector: int


class UbicacionCreate(UbicacionBase):
    pass


class UbicacionUpdate(BaseModel):
    id_sector: int | None = None


class UbicacionRead(UbicacionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sector: SectorRead
