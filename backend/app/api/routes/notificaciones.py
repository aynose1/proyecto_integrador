from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.notificacion import NotificacionRead

router = APIRouter(prefix="/notificaciones", tags=["notificaciones"])


@router.get("/me", response_model=list[NotificacionRead])
def listar_mis_notificaciones(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return crud.notificacion.get_multi_por_usuario(db, current_user.id)
