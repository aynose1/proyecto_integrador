from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.notificacion import NotificacionRead

router = APIRouter(prefix="/notificaciones", tags=["notificaciones"])


@router.get("/me", response_model=list[NotificacionRead])
def listar_mis_notificaciones(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return crud.notificacion.get_multi_por_usuario(db, current_user.id)


@router.get("", response_model=list[NotificacionRead], dependencies=[Depends(require_admin)])
def listar_notificaciones(db: Session = Depends(get_db)):
    """
    Cualquier administrador ve TODAS las notificaciones generadas por el
    sistema (discrepancias nivel/peso al recolectar) — no están
    asignadas a un admin en particular, ver models/notificacion.py.
    """
    return crud.notificacion.get_multi_todas(db)


@router.patch("/{notificacion_id}", response_model=NotificacionRead, dependencies=[Depends(require_admin)])
def marcar_notificacion_leida(notificacion_id: int, db: Session = Depends(get_db)):
    notif = crud.notificacion.get(db, notificacion_id)
    if not notif:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notificación no encontrada")
    return crud.notificacion.marcar_leida(db, notif)
