from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.ruta import RutaCreate, RutaRead, RutaSummary, RutaUpdate

router = APIRouter(prefix="/rutas", tags=["rutas"])


@router.get("/me", response_model=list[RutaSummary])
def listar_mis_rutas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> list:
    """El recolector consulta únicamente sus propias rutas asignadas."""
    return crud.ruta.get_multi_por_usuario(db, current_user.id, skip=skip, limit=limit)


@router.get("", response_model=list[RutaSummary], dependencies=[Depends(require_admin)])
def listar_rutas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> list:
    return crud.ruta.get_multi(db, skip=skip, limit=limit)


@router.get("/{ruta_id}", response_model=RutaRead)
def obtener_ruta(
    ruta_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    ruta_obj = crud.ruta.get(db, ruta_id)
    if not ruta_obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ruta no encontrada")

    # Protección BOLA/IDOR: un recolector solo puede ver el detalle de SU
    # propia ruta, aunque adivine o incremente el id en la URL.
    es_admin = current_user.tipo_usuario.tipo == "administrador"
    es_dueno = ruta_obj.id_usuario == current_user.id
    if not es_admin and not es_dueno:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes acceso a esta ruta")

    return ruta_obj


@router.post("", response_model=RutaRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def crear_ruta(payload: RutaCreate, db: Session = Depends(get_db)):
    return crud.ruta.create(db, payload)


@router.put("/{ruta_id}", response_model=RutaRead, dependencies=[Depends(require_admin)])
def actualizar_ruta(ruta_id: int, payload: RutaUpdate, db: Session = Depends(get_db)):
    ruta_obj = crud.ruta.get(db, ruta_id)
    if not ruta_obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ruta no encontrada")
    return crud.ruta.update(db, ruta_obj, payload)


@router.delete("/{ruta_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def eliminar_ruta(ruta_id: int, db: Session = Depends(get_db)) -> None:
    ruta_obj = crud.ruta.get(db, ruta_id)
    if not ruta_obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ruta no encontrada")
    crud.ruta.remove(db, ruta_id)
