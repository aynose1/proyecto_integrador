from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import require_admin, require_recolector
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.incidencia import IncidenciaCreate, IncidenciaRead, IncidenciaUpdate

router = APIRouter(prefix="/incidencias", tags=["incidencias"])


@router.post("", response_model=IncidenciaRead, status_code=status.HTTP_201_CREATED)
def reportar_incidencia(
    payload: IncidenciaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_recolector),
):
    """El recolector reporta desde la vista de escaneo QR (ej. lectura errónea del sensor)."""
    cont = crud.contenedor.get(db, payload.id_contenedor)
    if not cont:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Contenedor no encontrado")
    return crud.incidencia.create_de_recolector(db, payload, id_usuario=current_user.id)


@router.get("", response_model=list[IncidenciaRead], dependencies=[Depends(require_admin)])
def listar_incidencias(estado: str | None = None, db: Session = Depends(get_db)):
    """El administrador revisa las incidencias reportadas; puede filtrar por estado (ej. 'pendiente')."""
    return crud.incidencia.get_multi_por_estado(db, estado=estado)


@router.patch("/{incidencia_id}", response_model=IncidenciaRead, dependencies=[Depends(require_admin)])
def atender_incidencia(incidencia_id: int, payload: IncidenciaUpdate, db: Session = Depends(get_db)):
    """El administrador marca la incidencia como atendida (o el estado que corresponda)."""
    inc = crud.incidencia.get(db, incidencia_id)
    if not inc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Incidencia no encontrada")
    return crud.incidencia.update(db, inc, payload)
