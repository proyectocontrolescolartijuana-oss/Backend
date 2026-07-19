from datetime import date
import unicodedata
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.crud.crud_carga_academica import (
    create_carga_academica,
    delete_carga_academica,
    get_carga_academica,
    update_carga_academica
)
from app.crud.crud_detalles import (
    get_carga_academica_detalle,
    get_cargas_academicas_detalle
)
from app.database import get_db
from app.models.alumno import Alumno
from app.models.carga_academica import CargaAcademica
from app.models.grupo_materia import GrupoMateria
from app.models.historial_academico import HistorialAcademico
from app.models.materia import Materia
from app.models.materia_prerrequisito import MateriaPrerrequisito
from app.schemas.carga_academica import CargaAcademicaCreate, CargaAcademicaUpdate
from app.schemas.detalles import CargaAcademicaDetalleResponse


router = APIRouter(
    prefix="/cargas-academicas",
    tags=["Cargas academicas"]
)


ROMANOS_PREVIOS = {
    "II": "I",
    "III": "II",
    "IV": "III",
    "V": "IV",
    "VI": "V",
    "VII": "VI",
    "VIII": "VII",
    "IX": "VIII",
    "X": "IX"
}


def _normalizar_texto(texto):
    texto = unicodedata.normalize("NFD", texto or "")
    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    return " ".join(texto.upper().split())


def _materia_anterior_por_nombre(db: Session, materia: Materia):
    partes = _normalizar_texto(materia.nombre).split()

    if not partes:
        return None

    ultimo_token = partes[-1]
    token_previo = ROMANOS_PREVIOS.get(ultimo_token)

    if not token_previo:
        return None

    nombre_requerido = " ".join([*partes[:-1], token_previo])

    for candidata in db.query(Materia).all():
        if _normalizar_texto(candidata.nombre) == nombre_requerido:
            return candidata

    return None


def _materias_requeridas(db: Session, materia: Materia):
    prerrequisitos = (
        db.query(MateriaPrerrequisito)
        .options(joinedload(MateriaPrerrequisito.materia_requerida))
        .filter(
            MateriaPrerrequisito.id_materia == materia.id_materia,
            MateriaPrerrequisito.tipo == "OBLIGATORIO"
        )
        .all()
    )

    requeridas = [
        prerrequisito.materia_requerida
        for prerrequisito in prerrequisitos
        if prerrequisito.materia_requerida
    ]
    ids_requeridas = {
        requerida.id_materia
        for requerida in requeridas
    }
    materia_anterior = _materia_anterior_por_nombre(db, materia)

    if (
        materia_anterior
        and materia_anterior.id_materia not in ids_requeridas
    ):
        requeridas.append(materia_anterior)

    return requeridas


def _materia_aprobada(db: Session, alumno_id: int, materia_id: int):
    historial_aprobado = (
        db.query(HistorialAcademico.id_historial)
        .filter(
            HistorialAcademico.id_alumno == alumno_id,
            HistorialAcademico.id_materia == materia_id,
            HistorialAcademico.resultado == "APROBADO"
        )
        .first()
    )

    if historial_aprobado:
        return True

    carga_aprobada = (
        db.query(CargaAcademica.id_carga)
        .join(CargaAcademica.grupo_materia)
        .filter(
            CargaAcademica.id_alumno == alumno_id,
            GrupoMateria.id_materia == materia_id,
            CargaAcademica.estatus == "APROBADA"
        )
        .first()
    )

    return bool(carga_aprobada)


def _ultimo_resultado_materia(db: Session, alumno_id: int, materia_id: int):
    return (
        db.query(HistorialAcademico)
        .filter(
            HistorialAcademico.id_alumno == alumno_id,
            HistorialAcademico.id_materia == materia_id
        )
        .order_by(
            HistorialAcademico.fecha_cierre.desc(),
            HistorialAcademico.id_historial.desc()
        )
        .first()
    )


def _validar_prerrequisitos(
    db: Session,
    alumno_id: int,
    grupo_materia: GrupoMateria
):
    materia = grupo_materia.materia

    if not materia:
        return

    for requerida in _materias_requeridas(db, materia):
        if _materia_aprobada(db, alumno_id, requerida.id_materia):
            continue

        ultimo_resultado = _ultimo_resultado_materia(
            db,
            alumno_id,
            requerida.id_materia
        )
        motivo = (
            f"reprobo {requerida.nombre}"
            if ultimo_resultado
            and ultimo_resultado.resultado == "REPROBADO"
            else f"debe acreditar primero {requerida.nombre}"
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"No puede inscribirse a {materia.nombre} porque {motivo}."
            )
        )


def _validar_cupo(
    db: Session,
    grupo_materia: GrupoMateria,
    carga_id_actual: Optional[int] = None
):
    if not grupo_materia.cupo_maximo:
        return

    query = db.query(CargaAcademica).filter(
        CargaAcademica.id_grupo_materia == grupo_materia.id_grupo_materia,
        CargaAcademica.estatus != "BAJA"
    )

    if carga_id_actual is not None:
        query = query.filter(CargaAcademica.id_carga != carga_id_actual)

    inscritos = query.count()

    if inscritos >= grupo_materia.cupo_maximo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El grupo-materia ya alcanzo su cupo maximo"
        )


