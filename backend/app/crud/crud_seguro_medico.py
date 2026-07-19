from sqlalchemy.orm import Session

from app.crud._crud_utils import to_create_data, to_update_data
from app.models.seguro_medico import SeguroMedico


def get_seguros_medicos(db: Session):
    return db.query(SeguroMedico).all()


def get_seguro_medico(db: Session, seguro_id: int):
    return (
        db.query(SeguroMedico)
        .filter(SeguroMedico.id_seguro == seguro_id)
        .first()
    )


def create_seguro_medico(db: Session, seguro_data):
    nuevo_seguro = SeguroMedico(**to_create_data(seguro_data))

    db.add(nuevo_seguro)
    db.commit()
    db.refresh(nuevo_seguro)

    return nuevo_seguro


def update_seguro_medico(db: Session, seguro_id: int, seguro_data):
    seguro = get_seguro_medico(db, seguro_id)

    if not seguro:
        return None

    for key, value in to_update_data(seguro_data).items():
        setattr(seguro, key, value)

    db.commit()
    db.refresh(seguro)

    return seguro


def delete_seguro_medico(db: Session, seguro_id: int):
    seguro = get_seguro_medico(db, seguro_id)

    if not seguro:
        return False

    db.delete(seguro)
    db.commit()

    return True
