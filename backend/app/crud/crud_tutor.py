from sqlalchemy.orm import Session

from app.crud._crud_utils import to_create_data, to_update_data
from app.models.tutor import Tutor


def get_tutores(db: Session):
    return db.query(Tutor).all()


def get_tutor(db: Session, tutor_id: int):
    return (
        db.query(Tutor)
        .filter(Tutor.id_tutor == tutor_id)
        .first()
    )


def create_tutor(db: Session, tutor_data):
    nuevo_tutor = Tutor(**to_create_data(tutor_data))

    db.add(nuevo_tutor)
    db.commit()
    db.refresh(nuevo_tutor)

    return nuevo_tutor


def update_tutor(db: Session, tutor_id: int, tutor_data):
    tutor = get_tutor(db, tutor_id)

    if not tutor:
        return None

    for key, value in to_update_data(tutor_data).items():
        setattr(tutor, key, value)

    db.commit()
    db.refresh(tutor)

    return tutor


def delete_tutor(db: Session, tutor_id: int):
    tutor = get_tutor(db, tutor_id)

    if not tutor:
        return False

    db.delete(tutor)
    db.commit()

    return True
