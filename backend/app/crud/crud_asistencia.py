from sqlalchemy.orm import Session

from app.crud._crud_utils import to_create_data, to_update_data
from app.crud.crud_calificacion import validar_parcial_de_la_carga
from app.models.asistencia import Asistencia


def get_asistencias(db: Session):
    return db.query(Asistencia).all()


def get_asistencia(db: Session, asistencia_id: int):
    return (
        db.query(Asistencia)
        .filter(Asistencia.id_asistencia == asistencia_id)
        .first()
    )


def create_asistencia(db: Session, asistencia_data):
    datos = to_create_data(asistencia_data)

    if datos.get("id_parcial") is not None:
        validar_parcial_de_la_carga(
            db,
            datos["id_carga"],
            datos["id_parcial"]
        )

    nueva_asistencia = Asistencia(**datos)

    db.add(nueva_asistencia)
    db.commit()
    db.refresh(nueva_asistencia)

    return nueva_asistencia


def update_asistencia(db: Session, asistencia_id: int, asistencia_data):
    asistencia = get_asistencia(db, asistencia_id)

    if not asistencia:
        return None

    datos = to_update_data(asistencia_data)
    id_parcial = datos.get("id_parcial", asistencia.id_parcial)

    # Se valida la combinacion resultante carga + parcial, no solo lo enviado.
    if id_parcial is not None:
        validar_parcial_de_la_carga(
            db,
            datos.get("id_carga", asistencia.id_carga),
            id_parcial
        )

    for key, value in datos.items():
        setattr(asistencia, key, value)

    db.commit()
    db.refresh(asistencia)

    return asistencia


def delete_asistencia(db: Session, asistencia_id: int):
    asistencia = get_asistencia(db, asistencia_id)

    if not asistencia:
        return False

    db.delete(asistencia)
    db.commit()

    return True