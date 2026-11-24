from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.crud.crud_desglose import (
    get_desglose,
    guardar_desglose,
    validar_parcial_con_desglose,
    validar_parcial_del_grupo
)
from app.database import get_db
from app.models.docente import Docente
from app.models.grupo_materia import GrupoMateria
from app.models.periodo import Periodo
from app.models.usuario import Usuario
from app.schemas.desglose import DesgloseGuardar, DesgloseResponse


router = APIRouter(
    prefix="/calificaciones/desglose",
    tags=["Desglose de calificaciones"]
)


def _get_docente_actual(db: Session, usuario: Usuario):
    docente = (
        db.query(Docente)
        .filter(
            Docente.id_usuario == usuario.id_usuario,
            Docente.estado.is_(True)
        )
        .first()
    )

    if not docente:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario actual no tiene un perfil docente activo"
        )

    return docente


def _validar_grupo_docente(
    db: Session,
    grupo_materia_id: int,
    docente_id: int
):
    grupo_materia = (
        db.query(GrupoMateria)
        .join(GrupoMateria.periodo)
        .filter(
            GrupoMateria.id_grupo_materia == grupo_materia_id,
            GrupoMateria.id_docente == docente_id,
            Periodo.estado == "ACTIVO"
        )
        .first()
    )

    if not grupo_materia:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El grupo no esta activo o no esta asignado al docente actual"
        )

    return grupo_materia


@router.get(
    "/grupos/{grupo_materia_id}/parciales/{parcial_id}",
    response_model=DesgloseResponse
)
def obtener_desglose(
    grupo_materia_id: int,
    parcial_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    docente = _get_docente_actual(db, usuario)
    _validar_grupo_docente(db, grupo_materia_id, docente.id_docente)
    validar_parcial_del_grupo(db, grupo_materia_id, parcial_id)

    return get_desglose(db, grupo_materia_id, parcial_id)


@router.put(
    "/grupos/{grupo_materia_id}/parciales/{parcial_id}",
    response_model=DesgloseResponse
)
def guardar_desglose_parcial(
    grupo_materia_id: int,
    parcial_id: int,
    datos: DesgloseGuardar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    docente = _get_docente_actual(db, usuario)
    _validar_grupo_docente(db, grupo_materia_id, docente.id_docente)
    validar_parcial_con_desglose(db, grupo_materia_id, parcial_id)

    return guardar_desglose(
        db,
        grupo_materia_id,
        parcial_id,
        datos,
        usuario
    )