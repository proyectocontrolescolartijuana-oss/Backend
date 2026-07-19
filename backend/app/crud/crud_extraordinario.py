from sqlalchemy.orm import Session

from app.crud._crud_utils import to_create_data, to_update_data
from app.models.extraordinario import Extraordinario


def get_extraordinarios(db: Session):
    return db.query(Extraordinario).all()


def get_extraordinario(db: Session, extraordinario_id: int):
    return (
        db.query(Extraordinario)
        .filter(Extraordinario.id_extraordinario == extraordinario_id)
        .first()
    )


def create_extraordinario(db: Session, extraordinario_data):
    nuevo_extraordinario = Extraordinario(**to_create_data(extraordinario_data))

    db.add(nuevo_extraordinario)
    db.commit()
    db.refresh(nuevo_extraordinario)

    return nuevo_extraordinario


def update_extraordinario(db: Session, extraordinario_id: int, extraordinario_data):
    extraordinario = get_extraordinario(db, extraordinario_id)

    if not extraordinario:
        return None

    for key, value in to_update_data(extraordinario_data).items():
        setattr(extraordinario, key, value)

    db.commit()
    db.refresh(extraordinario)

    return extraordinario


def delete_extraordinario(db: Session, extraordinario_id: int):
    extraordinario = get_extraordinario(db, extraordinario_id)

    if not extraordinario:
        return False

    db.delete(extraordinario)
    db.commit()

    return True
