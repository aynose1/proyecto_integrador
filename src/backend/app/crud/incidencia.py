from datetime import date, datetime

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.catalogos import Estado
from app.models.incidencia import Incidencia
from app.schemas.incidencia import IncidenciaCreate, IncidenciaUpdate


class CRUDIncidencia(CRUDBase[Incidencia, IncidenciaCreate, IncidenciaUpdate]):
    def create_de_recolector(self, db: Session, obj_in: IncidenciaCreate, id_usuario: int) -> Incidencia:
        estado_pendiente = db.query(Estado).filter(Estado.estado == "pendiente").first()
        if not estado_pendiente:
            raise ValueError("El catálogo 'estados' no tiene un registro 'pendiente'. Revisa el seeder.")

        incidencia = Incidencia(
            id_contenedor=obj_in.id_contenedor,
            id_usuario=id_usuario,
            fecha_hora=datetime.utcnow(),
            id_motivo=obj_in.id_motivo,
            comentario=obj_in.comentario,
            id_estado=estado_pendiente.id,
        )
        db.add(incidencia)
        db.commit()
        db.refresh(incidencia)
        return incidencia

    def get_multi_por_estado(self, db: Session, estado: str | None = None) -> list[Incidencia]:
        query = db.query(Incidencia)
        if estado:
            query = query.join(Estado).filter(Estado.estado == estado)
        return query.order_by(Incidencia.fecha_hora.desc()).all()

    def get_multi_por_usuario(self, db: Session, id_usuario: int, fecha: date | None = None) -> list[Incidencia]:
        """
        Usado por la pestaña "Reportes" de la app móvil: el recolector
        solo ve SUS propios reportes (protección BOLA -- ver el mismo
        criterio que ya usa GET /rutas/me). fecha filtra por el día
        exacto en que se levantó el reporte, para el filtro de fecha
        de esa pantalla.
        """
        query = db.query(Incidencia).filter(Incidencia.id_usuario == id_usuario)
        if fecha is not None:
            query = query.filter(
                Incidencia.fecha_hora >= datetime.combine(fecha, datetime.min.time()),
                Incidencia.fecha_hora < datetime.combine(fecha, datetime.max.time()),
            )
        return query.order_by(Incidencia.fecha_hora.desc()).all()


incidencia = CRUDIncidencia(Incidencia)
