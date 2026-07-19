from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.crud_detalles import get_seguros_medicos_detalle
from app.crud.crud_seguro_medico import (
    create_seguro_medico,
    delete_seguro_medico,
    get_seguro_medico,
    update_seguro_medico
)
from app.database import get_db
from app.schemas.detalles import SeguroMedicoDetalleResponse
from app.schemas.seguro_medico import SeguroMedicoCreate, SeguroMedicoUpdate


router = APIRouter(
    prefix="/seguros-medicos",
    tags=["Seguros medicos"]
)


@router.get("/", response_model=list[SeguroMedicoDetalleResponse])
def listar_seguros_medicos(
    alumno_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return get_seguros_medicos_detalle(db, alumno_id=alumno_id)


@router.get("/{seguro_id}", response_model=SeguroMedicoDetalleResponse)
def obtener_seguro_medico(
    seguro_id: int,
    db: Session = Depends(get_db)
):
    seguro = next(
        (
            item for item in get_seguros_medicos_detalle(db)
            if item["id_seguro"] == seguro_id
        ),
        None
    )

    if not seguro:
        raise HTTPException(status_code=404, detail="Seguro medico no encontrado")

    return seguro


@router.post("/", response_model=SeguroMedicoDetalleResponse)
def crear_seguro_medico(
    seguro: SeguroMedicoCreate,
    db: Session = Depends(get_db)
):
    nuevo_seguro = create_seguro_medico(db, seguro)

    return next(
        item for item in get_seguros_medicos_detalle(db)
        if item["id_seguro"] == nuevo_seguro.id_seguro
    )


@router.patch("/{seguro_id}", response_model=SeguroMedicoDetalleResponse)
def actualizar_seguro_medico(
    seguro_id: int,
    seguro: SeguroMedicoUpdate,
    db: Session = Depends(get_db)
):
    seguro_actualizado = update_seguro_medico(db, seguro_id, seguro)

    if not seguro_actualizado:
        raise HTTPException(status_code=404, detail="Seguro medico no encontrado")

    return next(
        item for item in get_seguros_medicos_detalle(db)
        if item["id_seguro"] == seguro_id
    )


@router.delete("/{seguro_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_seguro_medico(
    seguro_id: int,
    db: Session = Depends(get_db)
):
    if not get_seguro_medico(db, seguro_id):
        raise HTTPException(status_code=404, detail="Seguro medico no encontrado")

    delete_seguro_medico(db, seguro_id)
