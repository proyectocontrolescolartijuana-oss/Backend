from sqlalchemy.orm import Session

from app.crud._crud_utils import to_create_data, to_update_data
from app.models.grupo_materia import GrupoMateria


def get_grupos_materias(db: Session):
    return db.query(GrupoMateria).all()


def get_grupo_materia(db: Session, grupo_materia_id: int):
    return (
        db.query(GrupoMateria)
        .filter(GrupoMateria.id_grupo_materia == grupo_materia_id)
        .first()
    )


def create_grupo_materia(db: Session, grupo_materia_data):
    nuevo_grupo_materia = GrupoMateria(**to_create_data(grupo_materia_data))

    db.add(nuevo_grupo_materia)
    db.commit()
    db.refresh(nuevo_grupo_materia)

    return nuevo_grupo_materia


def update_grupo_materia(db: Session, grupo_materia_id: int, grupo_materia_data):
    grupo_materia = get_grupo_materia(db, grupo_materia_id)

    if not grupo_materia:
        return None

    for key, value in to_update_data(grupo_materia_data).items():
        setattr(grupo_materia, key, value)

    db.commit()
    db.refresh(grupo_materia)

    return grupo_materia


def delete_grupo_materia(db: Session, grupo_materia_id: int):
    grupo_materia = get_grupo_materia(db, grupo_materia_id)

    if not grupo_materia:
        return False

    db.delete(grupo_materia)
    db.commit()

    return True
