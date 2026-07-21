from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class TipoUsuario(Base):
    """Catálogo: 'administrador' | 'recolector'."""
    __tablename__ = "tipos_usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tipo: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)


class Estado(Base):
    """Catálogo genérico de estados, reutilizado por Contenedor, DetalleRuta e Incidencia."""
    __tablename__ = "estados"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    estado: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)


class MotivoIncidencia(Base):
    """Catálogo: 'Lectura errónea' | 'Sensor dañado' | 'Contenedor dañado' | 'Otro'."""
    __tablename__ = "motivos_incidencia"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    motivo: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)


class TipoNotificacion(Base):
    __tablename__ = "tipos_notificacion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tipo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
