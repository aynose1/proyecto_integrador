from datetime import date

from sqlalchemy.orm import Session, selectinload

from app.crud.base import CRUDBase
from app.models.catalogos import Estado
from app.models.contenedor import Contenedor
from app.models.ruta import DetalleRuta, Ruta
from app.schemas.ruta import RutaCreate, RutaUpdate


def _estado_id_por_nombre(db: Session, nombre: str) -> int:
    estado = db.query(Estado).filter(Estado.estado == nombre).first()
    if not estado:
        raise ValueError(f"El catálogo 'estados' no tiene un registro '{nombre}'. Revisa el seeder.")
    return estado.id


def _estado_pendiente_id(db: Session) -> int:
    return _estado_id_por_nombre(db, "pendiente")


# Un detalle de ruta (contenedor DENTRO de una ruta) solo tiene sentido
# como pendiente o recolectado — nada de 'activo'/'inactivo' (eso es
# del contenedor en sí) ni 'atendido' (eso es de Incidencia). Mismo
# criterio que ya se aplicó a Contenedor.id_estado.
ESTADOS_VALIDOS_DETALLE_RUTA = {"pendiente", "recolectado"}

# La RUTA en sí (no sus contenedores) tiene su propio ciclo de vida,
# manual e independiente de si ya se recolectó todo.
ESTADOS_VALIDOS_RUTA = {"pendiente", "en progreso", "completada", "cancelada"}


class CRUDRuta(CRUDBase[Ruta, RutaCreate, RutaUpdate]):
    def _query_con_detalles(self, db: Session):
        # completada (y el listado de contenedores) necesitan detalles +
        # su estado ya cargados; sin esto cada acceso dispararía una
        # consulta nueva por ruta (N+1).
        return db.query(Ruta).options(
            selectinload(Ruta.detalles).joinedload(DetalleRuta.estado),
            selectinload(Ruta.detalles).joinedload(DetalleRuta.contenedor),
        )

    def get(self, db: Session, id: int) -> Ruta | None:
        return self._query_con_detalles(db).filter(Ruta.id == id).first()

    def get_multi(
        self, db: Session, skip: int = 0, limit: int = 100, fecha: date | None = None
    ) -> list[Ruta]:
        query = self._query_con_detalles(db)
        if fecha is not None:
            query = query.filter(Ruta.fecha == fecha)
        return query.order_by(Ruta.fecha.desc(), Ruta.id.desc()).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: RutaCreate) -> Ruta:
        estado_pendiente_id = _estado_pendiente_id(db)
        ruta = Ruta(
            nombre=obj_in.nombre,
            id_usuario=obj_in.id_usuario,
            fecha=obj_in.fecha,
            hora_inicio=obj_in.hora_inicio,
            hora_fin=obj_in.hora_fin,
            id_estado=estado_pendiente_id,
        )
        db.add(ruta)
        db.flush()  # para obtener ruta.id antes del commit

        for orden, id_contenedor in enumerate(obj_in.ids_contenedores, start=1):
            db.add(DetalleRuta(id_ruta=ruta.id, id_contenedor=id_contenedor, id_estado=estado_pendiente_id, orden=orden))

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
            for orden, id_contenedor in enumerate(obj_in.ids_contenedores, start=1):
                db.add(DetalleRuta(id_ruta=db_obj.id, id_contenedor=id_contenedor, id_estado=estado_pendiente_id, orden=orden))

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_por_usuario(
        self, db: Session, id_usuario: int, skip: int = 0, limit: int = 100, fecha: date | None = None
    ) -> list[Ruta]:
        """Usado por el recolector: solo sus propias rutas (protección BOLA)."""
        query = self._query_con_detalles(db).filter(Ruta.id_usuario == id_usuario)
        if fecha is not None:
            query = query.filter(Ruta.fecha == fecha)
        return query.order_by(Ruta.fecha.desc(), Ruta.id.desc()).offset(skip).limit(limit).all()

    def marcar_recolectado(self, db: Session, ruta: Ruta, codigo_contenedor: str) -> DetalleRuta | None:
        """
        Busca, dentro de ESTA ruta, el detalle cuyo contenedor tiene el
        codigo_contenedor escaneado, y lo pasa a estado 'recolectado'.
        Devuelve None si ese contenedor no forma parte de la ruta (para
        que la vista responda 404 en vez de modificar algo fuera de lugar).
        """
        detalle = (
            db.query(DetalleRuta)
            .join(Contenedor, DetalleRuta.id_contenedor == Contenedor.id)
            .filter(DetalleRuta.id_ruta == ruta.id, Contenedor.codigo_contenedor == codigo_contenedor)
            .first()
        )
        if not detalle:
            return None

        detalle.id_estado = _estado_id_por_nombre(db, "recolectado")
        db.add(detalle)
        db.commit()
        db.refresh(detalle)
        return detalle

    def estado_es_valido_para_detalle(self, db: Session, id_estado: int) -> bool:
        estado = db.query(Estado).filter(Estado.id == id_estado).first()
        return estado is not None and estado.estado in ESTADOS_VALIDOS_DETALLE_RUTA

    def actualizar_estado_detalle(
        self, db: Session, ruta_id: int, detalle_id: int, id_estado: int
    ) -> DetalleRuta | None:
        """
        Fuerza manualmente el estado de UN contenedor dentro de una
        ruta (para pruebas o correcciones desde la web), sin pasar por
        el flujo de escaneo de QR. Devuelve None si ese detalle no
        pertenece a esa ruta, para no modificar algo fuera de lugar.
        """
        detalle = (
            db.query(DetalleRuta)
            .filter(DetalleRuta.id == detalle_id, DetalleRuta.id_ruta == ruta_id)
            .first()
        )
        if not detalle:
            return None

        detalle.id_estado = id_estado
        db.add(detalle)
        db.commit()
        db.refresh(detalle)
        return detalle

    def estado_es_valido_para_ruta(self, db: Session, id_estado: int) -> bool:
        estado = db.query(Estado).filter(Estado.id == id_estado).first()
        return estado is not None and estado.estado in ESTADOS_VALIDOS_RUTA

    def actualizar_estado_ruta(self, db: Session, ruta: Ruta, id_estado: int) -> Ruta:
        """
        Cambia el estado propio de la ruta (pendiente/en progreso/
        completada/cancelada). Es independiente de `completada`: no
        toca ni un solo DetalleRuta, así que nunca desincroniza el
        cálculo de contenedores recolectados.
        """
        ruta.id_estado = id_estado
        db.add(ruta)
        db.commit()
        db.refresh(ruta)
        return ruta


ruta = CRUDRuta(Ruta)
