from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.catalogos import Estado
from app.models.contenedor import Contenedor
from app.schemas.contenedor import ContenedorCreate, ContenedorUpdate

# El catálogo 'estados' es genérico y también lo usan DetalleRuta
# (pendiente/recolectado) e Incidencia (pendiente/atendido). Un
# contenedor por sí mismo solo tiene sentido como activo o inactivo —
# nada de "pendiente" o "recolectado", eso es del contenedor DENTRO de
# una ruta (DetalleRuta), una entidad distinta. Esto no toca esa tabla
# para nada; solo restringe qué puede llevar Contenedor.id_estado.
ESTADOS_VALIDOS_CONTENEDOR = {"activo", "inactivo"}


class CRUDContenedor(CRUDBase[Contenedor, ContenedorCreate, ContenedorUpdate]):
    def get_by_codigo(self, db: Session, codigo_contenedor: str) -> Contenedor | None:
        """Usado por la vista de escaneo de QR: el QR codifica codigo_contenedor."""
        return db.query(Contenedor).filter(Contenedor.codigo_contenedor == codigo_contenedor).first()

    def estado_es_valido_para_contenedor(self, db: Session, id_estado: int) -> bool:
        estado = db.query(Estado).filter(Estado.id == id_estado).first()
        return estado is not None and estado.estado in ESTADOS_VALIDOS_CONTENEDOR


contenedor = CRUDContenedor(Contenedor)
