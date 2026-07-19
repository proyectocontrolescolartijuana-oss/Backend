from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.crud_detalles import get_historiales_academicos_detalle
from app.crud.crud_historial_academico import (
    create_historial_academico,
    delete_historial_academico,
    get_historial_academico,
    update_historial_academico
)
from app.database import get_db
from app.schemas.detalles import HistorialAcademicoDetalleResponse
from app.schemas.historial_academico import (
    HistorialAcademicoCreate,
    HistorialAcademicoUpdate
)


router = APIRouter(
    prefix="/historiales-academicos",
    tags=["Historiales academicos"]
)


@router.get(
    "/",
    response_model=list[HistorialAcademicoDetalleResponse]
)
def listar_historiales_academicos(
    alumno_id: Optional[int] = None,
    carrera_id: Optional[int] = None,
    materia_id: Optional[int] = None,
    periodo_id: Optional[int] = None,
    resultado: Optional[str] = None,
    tipo_evaluacion: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return get_historiales_academicos_detalle(
        db,
        alumno_id=alumno_id,
        carrera_id=carrera_id,
        materia_id=materia_id,
        periodo_id=periodo_id,
        resultado=resultado,
        tipo_evaluacion=tipo_evaluacion
    )



@router.get(
    "/{historial_id}",
    response_model=HistorialAcademicoDetalleResponse
)
def obtener_historial_academico(
    historial_id: int,
    db: Session = Depends(get_db)
):
    historial = next(
        (
            item for item in get_historiales_academicos_detalle(db)
            if item["id_historial"] == historial_id
        ),
        None
    )

    if not historial:
        raise HTTPException(
            status_code=404,
            detail="Historial academico no encontrado"
        )

    return historial


@router.post(
    "/",
    response_model=HistorialAcademicoDetalleResponse
)
def crear_historial_academico(
    historial: HistorialAcademicoCreate,
    db: Session = Depends(get_db)
):
    nuevo_historial = create_historial_academico(db, historial)

    return next(
        item for item in get_historiales_academicos_detalle(db)
        if item["id_historial"] == nuevo_historial.id_historial
    )


@router.patch(
    "/{historial_id}",
    response_model=HistorialAcademicoDetalleResponse
)
def actualizar_historial_academico(
    historial_id: int,
    historial: HistorialAcademicoUpdate,
    db: Session = Depends(get_db)
):
    historial_actualizado = update_historial_academico(db, historial_id, historial)

    if not historial_actualizado:
        raise HTTPException(
            status_code=404,
            detail="Historial academico no encontrado"
        )

    return next(
        item for item in get_historiales_academicos_detalle(db)
        if item["id_historial"] == historial_id
    )


@router.delete(
    "/{historial_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_historial_academico(
    historial_id: int,
    db: Session = Depends(get_db)
):
    if not get_historial_academico(db, historial_id):
        raise HTTPException(
            status_code=404,
            detail="Historial academico no encontrado"
        )

    delete_historial_academico(db, historial_id)
