from sqlalchemy.orm import Session

from app.crud._crud_utils import to_create_data, to_update_data
from app.models.asistencia import Asistencia


def get_asistencias(db: Session):
    return db.query(Asistencia).all()


def get_asistencia(db: Session, asistencia_id: int):
    return (
        db.query(Asistencia)
        .filter(Asistencia.id_asistencia == asistencia_id)
        .first()
    )


def create_asistencia(db: Session, asistencia_data):
    nueva_asistencia = Asistencia(**to_create_data(asistencia_data))

    db.add(nueva_asistencia)
    db.commit()
    db.refresh(nueva_asistencia)

    return nueva_asistencia


def update_asistencia(db: Session, asistencia_id: int, asistencia_data):
    asistencia = get_asistencia(db, asistencia_id)

    if not asistencia:
        return None

    for key, value in to_update_data(asistencia_data).items():
        setattr(asistencia, key, value)

    db.commit()
    db.refresh(asistencia)

    return asistencia


def delete_asistencia(db: Session, asistencia_id: int):
    asistencia = get_asistencia(db, asistencia_id)

    if not asistencia:
        return False

    db.delete(asistencia)
    db.commit()

    return True
