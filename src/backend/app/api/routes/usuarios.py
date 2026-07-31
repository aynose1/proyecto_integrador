from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioRead, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("/me", response_model=UsuarioRead)
def leer_mi_perfil(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    return current_user


@router.get("", response_model=list[UsuarioRead], dependencies=[Depends(require_admin)])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> list[Usuario]:
    return crud.usuario.get_multi(db, skip=skip, limit=limit)


@router.get("/{usuario_id}", response_model=UsuarioRead, dependencies=[Depends(require_admin)])
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)) -> Usuario:
    user = crud.usuario.get(db, usuario_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    return user


@router.post("", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def crear_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)) -> Usuario:
    if crud.usuario.get_by_codigo(db, payload.codigo_usuario):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un usuario con ese código")
    return crud.usuario.create(db, payload)


@router.put("/{usuario_id}", response_model=UsuarioRead, dependencies=[Depends(require_admin)])
def actualizar_usuario(usuario_id: int, payload: UsuarioUpdate, db: Session = Depends(get_db)) -> Usuario:
    user = crud.usuario.get(db, usuario_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    return crud.usuario.update(db, user, payload)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)) -> None:
    user = crud.usuario.get(db, usuario_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    crud.usuario.remove(db, usuario_id)
