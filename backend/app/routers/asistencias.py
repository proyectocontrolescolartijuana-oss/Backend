from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.security import get_current_user
from app.crud.crud_asistencia import (
    create_asistencia,
    delete_asistencia,
    update_asistencia
)
from app.crud.crud_detalles import (
    get_asistencia_detalle,
    get_asistencias_detalle,
    get_grupo_materia_detalle
)
from app.database import get_db
from app.models.alumno import Alumno
from app.models.asistencia import Asistencia
from app.models.carga_academica import CargaAcademica
from app.models.docente import Docente
from app.models.grupo_materia import GrupoMateria
from app.models.parcial import Parcial
from app.models.periodo import Periodo
from app.models.usuario import Usuario
from app.schemas.asistencia import (
    AsistenciaCreate,
    AsistenciaUpdate,
    CapturaAsistenciasBatch,
    CapturaAsistenciasResponse
)
from app.schemas.detalles import (
    AsistenciaDetalleResponse,
    GrupoMateriaDetalleResponse
)


router = APIRouter(
    prefix="/asistencias",
    tags=["Asistencias"]
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
    if not alumno:
        return None

    return {
        "id_alumno": alumno.id_alumno,
        "matricula": alumno.matricula,
        "numero_control": alumno.numero_control,
        "nombre": _nombre_usuario(alumno.usuario)
    }


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


def _validar_grupo_docente_activo(
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


def _get_grupos_docente_activos(db: Session, docente_id: int):
    grupos_ids = [
        grupo_id
        for (grupo_id,) in (
            db.query(GrupoMateria.id_grupo_materia)
            .join(GrupoMateria.periodo)
            .filter(
                GrupoMateria.id_docente == docente_id,
                Periodo.estado == "ACTIVO"
            )
            .order_by(GrupoMateria.id_grupo_materia)
            .all()
        )
    ]

    return [
        get_grupo_materia_detalle(db, grupo_id)
        for grupo_id in grupos_ids
    ]


def _validar_fecha_no_futura(fecha_captura: Optional[date]):
    if fecha_captura and fecha_captura > date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede capturar asistencia de dias futuros"
        )


def _get_parciales(db: Session):
    parciales = db.query(Parcial).order_by(Parcial.id_parcial).all()

    return [
        {
            "id_parcial": parcial.id_parcial,
            "nombre": parcial.nombre,
            "porcentaje": (
                float(parcial.porcentaje)
                if parcial.porcentaje is not None else None
            ),
            "fecha_inicio": None,
            "fecha_fin": None,
            "fechas": []
        }
        for parcial in parciales
    ]


def _validar_parcial(db: Session, parcial_id: Optional[int]):
    parciales = _get_parciales(db)

    if not parciales:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay parciales registrados"
        )

    parcial_id = parcial_id or parciales[0]["id_parcial"]

    if not any(parcial["id_parcial"] == parcial_id for parcial in parciales):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parcial no encontrado"
        )

    return parcial_id, parciales


def _get_parciales_con_fechas(
    parciales,
    asistencias,
    parcial_seleccionado_id: int,
    fecha_seleccionada: Optional[date] = None
):
    fechas_por_parcial = {
        parcial["id_parcial"]: set()
        for parcial in parciales
    }

    for asistencia in asistencias:
        if asistencia.id_parcial in fechas_por_parcial and asistencia.fecha:
            fechas_por_parcial[asistencia.id_parcial].add(asistencia.fecha)

    if fecha_seleccionada:
        fechas_por_parcial[parcial_seleccionado_id].add(fecha_seleccionada)

    return [
        {
            **parcial,
            "fechas": sorted(fechas_por_parcial[parcial["id_parcial"]])
        }
        for parcial in parciales
    ]


