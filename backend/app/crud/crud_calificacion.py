from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.calificacion import Calificacion
from app.models.carga_academica import CargaAcademica

from app.schemas.calificacion import (
    CalificacionCreate
)
from app.services.esquema_evaluacion import (
    EsquemaEvaluacionError,
    esquema_de_grupo_materia
)


def validar_parcial_de_la_carga(
    db: Session,
    id_carga: int,
    id_parcial: int
):
    """El parcial debe pertenecer a la modalidad del grupo de la carga."""
    carga = (
        db.query(CargaAcademica.id_grupo_materia)
        .filter(CargaAcademica.id_carga == id_carga)
        .first()
    )

    if not carga:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carga academica no encontrada"
        )

    try:
        esquema = esquema_de_grupo_materia(db, carga[0])
    except EsquemaEvaluacionError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )

    if not esquema.contiene(id_parcial):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"El parcial {id_parcial} no pertenece a la modalidad "
                f"{esquema.modalidad}"
            )
        )


def get_calificaciones(db: Session):
    return db.query(Calificacion).all()

def get_calificacion(db: Session, calificacion_id: int):
    return (
        db.query(Calificacion)
        .filter(Calificacion.id_calificacion == calificacion_id)
        .first()
    )

def create_calificacion(
    db: Session,
    calificacion: CalificacionCreate
):
    validar_parcial_de_la_carga(
        db,
        calificacion.id_carga,
        calificacion.id_parcial
    )

    nueva_calificacion = Calificacion(
        **calificacion.model_dump()
    )

    db.add(nueva_calificacion)

    db.commit()

    db.refresh(nueva_calificacion)

    return nueva_calificacion

def update_calificacion(
    db: Session,
    calificacion_id: int,
    calificacion_data
):
    calificacion = get_calificacion(db, calificacion_id)

    if not calificacion:
        return None

    update_data = calificacion_data.model_dump(
        exclude_unset=True
    )

    # Se valida la combinacion resultante carga + parcial, no solo lo enviado.
    validar_parcial_de_la_carga(
        db,
        update_data.get("id_carga", calificacion.id_carga),
        update_data.get("id_parcial", calificacion.id_parcial)
    )

    for key, value in update_data.items():
        setattr(calificacion, key, value)

    db.commit()
    db.refresh(calificacion)

    return calificacion

def delete_calificacion(
    db: Session,
    calificacion_id: int
):
    calificacion = get_calificacion(db, calificacion_id)

    if not calificacion:
        return False

    db.delete(calificacion)
    db.commit()

    return True