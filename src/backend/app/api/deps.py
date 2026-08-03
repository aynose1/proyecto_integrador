from fastapi import Depends, Header, HTTPException, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.core.security import decode_token
from app.db.session import get_db
from app.models.usuario import Usuario

bearer_scheme = HTTPBearer(auto_error=False)

# APIKeyHeader (no Header(...) a secas) a propósito: FastAPI la registra
# como esquema de seguridad en el OpenAPI/Swagger, así que /docs muestra
# un botón "Authorize" para esta llave, igual que ya lo hace para el
# Bearer JWT -- se mete una sola vez y todas las pruebas de "Try it out"
# ya la incluyen solas.
platform_api_key_scheme = APIKeyHeader(name="X-Platform-Key", auto_error=False)


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
    login, por eso usa una API Key fija en vez de JWT. Header distinto
    (X-API-Key) al de la plataforma (X-Platform-Key) a propósito: son
    dos actores y dos llaves completamente separadas.
    """
    if x_api_key != settings.DEVICE_API_KEY:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "API Key inválida")


def verify_platform_api_key(api_key: str | None = Depends(platform_api_key_scheme)) -> None:
    """
    Capa EXTRA de defensa en profundidad, aplicada a TODOS los endpoints
    de usuario (web + app móvil) junto con el JWT normal -- ver
    api/router.py, donde se aplica a nivel de router, no aquí endpoint
    por endpoint. No reemplaza el login/JWT: se necesitan ambos a la vez.
    """
    if api_key != settings.PLATFORM_API_KEY:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "API Key de plataforma inválida o faltante")
