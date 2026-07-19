from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.crud_contacto_emergencia import (
    create_contacto_emergencia,
    delete_contacto_emergencia,
    get_contacto_emergencia,
    update_contacto_emergencia
)
from app.crud.crud_detalles import get_contactos_emergencia_detalle
from app.database import get_db
from app.schemas.contacto_emergencia import (
    ContactoEmergenciaCreate,
    ContactoEmergenciaUpdate
)
from app.schemas.detalles import ContactoEmergenciaDetalleResponse


router = APIRouter(
    prefix="/contactos-emergencia",
    tags=["Contactos emergencia"]
)


@router.get("/", response_model=list[ContactoEmergenciaDetalleResponse])
def listar_contactos_emergencia(
    alumno_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return get_contactos_emergencia_detalle(db, alumno_id=alumno_id)


@router.get("/{contacto_id}", response_model=ContactoEmergenciaDetalleResponse)
def obtener_contacto_emergencia(
    contacto_id: int,
    db: Session = Depends(get_db)
):
    contacto = next(
        (
            item for item in get_contactos_emergencia_detalle(db)
            if item["id_contacto"] == contacto_id
        ),
        None
    )

    if not contacto:
        raise HTTPException(status_code=404, detail="Contacto de emergencia no encontrado")

    return contacto


@router.post("/", response_model=ContactoEmergenciaDetalleResponse)
def crear_contacto_emergencia(
    contacto: ContactoEmergenciaCreate,
    db: Session = Depends(get_db)
):
    nuevo_contacto = create_contacto_emergencia(db, contacto)

    return next(
        item for item in get_contactos_emergencia_detalle(db)
        if item["id_contacto"] == nuevo_contacto.id_contacto
    )


@router.patch("/{contacto_id}", response_model=ContactoEmergenciaDetalleResponse)
def actualizar_contacto_emergencia(
    contacto_id: int,
    contacto: ContactoEmergenciaUpdate,
    db: Session = Depends(get_db)
):
    contacto_actualizado = update_contacto_emergencia(db, contacto_id, contacto)

    if not contacto_actualizado:
        raise HTTPException(status_code=404, detail="Contacto de emergencia no encontrado")

    return next(
        item for item in get_contactos_emergencia_detalle(db)
        if item["id_contacto"] == contacto_id
    )


@router.delete("/{contacto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_contacto_emergencia(
    contacto_id: int,
    db: Session = Depends(get_db)
):
    if not get_contacto_emergencia(db, contacto_id):
        raise HTTPException(status_code=404, detail="Contacto de emergencia no encontrado")

    delete_contacto_emergencia(db, contacto_id)
