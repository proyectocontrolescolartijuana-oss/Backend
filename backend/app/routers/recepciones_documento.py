from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.crud_detalles import get_recepciones_documento_detalle
from app.crud.crud_recepcion_documento import (
    create_recepcion_documento,
    delete_recepcion_documento,
    get_recepcion_documento,
    update_recepcion_documento
)
from app.database import get_db
from app.schemas.detalles import RecepcionDocumentoDetalleResponse
from app.schemas.recepcion_documento import (
    RecepcionDocumentoCreate,
    RecepcionDocumentoUpdate
)


router = APIRouter(
    prefix="/recepciones-documento",
    tags=["Recepciones documento"]
)


@router.get(
    "/",
    response_model=list[RecepcionDocumentoDetalleResponse]
)
def listar_recepciones_documento(
    alumno_id: Optional[int] = None,
    recibido_por: Optional[int] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    db: Session = Depends(get_db)
):
    return get_recepciones_documento_detalle(
        db,
        alumno_id=alumno_id,
        recibido_por=recibido_por,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )


@router.get(
    "/{recepcion_id}",
    response_model=RecepcionDocumentoDetalleResponse
)
def obtener_recepcion_documento(
    recepcion_id: int,
    db: Session = Depends(get_db)
):
    recepcion = next(
        (
            item for item in get_recepciones_documento_detalle(db)
            if item["id_recepcion"] == recepcion_id
        ),
        None
    )

    if not recepcion:
        raise HTTPException(
            status_code=404,
            detail="Recepcion de documento no encontrada"
        )

    return recepcion


@router.post(
    "/",
    response_model=RecepcionDocumentoDetalleResponse
)
def crear_recepcion_documento(
    recepcion: RecepcionDocumentoCreate,
    db: Session = Depends(get_db)
):
    nueva_recepcion = create_recepcion_documento(db, recepcion)

    return next(
        item for item in get_recepciones_documento_detalle(db)
        if item["id_recepcion"] == nueva_recepcion.id_recepcion
    )


@router.patch(
    "/{recepcion_id}",
    response_model=RecepcionDocumentoDetalleResponse
)
def actualizar_recepcion_documento(
    recepcion_id: int,
    recepcion: RecepcionDocumentoUpdate,
    db: Session = Depends(get_db)
):
    recepcion_actualizada = update_recepcion_documento(
        db,
        recepcion_id,
        recepcion
    )

    if not recepcion_actualizada:
        raise HTTPException(
            status_code=404,
            detail="Recepcion de documento no encontrada"
        )

    return next(
        item for item in get_recepciones_documento_detalle(db)
        if item["id_recepcion"] == recepcion_id
    )


@router.delete(
    "/{recepcion_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_recepcion_documento(
    recepcion_id: int,
    db: Session = Depends(get_db)
):
    if not get_recepcion_documento(db, recepcion_id):
        raise HTTPException(
            status_code=404,
            detail="Recepcion de documento no encontrada"
        )

    delete_recepcion_documento(db, recepcion_id)
