from collections import Counter
from datetime import date
import json

from sqlalchemy.orm import Session, joinedload

from app.models.alumno import Alumno
from app.models.calificacion import Calificacion
from app.models.carga_academica import CargaAcademica
from app.models.cierre_periodo import CierrePeriodo
from app.models.cuatrimestre import Cuatrimestre
from app.models.grupo import Grupo
from app.models.grupo_materia import GrupoMateria
from app.models.historial_academico import HistorialAcademico
from app.models.inscripcion import Inscripcion
from app.models.parcial import Parcial
from app.models.periodo import Periodo
from app.models.plan_estudio import PlanEstudio
from app.models.plan_materia import PlanMateria
from app.services.elegibilidad_academica import validar_prerrequisitos


CALIFICACION_APROBATORIA = 70


def _periodo_pendiente_siguiente(db: Session, periodo: Periodo):
    return (
        db.query(Periodo)
        .filter(
            Periodo.estado == "PENDIENTE",
            Periodo.id_periodo != periodo.id_periodo,
        )
        .order_by(
            Periodo.fecha_inicio.asc(),
            Periodo.id_periodo.asc(),
        )
        .first()
    )


def _grupos_del_periodo(db: Session, periodo_id: int):
    return (
        db.query(Grupo)
        .join(GrupoMateria, GrupoMateria.id_grupo == Grupo.id_grupo)
        .options(
            joinedload(Grupo.carrera),
            joinedload(Grupo.cuatrimestre),
        )
        .filter(GrupoMateria.id_periodo == periodo_id)
        .distinct()
        .all()
    )


def _calificacion_final(carga: CargaAcademica, parciales_por_id):
    calificaciones = [
        calificacion
        for calificacion in carga_calificaciones(carga)
        if calificacion.calificacion is not None
    ]

    if not calificaciones:
        return None

    total = 0
    peso_total = 0

    for calificacion in calificaciones:
        parcial = parciales_por_id.get(calificacion.id_parcial)
        peso = float(parcial.porcentaje) if parcial and parcial.porcentaje else 0
        total += float(calificacion.calificacion) * peso
        peso_total += peso

    if peso_total > 0:
        return round(total / peso_total, 2)

    return round(
        sum(float(calificacion.calificacion) for calificacion in calificaciones)
        / len(calificaciones),
        2,
    )


def carga_calificaciones(carga: CargaAcademica):
    return getattr(carga, "calificaciones", [])


def _cargas_periodo(db: Session, periodo_id: int):
    return (
        db.query(CargaAcademica)
        .join(CargaAcademica.grupo_materia)
        .options(
            joinedload(CargaAcademica.grupo_materia)
            .joinedload(GrupoMateria.materia),
            joinedload(CargaAcademica.alumno),
        )
        .filter(
            GrupoMateria.id_periodo == periodo_id,
            CargaAcademica.estatus == "CURSANDO",
        )
        .all()
    )


def _calificaciones_por_carga(db: Session, cargas):
    cargas_ids = [carga.id_carga for carga in cargas]

    if not cargas_ids:
        return {}

    calificaciones = (
        db.query(Calificacion)
        .filter(Calificacion.id_carga.in_(cargas_ids))
        .all()
    )
    por_carga = {}

    for calificacion in calificaciones:
        por_carga.setdefault(calificacion.id_carga, []).append(calificacion)

    return por_carga


