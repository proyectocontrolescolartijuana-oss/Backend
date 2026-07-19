from sqlalchemy.orm import Session

from app.crud._crud_utils import to_create_data, to_update_data
from app.models.tipo_documento import TipoDocumento


def get_tipos_documento(db: Session):
    return db.query(TipoDocumento).all()


def get_tipo_documento(db: Session, tipo_documento_id: int):
    return (
        db.query(TipoDocumento)
        .filter(TipoDocumento.id_tipo_documento == tipo_documento_id)
        .first()
    )


def create_tipo_documento(db: Session, tipo_documento_data):
    nuevo_tipo_documento = TipoDocumento(**to_create_data(tipo_documento_data))

    db.add(nuevo_tipo_documento)
    db.commit()
    db.refresh(nuevo_tipo_documento)

    return nuevo_tipo_documento


def update_tipo_documento(db: Session, tipo_documento_id: int, tipo_documento_data):
    tipo_documento = get_tipo_documento(db, tipo_documento_id)

    if not tipo_documento:
        return None

    for key, value in to_update_data(tipo_documento_data).items():
        setattr(tipo_documento, key, value)

    db.commit()
    db.refresh(tipo_documento)

    return tipo_documento


def delete_tipo_documento(db: Session, tipo_documento_id: int):
    tipo_documento = get_tipo_documento(db, tipo_documento_id)

    if not tipo_documento:
        return False

    db.delete(tipo_documento)
    db.commit()

    return True
