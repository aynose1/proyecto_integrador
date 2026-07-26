from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user, require_admin, require_recolector
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.ruta import DetalleRutaEstadoUpdate, DetalleRutaRead, RecolectarContenedorRequest, RutaCreate, RutaRead, RutaSummary, RutaUpdate

router = APIRouter(prefix="/rutas", tags=["rutas"])


@router.get("/me", response_model=list[RutaSummary])
def listar_mis_rutas(
    fecha: date | None = Query(default=None, description="Filtra por fecha exacta (YYYY-MM-DD)"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> list:
    """El recolector consulta únicamente sus propias rutas asignadas."""
    return crud.ruta.get_multi_por_usuario(db, current_user.id, skip=skip, limit=limit, fecha=fecha)


@router.get("", response_model=list[RutaSummary], dependencies=[Depends(require_admin)])
def listar_rutas(
    fecha: date | None = Query(default=None, description="Filtra por fecha exacta (YYYY-MM-DD); si se omite, regresa de todas las fechas"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list:
    return crud.ruta.get_multi(db, skip=skip, limit=limit, fecha=fecha)


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


@router.post("/{ruta_id}/recolectar", response_model=DetalleRutaRead)
def marcar_contenedor_recolectado(
    ruta_id: int,
    payload: RecolectarContenedorRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_recolector),
):
    """
    Llamado por la app móvil al escanear el QR de un contenedor durante
    una ruta: pasa ese contenedor, dentro de ESTA ruta, de 'pendiente' a
    'recolectado'. Protegido contra BOLA: solo el recolector dueño de la
    ruta puede marcarla, igual que en GET /rutas/{id}.
    """
    ruta_obj = crud.ruta.get(db, ruta_id)
    if not ruta_obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ruta no encontrada")
    if ruta_obj.id_usuario != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes acceso a esta ruta")

    detalle = crud.ruta.marcar_recolectado(db, ruta_obj, payload.codigo_contenedor)
    if not detalle:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ese contenedor no forma parte de esta ruta")

    return detalle


@router.patch("/{ruta_id}/detalles/{detalle_id}", response_model=DetalleRutaRead, dependencies=[Depends(require_admin)])
def actualizar_estado_detalle(
    ruta_id: int,
    detalle_id: int,
    payload: DetalleRutaEstadoUpdate,
    db: Session = Depends(get_db),
):
    """
    El administrador fuerza manualmente pendiente/recolectado de un
    contenedor dentro de una ruta, sin pasar por el escaneo de QR — útil
    para pruebas o para corregir un registro. Restringido a esos dos
    estados: el catálogo 'estados' es compartido con Contenedor e
    Incidencia y no todos sus valores aplican aquí.
    """
    ruta_obj = crud.ruta.get(db, ruta_id)
    if not ruta_obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ruta no encontrada")

    if not crud.ruta.estado_es_valido_para_detalle(db, payload.id_estado):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "id_estado inválido: un contenedor dentro de una ruta solo puede estar 'pendiente' o 'recolectado'",
        )

    detalle = crud.ruta.actualizar_estado_detalle(db, ruta_id, detalle_id, payload.id_estado)
    if not detalle:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ese detalle no pertenece a esta ruta")

    return detalle
