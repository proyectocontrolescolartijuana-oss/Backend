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
from app.schemas.servicio_social import (
    ServicioSocialCreate,
    ServicioSocialEstatusUpdate,
    ServicioSocialUpdate
)
from app.models.servicio_social import ServicioSocial
from app.models.empresa import Empresa


router = APIRouter(
    prefix="/servicios-sociales",
    tags=["Servicios sociales"]
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

@router.patch(
    "/alumno/{alumno_id}/estatus",
    response_model=ServicioSocialDetalleResponse
)
def guardar_estatus_servicio(
    alumno_id: int,
    datos: ServicioSocialEstatusUpdate,
    db: Session = Depends(get_db)
):
    servicio = (
        db.query(ServicioSocial)
        .filter(ServicioSocial.id_alumno == alumno_id)
        .first()
    )

    if servicio is None:
        servicio = ServicioSocial(id_alumno=alumno_id)
        db.add(servicio)

    servicio.carta_unifront = datos.carta_unifront
    servicio.carta_procedencia = datos.carta_procedencia
    servicio.horas_completadas = datos.horas_completadas
    if datos.id_empresa is not None or datos.empresa_nombre is not None:
        servicio.id_empresa = resolver_empresa_id(
            db,
            datos.id_empresa,
            datos.empresa_nombre
        )
    db.commit()
    db.refresh(servicio)

    return next(
        item for item in get_servicios_sociales_detalle(db)
        if item["id_servicio"] == servicio.id_servicio
    )


@router.patch(
    "/alumno/{alumno_id}/estatus",
    response_model=ServicioSocialDetalleResponse
)
def guardar_estatus_servicio(
    alumno_id: int,
    datos: ServicioSocialEstatusUpdate,
    db: Session = Depends(get_db)
):
    servicio = (
        db.query(ServicioSocial)
        .filter(ServicioSocial.id_alumno == alumno_id)
        .first()
    )

    if servicio is None:
        servicio = ServicioSocial(id_alumno=alumno_id)
        db.add(servicio)

    servicio.carta_unifront = datos.carta_unifront
    servicio.carta_procedencia = datos.carta_procedencia
    db.commit()
    db.refresh(servicio)

    return next(
        item for item in get_servicios_sociales_detalle(db)
        if item["id_servicio"] == servicio.id_servicio
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
