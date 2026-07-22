from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.crud.base import CRUDBase
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate


class CRUDUsuario(CRUDBase[Usuario, UsuarioCreate, UsuarioUpdate]):
    def get_by_codigo(self, db: Session, codigo_usuario: str) -> Usuario | None:
        return db.query(Usuario).filter(Usuario.codigo_usuario == codigo_usuario).first()

    def create(self, db: Session, obj_in: UsuarioCreate) -> Usuario:
        # Nunca se guarda la contraseña en texto plano.
        data = obj_in.model_dump(exclude={"contrasena"})
        db_obj = Usuario(**data, contrasena_hash=hash_password(obj_in.contrasena))
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Usuario, obj_in: UsuarioUpdate) -> Usuario:
        data = obj_in.model_dump(exclude_unset=True, exclude={"contrasena"})
        for field, value in data.items():
            setattr(db_obj, field, value)
        if obj_in.contrasena:
            db_obj.contrasena_hash = hash_password(obj_in.contrasena)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, codigo_usuario: str, contrasena: str) -> Usuario | None:
        user = self.get_by_codigo(db, codigo_usuario)
        if not user or not verify_password(contrasena, user.contrasena_hash):
            return None
        return user


usuario = CRUDUsuario(Usuario)
