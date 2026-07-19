from sqlalchemy.orm import Session

from app.crud._crud_utils import to_create_data, to_update_data
from app.models.practica_profesional import PracticaProfesional


def get_practicas_profesionales(db: Session):
    return db.query(PracticaProfesional).all()


def get_practica_profesional(db: Session, practica_id: int):
    return (
        db.query(PracticaProfesional)
        .filter(PracticaProfesional.id_practica == practica_id)
        .first()
    )


def create_practica_profesional(db: Session, practica_data):
    nueva_practica = PracticaProfesional(**to_create_data(practica_data))

    db.add(nueva_practica)
    db.commit()
    db.refresh(nueva_practica)

    return nueva_practica


def update_practica_profesional(db: Session, practica_id: int, practica_data):
    practica = get_practica_profesional(db, practica_id)

    if not practica:
        return None

    for key, value in to_update_data(practica_data).items():
        setattr(practica, key, value)

    db.commit()
    db.refresh(practica)

    return practica


def delete_practica_profesional(db: Session, practica_id: int):
    practica = get_practica_profesional(db, practica_id)

    if not practica:
        return False

    db.delete(practica)
    db.commit()

    return True
