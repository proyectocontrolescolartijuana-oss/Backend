from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate
from app.core.security import (
    hash_password
)

DEFAULT_USER_PASSWORD = "Admin123*"

def get_usuarios(db: Session):
    return db.query(Usuario).all()

def get_usuario(db: Session, usuario_id: int):
    return (
        db.query(Usuario)
        .filter(Usuario.id_usuario == usuario_id)
        .first()
    )

def create_usuario(
    db: Session,
    usuario: UsuarioCreate
):
    usuario_data = usuario.model_dump(
        exclude={"password"}
    )

    nuevo_usuario = Usuario(
        **usuario_data,
        password=hash_password(usuario.password or DEFAULT_USER_PASSWORD)
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario

def update_usuario(
    db: Session,
    usuario_id: int,
    usuario_data
):
    usuario = get_usuario(db, usuario_id)

    if not usuario:
        return None

    update_data = usuario_data.model_dump(
        exclude_unset=True
    )

    password = update_data.pop("password", None)

    for key, value in update_data.items():
        setattr(usuario, key, value)

    if password is not None:
        usuario.password = hash_password(password)

    db.commit()
    db.refresh(usuario)

    return usuario

def delete_usuario(
    db: Session,
    usuario_id: int
):
    usuario = get_usuario(db, usuario_id)

    if not usuario:
        return False

    db.delete(usuario)
    db.commit()

    return True
