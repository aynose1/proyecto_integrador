from sqlalchemy import Date, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Ruta(Base):
    __tablename__ = "rutas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    # Recolector asignado a la ruta. Cada ruta pertenece a un solo recolector.
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
    fecha: Mapped["Date"] = mapped_column(Date, nullable=False)
    hora_inicio: Mapped["Time"] = mapped_column(Time, nullable=True)
    hora_fin: Mapped["Time"] = mapped_column(Time, nullable=True)

    recolector = relationship("Usuario", back_populates="rutas")
    detalles = relationship("DetalleRuta", back_populates="ruta", cascade="all, delete-orphan")


class DetalleRuta(Base):
    """Tabla puente N:N entre Rutas y Contenedores, con estado propio por contenedor-ruta."""
    __tablename__ = "detalles_rutas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_ruta: Mapped[int] = mapped_column(ForeignKey("rutas.id"), nullable=False, index=True)
    id_contenedor: Mapped[int] = mapped_column(ForeignKey("contenedores.id"), nullable=False, index=True)
    id_estado: Mapped[int] = mapped_column(ForeignKey("estados.id"), nullable=False)
    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    ruta = relationship("Ruta", back_populates="detalles")
    contenedor = relationship("Contenedor")
    estado = relationship("Estado")
