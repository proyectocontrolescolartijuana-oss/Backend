from sqlalchemy.orm import Session

from app.crud._crud_utils import to_create_data, to_update_data
from app.models.grupo import Grupo


def get_grupos(db: Session):
    return db.query(Grupo).all()


def get_grupo(db: Session, grupo_id: int):
    return (
        db.query(Grupo)
        .filter(Grupo.id_grupo == grupo_id)
        .first()
    )


def create_grupo(db: Session, grupo_data):
    nuevo_grupo = Grupo(**to_create_data(grupo_data))

    db.add(nuevo_grupo)
    db.commit()
    db.refresh(nuevo_grupo)

    return nuevo_grupo


def update_grupo(db: Session, grupo_id: int, grupo_data):
    grupo = get_grupo(db, grupo_id)

    if not grupo:
        return None

    for key, value in to_update_data(grupo_data).items():
        setattr(grupo, key, value)

    db.commit()
    db.refresh(grupo)

    return grupo


def delete_grupo(db: Session, grupo_id: int):
    grupo = get_grupo(db, grupo_id)

    if not grupo:
        return False

    db.delete(grupo)
    db.commit()

    return True
