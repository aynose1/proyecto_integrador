from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Incidencia(Base):
    """
    Reporte que levanta un recolector desde la vista de escaneo QR cuando
    detecta una inconsistencia (ej. el sensor marca nivel alto pero el
    contenedor está vacío físicamente). El administrador la atiende desde
    la web y actualiza id_estado (pendiente -> atendido).
    """
    __tablename__ = "incidencias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_contenedor: Mapped[int] = mapped_column(ForeignKey("contenedores.id"), nullable=False, index=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    fecha_hora: Mapped["DateTime"] = mapped_column(DateTime, nullable=False)
    id_motivo: Mapped[int] = mapped_column(ForeignKey("motivos_incidencia.id"), nullable=False)
    comentario: Mapped[str | None] = mapped_column(Text, nullable=True)
    id_estado: Mapped[int] = mapped_column(ForeignKey("estados.id"), nullable=False)

    contenedor = relationship("Contenedor", back_populates="incidencias")
    usuario = relationship("Usuario", back_populates="incidencias")
    motivo = relationship("MotivoIncidencia")
    estado = relationship("Estado")
