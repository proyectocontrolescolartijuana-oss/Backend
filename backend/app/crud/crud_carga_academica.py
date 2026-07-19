from sqlalchemy.orm import Session

from app.crud._crud_utils import to_create_data, to_update_data
from app.models.carga_academica import CargaAcademica


def get_cargas_academicas(db: Session):
    return db.query(CargaAcademica).all()


def get_carga_academica(db: Session, carga_id: int):
    return (
        db.query(CargaAcademica)
        .filter(CargaAcademica.id_carga == carga_id)
        .first()
    )


def create_carga_academica(db: Session, carga_data):
    nueva_carga = CargaAcademica(**to_create_data(carga_data))

    db.add(nueva_carga)
    db.commit()
    db.refresh(nueva_carga)

    return nueva_carga


def update_carga_academica(db: Session, carga_id: int, carga_data):
    carga = get_carga_academica(db, carga_id)

    if not carga:
        return None

    for key, value in to_update_data(carga_data).items():
        setattr(carga, key, value)

    db.commit()
    db.refresh(carga)

    return carga


def delete_carga_academica(db: Session, carga_id: int):
    carga = get_carga_academica(db, carga_id)

    if not carga:
        return False

    db.delete(carga)
    db.commit()

    return True