def _cerrar_cargas(db: Session, periodo_id: int, resumen: dict, preview: bool):
    cargas = _cargas_periodo(db, periodo_id)
    parciales = db.query(Parcial).all()
    parciales_por_id = {parcial.id_parcial: parcial for parcial in parciales}
    calificaciones_por_carga = _calificaciones_por_carga(db, cargas)
    incompletas = []

    for carga in cargas:
        setattr(carga, "calificaciones", calificaciones_por_carga.get(carga.id_carga, []))

        if parciales and len(carga_calificaciones(carga)) < len(parciales):
            incompletas.append(carga)

    if incompletas:
        resumen["calificaciones_incompletas"] = len(incompletas)
        resumen["advertencias"].append(
            "Hay cargas con calificaciones incompletas; se marcarian como NP."
        )

    for carga in cargas:
        grupo_materia = carga.grupo_materia
        materia = grupo_materia.materia if grupo_materia else None
        final = _calificacion_final(carga, parciales_por_id)
        resultado = (
            "NP"
            if final is None
            else "APROBADO"
            if final >= CALIFICACION_APROBATORIA
            else "REPROBADO"
        )

        resumen["cargas_cerradas"] += 1

        if preview:
            continue

        carga.estatus = (
            "NP"
            if resultado == "NP"
            else "APROBADA"
            if resultado == "APROBADO"
            else "REPROBADA"
        )

        historial = (
            db.query(HistorialAcademico)
            .filter(
                HistorialAcademico.id_alumno == carga.id_alumno,
                HistorialAcademico.id_materia == grupo_materia.id_materia,
                HistorialAcademico.id_periodo == periodo_id,
                HistorialAcademico.tipo_evaluacion == carga.oportunidad,
            )
            .first()
        )
        datos_historial = {
            "id_alumno": carga.id_alumno,
            "id_materia": materia.id_materia if materia else grupo_materia.id_materia,
            "id_periodo": periodo_id,
            "tipo_evaluacion": carga.oportunidad,
            "oportunidad": carga.intento or 1,
            "calificacion_final": final,
            "resultado": resultado,
            "fecha_cierre": date.today(),
        }

        if historial:
            for key, value in datos_historial.items():
                setattr(historial, key, value)
            continue

        db.add(HistorialAcademico(**datos_historial))


def _resolver_plan_grupo(db: Session, grupo: Grupo, inscripciones):
    if grupo.id_plan:
        return grupo.id_plan, False

    planes_alumnos = [
        inscripcion.alumno.id_plan
        for inscripcion in inscripciones
        if inscripcion.alumno and inscripcion.alumno.id_plan
    ]

    if planes_alumnos:
        return Counter(planes_alumnos).most_common(1)[0][0], len(set(planes_alumnos)) > 1

    plan = (
        db.query(PlanEstudio)
        .filter(
            PlanEstudio.id_carrera == grupo.id_carrera,
            PlanEstudio.vigente.is_(True),
        )
        .order_by(PlanEstudio.id_plan.desc())
        .first()
    )

    if plan:
        return plan.id_plan, False

    plan = (
        db.query(PlanEstudio)
        .filter(PlanEstudio.id_carrera == grupo.id_carrera)
        .order_by(PlanEstudio.id_plan.desc())
        .first()
    )

    return (plan.id_plan if plan else None), False


def _inscripciones_grupo_periodo(db: Session, grupo_id: int, periodo_id: int):
    return (
        db.query(Inscripcion)
        .options(joinedload(Inscripcion.alumno))
        .filter(
            Inscripcion.id_grupo == grupo_id,
            Inscripcion.id_periodo == periodo_id,
            Inscripcion.estado == "ACTIVO",
        )
        .all()
    )


def _materias_plan_cuatrimestre(db: Session, id_plan: int, id_cuatrimestre: int):
    return (
        db.query(PlanMateria)
        .options(joinedload(PlanMateria.materia))
        .filter(
            PlanMateria.id_plan == id_plan,
            PlanMateria.id_cuatrimestre == id_cuatrimestre,
            PlanMateria.obligatoria.is_(True),
        )
        .order_by(PlanMateria.id_plan_materia)
        .all()
    )


def _ids_materias_obligatorias_plan(db: Session, id_plan: int):
    return {
        id_materia
        for (id_materia,) in (
            db.query(PlanMateria.id_materia)
            .filter(
                PlanMateria.id_plan == id_plan,
                PlanMateria.obligatoria.is_(True),
            )
            .all()
        )
    }


