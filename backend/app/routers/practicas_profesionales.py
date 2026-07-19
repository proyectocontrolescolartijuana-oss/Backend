from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.crud_detalles import get_practicas_profesionales_detalle
from app.crud.crud_practica_profesional import (
    create_practica_profesional,
    delete_practica_profesional,
    get_practica_profesional,
    update_practica_profesional
)
from app.database import get_db
from app.schemas.detalles import PracticaProfesionalDetalleResponse
from app.schemas.practica_profesional import (
    PracticaProfesionalCreate,
    PracticaProfesionalUpdate
)


router = APIRouter(
    prefix="/practicas-profesionales",
    tags=["Practicas profesionales"]
)


@router.get("/", response_model=list[PracticaProfesionalDetalleResponse])
def listar_practicas_profesionales(
    alumno_id: Optional[int] = None,
    empresa_id: Optional[int] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return get_practicas_profesionales_detalle(
        db,
        alumno_id=alumno_id,
        empresa_id=empresa_id,
        estado=estado
    )


@router.get("/{practica_id}", response_model=PracticaProfesionalDetalleResponse)
def obtener_practica_profesional(
    practica_id: int,
    db: Session = Depends(get_db)
):
    practica = next(
        (
            item for item in get_practicas_profesionales_detalle(db)
            if item["id_practica"] == practica_id
        ),
        None
    )

    if not practica:
        raise HTTPException(status_code=404, detail="Practica profesional no encontrada")

    return practica


@router.post("/", response_model=PracticaProfesionalDetalleResponse)
def crear_practica_profesional(
    practica: PracticaProfesionalCreate,
    db: Session = Depends(get_db)
):
    nueva_practica = create_practica_profesional(db, practica)

    return next(
        item for item in get_practicas_profesionales_detalle(db)
        if item["id_practica"] == nueva_practica.id_practica
    )


@router.patch("/{practica_id}", response_model=PracticaProfesionalDetalleResponse)
def actualizar_practica_profesional(
    practica_id: int,
    practica: PracticaProfesionalUpdate,
    db: Session = Depends(get_db)
):
    practica_actualizada = update_practica_profesional(db, practica_id, practica)

    if not practica_actualizada:
        raise HTTPException(status_code=404, detail="Practica profesional no encontrada")

    return next(
        item for item in get_practicas_profesionales_detalle(db)
        if item["id_practica"] == practica_id
    )


@router.delete("/{practica_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_practica_profesional(
    practica_id: int,
    db: Session = Depends(get_db)
):
    if not get_practica_profesional(db, practica_id):
        raise HTTPException(status_code=404, detail="Practica profesional no encontrada")

    delete_practica_profesional(db, practica_id)
