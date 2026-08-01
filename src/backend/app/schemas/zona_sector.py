from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ZonaBase(BaseModel):
    nombre: str = Field(max_length=100)


class ZonaCreate(ZonaBase):
    pass


class ZonaUpdate(BaseModel):
    nombre: str | None = Field(default=None, max_length=100)


class ZonaRead(ZonaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class SectorBase(BaseModel):
    nombre: str = Field(max_length=100)
    id_zona: int


class SectorCreate(SectorBase):
    # Opcionales: un sector se puede crear sin ubicar en el mapa todavía,
    # y capturarse después editándolo.
    latitud: Decimal | None = Field(default=None, ge=-90, le=90)
    longitud: Decimal | None = Field(default=None, ge=-180, le=180)


class SectorUpdate(BaseModel):
    nombre: str | None = Field(default=None, max_length=100)
    id_zona: int | None = None
    latitud: Decimal | None = Field(default=None, ge=-90, le=90)
    longitud: Decimal | None = Field(default=None, ge=-180, le=180)


class SectorRead(SectorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    latitud: Decimal | None
    longitud: Decimal | None
    zona: ZonaRead
