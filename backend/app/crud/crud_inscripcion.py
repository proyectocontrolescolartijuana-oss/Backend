from sqlalchemy.orm import Session

from app.crud._crud_utils import to_create_data, to_update_data
from app.models.inscripcion import Inscripcion


def get_inscripciones(db: Session):
    return db.query(Inscripcion).all()


def get_inscripcion(db: Session, inscripcion_id: int):
    return (
        db.query(Inscripcion)
        .filter(Inscripcion.id_inscripcion == inscripcion_id)
        .first()
    )


def create_inscripcion(db: Session, inscripcion_data):
    nueva_inscripcion = Inscripcion(**to_create_data(inscripcion_data))

    db.add(nueva_inscripcion)
    db.commit()
    db.refresh(nueva_inscripcion)

    return nueva_inscripcion


def update_inscripcion(db: Session, inscripcion_id: int, inscripcion_data):
    inscripcion = get_inscripcion(db, inscripcion_id)

    if not inscripcion:
        return None

    for key, value in to_update_data(inscripcion_data).items():
        setattr(inscripcion, key, value)

    db.commit()
    db.refresh(inscripcion)

    return inscripcion


def delete_inscripcion(db: Session, inscripcion_id: int):
    inscripcion = get_inscripcion(db, inscripcion_id)

    if not inscripcion:
        return False

    db.delete(inscripcion)
    db.commit()

    return True
