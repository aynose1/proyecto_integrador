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
    pass


class SectorUpdate(BaseModel):
    nombre: str | None = Field(default=None, max_length=100)
    id_zona: int | None = None


class SectorRead(SectorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    zona: ZonaRead
