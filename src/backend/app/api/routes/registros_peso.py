from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user, verify_device_api_key
from app.db.session import get_db
from app.models.registro_nivel import OrigenRegistro
from app.models.usuario import Usuario
from app.schemas.registro_peso import RegistroPesoRead, RegistroPesoSensorCreate

router = APIRouter(tags=["registros-peso"])


@router.post(
    "/registros-peso",
    response_model=RegistroPesoRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_device_api_key)],
)
def registrar_lectura_sensor_peso(payload: RegistroPesoSensorCreate, db: Session = Depends(get_db)):
    """
    Endpoint que consume el sensor de peso (celda de carga) de cada
    contenedor. Coexiste con /registros-nivel (sensor ultrasónico) —
    son dos sensores físicos independientes en el mismo contenedor,
    cada uno con su propia tabla de historial.

    A diferencia de nivel, el sensor ya manda directo el peso del
    contenido en Kg: no hay ningún dato de calibración que validar aquí
    (no existe equivalente a altura_cm para peso).
    """
    cont = crud.contenedor.get_by_codigo(db, payload.codigo_contenedor)
    if not cont:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No existe un contenedor con ese código")

    return crud.registro_peso.registrar_lectura(
        db,
        contenedor=cont,
        peso_kg=payload.peso_kg,
        origen=OrigenRegistro.sensor,
        fecha_hora=payload.fecha_hora,
    )


@router.get("/contenedores/{contenedor_id}/registros-peso", response_model=list[RegistroPesoRead])
def historial_peso_contenedor(
    contenedor_id: int,
    desde: datetime | None = None,
    hasta: datetime | None = None,
    db: Session = Depends(get_db),
    _current_user: Usuario = Depends(get_current_user),
):
    """Historial de peso, análogo a /contenedores/{id}/registros-nivel."""
    cont = crud.contenedor.get(db, contenedor_id)
    if not cont:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Contenedor no encontrado")
    return crud.registro_peso.historial_por_contenedor(db, contenedor_id, desde=desde, hasta=hasta)
