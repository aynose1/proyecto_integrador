from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.notificacion import Notificacion
from app.schemas.notificacion import NotificacionCreate


class CRUDNotificacion(CRUDBase[Notificacion, NotificacionCreate, NotificacionCreate]):
    def get_multi_por_usuario(self, db: Session, id_usuario: int) -> list[Notificacion]:
        return (
            db.query(Notificacion)
            .filter(Notificacion.id_usuario == id_usuario)
            .order_by(Notificacion.id.desc())
            .all()
        )

    def get_multi_todas(self, db: Session) -> list[Notificacion]:
        """
        Cualquier administrador ve todas las notificaciones: id_usuario
        es opcional a propósito (ver models/notificacion.py), porque
        este sistema no distingue "qué admin es dueño de qué contenedor".

        NOTA: por ahora este listado siempre viene vacío -- la única
        fuente que generaba Notificacion (la detección automática de
        discrepancias nivel/peso al recolectar) se quitó a propósito.
        El modelo/endpoint se deja tal cual como infraestructura lista
        para lo que se reemplace.
        """
        return db.query(Notificacion).order_by(Notificacion.id.desc()).all()

    def marcar_leida(self, db: Session, notif: Notificacion) -> Notificacion:
        notif.leida = True
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif


notificacion = CRUDNotificacion(Notificacion)
