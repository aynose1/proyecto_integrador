from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.core.rate_limit import limiter
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.db.session import get_db
from app.models.catalogos import TipoUsuario
from app.schemas.usuario import (
    AdminRegisterRequest,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    UsuarioCreate,
    UsuarioRead,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
def register_admin(
    request: Request,
    payload: AdminRegisterRequest,
    db: Session = Depends(get_db),
) -> UsuarioRead:
    """
    Auto-registro público solo para administradores (plataforma web).
    Los recolectores siguen siendo dados de alta por un administrador.
    """
    if crud.usuario.get_by_codigo(db, payload.codigo_usuario):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un usuario con ese código")

    tipo_admin = db.query(TipoUsuario).filter(TipoUsuario.tipo == "administrador").first()
    if not tipo_admin:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Catálogo tipos_usuarios incompleto: falta 'administrador'",
        )

    create_payload = UsuarioCreate(
        codigo_usuario=payload.codigo_usuario,
        nombre=payload.nombre,
        apellido_paterno=payload.apellido_paterno,
        apellido_materno=payload.apellido_materno,
        contrasena=payload.contrasena,
        id_tipo_usuario=tipo_admin.id,
    )
    return crud.usuario.create(db, create_payload)


@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
def login(request: Request, credentials: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """
    Login único para administradores y recolectores: ambos usan
    codigo_usuario + contrasena. El recolector nunca se auto-registra,
    solo un administrador lo da de alta previamente (POST /usuarios).
    """
    user = crud.usuario.authenticate(db, credentials.codigo_usuario, credentials.contrasena)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Código de usuario o contraseña incorrectos")

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    payload = decode_token(body.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token inválido o expirado")

    user = crud.usuario.get(db, int(payload["sub"]))
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario no encontrado")

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )
