from sqlalchemy.orm import Session, joinedload

from app.models.carrera import Carrera
from app.models.cuatrimestre import Cuatrimestre
from app.models.materia import Materia
from app.models.plan_estudio import PlanEstudio
from app.models.plan_materia import PlanMateria
from app.schemas.plan_estudio import PlanEstudioCreate, PlanEstudioUpdate


PLAN_RELATIONS = (
    joinedload(PlanEstudio.carrera),
    joinedload(PlanEstudio.materias).joinedload(PlanMateria.materia),
    joinedload(PlanEstudio.materias).joinedload(PlanMateria.cuatrimestre),
)

PLAN_FIELDS = {
    "id_carrera",
    "nombre_plan",
    "fecha_inicio",
    "fecha_fin",
    "vigente",
}


def _plan_query(db: Session):
    return db.query(PlanEstudio).options(*PLAN_RELATIONS)


def _materia_plan_query(db: Session):
    return (
        db.query(PlanMateria)
        .options(
            joinedload(PlanMateria.materia),
            joinedload(PlanMateria.cuatrimestre),
        )
    )


def _normalizar_plan_materia(data):
    if hasattr(data, "model_dump"):
        data = data.model_dump(exclude_unset=True)

    return dict(data)


def _validar_carrera(db: Session, id_carrera: int):
    existe = (
        db.query(Carrera.id_carrera)
        .filter(Carrera.id_carrera == id_carrera)
        .first()
    )

    if not existe:
        raise ValueError("Carrera no encontrada")


def _validar_referencias_plan_materia(
    db: Session,
    *,
    id_materia: int | None = None,
    id_cuatrimestre: int | None = None
):
    if id_materia is not None:
        existe_materia = (
            db.query(Materia.id_materia)
            .filter(Materia.id_materia == id_materia)
            .first()
        )

        if not existe_materia:
            raise ValueError("Materia no encontrada")

    if id_cuatrimestre is not None:
        existe_cuatrimestre = (
            db.query(Cuatrimestre.id_cuatrimestre)
            .filter(Cuatrimestre.id_cuatrimestre == id_cuatrimestre)
            .first()
        )

        if not existe_cuatrimestre:
            raise ValueError("Cuatrimestre no encontrado")


def _validar_materia_no_duplicada(
    db: Session,
    *,
    id_plan: int,
    id_materia: int,
    excluir_id_plan_materia: int | None = None
):
    query = db.query(PlanMateria).filter(
        PlanMateria.id_plan == id_plan,
        PlanMateria.id_materia == id_materia,
    )

    if excluir_id_plan_materia is not None:
        query = query.filter(
            PlanMateria.id_plan_materia != excluir_id_plan_materia
        )

    if query.first():
        raise ValueError("La materia ya existe en este plan de estudios")


def _validar_materias_sin_duplicados(materias_data):
    materias_vistas = set()
    relaciones_vistas = set()

    for materia_data in materias_data:
        id_plan_materia = materia_data.get("id_plan_materia")
        id_materia = materia_data.get("id_materia")

        if id_plan_materia is not None:
            if id_plan_materia in relaciones_vistas:
                raise ValueError("Hay materias del plan repetidas en la solicitud")

            relaciones_vistas.add(id_plan_materia)

        if id_materia in materias_vistas:
            raise ValueError("Hay materias repetidas en la solicitud")

        materias_vistas.add(id_materia)


def _sincronizar_materias_plan(
    db: Session,
    plan: PlanEstudio,
    materias_data
):
    materias_data = [
        _normalizar_plan_materia(materia)
        for materia in materias_data
    ]

    _validar_materias_sin_duplicados(materias_data)

    materias_existentes = {
        materia.id_plan_materia: materia
        for materia in plan.materias
    }
    ids_recibidos = {
        materia["id_plan_materia"]
        for materia in materias_data
        if materia.get("id_plan_materia") is not None
    }

    for id_plan_materia, materia in materias_existentes.items():
        if id_plan_materia not in ids_recibidos:
            db.delete(materia)

    db.flush()

    for materia_data in materias_data:
        id_plan_materia = materia_data.pop("id_plan_materia", None)

        _validar_referencias_plan_materia(
            db,
            id_materia=materia_data.get("id_materia"),
            id_cuatrimestre=materia_data.get("id_cuatrimestre"),
        )

        if id_plan_materia is None:
            db.add(
                PlanMateria(
                    id_plan=plan.id_plan,
                    **materia_data
                )
            )

            continue

        materia_plan = materias_existentes.get(id_plan_materia)

        if not materia_plan:
            raise ValueError("Materia del plan no encontrada")

        for key, value in materia_data.items():
            setattr(materia_plan, key, value)


def crear_plan_estudio(
    db: Session,
    plan_data: PlanEstudioCreate
):
    datos_plan = plan_data.model_dump(exclude={"materias"})
    materias_data = plan_data.materias

    _validar_carrera(db, datos_plan["id_carrera"])

    nuevo_plan = PlanEstudio(**datos_plan)

    db.add(nuevo_plan)
    db.flush()

    _validar_materias_sin_duplicados([
        _normalizar_plan_materia(materia)
        for materia in materias_data
    ])

    for materia in materias_data:
        materia_data = _normalizar_plan_materia(materia)

        _validar_referencias_plan_materia(
            db,
            id_materia=materia_data.get("id_materia"),
            id_cuatrimestre=materia_data.get("id_cuatrimestre"),
        )

        db.add(
            PlanMateria(
                id_plan=nuevo_plan.id_plan,
                **materia_data
            )
        )

    db.commit()

    return obtener_plan_por_id(db, nuevo_plan.id_plan)


