from sqlalchemy.orm import Session

from app.crud._crud_utils import to_create_data, to_update_data
from app.models.recepcion_documento import RecepcionDocumento


def get_recepciones_documento(db: Session):
    return db.query(RecepcionDocumento).all()


def get_recepcion_documento(db: Session, recepcion_id: int):
    return (
        db.query(RecepcionDocumento)
        .filter(RecepcionDocumento.id_recepcion == recepcion_id)
        .first()
    )


def create_recepcion_documento(db: Session, recepcion_data):
    nueva_recepcion = RecepcionDocumento(**to_create_data(recepcion_data))

    db.add(nueva_recepcion)
    db.commit()
    db.refresh(nueva_recepcion)

    return nueva_recepcion


def update_recepcion_documento(db: Session, recepcion_id: int, recepcion_data):
    recepcion = get_recepcion_documento(db, recepcion_id)

    if not recepcion:
        return None

    for key, value in to_update_data(recepcion_data).items():
        setattr(recepcion, key, value)

    db.commit()
    db.refresh(recepcion)

    return recepcion


def delete_recepcion_documento(db: Session, recepcion_id: int):
    recepcion = get_recepcion_documento(db, recepcion_id)

    if not recepcion:
        return False

    db.delete(recepcion)
    db.commit()

    return True
