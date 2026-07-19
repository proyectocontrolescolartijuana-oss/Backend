from sqlalchemy.orm import Session

from app.crud._crud_utils import to_create_data, to_update_data
from app.models.cuatrimestre import Cuatrimestre


def get_cuatrimestres(db: Session):
    return db.query(Cuatrimestre).all()


def get_cuatrimestre(db: Session, cuatrimestre_id: int):
    return (
        db.query(Cuatrimestre)
        .filter(Cuatrimestre.id_cuatrimestre == cuatrimestre_id)
        .first()
    )


def create_cuatrimestre(db: Session, cuatrimestre_data):
    nuevo_cuatrimestre = Cuatrimestre(**to_create_data(cuatrimestre_data))

    db.add(nuevo_cuatrimestre)
    db.commit()
    db.refresh(nuevo_cuatrimestre)

    return nuevo_cuatrimestre


def update_cuatrimestre(db: Session, cuatrimestre_id: int, cuatrimestre_data):
    cuatrimestre = get_cuatrimestre(db, cuatrimestre_id)

    if not cuatrimestre:
        return None

    for key, value in to_update_data(cuatrimestre_data).items():
        setattr(cuatrimestre, key, value)

    db.commit()
    db.refresh(cuatrimestre)

    return cuatrimestre


def delete_cuatrimestre(db: Session, cuatrimestre_id: int):
    cuatrimestre = get_cuatrimestre(db, cuatrimestre_id)

    if not cuatrimestre:
        return False

    db.delete(cuatrimestre)
    db.commit()

    return True
