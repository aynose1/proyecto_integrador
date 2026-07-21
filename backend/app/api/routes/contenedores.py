from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.contenedor import ContenedorCreate, ContenedorRead, ContenedorUpdate

router = APIRouter(prefix="/contenedores", tags=["contenedores"])


@router.get("", response_model=list[ContenedorRead])
def listar_contenedores(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _current_user: Usuario = Depends(get_current_user),  # admin o recolector, ambos pueden listar
) -> list:
    return crud.contenedor.get_multi(db, skip=skip, limit=limit)


@router.get("/qr/{codigo_contenedor}", response_model=ContenedorRead)
def obtener_contenedor_por_qr(
    codigo_contenedor: str,
    db: Session = Depends(get_db),
    _current_user: Usuario = Depends(get_current_user),
):
    """Usado por la vista de escaneo de QR en la app móvil."""
    cont = crud.contenedor.get_by_codigo(db, codigo_contenedor)
    if not cont:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No existe un contenedor con ese código QR")
    return cont


@router.get("/{contenedor_id}", response_model=ContenedorRead)
def obtener_contenedor(
    contenedor_id: int,
    db: Session = Depends(get_db),
    _current_user: Usuario = Depends(get_current_user),
):
    cont = crud.contenedor.get(db, contenedor_id)
    if not cont:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Contenedor no encontrado")
    return cont


@router.post("", response_model=ContenedorRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def crear_contenedor(payload: ContenedorCreate, db: Session = Depends(get_db)):
    if crud.contenedor.get_by_codigo(db, payload.codigo_contenedor):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un contenedor con ese código")
    return crud.contenedor.create(db, payload)


@router.put("/{contenedor_id}", response_model=ContenedorRead, dependencies=[Depends(require_admin)])
def actualizar_contenedor(contenedor_id: int, payload: ContenedorUpdate, db: Session = Depends(get_db)):
    cont = crud.contenedor.get(db, contenedor_id)
    if not cont:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Contenedor no encontrado")
    return crud.contenedor.update(db, cont, payload)


@router.delete("/{contenedor_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def eliminar_contenedor(contenedor_id: int, db: Session = Depends(get_db)) -> None:
    cont = crud.contenedor.get(db, contenedor_id)
    if not cont:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Contenedor no encontrado")
    crud.contenedor.remove(db, contenedor_id)
