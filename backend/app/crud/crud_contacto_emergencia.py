from sqlalchemy.orm import Session

from app.crud._crud_utils import to_create_data, to_update_data
from app.models.contacto_emergencia import ContactoEmergencia


def get_contactos_emergencia(db: Session):
    return db.query(ContactoEmergencia).all()


def get_contacto_emergencia(db: Session, contacto_id: int):
    return (
        db.query(ContactoEmergencia)
        .filter(ContactoEmergencia.id_contacto == contacto_id)
        .first()
    )


def create_contacto_emergencia(db: Session, contacto_data):
    nuevo_contacto = ContactoEmergencia(**to_create_data(contacto_data))

    db.add(nuevo_contacto)
    db.commit()
    db.refresh(nuevo_contacto)

    return nuevo_contacto


def update_contacto_emergencia(db: Session, contacto_id: int, contacto_data):
    contacto = get_contacto_emergencia(db, contacto_id)

    if not contacto:
        return None

    for key, value in to_update_data(contacto_data).items():
        setattr(contacto, key, value)

    db.commit()
    db.refresh(contacto)

    return contacto


def delete_contacto_emergencia(db: Session, contacto_id: int):
    contacto = get_contacto_emergencia(db, contacto_id)

    if not contacto:
        return False

    db.delete(contacto)
    db.commit()

    return True
