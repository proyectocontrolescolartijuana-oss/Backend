from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.crud_alumno_tutor import (
    create_alumno_tutor,
    delete_alumno_tutor,
    get_alumno_tutor
)
from app.crud.crud_detalles import (
    get_alumnos_por_tutor,
    get_alumnos_tutores_detalle,
    get_tutores_por_alumno
)
from app.database import get_db
from app.schemas.detalles import (
    AlumnoRelacionadoResponse,
    AlumnoTutorDetalleResponse,
    TutorRelacionadoResponse
)
from app.schemas.alumno_tutor import AlumnoTutorCreate, AlumnoTutorResponse


router = APIRouter(
    prefix="/alumnos-tutores",
    tags=["Alumnos tutores"]
)


@router.get(
    "/",
    response_model=list[AlumnoTutorDetalleResponse]
)
def listar_alumnos_tutores(
    db: Session = Depends(get_db)
):
    return get_alumnos_tutores_detalle(db)


@router.get(
    "/alumno/{alumno_id}",
    response_model=list[TutorRelacionadoResponse]
)
def listar_tutores_por_alumno(
    alumno_id: int,
    db: Session = Depends(get_db)
):
    return get_tutores_por_alumno(db, alumno_id)


@router.get(
    "/tutor/{tutor_id}",
    response_model=list[AlumnoRelacionadoResponse]
)
def listar_alumnos_por_tutor(
    tutor_id: int,
    db: Session = Depends(get_db)
):
    return get_alumnos_por_tutor(db, tutor_id)


@router.get(
    "/{alumno_id}/{tutor_id}",
    response_model=AlumnoTutorResponse
)
def obtener_alumno_tutor(
    alumno_id: int,
    tutor_id: int,
    db: Session = Depends(get_db)
):
    relacion = get_alumno_tutor(db, alumno_id, tutor_id)

    if not relacion:
        raise HTTPException(
            status_code=404,
            detail="Relacion alumno tutor no encontrada"
        )

    return relacion


@router.post(
    "/",
    response_model=AlumnoTutorResponse
)
def crear_alumno_tutor(
    relacion: AlumnoTutorCreate,
    db: Session = Depends(get_db)
):
    return create_alumno_tutor(
        db,
        relacion.id_alumno,
        relacion.id_tutor
    )


@router.delete(
    "/{alumno_id}/{tutor_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_alumno_tutor(
    alumno_id: int,
    tutor_id: int,
    db: Session = Depends(get_db)
):
    eliminada = delete_alumno_tutor(db, alumno_id, tutor_id)

    if not eliminada:
        raise HTTPException(
            status_code=404,
            detail="Relacion alumno tutor no encontrada"
        )
