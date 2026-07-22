from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.zona_sector import ZonaCreate, ZonaRead, ZonaUpdate

router = APIRouter(prefix="/zonas", tags=["zonas"])


@router.get("", response_model=list[ZonaRead])
def listar_zonas(db: Session = Depends(get_db), _u: Usuario = Depends(get_current_user)):
    """Usado para llenar el select de zona al dar de alta un contenedor."""
    return crud.zona.get_multi(db, limit=1000)


@router.post("", response_model=ZonaRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def crear_zona(payload: ZonaCreate, db: Session = Depends(get_db)):
    if crud.zona.get_by_nombre(db, payload.nombre):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe una zona con ese nombre")
    return crud.zona.create(db, payload)


@router.put("/{zona_id}", response_model=ZonaRead, dependencies=[Depends(require_admin)])
def actualizar_zona(zona_id: int, payload: ZonaUpdate, db: Session = Depends(get_db)):
    zona_obj = crud.zona.get(db, zona_id)
    if not zona_obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Zona no encontrada")
    return crud.zona.update(db, zona_obj, payload)


@router.delete("/{zona_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def eliminar_zona(zona_id: int, db: Session = Depends(get_db)) -> None:
    zona_obj = crud.zona.get(db, zona_id)
    if not zona_obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Zona no encontrada")
    # El cascade="all, delete-orphan" en el modelo elimina también sus sectores.
    crud.zona.remove(db, zona_id)
