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


def _calcular_nivel_porcentaje(distancia_cm, altura_cm) -> float:
    """
    Convierte la distancia cruda del sensor ultrasónico (cm desde el
    sensor hasta la basura) en un porcentaje de llenado, usando la
    altura instalada del sensor (cm hasta el fondo del contenedor
    vacío). A mayor distancia medida, menos lleno está el contenedor.
    Se acota entre 0 y 100 por si el sensor da una lectura fuera de
    rango (ruido, obstrucción, mala calibración).
    """
    distancia = float(distancia_cm)
    altura = float(altura_cm)
    nivel = 100 - (distancia / altura * 100)
    return round(max(0.0, min(100.0, nivel)), 2)


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
    es un usuario del sistema. Recibe la distancia cruda medida y el
    backend calcula el porcentaje de llenado, usando altura_cm del
    contenedor.
    """
    cont = crud.contenedor.get_by_codigo(db, payload.codigo_contenedor)
    if not cont:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No existe un contenedor con ese código")

    if not cont.altura_cm:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Este contenedor no tiene configurada su altura (altura_cm). "
            "Captúrala desde la web antes de que el sensor pueda enviar lecturas.",
        )

    nivel_porcentaje = _calcular_nivel_porcentaje(payload.distancia_cm, cont.altura_cm)

    return crud.registro_nivel.registrar_lectura(
        db,
        contenedor=cont,
        nivel_porcentaje=nivel_porcentaje,
        origen=OrigenRegistro.sensor,
        fecha_hora=payload.fecha_hora,
        distancia_cm=payload.distancia_cm,
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
