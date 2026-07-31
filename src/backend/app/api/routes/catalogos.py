from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.catalogos import (
    EstadoRead,
    MotivoIncidenciaRead,
    TipoNotificacionRead,
    TipoUsuarioRead,
)

router = APIRouter(prefix="/catalogos", tags=["catalogos"])


@router.get("/tipos-usuario", response_model=list[TipoUsuarioRead])
def listar_tipos_usuario(db: Session = Depends(get_db), _u: Usuario = Depends(get_current_user)):
    return crud.catalogos.tipo_usuario.get_multi(db, limit=1000)


@router.get("/estados", response_model=list[EstadoRead])
def listar_estados(db: Session = Depends(get_db), _u: Usuario = Depends(get_current_user)):
    return crud.catalogos.estado.get_multi(db, limit=1000)


@router.get("/motivos-incidencia", response_model=list[MotivoIncidenciaRead])
def listar_motivos_incidencia(db: Session = Depends(get_db), _u: Usuario = Depends(get_current_user)):
    return crud.catalogos.motivo_incidencia.get_multi(db, limit=1000)


@router.get("/tipos-notificacion", response_model=list[TipoNotificacionRead])
def listar_tipos_notificacion(db: Session = Depends(get_db), _u: Usuario = Depends(get_current_user)):
    return crud.catalogos.tipo_notificacion.get_multi(db, limit=1000)
