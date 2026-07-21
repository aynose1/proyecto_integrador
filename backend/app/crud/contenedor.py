from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.contenedor import Contenedor
from app.schemas.contenedor import ContenedorCreate, ContenedorUpdate


class CRUDContenedor(CRUDBase[Contenedor, ContenedorCreate, ContenedorUpdate]):
    def get_by_codigo(self, db: Session, codigo_contenedor: str) -> Contenedor | None:
        """Usado por la vista de escaneo de QR: el QR codifica codigo_contenedor."""
        return db.query(Contenedor).filter(Contenedor.codigo_contenedor == codigo_contenedor).first()


contenedor = CRUDContenedor(Contenedor)