def _validar_carga_academica(
    db: Session,
    *,
    alumno_id: int,
    grupo_materia_id: int,
    carga_id_actual: Optional[int] = None
):
    alumno = (
        db.query(Alumno)
        .filter(Alumno.id_alumno == alumno_id)
        .first()
    )

    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alumno no encontrado"
        )

    grupo_materia = (
        db.query(GrupoMateria)
        .options(joinedload(GrupoMateria.materia))
        .filter(GrupoMateria.id_grupo_materia == grupo_materia_id)
        .first()
    )

    if not grupo_materia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo materia no encontrado"
        )

    duplicada = db.query(CargaAcademica).filter(
        CargaAcademica.id_alumno == alumno_id,
        CargaAcademica.id_grupo_materia == grupo_materia_id,
        CargaAcademica.estatus != "BAJA"
    )

    if carga_id_actual is not None:
        duplicada = duplicada.filter(CargaAcademica.id_carga != carga_id_actual)

    if duplicada.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El alumno ya esta inscrito en este grupo-materia"
        )

    misma_materia = (
        db.query(CargaAcademica)
        .join(CargaAcademica.grupo_materia)
        .filter(
            CargaAcademica.id_alumno == alumno_id,
            GrupoMateria.id_materia == grupo_materia.id_materia,
            GrupoMateria.id_periodo == grupo_materia.id_periodo,
            CargaAcademica.estatus != "BAJA"
        )
    )

    if carga_id_actual is not None:
        misma_materia = misma_materia.filter(
            CargaAcademica.id_carga != carga_id_actual
        )

    if misma_materia.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "El alumno ya cursa esta materia en el mismo periodo"
            )
        )

    _validar_cupo(db, grupo_materia, carga_id_actual)
    _validar_prerrequisitos(db, alumno_id, grupo_materia)


@router.get(
    "/",
    response_model=list[CargaAcademicaDetalleResponse]
)
def listar_cargas_academicas(
    alumno_id: Optional[int] = None,
    grupo_materia_id: Optional[int] = None,
    grupo_id: Optional[int] = None,
    docente_id: Optional[int] = None,
    materia_id: Optional[int] = None,
    periodo_id: Optional[int] = None,
    estatus: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return get_cargas_academicas_detalle(
        db,
        alumno_id=alumno_id,
        grupo_materia_id=grupo_materia_id,
        grupo_id=grupo_id,
        docente_id=docente_id,
        materia_id=materia_id,
        periodo_id=periodo_id,
        estatus=estatus
    )


@router.get(
    "/{carga_id}",
    response_model=CargaAcademicaDetalleResponse
)
def obtener_carga_academica(
    carga_id: int,
    db: Session = Depends(get_db)
):
    carga = get_carga_academica_detalle(db, carga_id)

    if not carga:
        raise HTTPException(
            status_code=404,
            detail="Carga academica no encontrada"
        )

    return carga


@router.post(
    "/",
    response_model=CargaAcademicaDetalleResponse
)
def crear_carga_academica(
    carga: CargaAcademicaCreate,
    db: Session = Depends(get_db)
):
    _validar_carga_academica(
        db,
        alumno_id=carga.id_alumno,
        grupo_materia_id=carga.id_grupo_materia
    )

    carga_data = carga.model_copy(
        update={
            "intento": carga.intento or 1,
            "fecha_inscripcion": carga.fecha_inscripcion or date.today()
        }
    )
    nueva_carga = create_carga_academica(db, carga_data)

    return get_carga_academica_detalle(db, nueva_carga.id_carga)


@router.patch(
    "/{carga_id}",
    response_model=CargaAcademicaDetalleResponse
)
def actualizar_carga_academica(
    carga_id: int,
    carga: CargaAcademicaUpdate,
    db: Session = Depends(get_db)
):
    carga_actual = get_carga_academica(db, carga_id)

    if not carga_actual:
        raise HTTPException(
            status_code=404,
            detail="Carga academica no encontrada"
        )

    update_data = carga.model_dump(exclude_unset=True)

    if "id_alumno" in update_data or "id_grupo_materia" in update_data:
        _validar_carga_academica(
            db,
            alumno_id=update_data.get("id_alumno", carga_actual.id_alumno),
            grupo_materia_id=update_data.get(
                "id_grupo_materia",
                carga_actual.id_grupo_materia
            ),
            carga_id_actual=carga_id
        )

    carga_actualizada = update_carga_academica(db, carga_id, carga)

    if not carga_actualizada:
        raise HTTPException(
            status_code=404,
            detail="Carga academica no encontrada"
        )

    return get_carga_academica_detalle(db, carga_id)


@router.delete(
    "/{carga_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_carga_academica(
    carga_id: int,
    db: Session = Depends(get_db)
):
    eliminada = delete_carga_academica(db, carga_id)

    if not eliminada:
        raise HTTPException(
            status_code=404,
            detail="Carga academica no encontrada"
        )