def _build_captura_response(
    db: Session,
    grupo_materia_id: int,
    parcial_id: Optional[int] = None,
    fecha_seleccionada: Optional[date] = None
):
    grupo_materia = get_grupo_materia_detalle(db, grupo_materia_id)
    parcial_seleccionado_id, parciales = _validar_parcial(db, parcial_id)
    cargas = (
        db.query(CargaAcademica)
        .options(
            joinedload(CargaAcademica.alumno)
            .joinedload(Alumno.usuario)
        )
        .filter(
            CargaAcademica.id_grupo_materia == grupo_materia_id,
            CargaAcademica.estatus == "CURSANDO"
        )
        .order_by(CargaAcademica.id_alumno)
        .all()
    )

    cargas_ids = [carga.id_carga for carga in cargas]
    asistencias = []

    if cargas_ids:
        asistencias = (
            db.query(Asistencia)
            .filter(Asistencia.id_carga.in_(cargas_ids))
            .order_by(Asistencia.fecha, Asistencia.id_asistencia)
            .all()
        )

    parciales_asistencia = _get_parciales_con_fechas(
        parciales,
        asistencias,
        parcial_seleccionado_id,
        fecha_seleccionada
    )
    parcial_seleccionado = next(
        parcial
        for parcial in parciales_asistencia
        if parcial["id_parcial"] == parcial_seleccionado_id
    )
    fechas = sorted(
        {
            asistencia.fecha
            for asistencia in asistencias
            if asistencia.fecha is not None
            and asistencia.id_parcial == parcial_seleccionado_id
        }
    )

    fechas = parcial_seleccionado["fechas"]

    asistencias_por_celda = {
        (asistencia.id_carga, asistencia.fecha): asistencia
        for asistencia in asistencias
        if asistencia.id_parcial == parcial_seleccionado_id
    }

    def _asistencia_celda(carga, fecha_clase):
        asistencia = asistencias_por_celda.get(
            (carga.id_carga, fecha_clase)
        )

        return {
            "id_asistencia": (
                asistencia.id_asistencia
                if asistencia else None
            ),
            "id_carga": carga.id_carga,
            "fecha": fecha_clase,
            "id_parcial": parcial_seleccionado_id,
            "asistencia": bool(asistencia.asistencia) if asistencia else False
        }

    total_clases = len(fechas)
    alumnos = []

    for carga in cargas:
        celdas = [
            _asistencia_celda(carga, fecha_clase)
            for fecha_clase in fechas
        ]
        total_asistencias = sum(
            1 for asistencia in celdas
            if asistencia["asistencia"]
        )
        porcentaje = (
            round((total_asistencias / total_clases) * 100, 2)
            if total_clases else None
        )

        alumnos.append({
            "id_carga": carga.id_carga,
            "estatus": carga.estatus,
            "alumno": _alumno_detalle(carga.alumno),
            "asistencias": celdas,
            "total_asistencias": total_asistencias,
            "total_clases": total_clases,
            "porcentaje_asistencia": porcentaje
        })

    alumnos_en_riesgo = sum(
        1
        for alumno in alumnos
        if alumno["porcentaje_asistencia"] is not None
        and alumno["porcentaje_asistencia"] < 80
    )

    return {
        "grupo_materia": grupo_materia,
        "parcial_seleccionado_id": parcial_seleccionado_id,
        "fecha_seleccionada": fecha_seleccionada,
        "fechas": fechas,
        "parciales": parciales_asistencia,
        "resumen": {
            "total_alumnos": len(alumnos),
            "total_clases": total_clases,
            "alumnos_en_riesgo": alumnos_en_riesgo
        },
        "alumnos": alumnos
    }


@router.get(
    "/",
    response_model=list[AsistenciaDetalleResponse]
)
def listar_asistencias(
    alumno_id: Optional[int] = None,
    grupo_id: Optional[int] = None,
    materia_id: Optional[int] = None,
    periodo_id: Optional[int] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    db: Session = Depends(get_db)
):
    return get_asistencias_detalle(
        db,
        alumno_id=alumno_id,
        grupo_id=grupo_id,
        materia_id=materia_id,
        periodo_id=periodo_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )


