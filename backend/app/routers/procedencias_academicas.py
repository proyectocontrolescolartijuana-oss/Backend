from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.crud_detalles import get_procedencias_academicas_detalle
from app.crud.crud_procedencia_academica import (
    create_procedencia_academica,
    delete_procedencia_academica,
    get_procedencia_academica,
    update_procedencia_academica
)
from app.database import get_db
from app.schemas.detalles import ProcedenciaAcademicaDetalleResponse
from app.schemas.procedencia_academica import (
    ProcedenciaAcademicaCreate,
    ProcedenciaAcademicaUpdate
)


router = APIRouter(
    prefix="/procedencias-academicas",
    tags=["Procedencias academicas"]
)


@router.get("/", response_model=list[ProcedenciaAcademicaDetalleResponse])
def listar_procedencias_academicas(
    alumno_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return get_procedencias_academicas_detalle(db, alumno_id=alumno_id)


@router.get("/{procedencia_id}", response_model=ProcedenciaAcademicaDetalleResponse)
def obtener_procedencia_academica(
    procedencia_id: int,
    db: Session = Depends(get_db)
):
    procedencia = next(
        (
            item for item in get_procedencias_academicas_detalle(db)
            if item["id_procedencia"] == procedencia_id
        ),
        None
    )

    if not procedencia:
        raise HTTPException(status_code=404, detail="Procedencia academica no encontrada")

    return procedencia


@router.post("/", response_model=ProcedenciaAcademicaDetalleResponse)
def crear_procedencia_academica(
    procedencia: ProcedenciaAcademicaCreate,
    db: Session = Depends(get_db)
):
    nueva_procedencia = create_procedencia_academica(db, procedencia)

    return next(
        item for item in get_procedencias_academicas_detalle(db)
        if item["id_procedencia"] == nueva_procedencia.id_procedencia
    )


@router.patch("/{procedencia_id}", response_model=ProcedenciaAcademicaDetalleResponse)
def actualizar_procedencia_academica(
    procedencia_id: int,
    procedencia: ProcedenciaAcademicaUpdate,
    db: Session = Depends(get_db)
):
    procedencia_actualizada = update_procedencia_academica(
        db,
        procedencia_id,
        procedencia
    )

    if not procedencia_actualizada:
        raise HTTPException(status_code=404, detail="Procedencia academica no encontrada")

    return next(
        item for item in get_procedencias_academicas_detalle(db)
        if item["id_procedencia"] == procedencia_id
    )


@router.delete("/{procedencia_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_procedencia_academica(
    procedencia_id: int,
    db: Session = Depends(get_db)
):
    if not get_procedencia_academica(db, procedencia_id):
        raise HTTPException(status_code=404, detail="Procedencia academica no encontrada")

    delete_procedencia_academica(db, procedencia_id)
