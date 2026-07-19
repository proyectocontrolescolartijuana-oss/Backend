from sqlalchemy.orm import Session

from app.crud._crud_utils import to_create_data, to_update_data
from app.models.servicio_social import ServicioSocial


def get_servicios_sociales(db: Session):
    return db.query(ServicioSocial).all()


def get_servicio_social(db: Session, servicio_id: int):
    return (
        db.query(ServicioSocial)
        .filter(ServicioSocial.id_servicio == servicio_id)
        .first()
    )


def create_servicio_social(db: Session, servicio_data):
    nuevo_servicio = ServicioSocial(**to_create_data(servicio_data))

    db.add(nuevo_servicio)
    db.commit()
    db.refresh(nuevo_servicio)

    return nuevo_servicio


def update_servicio_social(db: Session, servicio_id: int, servicio_data):
    servicio = get_servicio_social(db, servicio_id)

    if not servicio:
        return None

    for key, value in to_update_data(servicio_data).items():
        setattr(servicio, key, value)

    db.commit()
    db.refresh(servicio)

    return servicio


def delete_servicio_social(db: Session, servicio_id: int):
    servicio = get_servicio_social(db, servicio_id)

    if not servicio:
        return False

    db.delete(servicio)
    db.commit()

    return True
