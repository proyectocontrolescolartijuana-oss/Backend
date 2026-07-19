from sqlalchemy.orm import Session

from app.models.rol import Rol
from app.schemas.rol import RolCreate

def get_roles(db: Session):
    return db.query(Rol).all()

def get_rol(db: Session, rol_id: int):
    return (
        db.query(Rol)
        .filter(Rol.id_rol == rol_id)
        .first()
    )

def create_rol(
    db: Session,
    rol: RolCreate
):
    nuevo_rol = Rol(
        **rol.model_dump()
    )

    db.add(nuevo_rol)
    db.commit()
    db.refresh(nuevo_rol)

    return nuevo_rol

def update_rol(
    db: Session,
    rol_id: int,
    rol_data
):
    rol = get_rol(db, rol_id)

    if not rol:
        return None

    update_data = rol_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(rol, key, value)

    db.commit()
    db.refresh(rol)

    return rol

def delete_rol(
    db: Session,
    rol_id: int
):
    rol = get_rol(db, rol_id)

    if not rol:
        return False

    db.delete(rol)
    db.commit()

    return True