@router.get(
    "/captura/grupos",
    response_model=list[GrupoMateriaDetalleResponse]
)
def listar_grupos_captura_asistencia(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    docente = _get_docente_actual(db, usuario)

    return _get_grupos_docente_activos(db, docente.id_docente)


@router.get(
    "/captura/grupos/{grupo_materia_id}",
    response_model=CapturaAsistenciasResponse
)
def obtener_captura_asistencia_grupo(
    grupo_materia_id: int,
    parcial_id: Optional[int] = None,
    fecha: Optional[date] = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    _validar_fecha_no_futura(fecha)

    docente = _get_docente_actual(db, usuario)
    _validar_grupo_docente_activo(
        db,
        grupo_materia_id,
        docente.id_docente
    )

    return _build_captura_response(
        db,
        grupo_materia_id,
        parcial_id,
        fecha
    )


@router.post(
    "/captura",
    response_model=CapturaAsistenciasResponse
)
def guardar_captura_asistencia(
    captura: CapturaAsistenciasBatch,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    _validar_fecha_no_futura(captura.fecha)
    parcial_seleccionado_id, _ = _validar_parcial(db, captura.id_parcial)

    docente = _get_docente_actual(db, usuario)
    _validar_grupo_docente_activo(
        db,
        captura.grupo_materia_id,
        docente.id_docente
    )

    cargas_validas = {
        id_carga
        for (id_carga,) in (
            db.query(CargaAcademica.id_carga)
            .filter(
                CargaAcademica.id_grupo_materia == captura.grupo_materia_id,
                CargaAcademica.estatus == "CURSANDO"
            )
            .all()
        )
    }

    for item in captura.asistencias:
        fecha_asistencia = item.fecha or captura.fecha

        if not fecha_asistencia:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de asistencia es requerida"
            )

        _validar_fecha_no_futura(fecha_asistencia)

        if item.id_carga not in cargas_validas:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="La carga academica no pertenece al grupo activo asignado"
            )

        asistencias_existentes = (
            db.query(Asistencia)
            .filter(
                Asistencia.id_carga == item.id_carga,
                Asistencia.fecha == fecha_asistencia
            )
            .all()
        )

        if asistencias_existentes:
            for asistencia in asistencias_existentes:
                asistencia.asistencia = item.asistencia
                asistencia.id_parcial = parcial_seleccionado_id
            continue

        db.add(
            Asistencia(
                id_carga=item.id_carga,
                id_parcial=parcial_seleccionado_id,
                fecha=fecha_asistencia,
                asistencia=item.asistencia
            )
        )

    db.commit()

    return _build_captura_response(
        db,
        captura.grupo_materia_id,
        parcial_seleccionado_id,
        captura.fecha
    )


@router.get(
    "/{asistencia_id}",
    response_model=AsistenciaDetalleResponse
)
def obtener_asistencia(
    asistencia_id: int,
    db: Session = Depends(get_db)
):
    asistencia = get_asistencia_detalle(db, asistencia_id)

    if not asistencia:
        raise HTTPException(
            status_code=404,
            detail="Asistencia no encontrada"
        )

    return asistencia


@router.post(
    "/",
    response_model=AsistenciaDetalleResponse
)
def crear_asistencia(
    asistencia: AsistenciaCreate,
    db: Session = Depends(get_db)
):
    nueva_asistencia = create_asistencia(db, asistencia)

    return get_asistencia_detalle(db, nueva_asistencia.id_asistencia)


@router.patch(
    "/{asistencia_id}",
    response_model=AsistenciaDetalleResponse
)
def actualizar_asistencia(
    asistencia_id: int,
    asistencia: AsistenciaUpdate,
    db: Session = Depends(get_db)
):
    asistencia_actualizada = update_asistencia(db, asistencia_id, asistencia)

    if not asistencia_actualizada:
        raise HTTPException(
            status_code=404,
            detail="Asistencia no encontrada"
        )

    return get_asistencia_detalle(db, asistencia_id)


@router.delete(
    "/{asistencia_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_asistencia(
    asistencia_id: int,
    db: Session = Depends(get_db)
):
    eliminada = delete_asistencia(db, asistencia_id)

    if not eliminada:
        raise HTTPException(
            status_code=404,
            detail="Asistencia no encontrada"
        )
