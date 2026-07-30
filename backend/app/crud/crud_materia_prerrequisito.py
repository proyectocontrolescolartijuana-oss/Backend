from sqlalchemy.orm import Session, joinedload

from app.models import init as _models_init
from app.models.materia import Materia
from app.models.materia_prerrequisito import MateriaPrerrequisito


PRERREQUISITO_RELATIONS = (
    joinedload(MateriaPrerrequisito.materia_requerida),
)


def _query(db: Session):
    return db.query(MateriaPrerrequisito).options(*PRERREQUISITO_RELATIONS)


def _materia_existe(db: Session, materia_id: int):
    return (
        db.query(Materia.id_materia)
        .filter(Materia.id_materia == materia_id)
        .first()
    )


def listar_prerrequisitos(db: Session, materia_id: int):
    return (
        _query(db)
        .filter(MateriaPrerrequisito.id_materia == materia_id)
        .order_by(MateriaPrerrequisito.id_prerrequisito)
        .all()
    )


def obtener_prerrequisito(db: Session, materia_id: int, prerrequisito_id: int):
    return (
        _query(db)
        .filter(
            MateriaPrerrequisito.id_materia == materia_id,
            MateriaPrerrequisito.id_prerrequisito == prerrequisito_id,
        )
        .first()
    )


def crear_prerrequisito(db: Session, materia_id: int, datos):
    if not _materia_existe(db, materia_id):
        return None

    data = datos.model_dump()
    id_materia_requerida = data["id_materia_requerida"]

    if materia_id == id_materia_requerida:
        raise ValueError("Una materia no puede ser prerrequisito de si misma")

    if not _materia_existe(db, id_materia_requerida):
        raise ValueError("Materia requerida no encontrada")

    duplicado = (
        db.query(MateriaPrerrequisito.id_prerrequisito)
        .filter(
            MateriaPrerrequisito.id_materia == materia_id,
            MateriaPrerrequisito.id_materia_requerida == id_materia_requerida,
        )
        .first()
    )

    if duplicado:
        raise ValueError("Este prerrequisito ya esta registrado")

    prerrequisito = MateriaPrerrequisito(
        id_materia=materia_id,
        **data
    )

    db.add(prerrequisito)
    db.commit()

    return obtener_prerrequisito(
        db,
        materia_id,
        prerrequisito.id_prerrequisito
    )


def actualizar_prerrequisito(db: Session, materia_id: int, prerrequisito_id: int, datos):
    prerrequisito = obtener_prerrequisito(db, materia_id, prerrequisito_id)

    if not prerrequisito:
        return None

    data = datos.model_dump(exclude_unset=True)
    id_materia_requerida = data.get(
        "id_materia_requerida",
        prerrequisito.id_materia_requerida
    )

    if materia_id == id_materia_requerida:
        raise ValueError("Una materia no puede ser prerrequisito de si misma")

    if "id_materia_requerida" in data and not _materia_existe(db, id_materia_requerida):
        raise ValueError("Materia requerida no encontrada")

    if "id_materia_requerida" in data:
        duplicado = (
            db.query(MateriaPrerrequisito.id_prerrequisito)
            .filter(
                MateriaPrerrequisito.id_materia == materia_id,
                MateriaPrerrequisito.id_materia_requerida == id_materia_requerida,
                MateriaPrerrequisito.id_prerrequisito != prerrequisito_id,
            )
            .first()
        )

        if duplicado:
            raise ValueError("Este prerrequisito ya esta registrado")

    for key, value in data.items():
        setattr(prerrequisito, key, value)

    db.commit()

    return obtener_prerrequisito(db, materia_id, prerrequisito_id)


def eliminar_prerrequisito(db: Session, materia_id: int, prerrequisito_id: int):
    prerrequisito = obtener_prerrequisito(db, materia_id, prerrequisito_id)

    if not prerrequisito:
        return False

    db.delete(prerrequisito)
    db.commit()

    return True
