from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.catalogos import Estado, TipoNotificacion
from app.models.contenedor import Contenedor
from app.models.notificacion import Notificacion
from app.models.ruta import DetalleRuta
from app.schemas.notificacion import NotificacionCreate

# Porcentaje de nivel/peso por debajo del cual se considera "vacío de
# verdad". Un sensor real casi nunca marca exactamente 0%, así que se
# da un margen en vez de exigir 0 exacto.
UMBRAL_DISCREPANCIA_PCT = 10


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
        Cualquier administrador ve todas las notificaciones, no solo las
        propias: id_usuario es opcional a propósito (ver
        models/notificacion.py) porque este sistema no distingue "qué
        admin es dueño de qué contenedor".
        """
        return db.query(Notificacion).order_by(Notificacion.id.desc()).all()

    def marcar_leida(self, db: Session, notif: Notificacion) -> Notificacion:
        notif.leida = True
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif

    def revisar_discrepancia_recoleccion(self, db: Session, contenedor: Contenedor) -> None:
        """
        Se llama después de CADA lectura nueva de nivel o de peso (ver
        crud/registro_nivel.py y crud/registro_peso.py). Busca si este
        contenedor tiene una recolección reciente todavía sin revisar
        (discrepancia_revisada=False) — si la hay, esta lectura que
        acaba de llegar ES "la siguiente lectura real" después de la
        recolección, así que se compara contra el umbral, y se marca
        como revisada para no volver a evaluarla con lecturas futuras
        (evita generar varias notificaciones por la misma recolección).
        """
        detalle = (
            db.query(DetalleRuta)
            .join(Estado, DetalleRuta.id_estado == Estado.id)
            .filter(
                DetalleRuta.id_contenedor == contenedor.id,
                Estado.estado == "recolectado",
                DetalleRuta.fecha_recolectado.isnot(None),
                DetalleRuta.discrepancia_revisada.is_(False),
            )
            .order_by(DetalleRuta.fecha_recolectado.desc())
            .first()
        )
        if not detalle:
            return

        detalle.discrepancia_revisada = True
        db.add(detalle)

        nivel_pct = float(contenedor.nivel_actual or 0)
        capacidad = float(contenedor.capacidad_max or 0)
        peso_pct = (float(contenedor.peso_actual or 0) / capacidad * 100) if capacidad > 0 else 0.0

        if nivel_pct >= UMBRAL_DISCREPANCIA_PCT or peso_pct >= UMBRAL_DISCREPANCIA_PCT:
            tipo = (
                db.query(TipoNotificacion)
                .filter(TipoNotificacion.tipo == "Posible recolección no confirmada")
                .first()
            )
            if tipo:
                notif = Notificacion(
                    contenido=(
                        f"El contenedor '{contenedor.nombre}' ({contenedor.codigo_contenedor}) se marcó como "
                        f"recolectado, pero la siguiente lectura del sensor sigue mostrando "
                        f"{nivel_pct:.0f}% de nivel y {float(contenedor.peso_actual or 0):.1f} Kg de peso. "
                        f"Puede que no se haya recolectado realmente, o que el sensor tenga una falla."
                    ),
                    id_contenedor=contenedor.id,
                    id_tipo_notificacion=tipo.id,
                    id_usuario=None,
                )
                db.add(notif)

        db.commit()


notificacion = CRUDNotificacion(Notificacion)
