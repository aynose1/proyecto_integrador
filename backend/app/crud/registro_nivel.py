from datetime import datetime

from sqlalchemy.orm import Session

from app.models.contenedor import Contenedor
from app.models.registro_nivel import OrigenRegistro, RegistroNivel


class CRUDRegistroNivel:
    def registrar_lectura(
        self,
        db: Session,
        *,
        contenedor: Contenedor,
        nivel_porcentaje,
        origen: OrigenRegistro,
        fecha_hora: datetime | None = None,
    ) -> RegistroNivel:
        """
        Inserta un registro en el historial Y actualiza Contenedor.nivel_actual
        en la misma transacción, como se definió: nivel_actual es un valor
        denormalizado que siempre refleja la lectura más reciente.
        """
        registro = RegistroNivel(
            id_contenedor=contenedor.id,
            fecha_hora=fecha_hora or datetime.utcnow(),
            nivel_porcentaje=nivel_porcentaje,
            origen=origen,
        )
        db.add(registro)
        contenedor.nivel_actual = nivel_porcentaje
        db.add(contenedor)
        db.commit()
        db.refresh(registro)
        db.refresh(contenedor)
        return registro

    def historial_por_contenedor(
        self,
        db: Session,
        id_contenedor: int,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        origen: OrigenRegistro | None = None,
    ) -> list[RegistroNivel]:
        query = db.query(RegistroNivel).filter(RegistroNivel.id_contenedor == id_contenedor)
        if desde:
            query = query.filter(RegistroNivel.fecha_hora >= desde)
        if hasta:
            query = query.filter(RegistroNivel.fecha_hora <= hasta)
        if origen:
            query = query.filter(RegistroNivel.origen == origen)
        return query.order_by(RegistroNivel.fecha_hora.desc()).all()


registro_nivel = CRUDRegistroNivel()
