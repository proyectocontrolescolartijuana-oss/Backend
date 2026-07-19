from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.crud_detalles import get_inscripciones_detalle
from app.crud.crud_inscripcion import (
    create_inscripcion,
    delete_inscripcion,
    get_inscripcion,
    update_inscripcion
)
from app.database import get_db
from app.schemas.detalles import InscripcionDetalleResponse
from app.schemas.inscripcion import InscripcionCreate, InscripcionUpdate


router = APIRouter(
    prefix="/inscripciones",
    tags=["Inscripciones"]
)


@router.get(
    "/",
    response_model=list[InscripcionDetalleResponse]
)
def listar_inscripciones(
    alumno_id: Optional[int] = None,
    grupo_id: Optional[int] = None,
    periodo_id: Optional[int] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return get_inscripciones_detalle(
        db,
        alumno_id=alumno_id,
        grupo_id=grupo_id,
        periodo_id=periodo_id,
        estado=estado
    )


@router.get(
    "/{inscripcion_id}",
    response_model=InscripcionDetalleResponse
)
def obtener_inscripcion(
    inscripcion_id: int,
    db: Session = Depends(get_db)
):
    inscripciones = get_inscripciones_detalle(db)
    inscripcion = next(
        (
            item for item in inscripciones
            if item["id_inscripcion"] == inscripcion_id
        ),
        None
    )

    if not inscripcion:
        raise HTTPException(
            status_code=404,
            detail="Inscripcion no encontrada"
        )

    return inscripcion


@router.post(
    "/",
    response_model=InscripcionDetalleResponse
)
def crear_inscripcion(
    inscripcion: InscripcionCreate,
    db: Session = Depends(get_db)
):
    nueva_inscripcion = create_inscripcion(db, inscripcion)
    inscripciones = get_inscripciones_detalle(db)

    return next(
        item for item in inscripciones
        if item["id_inscripcion"] == nueva_inscripcion.id_inscripcion
    )


@router.patch(
    "/{inscripcion_id}",
    response_model=InscripcionDetalleResponse
)
def actualizar_inscripcion(
    inscripcion_id: int,
    inscripcion: InscripcionUpdate,
    db: Session = Depends(get_db)
):
    inscripcion_actualizada = update_inscripcion(db, inscripcion_id, inscripcion)

    if not inscripcion_actualizada:
        raise HTTPException(
            status_code=404,
            detail="Inscripcion no encontrada"
        )

    inscripciones = get_inscripciones_detalle(db)

    return next(
        item for item in inscripciones
        if item["id_inscripcion"] == inscripcion_id
    )


@router.delete(
    "/{inscripcion_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_inscripcion(
    inscripcion_id: int,
    db: Session = Depends(get_db)
):
    if not get_inscripcion(db, inscripcion_id):
        raise HTTPException(
            status_code=404,
            detail="Inscripcion no encontrada"
        )

    delete_inscripcion(db, inscripcion_id)
