from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user, require_recolector, verify_device_api_key
from app.db.session import get_db
from app.models.registro_nivel import OrigenRegistro
from app.models.usuario import Usuario
from app.schemas.registro_nivel import RegistroNivelRead, RegistroNivelSensorCreate

router = APIRouter(tags=["registros-nivel"])


@router.post(
    "/registros-nivel",
    response_model=RegistroNivelRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_device_api_key)],
)
def registrar_lectura_sensor(payload: RegistroNivelSensorCreate, db: Session = Depends(get_db)):
    """
    Endpoint que consume el sistema embebido de cada contenedor.
    Se autentica con API Key (X-API-Key), no con JWT: el dispositivo no
    es un usuario del sistema.
    """
    cont = crud.contenedor.get_by_codigo(db, payload.codigo_contenedor)
    if not cont:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No existe un contenedor con ese código")

    return crud.registro_nivel.registrar_lectura(
        db,
        contenedor=cont,
        nivel_porcentaje=payload.nivel_porcentaje,
        origen=OrigenRegistro.sensor,
        fecha_hora=payload.fecha_hora,
    )


@router.get("/contenedores/{contenedor_id}/registros-nivel", response_model=list[RegistroNivelRead])
def historial_nivel_contenedor(
    contenedor_id: int,
    desde: datetime | None = None,
    hasta: datetime | None = None,
    db: Session = Depends(get_db),
    _current_user: Usuario = Depends(get_current_user),
):
    """Historial usado por el dashboard para graficar frecuencia de llenado."""
    cont = crud.contenedor.get(db, contenedor_id)
    if not cont:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Contenedor no encontrado")
    return crud.registro_nivel.historial_por_contenedor(db, contenedor_id, desde=desde, hasta=hasta)


@router.post(
    "/contenedores/{contenedor_id}/vaciar",
    response_model=RegistroNivelRead,
    status_code=status.HTTP_201_CREATED,
)
def marcar_contenedor_vaciado(
    contenedor_id: int,
    db: Session = Depends(get_db),
    _current_user: Usuario = Depends(require_recolector),
):
    """
    Acción desde la vista de escaneo QR: el recolector confirma que vació
    el contenedor. Genera un registro manual con nivel 0% y sincroniza
    Contenedor.nivel_actual.
    """
    cont = crud.contenedor.get(db, contenedor_id)
    if not cont:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Contenedor no encontrado")

    return crud.registro_nivel.registrar_lectura(
        db, contenedor=cont, nivel_porcentaje=0, origen=OrigenRegistro.manual
    )
