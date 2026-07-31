from app.crud.base import CRUDBase
from app.models.catalogos import Estado, MotivoIncidencia, TipoNotificacion, TipoUsuario
from pydantic import BaseModel


class _NoOp(BaseModel):
    """Estos catálogos no se crean/editan desde la API, solo se listan (se siembran por Alembic)."""
    pass


tipo_usuario = CRUDBase[TipoUsuario, _NoOp, _NoOp](TipoUsuario)
estado = CRUDBase[Estado, _NoOp, _NoOp](Estado)
motivo_incidencia = CRUDBase[MotivoIncidencia, _NoOp, _NoOp](MotivoIncidencia)
tipo_notificacion = CRUDBase[TipoNotificacion, _NoOp, _NoOp](TipoNotificacion)
