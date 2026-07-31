from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Zona(Base):
    """
    Ej. 'Edificio A', 'Edificio B', 'Edificio C'. El administrador puede
    dar de alta nuevas zonas desde la web; no es un enum fijo.
    """
    __tablename__ = "zonas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    sectores = relationship("Sector", back_populates="zona", cascade="all, delete-orphan")


class Sector(Base):
    """
    Un sector pertenece a exactamente una zona (ej. 'Planta baja' dentro
    de 'Edificio A'). El administrador los agrega desde la web, filtrando
    por la zona a la que pertenecen.
    """
    __tablename__ = "sectores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    id_zona: Mapped[int] = mapped_column(ForeignKey("zonas.id"), nullable=False, index=True)

    zona = relationship("Zona", back_populates="sectores")
