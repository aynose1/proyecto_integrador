from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Ubicacion(Base):
    """
    Referencia únicamente al sector; la zona se obtiene vía sector.zona.
    Esto evita el caso inconsistente de guardar un id_zona que no
    corresponda al id_zona real del sector elegido.
    """
    __tablename__ = "ubicaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_sector: Mapped[int] = mapped_column(ForeignKey("sectores.id"), nullable=False)

    sector = relationship("Sector")
    contenedores = relationship("Contenedor", back_populates="ubicacion")
