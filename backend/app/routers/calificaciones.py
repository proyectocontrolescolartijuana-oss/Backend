from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.security import get_current_user
from app.crud.crud_calificacion import (
    create_calificacion,
    delete_calificacion,
    get_calificacion,
    update_calificacion
)
from app.crud.crud_detalles import (
    get_calificaciones_detalle,
    get_grupo_materia_detalle,
    get_grupos_materias_detalle
)
from app.database import get_db
from app.models.alumno import Alumno
from app.models.calificacion import Calificacion
from app.models.carga_academica import CargaAcademica
from app.models.cuatrimestre import Cuatrimestre
from app.models.docente import Docente
from app.models.grupo import Grupo
from app.models.grupo_materia import GrupoMateria
from app.models.parcial import Parcial
from app.models.usuario import Usuario
from app.schemas.calificacion import (
    BoletaFinalResponse,
    CalificacionCreate,
    CalificacionUpdate,
    CapturaCalificacionesBatch,
    CapturaCalificacionesResponse,
    CuadroHonorResponse
)
from app.schemas.detalles import (
    CalificacionDetalleResponse,
    GrupoMateriaDetalleResponse
)


router = APIRouter(
    prefix="/calificaciones",
    tags=["Calificaciones"]
)


def _nombre_usuario(usuario):
    if not usuario:
        return None

    partes = [
        usuario.apellido_paterno,
        usuario.apellido_materno,
        usuario.nombre
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


def _parcial_detalle(parcial):
    return {
        "id_parcial": parcial.id_parcial,
        "nombre": parcial.nombre,
        "porcentaje": (
            float(parcial.porcentaje)
            if parcial.porcentaje is not None else None
        )
    }


def _calcular_calificacion_final(calificaciones, parciales_por_id):
    calificaciones_validas = [
        calificacion
        for calificacion in calificaciones
        if calificacion.calificacion is not None
    ]

    if not calificaciones_validas:
        return None

    total = 0
    peso_total = 0

    for calificacion in calificaciones_validas:
        parcial = parciales_por_id.get(calificacion.id_parcial)
        peso = (
            float(parcial.porcentaje)
            if parcial and parcial.porcentaje is not None
            else 0
        )

        total += float(calificacion.calificacion) * peso
        peso_total += peso

    if peso_total > 0:
        return round(total / peso_total, 2)

    promedio = sum(
        float(calificacion.calificacion)
        for calificacion in calificaciones_validas
    ) / len(calificaciones_validas)

    return round(promedio, 2)


def _generacion_alumno(alumno):
    if not alumno or not alumno.fecha_ingreso:
        return None

    anio_inicio = alumno.fecha_ingreso.year

    return f"{anio_inicio}-{anio_inicio + 3}"


def _build_cuadro_honor_response(
    cargas,
    calificaciones_por_carga,
    parciales_por_id,
    tipo,
    cuatrimestre=None
):
    alumnos = {}

    for carga in cargas:
        grupo_materia = carga.grupo_materia
        grupo = grupo_materia.grupo if grupo_materia else None
        cuatrimestre_model = grupo.cuatrimestre if grupo else None
        alumno = carga.alumno

        if not alumno:
            continue

        calificacion_final = _calcular_calificacion_final(
            calificaciones_por_carga.get(carga.id_carga, []),
            parciales_por_id
        )

        if calificacion_final is None:
            continue

        alumno_item = alumnos.setdefault(
            alumno.id_alumno,
            {
                "id_alumno": alumno.id_alumno,
                "matricula": alumno.matricula,
                "numero_control": alumno.numero_control,
                "nombre": _nombre_usuario(alumno.usuario),
                "carrera": alumno.carrera.nombre if alumno.carrera else None,
                "grupo": grupo.nombre if grupo else None,
                "cuatrimestre": (
                    cuatrimestre_model.numero
                    if cuatrimestre_model else None
                ),
                "generacion": _generacion_alumno(alumno),
                "calificaciones_finales": [],
                "cuatrimestres": set(),
                "estatus": alumno.estatus
            }
        )

        alumno_item["calificaciones_finales"].append(calificacion_final)

        if cuatrimestre_model and cuatrimestre_model.numero:
            alumno_item["cuatrimestres"].add(cuatrimestre_model.numero)

    alumnos_response = []

    for alumno in alumnos.values():
        calificaciones_finales = alumno.pop("calificaciones_finales")
        cuatrimestres = alumno.pop("cuatrimestres")
        promedio = round(
            sum(calificaciones_finales) / len(calificaciones_finales),
            2
        )

        if promedio < 90:
            continue

        alumnos_response.append({
            **alumno,
            "promedio": promedio,
            "materias": len(calificaciones_finales),
            "cuatrimestres_evaluados": (
                len(cuatrimestres)
                if tipo == "egresados" else None
            )
        })

    alumnos_response.sort(
        key=lambda alumno: alumno["promedio"],
        reverse=True
    )

    return {
        "tipo": tipo,
        "cuatrimestre": cuatrimestre,
        "alumnos": alumnos_response
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


def _get_alumno_actual(db: Session, usuario: Usuario):
    alumno = (
        db.query(Alumno)
        .options(
            joinedload(Alumno.usuario),
            joinedload(Alumno.carrera)
        )
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


def _validar_grupo_docente(
    db: Session,
    grupo_materia_id: int,
    docente_id: int
):
    grupo_materia = (
        db.query(GrupoMateria)
        .filter(
            GrupoMateria.id_grupo_materia == grupo_materia_id,
            GrupoMateria.id_docente == docente_id
        )
        .first()
    )

    if not grupo_materia:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El grupo no esta asignado al docente actual"
        )

    return grupo_materia


def _build_captura_response(db: Session, grupo_materia_id: int):
    grupo_materia = get_grupo_materia_detalle(db, grupo_materia_id)
    parciales = db.query(Parcial).order_by(Parcial.id_parcial).all()
    cargas = (
        db.query(CargaAcademica)
        .options(
            joinedload(CargaAcademica.alumno)
            .joinedload(Alumno.usuario)
        )
        .filter(CargaAcademica.id_grupo_materia == grupo_materia_id)
        .join(CargaAcademica.alumno)
        .join(Alumno.usuario)
        .order_by(
            Usuario.apellido_paterno,
            Usuario.apellido_materno,
            Usuario.nombre
        )
        .all()
    )

    cargas_ids = [carga.id_carga for carga in cargas]
    calificaciones = []

    if cargas_ids:
        calificaciones = (
            db.query(Calificacion)
            .filter(Calificacion.id_carga.in_(cargas_ids))
            .all()
        )

    calificaciones_por_celda = {
        (calificacion.id_carga, calificacion.id_parcial): calificacion
        for calificacion in calificaciones
    }

    def _calificacion_celda(carga, parcial):
        calificacion = calificaciones_por_celda.get(
            (carga.id_carga, parcial.id_parcial)
        )

        return {
            "id_calificacion": (
                calificacion.id_calificacion
                if calificacion else None
            ),
            "id_carga": carga.id_carga,
            "id_parcial": parcial.id_parcial,
            "calificacion": (
                float(calificacion.calificacion)
                if calificacion
                and calificacion.calificacion is not None
                else None
            )
        }

    return {
        "grupo_materia": grupo_materia,
        "parciales": [
            _parcial_detalle(parcial)
            for parcial in parciales
        ],
        "alumnos": [
            {
                "id_carga": carga.id_carga,
                "estatus": carga.estatus,
                "alumno": _alumno_detalle(carga.alumno),
                "calificaciones": [
                    _calificacion_celda(carga, parcial)
                    for parcial in parciales
                ]
            }
            for carga in cargas
        ]
    }


def _build_boleta_final(db: Session, alumno_id: int, periodo_id: int):
    alumno = (
        db.query(Alumno)
        .options(
            joinedload(Alumno.usuario),
            joinedload(Alumno.carrera)
        )
        .filter(Alumno.id_alumno == alumno_id)
        .first()
    )

    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alumno no encontrado"
        )

    cargas = (
        db.query(CargaAcademica)
        .join(CargaAcademica.grupo_materia)
        .options(
            joinedload(CargaAcademica.grupo_materia)
            .joinedload(GrupoMateria.materia),
            joinedload(CargaAcademica.grupo_materia)
            .joinedload(GrupoMateria.periodo),
            joinedload(CargaAcademica.grupo_materia)
            .joinedload(GrupoMateria.grupo)
            .joinedload(Grupo.cuatrimestre)
        )
        .filter(
            CargaAcademica.id_alumno == alumno_id,
            CargaAcademica.estatus != "BAJA",
            GrupoMateria.id_periodo == periodo_id
        )
        .all()
    )

    cargas_ids = [carga.id_carga for carga in cargas]
    parciales = db.query(Parcial).order_by(Parcial.id_parcial).all()
    parciales_por_id = {
        parcial.id_parcial: parcial
        for parcial in parciales
    }
    calificaciones = []

    if cargas_ids:
        calificaciones = (
            db.query(Calificacion)
            .filter(Calificacion.id_carga.in_(cargas_ids))
            .all()
        )

    calificaciones_por_carga = {}

    for calificacion in calificaciones:
        calificaciones_por_carga.setdefault(
            calificacion.id_carga,
            []
        ).append(calificacion)

    materias = []
    periodo = None
    cuatrimestre = None

    for carga in cargas:
        grupo_materia = carga.grupo_materia
        materia = grupo_materia.materia if grupo_materia else None
        periodo = periodo or (grupo_materia.periodo if grupo_materia else None)
        grupo = grupo_materia.grupo if grupo_materia else None
        cuatrimestre = cuatrimestre or (
            grupo.cuatrimestre
            if grupo and grupo.cuatrimestre else None
        )
        calificacion_final = _calcular_calificacion_final(
            calificaciones_por_carga.get(carga.id_carga, []),
            parciales_por_id
        )

        materias.append({
            "id_materia": materia.id_materia if materia else None,
            "nombre": materia.nombre if materia else None,
            "clave": materia.clave if materia else None,
            "calificacion_final": calificacion_final
        })

    calificaciones_finales = [
        materia["calificacion_final"]
        for materia in materias
        if materia["calificacion_final"] is not None
    ]
    promedio_general = None

    if calificaciones_finales:
        promedio_general = round(
            sum(calificaciones_finales) / len(calificaciones_finales),
            2
        )

    return {
        "alumno": _alumno_detalle(alumno),
        "carrera": {
            "id_carrera": alumno.carrera.id_carrera,
            "clave": alumno.carrera.clave,
            "rvoe": alumno.carrera.rvoe,
            "nombre": alumno.carrera.nombre,
            "logo":alumno.carrera.logo
        } if alumno.carrera else None,
        "periodo": {
            "id_periodo": periodo.id_periodo,
            "nombre": periodo.nombre
        } if periodo else None,
        "cuatrimestre": {
            "numero": cuatrimestre.numero,
            "nombre": cuatrimestre.nombre
        } if cuatrimestre else None,
        "materias": materias,
        "promedio_general": promedio_general,
        "asignaturas_acreditadas": len([
            calificacion
            for calificacion in calificaciones_finales
            if calificacion >= 70
        ])
    }


@router.get(
    "/",
    response_model=list[CalificacionDetalleResponse]
)
def listar_calificaciones(
    alumno_id: Optional[int] = None,
    materia_id: Optional[int] = None,
    grupo_id: Optional[int] = None,
    periodo_id: Optional[int] = None,
    parcial_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return get_calificaciones_detalle(
        db,
        alumno_id=alumno_id,
        materia_id=materia_id,
        grupo_id=grupo_id,
        periodo_id=periodo_id,
        parcial_id=parcial_id
    )


@router.get(
    "/captura/grupos",
    response_model=list[GrupoMateriaDetalleResponse]
)
def listar_grupos_captura(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    docente = _get_docente_actual(db, usuario)

    return get_grupos_materias_detalle(
        db,
        docente_id=docente.id_docente
    )


@router.get(
    "/cuadro-honor",
    response_model=CuadroHonorResponse
)
def obtener_cuadro_honor(
    cuatrimestre: Optional[int] = None,
    egresados: bool = False,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    if not egresados and (
        cuatrimestre is None or cuatrimestre < 1 or cuatrimestre > 9
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selecciona un cuatrimestre entre 1 y 9"
        )

    query = (
        db.query(CargaAcademica)
        .join(CargaAcademica.alumno)
        .join(CargaAcademica.grupo_materia)
        .join(GrupoMateria.grupo)
        .options(
            joinedload(CargaAcademica.alumno)
            .joinedload(Alumno.usuario),
            joinedload(CargaAcademica.alumno)
            .joinedload(Alumno.carrera),
            joinedload(CargaAcademica.grupo_materia)
            .joinedload(GrupoMateria.grupo)
            .joinedload(Grupo.cuatrimestre)
        )
        .filter(CargaAcademica.estatus != "BAJA")
    )

    if egresados:
        query = query.filter(
            Alumno.estatus.in_(["EGRESADO", "TITULADO"]),
            Grupo.cuatrimestre.has(
                Cuatrimestre.numero.between(1, 9)
            )
        )
    else:
        query = query.filter(
            Grupo.cuatrimestre.has(numero=cuatrimestre)
        )

    cargas = query.all()
    cargas_ids = [carga.id_carga for carga in cargas]
    parciales = db.query(Parcial).order_by(Parcial.id_parcial).all()
    parciales_por_id = {
        parcial.id_parcial: parcial
        for parcial in parciales
    }
    calificaciones_por_carga = {}

    if cargas_ids:
        calificaciones = (
            db.query(Calificacion)
            .filter(Calificacion.id_carga.in_(cargas_ids))
            .all()
        )

        for calificacion in calificaciones:
            calificaciones_por_carga.setdefault(
                calificacion.id_carga,
                []
            ).append(calificacion)

    return _build_cuadro_honor_response(
        cargas,
        calificaciones_por_carga,
        parciales_por_id,
        "egresados" if egresados else "cuatrimestre",
        None if egresados else cuatrimestre
    )


@router.get(
    "/boleta-final",
    response_model=BoletaFinalResponse
)
def obtener_boleta_final(
    alumno_id: int,
    periodo_id: int,
    db: Session = Depends(get_db)
):
    return _build_boleta_final(db, alumno_id, periodo_id)


@router.get(
    "/boleta-final/me",
    response_model=BoletaFinalResponse
)
def obtener_mi_boleta_final(
    periodo_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    alumno = _get_alumno_actual(db, usuario)

    return _build_boleta_final(db, alumno.id_alumno, periodo_id)


@router.get(
    "/captura/grupos/{grupo_materia_id}",
    response_model=CapturaCalificacionesResponse
)
def obtener_captura_grupo(
    grupo_materia_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    docente = _get_docente_actual(db, usuario)
    _validar_grupo_docente(db, grupo_materia_id, docente.id_docente)

    return _build_captura_response(db, grupo_materia_id)


@router.post(
    "/captura",
    response_model=CapturaCalificacionesResponse
)
def guardar_captura_calificaciones(
    captura: CapturaCalificacionesBatch,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    docente = _get_docente_actual(db, usuario)
    _validar_grupo_docente(
        db,
        captura.grupo_materia_id,
        docente.id_docente
    )

    cargas_validas = {
        id_carga
        for (id_carga,) in (
            db.query(CargaAcademica.id_carga)
            .filter(
                CargaAcademica.id_grupo_materia == captura.grupo_materia_id
            )
            .all()
        )
    }

    parciales_validos = {
        id_parcial
        for (id_parcial,) in db.query(Parcial.id_parcial).all()
    }

    for item in captura.calificaciones:
        if item.id_carga not in cargas_validas:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="La carga academica no pertenece al grupo asignado"
            )

        if item.id_parcial not in parciales_validos:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parcial no encontrado"
            )

        calificacion = (
            db.query(Calificacion)
            .filter(
                Calificacion.id_carga == item.id_carga,
                Calificacion.id_parcial == item.id_parcial
            )
            .first()
        )

        if calificacion:
            calificacion.calificacion = item.calificacion
            calificacion.capturado_por = usuario.id_usuario
            continue

        if item.calificacion is None:
            continue

        db.add(
            Calificacion(
                id_carga=item.id_carga,
                id_parcial=item.id_parcial,
                calificacion=item.calificacion,
                capturado_por=usuario.id_usuario
            )
        )

    db.commit()

    return _build_captura_response(db, captura.grupo_materia_id)


@router.get(
    "/{calificacion_id}",
    response_model=CalificacionDetalleResponse
)
def obtener_calificacion(
    calificacion_id: int,
    db: Session = Depends(get_db)
):
    calificacion = next(
        (
            item for item in get_calificaciones_detalle(db)
            if item["id_calificacion"] == calificacion_id
        ),
        None
    )

    if not calificacion:
        raise HTTPException(
            status_code=404,
            detail="Calificacion no encontrada"
        )

    return calificacion


@router.post(
    "/",
    response_model=CalificacionDetalleResponse
)
def crear_calificacion(
    calificacion: CalificacionCreate,
    db: Session = Depends(get_db)
):
    nueva_calificacion = create_calificacion(db, calificacion)

    return next(
        item for item in get_calificaciones_detalle(db)
        if item["id_calificacion"] == nueva_calificacion.id_calificacion
    )


@router.patch(
    "/{calificacion_id}",
    response_model=CalificacionDetalleResponse
)
def actualizar_calificacion(
    calificacion_id: int,
    calificacion: CalificacionUpdate,
    db: Session = Depends(get_db)
):
    calificacion_actualizada = update_calificacion(
        db,
        calificacion_id,
        calificacion
    )

    if not calificacion_actualizada:
        raise HTTPException(
            status_code=404,
            detail="Calificacion no encontrada"
        )

    return next(
        item for item in get_calificaciones_detalle(db)
        if item["id_calificacion"] == calificacion_id
    )


@router.delete(
    "/{calificacion_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_calificacion(
    calificacion_id: int,
    db: Session = Depends(get_db)
):
    if not get_calificacion(db, calificacion_id):
        raise HTTPException(
            status_code=404,
            detail="Calificacion no encontrada"
        )

    delete_calificacion(db, calificacion_id)
