from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Usuario(Base):
    """
    Administradores y recolectores viven en la misma tabla, diferenciados
    por id_tipo_usuario.
    - Un administrador puede auto-registrarse desde la web (POST /auth/register).
    - Los recolectores los crea un administrador autenticado (POST /usuarios).
    - El seeder deja un admin inicial (ADMIN001) para el primer acceso.
    """
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo_usuario: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido_paterno: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido_materno: Mapped[str] = mapped_column(String(100), nullable=True)
    contrasena_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    id_tipo_usuario: Mapped[int] = mapped_column(ForeignKey("tipos_usuarios.id"), nullable=False)

    tipo_usuario = relationship("TipoUsuario")
    rutas = relationship("Ruta", back_populates="recolector")
    incidencias = relationship("Incidencia", back_populates="usuario")
