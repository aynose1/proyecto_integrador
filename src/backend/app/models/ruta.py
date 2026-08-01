from datetime import datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Time
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

    @property
    def completada(self) -> bool:
        """
        Calculado, no almacenado: una ruta está completada cuando tiene
        al menos un contenedor y todos sus detalles quedaron en estado
        'recolectado'. Al no guardarse en la BD, nunca puede desincronizarse.
        """
        return bool(self.detalles) and all(d.estado.estado == "recolectado" for d in self.detalles)


class DetalleRuta(Base):
    """Tabla puente N:N entre Rutas y Contenedores, con estado propio por contenedor-ruta."""
    __tablename__ = "detalles_rutas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_ruta: Mapped[int] = mapped_column(ForeignKey("rutas.id"), nullable=False, index=True)
    id_contenedor: Mapped[int] = mapped_column(ForeignKey("contenedores.id"), nullable=False, index=True)
    id_estado: Mapped[int] = mapped_column(ForeignKey("estados.id"), nullable=False)
    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Cuándo se marcó como 'recolectado' (por escaneo QR o forzado por
    # admin) -- usado para saber cuál es "la siguiente lectura real" del
    # sensor después de la recolección, en la detección de discrepancias
    # (ver crud/notificacion.py::revisar_discrepancia_recoleccion).
    fecha_recolectado: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    # Evita generar más de una notificación de discrepancia por cada
    # vez que se marca recolectado.
    discrepancia_revisada: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    ruta = relationship("Ruta", back_populates="detalles")
    contenedor = relationship("Contenedor")
    estado = relationship("Estado")
