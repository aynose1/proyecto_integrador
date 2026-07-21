from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.zona_sector import Sector, Zona
from app.schemas.zona_sector import SectorCreate, SectorUpdate, ZonaCreate, ZonaUpdate


class CRUDZona(CRUDBase[Zona, ZonaCreate, ZonaUpdate]):
    def get_by_nombre(self, db: Session, nombre: str) -> Zona | None:
        return db.query(Zona).filter(Zona.nombre == nombre).first()


class CRUDSector(CRUDBase[Sector, SectorCreate, SectorUpdate]):
    def get_multi_por_zona(self, db: Session, id_zona: int) -> list[Sector]:
        """Usado por el formulario de alta de contenedor: sectores seleccionables de una zona."""
        return db.query(Sector).filter(Sector.id_zona == id_zona).all()


zona = CRUDZona(Zona)
sector = CRUDSector(Sector)
