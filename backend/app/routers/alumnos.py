from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session, joinedload

from app.schemas.alumno import (
    AlumnoCreate,
    AlumnoDetalleResponse,
    AlumnoResponse,
    AlumnoUpdate
)

from app.crud.crud_alumno import (
    get_alumnos,
    get_alumno,
    create_alumno,
    get_siguiente_matricula,
    update_alumno,
    delete_alumno
)

from app.database import get_db
from app.models.alumno import Alumno

router = APIRouter(
    prefix="/alumnos",
    tags=["Alumnos"]
)


def _nombre_usuario(usuario):
    if not usuario:
        return None

    partes = [
        usuario.nombre,
        usuario.apellido_paterno,
        usuario.apellido_materno
    ]

    return " ".join(parte for parte in partes if parte)


def _alumno_detalle(alumno):
    return {
        "id_alumno": alumno.id_alumno,
        "matricula": alumno.matricula,
        "numero_control": alumno.numero_control,
        "nombre": _nombre_usuario(alumno.usuario),
        "estatus": alumno.estatus,
        "id_carrera": alumno.id_carrera,
        "id_plan": alumno.id_plan,
        "carrera": {
            "id_carrera": alumno.carrera.id_carrera,
            "clave": alumno.carrera.clave,
            "rvoe": alumno.carrera.rvoe,
            "nombre": alumno.carrera.nombre
        } if alumno.carrera else None,
        "plan": {
            "id_plan": alumno.plan.id_plan,
            "nombre_plan": alumno.plan.nombre_plan
        } if alumno.plan else None
    }




@router.get(
    "/",
    response_model=list[AlumnoResponse]
)
def listar_alumnos(
    db: Session = Depends(get_db)
):
    return get_alumnos(db)


@router.get(
    "/detalle",
    response_model=list[AlumnoDetalleResponse]
)
def listar_alumnos_detalle(
    db: Session = Depends(get_db)
):
    alumnos = (
        db.query(Alumno)
        .options(
            joinedload(Alumno.usuario),
            joinedload(Alumno.carrera),
            joinedload(Alumno.plan)
        )
        .order_by(Alumno.id_alumno.desc())
        .all()
    )

    return [_alumno_detalle(alumno) for alumno in alumnos]


@router.get("/siguiente-matricula")
def obtener_siguiente_matricula(
    db: Session = Depends(get_db)
):
    try:
        return {
            "matricula": get_siguiente_matricula(db)
        }
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error


@router.get(
    "/{alumno_id}",
    response_model=AlumnoResponse
)
def obtener_alumno(
    alumno_id: int,
    db: Session = Depends(get_db)
):

    alumno = get_alumno(
        db,
        alumno_id
    )

    if not alumno:
        raise HTTPException(
            status_code=404,
            detail="Alumno no encontrado"
        )

    return alumno


@router.post(
    "/",
    response_model=AlumnoResponse
)
def crear_alumno(
    alumno: AlumnoCreate,
    db: Session = Depends(get_db)
):
    try:
        return create_alumno(
            db,
            alumno
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error


@router.patch(
    "/{alumno_id}",
    response_model=AlumnoResponse
)
def actualizar_alumno(
    alumno_id: int,
    alumno: AlumnoUpdate,
    db: Session = Depends(get_db)
):

    alumno_actualizado = update_alumno(
        db,
        alumno_id,
        alumno
    )

    if not alumno_actualizado:
        raise HTTPException(
            status_code=404,
            detail="Alumno no encontrado"
        )

    return alumno_actualizado


@router.delete(
    "/{alumno_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_alumno(
    alumno_id: int,
    db: Session = Depends(get_db)
):

    eliminado = delete_alumno(
        db,
        alumno_id
    )

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="Alumno no encontrado"
        )
