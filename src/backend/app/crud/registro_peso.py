from datetime import datetime

from sqlalchemy.orm import Session

from app.models.contenedor import Contenedor
from app.models.registro_nivel import OrigenRegistro
from app.models.registro_peso import RegistroPeso


class CRUDRegistroPeso:
    def registrar_lectura(
        self,
        db: Session,
        *,
        contenedor: Contenedor,
        peso_kg,
        origen: OrigenRegistro,
        fecha_hora: datetime | None = None,
    ) -> RegistroPeso:
        """
        Inserta un registro en el historial Y actualiza
        Contenedor.peso_actual en la misma transacción — mismo patrón
        que registro_nivel.registrar_lectura: peso_actual es un valor
        denormalizado que siempre refleja la lectura más reciente.
        """
        registro = RegistroPeso(
            id_contenedor=contenedor.id,
            fecha_hora=fecha_hora or datetime.utcnow(),
            peso_kg=peso_kg,
            origen=origen,
        )
        db.add(registro)
        contenedor.peso_actual = peso_kg
        db.add(contenedor)
        db.commit()
        db.refresh(registro)
        db.refresh(contenedor)

        from app.crud.notificacion import notificacion as crud_notificacion

        crud_notificacion.revisar_discrepancia_recoleccion(db, contenedor)

        return registro

    def historial_por_contenedor(
        self,
        db: Session,
        id_contenedor: int,
        desde: datetime | None = None,
        hasta: datetime | None = None,
    ) -> list[RegistroPeso]:
        query = db.query(RegistroPeso).filter(RegistroPeso.id_contenedor == id_contenedor)
        if desde:
            query = query.filter(RegistroPeso.fecha_hora >= desde)
        if hasta:
            query = query.filter(RegistroPeso.fecha_hora <= hasta)
        return query.order_by(RegistroPeso.fecha_hora.desc()).all()


registro_peso = CRUDRegistroPeso()
