from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.core.security import decode_token
from app.db.session import get_db
from app.models.usuario import Usuario

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No se proporcionó un token de acceso")

    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido o expirado")

    user = crud.usuario.get(db, int(payload["sub"]))
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario no encontrado")
    return user


def require_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if current_user.tipo_usuario.tipo != "administrador":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Se requiere rol de administrador")
    return current_user


def require_recolector(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if current_user.tipo_usuario.tipo != "recolector":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Se requiere rol de recolector")
    return current_user


def verify_device_api_key(x_api_key: str = Header(...)) -> None:
    """
    Autenticación del sistema embebido (sensores). No es un usuario con
    login, por eso usa una API Key fija en vez de JWT.
    """
    if x_api_key != settings.DEVICE_API_KEY:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "API Key inválida")