def _ids_materias_aprobadas_alumno(db: Session, alumno_id: int):
    return {
        id_materia
        for (id_materia,) in (
            db.query(HistorialAcademico.id_materia)
            .filter(
                HistorialAcademico.id_alumno == alumno_id,
                HistorialAcademico.resultado == "APROBADO",
            )
            .distinct()
            .all()
        )
    }


def _alumno_completo_plan(db: Session, alumno: Alumno):
    if not alumno or not alumno.id_plan:
        return False

    materias_plan = _ids_materias_obligatorias_plan(db, alumno.id_plan)

    if not materias_plan:
        return False

    materias_aprobadas = _ids_materias_aprobadas_alumno(
        db,
        alumno.id_alumno,
    )

    return materias_plan.issubset(materias_aprobadas)


def _cerrar_grupo_terminal(
    db: Session,
    *,
    grupo: Grupo,
    inscripciones,
    resumen: dict,
    preview: bool,
):
    resumen["grupos_finalizados"] += 1
    resumen["grupos_cerrados"] += 1

    if not preview:
        grupo.estatus = "CERRADO"

    for inscripcion in inscripciones:
        alumno = inscripcion.alumno

        if not preview:
            inscripcion.estado = "FINALIZADO"

        if not alumno or alumno.estatus != "ACTIVO":
            continue

        if _alumno_completo_plan(db, alumno):
            resumen["alumnos_egresados"] += 1

            if not preview:
                alumno.estatus = "EGRESADO"
            continue

        resumen["advertencias"].append(
            f"Alumno {alumno.matricula} no egreso porque aun tiene materias pendientes o reprobadas."
        )


def _buscar_o_crear_grupo_materia(
    db: Session,
    *,
    grupo_id: int,
    materia_id: int,
    periodo_id: int,
    preview: bool,
):
    existente = (
        db.query(GrupoMateria)
        .filter(
            GrupoMateria.id_grupo == grupo_id,
            GrupoMateria.id_materia == materia_id,
            GrupoMateria.id_periodo == periodo_id,
        )
        .first()
    )

    if existente:
        return existente, False

    if preview:
        return None, True

    grupo_materia = GrupoMateria(
        id_grupo=grupo_id,
        id_materia=materia_id,
        id_docente=None,
        id_periodo=periodo_id,
        aula=None,
        cupo_maximo=None,
    )
    db.add(grupo_materia)
    db.flush()

    return grupo_materia, True


def _crear_inscripcion_si_falta(
    db: Session,
    *,
    alumno_id: int,
    grupo_id: int,
    periodo_id: int,
    preview: bool,
):
    existente = (
        db.query(Inscripcion)
        .filter(
            Inscripcion.id_alumno == alumno_id,
            Inscripcion.id_grupo == grupo_id,
            Inscripcion.id_periodo == periodo_id,
        )
        .first()
    )

    if existente or preview:
        return False

    db.add(
        Inscripcion(
            id_alumno=alumno_id,
            id_grupo=grupo_id,
            id_periodo=periodo_id,
            fecha_inscripcion=date.today(),
            estado="ACTIVO",
        )
    )

    return True


def _crear_carga_si_puede(db: Session, alumno: Alumno, grupo_materia, resumen, preview):
    duplicada = (
        db.query(CargaAcademica)
        .join(CargaAcademica.grupo_materia)
        .filter(
            CargaAcademica.id_alumno == alumno.id_alumno,
            GrupoMateria.id_materia == grupo_materia.id_materia,
            GrupoMateria.id_periodo == grupo_materia.id_periodo,
            CargaAcademica.estatus != "BAJA",
        )
        .first()
    )

    if duplicada:
        return

    try:
        validar_prerrequisitos(db, alumno.id_alumno, grupo_materia)
    except ValueError as error:
        resumen["alumnos_omitidos"].append({
            "id_alumno": alumno.id_alumno,
            "id_materia": grupo_materia.id_materia,
            "motivo": str(error),
        })
        return

    resumen["cargas_creadas"] += 1

    if preview:
        return

    db.add(
        CargaAcademica(
            id_alumno=alumno.id_alumno,
            id_grupo_materia=grupo_materia.id_grupo_materia,
            oportunidad="ORDINARIO",
            intento=1,
            estatus="CURSANDO",
            fecha_inscripcion=date.today(),
        )
    )


