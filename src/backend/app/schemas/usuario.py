from pydantic import BaseModel, ConfigDict, Field

from app.schemas.catalogos import TipoUsuarioRead


class UsuarioBase(BaseModel):
    codigo_usuario: str = Field(max_length=20)
    nombre: str = Field(max_length=100)
    apellido_paterno: str = Field(max_length=100)
    apellido_materno: str | None = Field(default=None, max_length=100)


class UsuarioCreate(UsuarioBase):
    contrasena: str = Field(min_length=8)
    id_tipo_usuario: int


class UsuarioUpdate(BaseModel):
    nombre: str | None = Field(default=None, max_length=100)
    apellido_paterno: str | None = Field(default=None, max_length=100)
    apellido_materno: str | None = Field(default=None, max_length=100)
    contrasena: str | None = Field(default=None, min_length=8)
    id_tipo_usuario: int | None = None


class UsuarioRead(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tipo_usuario: TipoUsuarioRead


class AdminRegisterRequest(BaseModel):
    codigo_usuario: str = Field(max_length=20)
    nombre: str = Field(max_length=100)
    apellido_paterno: str = Field(max_length=100)
    apellido_materno: str | None = Field(default=None, max_length=100)
    contrasena: str = Field(min_length=8)


class LoginRequest(BaseModel):
    codigo_usuario: str
    contrasena: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str
