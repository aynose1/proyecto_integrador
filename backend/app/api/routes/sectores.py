from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.zona_sector import SectorCreate, SectorRead, SectorUpdate

router = APIRouter(prefix="/sectores", tags=["sectores"])


@router.get("", response_model=list[SectorRead])
def listar_sectores(
    id_zona: int | None = None,
    db: Session = Depends(get_db),
    _u: Usuario = Depends(get_current_user),
):
    """
    Si se manda id_zona, filtra solo los sectores de esa zona (para que
    el formulario de alta de contenedor primero elija zona y luego
    muestre únicamente sus sectores).
    """
    if id_zona is not None:
        return crud.sector.get_multi_por_zona(db, id_zona)
    return crud.sector.get_multi(db, limit=1000)


@router.post("", response_model=SectorRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def crear_sector(payload: SectorCreate, db: Session = Depends(get_db)):
    if not crud.zona.get(db, payload.id_zona):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "La zona indicada no existe")
    return crud.sector.create(db, payload)


@router.put("/{sector_id}", response_model=SectorRead, dependencies=[Depends(require_admin)])
def actualizar_sector(sector_id: int, payload: SectorUpdate, db: Session = Depends(get_db)):
    sector_obj = crud.sector.get(db, sector_id)
    if not sector_obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Sector no encontrado")
    if payload.id_zona is not None and not crud.zona.get(db, payload.id_zona):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "La zona indicada no existe")
    return crud.sector.update(db, sector_obj, payload)


@router.delete("/{sector_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def eliminar_sector(sector_id: int, db: Session = Depends(get_db)) -> None:
    sector_obj = crud.sector.get(db, sector_id)
    if not sector_obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Sector no encontrado")
    crud.sector.remove(db, sector_id)