def _avanzar_grupos_y_generar_oferta(
    db: Session,
    periodo_id: int,
    periodo_siguiente: Periodo | None,
    resumen: dict,
    preview: bool,
):
    grupos = _grupos_del_periodo(db, periodo_id)
    cuatrimestres = db.query(Cuatrimestre).all()
    cuatrimestres_por_numero = {
        cuatrimestre.numero: cuatrimestre
        for cuatrimestre in cuatrimestres
    }

    for grupo in grupos:
        inscripciones = _inscripciones_grupo_periodo(
            db,
            grupo.id_grupo,
            periodo_id,
        )
        alumnos = [
            inscripcion.alumno
            for inscripcion in inscripciones
            if inscripcion.alumno and inscripcion.alumno.estatus == "ACTIVO"
        ]

        if not grupo.carrera or not grupo.cuatrimestre:
            resumen["advertencias"].append(
                f"Grupo {grupo.nombre or grupo.id_grupo} sin carrera o cuatrimestre."
            )
            continue

        numero_actual = grupo.cuatrimestre.numero
        ultimo_cuatrimestre = grupo.carrera.duracion_cuatrimestres

        if numero_actual >= ultimo_cuatrimestre:
            _cerrar_grupo_terminal(
                db,
                grupo=grupo,
                inscripciones=inscripciones,
                resumen=resumen,
                preview=preview,
            )
            continue

        siguiente_cuatrimestre = cuatrimestres_por_numero.get(numero_actual + 1)

        if not siguiente_cuatrimestre:
            resumen["advertencias"].append(
                f"No existe el cuatrimestre {numero_actual + 1} para {grupo.nombre}."
            )
            continue

        if not periodo_siguiente:
            resumen["advertencias"].append(
                f"Grupo {grupo.nombre} no genero oferta porque no hay periodo pendiente."
            )
            continue

        resumen["grupos_avanzados"] += 1

        id_plan, planes_mixtos = _resolver_plan_grupo(db, grupo, inscripciones)

        if planes_mixtos:
            resumen["advertencias"].append(
                f"Grupo {grupo.nombre} tiene alumnos de mas de un plan; se uso el plan {id_plan}."
            )

        if not id_plan:
            resumen["advertencias"].append(
                f"No se encontro plan de estudios para el grupo {grupo.nombre}."
            )
            continue

        materias_plan = _materias_plan_cuatrimestre(
            db,
            id_plan,
            siguiente_cuatrimestre.id_cuatrimestre,
        )

        if len(materias_plan) != 5:
            resumen["advertencias"].append(
                f"El grupo {grupo.nombre} tiene {len(materias_plan)} materias en el plan para {siguiente_cuatrimestre.nombre}."
            )

        if not preview:
            grupo.id_cuatrimestre = siguiente_cuatrimestre.id_cuatrimestre

        for inscripcion in inscripciones:
            if not preview:
                inscripcion.estado = "FINALIZADO"

            if inscripcion.alumno and inscripcion.alumno.estatus == "ACTIVO":
                if _crear_inscripcion_si_falta(
                    db,
                    alumno_id=inscripcion.id_alumno,
                    grupo_id=grupo.id_grupo,
                    periodo_id=periodo_siguiente.id_periodo,
                    preview=preview,
                ):
                    resumen["inscripciones_creadas"] += 1
                elif preview:
                    resumen["inscripciones_creadas"] += 1

        for materia_plan in materias_plan:
            grupo_materia, creada = _buscar_o_crear_grupo_materia(
                db,
                grupo_id=grupo.id_grupo,
                materia_id=materia_plan.id_materia,
                periodo_id=periodo_siguiente.id_periodo,
                preview=preview,
            )

            if creada:
                resumen["materias_grupo_creadas"] += 1

            if grupo_materia is None and preview:
                grupo_materia = GrupoMateria(
                    id_grupo=grupo.id_grupo,
                    id_materia=materia_plan.id_materia,
                    id_periodo=periodo_siguiente.id_periodo,
                    materia=materia_plan.materia,
                )

            for alumno in alumnos:
                _crear_carga_si_puede(db, alumno, grupo_materia, resumen, preview)


