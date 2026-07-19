from sqlalchemy.orm import Session

from app.crud._crud_utils import to_create_data, to_update_data
from app.models.historial_academico import HistorialAcademico


def get_historiales_academicos(db: Session):
    return db.query(HistorialAcademico).all()


def get_historial_academico(db: Session, historial_id: int):
    return (
        db.query(HistorialAcademico)
        .filter(HistorialAcademico.id_historial == historial_id)
        .first()
    )


def create_historial_academico(db: Session, historial_data):
    nuevo_historial = HistorialAcademico(**to_create_data(historial_data))

    db.add(nuevo_historial)
    db.commit()
    db.refresh(nuevo_historial)

    return nuevo_historial


def update_historial_academico(db: Session, historial_id: int, historial_data):
    historial = get_historial_academico(db, historial_id)

    if not historial:
        return None

    for key, value in to_update_data(historial_data).items():
        setattr(historial, key, value)

    db.commit()
    db.refresh(historial)

    return historial


def delete_historial_academico(db: Session, historial_id: int):
    historial = get_historial_academico(db, historial_id)

    if not historial:
        return False

    db.delete(historial)
    db.commit()

    return True
