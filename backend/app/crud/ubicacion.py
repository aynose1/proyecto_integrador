from app.crud.base import CRUDBase
from app.models.ubicacion import Ubicacion
from app.schemas.ubicacion import UbicacionCreate, UbicacionUpdate

ubicacion = CRUDBase[Ubicacion, UbicacionCreate, UbicacionUpdate](Ubicacion)
