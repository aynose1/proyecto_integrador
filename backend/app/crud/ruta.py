from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.catalogos import Estado
from app.models.ruta import DetalleRuta, Ruta
from app.schemas.ruta import RutaCreate, RutaUpdate


def _estado_pendiente_id(db: Session) -> int:
    estado = db.query(Estado).filter(Estado.estado == "pendiente").first()
    if not estado:
        raise ValueError("El catálogo 'estados' no tiene un registro 'pendiente'. Revisa el seeder.")
    return estado.id


class CRUDRuta(CRUDBase[Ruta, RutaCreate, RutaUpdate]):
    def create(self, db: Session, obj_in: RutaCreate) -> Ruta:
        estado_pendiente_id = _estado_pendiente_id(db)
        ruta = Ruta(
            nombre=obj_in.nombre,
            id_usuario=obj_in.id_usuario,
            fecha=obj_in.fecha,
            hora_inicio=obj_in.hora_inicio,
            hora_fin=obj_in.hora_fin,
        )
        db.add(ruta)
        db.flush()  # para obtener ruta.id antes del commit

        for id_contenedor in obj_in.ids_contenedores:
            db.add(DetalleRuta(id_ruta=ruta.id, id_contenedor=id_contenedor, id_estado=estado_pendiente_id))

        db.commit()
        db.refresh(ruta)
        return ruta

    def update(self, db: Session, db_obj: Ruta, obj_in: RutaUpdate) -> Ruta:
        data = obj_in.model_dump(exclude_unset=True, exclude={"ids_contenedores"})
        for field, value in data.items():
            setattr(db_obj, field, value)

        if obj_in.ids_contenedores is not None:
            # Reemplaza el detalle completo de contenedores de la ruta.
            db.query(DetalleRuta).filter(DetalleRuta.id_ruta == db_obj.id).delete()
            estado_pendiente_id = _estado_pendiente_id(db)
            for id_contenedor in obj_in.ids_contenedores:
                db.add(DetalleRuta(id_ruta=db_obj.id, id_contenedor=id_contenedor, id_estado=estado_pendiente_id))

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_por_usuario(self, db: Session, id_usuario: int, skip: int = 0, limit: int = 100) -> list[Ruta]:
        """Usado por el recolector: solo sus propias rutas (protección BOLA)."""
        return (
            db.query(Ruta)
            .filter(Ruta.id_usuario == id_usuario)
            .offset(skip)
            .limit(limit)
            .all()
        )


ruta = CRUDRuta(Ruta)
