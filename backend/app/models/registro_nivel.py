import enum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class OrigenRegistro(str, enum.Enum):
    sensor = "sensor"
    manual = "manual"


class RegistroNivel(Base):
    """
    Historial de nivel de llenado de un contenedor.
    - origen='sensor': lectura automática del sistema embebido (vía API Key).
    - origen='manual': generada cuando el recolector marca un contenedor
      como 'vaciado' desde la app móvil (nivel_porcentaje = 0).
    """
    __tablename__ = "registros_nivel"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_contenedor: Mapped[int] = mapped_column(ForeignKey("contenedores.id"), nullable=False, index=True)
    fecha_hora: Mapped["DateTime"] = mapped_column(DateTime, nullable=False, index=True)
    nivel_porcentaje: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    origen: Mapped[OrigenRegistro] = mapped_column(Enum(OrigenRegistro), nullable=False)

    contenedor = relationship("Contenedor", back_populates="registros_nivel")
