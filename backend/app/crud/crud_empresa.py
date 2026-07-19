from sqlalchemy.orm import Session

from app.crud._crud_utils import to_create_data, to_update_data
from app.models.empresa import Empresa


def get_empresas(db: Session):
    return db.query(Empresa).all()


def get_empresa(db: Session, empresa_id: int):
    return (
        db.query(Empresa)
        .filter(Empresa.id_empresa == empresa_id)
        .first()
    )


def create_empresa(db: Session, empresa_data):
    nueva_empresa = Empresa(**to_create_data(empresa_data))

    db.add(nueva_empresa)
    db.commit()
    db.refresh(nueva_empresa)

    return nueva_empresa


def update_empresa(db: Session, empresa_id: int, empresa_data):
    empresa = get_empresa(db, empresa_id)

    if not empresa:
        return None

    for key, value in to_update_data(empresa_data).items():
        setattr(empresa, key, value)

    db.commit()
    db.refresh(empresa)

    return empresa


def delete_empresa(db: Session, empresa_id: int):
    empresa = get_empresa(db, empresa_id)

    if not empresa:
        return False

    db.delete(empresa)
    db.commit()

    return True
