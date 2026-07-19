from sqlalchemy.orm import Session

from app.crud._crud_utils import to_create_data, to_update_data
from app.models.documento_alumno import DocumentoAlumno


def get_documentos_alumno(db: Session):
    return db.query(DocumentoAlumno).all()


def get_documento_alumno(db: Session, documento_id: int):
    return (
        db.query(DocumentoAlumno)
        .filter(DocumentoAlumno.id_documento == documento_id)
        .first()
    )


def create_documento_alumno(db: Session, documento_data):
    nuevo_documento = DocumentoAlumno(**to_create_data(documento_data))

    db.add(nuevo_documento)
    db.commit()
    db.refresh(nuevo_documento)

    return nuevo_documento


def update_documento_alumno(db: Session, documento_id: int, documento_data):
    documento = get_documento_alumno(db, documento_id)

    if not documento:
        return None

    for key, value in to_update_data(documento_data).items():
        setattr(documento, key, value)

    db.commit()
    db.refresh(documento)

    return documento


def delete_documento_alumno(db: Session, documento_id: int):
    documento = get_documento_alumno(db, documento_id)

    if not documento:
        return False

    db.delete(documento)
    db.commit()

    return True