def _resumen_base(periodo: Periodo, periodo_siguiente: Periodo | None):
    return {
        "periodo_cerrado": {
            "id_periodo": periodo.id_periodo,
            "nombre": periodo.nombre,
        },
        "periodo_activado": {
            "id_periodo": periodo_siguiente.id_periodo,
            "nombre": periodo_siguiente.nombre,
        } if periodo_siguiente else None,
        "cargas_cerradas": 0,
        "grupos_avanzados": 0,
        "grupos_finalizados": 0,
        "grupos_cerrados": 0,
        "alumnos_egresados": 0,
        "materias_grupo_creadas": 0,
        "inscripciones_creadas": 0,
        "cargas_creadas": 0,
        "calificaciones_incompletas": 0,
        "alumnos_omitidos": [],
        "advertencias": [],
    }


def previsualizar_cierre_periodo(db: Session, periodo_id: int):
    periodo = db.query(Periodo).filter(Periodo.id_periodo == periodo_id).first()

    if not periodo:
        raise ValueError("Periodo no encontrado")

    periodo_siguiente = _periodo_pendiente_siguiente(db, periodo)
    resumen = _resumen_base(periodo, periodo_siguiente)

    if not periodo_siguiente:
        resumen["advertencias"].append(
            "No hay periodo pendiente para activar despues del cierre."
        )

    _cerrar_cargas(db, periodo_id, resumen, preview=True)
    _avanzar_grupos_y_generar_oferta(
        db,
        periodo_id,
        periodo_siguiente,
        resumen,
        preview=True,
    )

    return resumen


def cerrar_periodo_completo(db: Session, periodo_id: int):
    periodo = db.query(Periodo).filter(Periodo.id_periodo == periodo_id).first()

    if not periodo:
        raise ValueError("Periodo no encontrado")

    if periodo.estado == "CERRADO":
        raise ValueError("El periodo ya esta cerrado")

    periodo_siguiente = _periodo_pendiente_siguiente(db, periodo)
    resumen = _resumen_base(periodo, periodo_siguiente)

    if not periodo_siguiente:
        resumen["advertencias"].append(
            "No hay periodo pendiente para activar despues del cierre."
        )

    _cerrar_cargas(db, periodo_id, resumen, preview=False)
    _avanzar_grupos_y_generar_oferta(
        db,
        periodo_id,
        periodo_siguiente,
        resumen,
        preview=False,
    )

    periodo.estado = "CERRADO"

    if periodo_siguiente:
        (
            db.query(Periodo)
            .filter(
                Periodo.estado == "ACTIVO",
                Periodo.id_periodo.notin_([
                    periodo.id_periodo,
                    periodo_siguiente.id_periodo,
                ]),
            )
            .update(
                {Periodo.estado: "PENDIENTE"},
                synchronize_session=False,
            )
        )
        periodo_siguiente.estado = "ACTIVO"

    db.add(
        CierrePeriodo(
            id_periodo_cerrado=periodo.id_periodo,
            id_periodo_activado=(
                periodo_siguiente.id_periodo if periodo_siguiente else None
            ),
            resumen_json=json.dumps(resumen, default=str),
        )
    )
    db.commit()
    db.refresh(periodo)

    return periodo, resumen
