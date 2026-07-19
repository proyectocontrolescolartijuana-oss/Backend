from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.crud.crud_kardex import (
    buscar_alumnos_kardex,
    get_kardex_by_matricula,
    get_kardex_by_query,
)
from app.database import get_db
from app.models.alumno import Alumno
from app.models.usuario import Usuario
from app.schemas.kardex import KardexAlumnoBusqueda, KardexResponse

router = APIRouter(prefix="/kardex", tags=["Kardex"])


def _get_alumno_actual(db: Session, usuario: Usuario):
    alumno = (
        db.query(Alumno)
        .filter(
            Alumno.id_usuario == usuario.id_usuario,
            Alumno.estatus != "BAJA"
        )
        .first()
    )

    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario actual no tiene un perfil de alumno activo"
        )

    return alumno


@router.get("/buscar", response_model=list[KardexAlumnoBusqueda])
def buscar_alumnos(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
):
    return buscar_alumnos_kardex(db, query=q)


@router.get("/me", response_model=KardexResponse)
def obtener_mi_kardex(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    alumno = _get_alumno_actual(db, usuario)
    kardex = get_kardex_by_matricula(db, alumno.matricula)

    if not kardex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alumno no encontrado"
        )

    return kardex


@router.get("", response_model=KardexResponse)
def obtener_kardex(
    matricula: str | None = Query(None, min_length=1),
    q: str | None = Query(None, min_length=1),
    db: Session = Depends(get_db),
):
    termino = matricula or q or ""
    kardex = get_kardex_by_query(db, query=termino)

    if not kardex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alumno no encontrado"
        )

    return kardex
