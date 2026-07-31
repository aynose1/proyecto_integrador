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


notificacion = CRUDNotificacion(Notificacion)
