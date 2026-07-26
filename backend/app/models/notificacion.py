from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    id_contenedor: Mapped[int] = mapped_column(ForeignKey("contenedores.id"), nullable=False)
    id_tipo_notificacion: Mapped[int] = mapped_column(ForeignKey("tipos_notificacion.id"), nullable=False)
    # Destinatario de la notificación (ej. el administrador a cargo)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    contenedor = relationship("Contenedor")
    tipo_notificacion = relationship("TipoNotificacion")
    usuario = relationship("Usuario")