def obtener_planes(db: Session):
    return (
        _plan_query(db)
        .order_by(PlanEstudio.id_plan)
        .all()
    )


def obtener_plan_por_id(
    db: Session,
    id_plan: int
):
    return (
        _plan_query(db)
        .filter(PlanEstudio.id_plan == id_plan)
        .first()
    )


def obtener_materia_plan_por_id(
    db: Session,
    id_plan: int,
    id_plan_materia: int
):
    return (
        _materia_plan_query(db)
        .filter(
            PlanMateria.id_plan == id_plan,
            PlanMateria.id_plan_materia == id_plan_materia,
        )
        .first()
    )


def actualizar_plan(
    db: Session,
    id_plan: int,
    datos: PlanEstudioUpdate
):
    plan = obtener_plan_por_id(db, id_plan)

    if not plan:
        return None

    update_data = datos.model_dump(exclude_unset=True)
    materias_data = update_data.pop("materias", None)

    if "id_carrera" in update_data:
        _validar_carrera(db, update_data["id_carrera"])

    for key, value in update_data.items():
        if key in PLAN_FIELDS:
            setattr(plan, key, value)

    if materias_data is not None:
        _sincronizar_materias_plan(db, plan, materias_data)

    db.commit()

    return obtener_plan_por_id(db, id_plan)


def eliminar_plan(
    db: Session,
    id_plan: int
):
    plan = obtener_plan_por_id(db, id_plan)

    if not plan:
        return None

    db.delete(plan)
    db.commit()

    return plan


def agregar_materia_a_plan(
    db: Session,
    id_plan: int,
    materia_data
):
    plan = obtener_plan_por_id(db, id_plan)

    if not plan:
        return None

    data = _normalizar_plan_materia(materia_data)

    _validar_referencias_plan_materia(
        db,
        id_materia=data.get("id_materia"),
        id_cuatrimestre=data.get("id_cuatrimestre"),
    )
    _validar_materia_no_duplicada(
        db,
        id_plan=id_plan,
        id_materia=data["id_materia"],
    )

    nueva_materia = PlanMateria(
        id_plan=id_plan,
        **data
    )

    db.add(nueva_materia)
    db.commit()
    db.refresh(nueva_materia)

    return obtener_materia_plan_por_id(
        db,
        id_plan,
        nueva_materia.id_plan_materia
    )


def actualizar_materia_de_plan(
    db: Session,
    id_plan: int,
    id_plan_materia: int,
    materia_data
):
    materia_plan = obtener_materia_plan_por_id(
        db,
        id_plan,
        id_plan_materia
    )

    if not materia_plan:
        return None

    data = _normalizar_plan_materia(materia_data)

    if not data:
        return materia_plan

    _validar_referencias_plan_materia(
        db,
        id_materia=data.get("id_materia"),
        id_cuatrimestre=data.get("id_cuatrimestre"),
    )

    if "id_materia" in data:
        _validar_materia_no_duplicada(
            db,
            id_plan=id_plan,
            id_materia=data["id_materia"],
            excluir_id_plan_materia=id_plan_materia,
        )

    for key, value in data.items():
        setattr(materia_plan, key, value)

    db.commit()

    return obtener_materia_plan_por_id(
        db,
        id_plan,
        id_plan_materia
    )


def eliminar_materia_de_plan(
    db: Session,
    id_plan: int,
    id_plan_materia: int
):
    materia_plan = obtener_materia_plan_por_id(
        db,
        id_plan,
        id_plan_materia
    )

    if not materia_plan:
        return False

    db.delete(materia_plan)
    db.commit()

    return True


def transformar_plan(plan):
    cuatrimestres_dict = {}

    materias_ordenadas = sorted(
        plan.materias,
        key=lambda pm: (
            pm.cuatrimestre.numero,
            pm.materia.nombre
        )
    )

    for pm in materias_ordenadas:
        id_cuatri = pm.cuatrimestre.id_cuatrimestre

        if id_cuatri not in cuatrimestres_dict:
            cuatrimestres_dict[id_cuatri] = {
                "id_cuatrimestre": id_cuatri,
                "numero": pm.cuatrimestre.numero,
                "nombre": pm.cuatrimestre.nombre,
                "materias": []
            }

        cuatrimestres_dict[id_cuatri]["materias"].append({
            "id_plan_materia": pm.id_plan_materia,
            "id_cuatrimestre": pm.id_cuatrimestre,
            "obligatoria": pm.obligatoria,
            "materia": {
                "id_materia": pm.materia.id_materia,
                "clave": pm.materia.clave,
                "nombre": pm.materia.nombre,
                "creditos": float(pm.materia.creditos)
            }
        })

    return {
        "id_plan": plan.id_plan,
        "id_carrera": plan.id_carrera,
        "nombre_plan": plan.nombre_plan,
        "fecha_inicio": plan.fecha_inicio,
        "fecha_fin": plan.fecha_fin,
        "vigente": plan.vigente,

        "carrera": {
            "id_carrera": plan.carrera.id_carrera,
            "nombre": plan.carrera.nombre
        },

        "cuatrimestres": sorted(
            cuatrimestres_dict.values(),
            key=lambda cuatrimestre: cuatrimestre["numero"]
        )
    }
