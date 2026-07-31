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
    PracticaProfesionalEstatusUpdate,
    PracticaProfesionalUpdate
)
from app.models.practica_profesional import PracticaProfesional
from app.models.empresa import Empresa


router = APIRouter(
    prefix="/practicas-profesionales",
    tags=["Practicas profesionales"]
)


def resolver_empresa_id(db: Session, empresa_id: Optional[int], empresa_nombre: Optional[str]):
    if empresa_id is not None:
        return empresa_id

    if empresa_nombre is None:
        return None

    nombre = empresa_nombre.strip()
    if not nombre:
        return None

    empresa = (
        db.query(Empresa)
        .filter(Empresa.nombre == nombre)
        .first()
    )
    if empresa is None:
        empresa = Empresa(nombre=nombre)
        db.add(empresa)
        db.flush()

    return empresa.id_empresa


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


@router.patch(
    "/alumno/{alumno_id}/estatus",
    response_model=PracticaProfesionalDetalleResponse
)
def guardar_estatus_practica(
    alumno_id: int,
    datos: PracticaProfesionalEstatusUpdate,
    db: Session = Depends(get_db)
):
    practica = (
        db.query(PracticaProfesional)
        .filter(PracticaProfesional.id_alumno == alumno_id)
        .first()
    )

    if practica is None:
        practica = PracticaProfesional(id_alumno=alumno_id)
        db.add(practica)

    practica.oficio_campo = datos.oficio_campo
    practica.horas_campo = datos.horas_campo
    db.commit()
    db.refresh(practica)

    return next(
        item for item in get_practicas_profesionales_detalle(db)
        if item["id_practica"] == practica.id_practica
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

@router.patch(
    "/alumno/{alumno_id}/estatus",
    response_model=PracticaProfesionalDetalleResponse
)
def guardar_estatus_practica(
    alumno_id: int,
    datos: PracticaProfesionalEstatusUpdate,
    db: Session = Depends(get_db)
):
    practica = (
        db.query(PracticaProfesional)
        .filter(PracticaProfesional.id_alumno == alumno_id)
        .first()
    )

    if practica is None:
        practica = PracticaProfesional(id_alumno=alumno_id)
        db.add(practica)

    practica.oficio_campo = datos.oficio_campo
    practica.horas_campo = datos.horas_campo
    if datos.id_empresa is not None or datos.empresa_nombre is not None:
        practica.id_empresa = resolver_empresa_id(
            db,
            datos.id_empresa,
            datos.empresa_nombre
        )
    db.commit()
    db.refresh(practica)

    return next(
        item for item in get_practicas_profesionales_detalle(db)
        if item["id_practica"] == practica.id_practica
    )



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
