from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.registro_nivel import OrigenRegistro  # mismo catálogo sensor/manual, reutilizado


class RegistroPeso(Base):
    """
    Historial de peso del CONTENIDO de un contenedor, medido por un
    sensor de peso (celda de carga) independiente del sensor de nivel
    (ultrasónico) — ambos sensores coexisten físicamente en el mismo
    contenedor, cada uno con su propia tabla de historial.

    A diferencia de nivel, el sensor de peso ya manda directo el peso
    del contenido en Kg: no necesita ninguna calibración/tara guardada
    en Contenedor (el sensor ya aísla el peso del contenedor vacío).
    """
    __tablename__ = "registros_peso"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_contenedor: Mapped[int] = mapped_column(ForeignKey("contenedores.id"), nullable=False, index=True)
    fecha_hora: Mapped["DateTime"] = mapped_column(DateTime, nullable=False, index=True)
    peso_kg: Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)
    origen: Mapped[OrigenRegistro] = mapped_column(Enum(OrigenRegistro), nullable=False)

    contenedor = relationship("Contenedor", back_populates="registros_peso")
