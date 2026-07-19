from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.crud_detalles import get_servicios_sociales_detalle
from app.crud.crud_servicio_social import (
    create_servicio_social,
    delete_servicio_social,
    get_servicio_social,
    update_servicio_social
)
from app.database import get_db
from app.schemas.detalles import ServicioSocialDetalleResponse
from app.schemas.servicio_social import ServicioSocialCreate, ServicioSocialUpdate


router = APIRouter(
    prefix="/servicios-sociales",
    tags=["Servicios sociales"]
)


@router.get("/", response_model=list[ServicioSocialDetalleResponse])
def listar_servicios_sociales(
    alumno_id: Optional[int] = None,
    empresa_id: Optional[int] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return get_servicios_sociales_detalle(
        db,
        alumno_id=alumno_id,
        empresa_id=empresa_id,
        estado=estado
    )


@router.get("/{servicio_id}", response_model=ServicioSocialDetalleResponse)
def obtener_servicio_social(
    servicio_id: int,
    db: Session = Depends(get_db)
):
    servicio = next(
        (
            item for item in get_servicios_sociales_detalle(db)
            if item["id_servicio"] == servicio_id
        ),
        None
    )

    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio social no encontrado")

    return servicio


@router.post("/", response_model=ServicioSocialDetalleResponse)
def crear_servicio_social(
    servicio: ServicioSocialCreate,
    db: Session = Depends(get_db)
):
    nuevo_servicio = create_servicio_social(db, servicio)

    return next(
        item for item in get_servicios_sociales_detalle(db)
        if item["id_servicio"] == nuevo_servicio.id_servicio
    )


@router.patch("/{servicio_id}", response_model=ServicioSocialDetalleResponse)
def actualizar_servicio_social(
    servicio_id: int,
    servicio: ServicioSocialUpdate,
    db: Session = Depends(get_db)
):
    servicio_actualizado = update_servicio_social(db, servicio_id, servicio)

    if not servicio_actualizado:
        raise HTTPException(status_code=404, detail="Servicio social no encontrado")

    return next(
        item for item in get_servicios_sociales_detalle(db)
        if item["id_servicio"] == servicio_id
    )


@router.delete("/{servicio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_servicio_social(
    servicio_id: int,
    db: Session = Depends(get_db)
):
    if not get_servicio_social(db, servicio_id):
        raise HTTPException(status_code=404, detail="Servicio social no encontrado")

    delete_servicio_social(db, servicio_id)
