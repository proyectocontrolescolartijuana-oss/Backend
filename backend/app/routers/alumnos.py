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
from app.models.inscripcion import Inscripcion
from app.models.usuario import Usuario

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


def _grupo_detalle(grupo):
    if not grupo:
        return None

    return {
        "id_grupo": grupo.id_grupo,
        "nombre": grupo.nombre,
        "turno": grupo.turno,
        "id_carrera": grupo.id_carrera
    }


def _grupo_actual(db, alumno_id):
    inscripcion = (
        db.query(Inscripcion)
        .filter(Inscripcion.id_alumno == alumno_id)
        .order_by(
            Inscripcion.fecha_inscripcion.desc(),
            Inscripcion.id_inscripcion.desc()
        )
        .first()
    )

    return inscripcion.grupo if inscripcion else None


def _alumno_detalle(alumno, db=None):
    return {
        "id_alumno": alumno.id_alumno,
        "matricula": alumno.matricula,
        "numero_control": alumno.numero_control,
        "id_usuario": alumno.id_usuario,
        "nombre": _nombre_usuario(alumno.usuario),
        "nombres": alumno.usuario.nombre if alumno.usuario else None,
        "apellido_paterno": (
            alumno.usuario.apellido_paterno if alumno.usuario else None
        ),
        "apellido_materno": (
            alumno.usuario.apellido_materno if alumno.usuario else None
        ),
        "estatus": alumno.estatus,
        "id_carrera": alumno.id_carrera,
        "id_plan": alumno.id_plan,
        "fecha_nacimiento": alumno.fecha_nacimiento,
        "ciudad_nacimiento": alumno.ciudad_nacimiento,
        "municipio_nacimiento": alumno.municipio_nacimiento,
        "nacionalidad": alumno.nacionalidad,
        "sexo": alumno.sexo,
        "curp": alumno.curp,
        "direccion": alumno.direccion,
        "ciudad": alumno.ciudad,
        "estado": alumno.estado,
        "correo_contacto": alumno.correo_contacto,
        "fecha_ingreso": alumno.fecha_ingreso,
        "foto": alumno.foto,
        "carrera": {
            "id_carrera": alumno.carrera.id_carrera,
            "clave": alumno.carrera.clave,
            "rvoe": alumno.carrera.rvoe,
            "nombre": alumno.carrera.nombre
        } if alumno.carrera else None,
        "plan": {
            "id_plan": alumno.plan.id_plan,
            "nombre_plan": alumno.plan.nombre_plan
        } if alumno.plan else None,
        "grupo": _grupo_detalle(_grupo_actual(db, alumno.id_alumno)) if db else None
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
        .join(Alumno.usuario)
        .options(
            joinedload(Alumno.usuario),
            joinedload(Alumno.carrera),
            joinedload(Alumno.plan)
        )
        .order_by(
            Usuario.apellido_paterno,
            Usuario.apellido_materno,
            Usuario.nombre
        )
        .all()
    )

    return [_alumno_detalle(alumno, db) for alumno in alumnos]


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
    "/{alumno_id}/detalle",
    response_model=AlumnoDetalleResponse
)
def obtener_alumno_detalle(
    alumno_id: int,
    db: Session = Depends(get_db)
):
    alumno = (
        db.query(Alumno)
        .options(
            joinedload(Alumno.usuario),
            joinedload(Alumno.carrera),
            joinedload(Alumno.plan)
        )
        .filter(Alumno.id_alumno == alumno_id)
        .first()
    )

    if not alumno:
        raise HTTPException(
            status_code=404,
            detail="Alumno no encontrado"
        )

    return _alumno_detalle(alumno)


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
