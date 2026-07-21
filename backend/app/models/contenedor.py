from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Contenedor(Base):
    __tablename__ = "contenedores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    # codigo_contenedor es el valor que se codifica en el QR físico del contenedor
    codigo_contenedor: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    capacidad_max: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)

    id_ubicacion: Mapped[int] = mapped_column(ForeignKey("ubicaciones.id"), nullable=False)
    id_estado: Mapped[int] = mapped_column(ForeignKey("estados.id"), nullable=False)

    # Valor denormalizado: se actualiza en cada lectura nueva (sensor o manual)
    # para que la app móvil y el dashboard lo lean sin tener que calcular
    # el registro más reciente de RegistroNivel en cada consulta.
    nivel_actual: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)

    ubicacion = relationship("Ubicacion", back_populates="contenedores")
    estado = relationship("Estado")
    registros_nivel = relationship(
        "RegistroNivel", back_populates="contenedor", order_by="RegistroNivel.fecha_hora.desc()"
    )
    incidencias = relationship("Incidencia", back_populates="contenedor")
