from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    id_contenedor: Mapped[int] = mapped_column(ForeignKey("contenedores.id"), nullable=False)
    id_tipo_notificacion: Mapped[int] = mapped_column(ForeignKey("tipos_notificacion.id"), nullable=False)
    # Opcional a propósito: en este sistema cualquier administrador puede
    # atender cualquier contenedor (no existe "qué admin es dueño de qué
    # contenedor/sector"), así que una notificación sin id_usuario es
    # visible para todos los administradores, no solo uno.
    id_usuario: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    leida: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    contenedor = relationship("Contenedor")
    tipo_notificacion = relationship("TipoNotificacion")
    usuario = relationship("Usuario")
