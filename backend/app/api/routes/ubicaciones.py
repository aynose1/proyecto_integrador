from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.ubicacion import UbicacionCreate, UbicacionRead, UbicacionUpdate

router = APIRouter(prefix="/ubicaciones", tags=["ubicaciones"])


@router.get("", response_model=list[UbicacionRead])
def listar_ubicaciones(db: Session = Depends(get_db), _u: Usuario = Depends(get_current_user)):
    return crud.ubicacion.get_multi(db, limit=1000)


@router.post("", response_model=UbicacionRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def crear_ubicacion(payload: UbicacionCreate, db: Session = Depends(get_db)):
    if not crud.sector.get(db, payload.id_sector):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "El sector indicado no existe")
    return crud.ubicacion.create(db, payload)


@router.put("/{ubicacion_id}", response_model=UbicacionRead, dependencies=[Depends(require_admin)])
def actualizar_ubicacion(ubicacion_id: int, payload: UbicacionUpdate, db: Session = Depends(get_db)):
    ubic = crud.ubicacion.get(db, ubicacion_id)
    if not ubic:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ubicación no encontrada")
    if payload.id_sector is not None and not crud.sector.get(db, payload.id_sector):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "El sector indicado no existe")
    return crud.ubicacion.update(db, ubic, payload)


@router.delete("/{ubicacion_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def eliminar_ubicacion(ubicacion_id: int, db: Session = Depends(get_db)) -> None:
    ubic = crud.ubicacion.get(db, ubicacion_id)
    if not ubic:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ubicación no encontrada")
    crud.ubicacion.remove(db, ubicacion_id)
