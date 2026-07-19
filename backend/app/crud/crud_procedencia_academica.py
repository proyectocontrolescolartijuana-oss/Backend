from sqlalchemy.orm import Session

from app.crud._crud_utils import to_create_data, to_update_data
from app.models.procedencia_academica import ProcedenciaAcademica


def get_procedencias_academicas(db: Session):
    return db.query(ProcedenciaAcademica).all()


def get_procedencia_academica(db: Session, procedencia_id: int):
    return (
        db.query(ProcedenciaAcademica)
        .filter(ProcedenciaAcademica.id_procedencia == procedencia_id)
        .first()
    )


def create_procedencia_academica(db: Session, procedencia_data):
    nueva_procedencia = ProcedenciaAcademica(**to_create_data(procedencia_data))

    db.add(nueva_procedencia)
    db.commit()
    db.refresh(nueva_procedencia)

    return nueva_procedencia


def update_procedencia_academica(db: Session, procedencia_id: int, procedencia_data):
    procedencia = get_procedencia_academica(db, procedencia_id)

    if not procedencia:
        return None

    for key, value in to_update_data(procedencia_data).items():
        setattr(procedencia, key, value)

    db.commit()
    db.refresh(procedencia)

    return procedencia


def delete_procedencia_academica(db: Session, procedencia_id: int):
    procedencia = get_procedencia_academica(db, procedencia_id)

    if not procedencia:
        return False

    db.delete(procedencia)
    db.commit()

    return True
