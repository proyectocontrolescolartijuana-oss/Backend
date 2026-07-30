import unicodedata

from sqlalchemy.orm import Session, joinedload

from app.models.carga_academica import CargaAcademica
from app.models.grupo_materia import GrupoMateria
from app.models.historial_academico import HistorialAcademico
from app.models.materia import Materia
from app.models.materia_prerrequisito import MateriaPrerrequisito


ROMANOS_PREVIOS = {
    "II": "I",
    "III": "II",
    "IV": "III",
    "V": "IV",
    "VI": "V",
    "VII": "VI",
    "VIII": "VII",
    "IX": "VIII",
    "X": "IX",
}


def normalizar_texto(texto):
    texto = unicodedata.normalize("NFD", texto or "")
    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    return " ".join(texto.upper().split())


def materia_anterior_por_nombre(db: Session, materia: Materia):
    partes = normalizar_texto(materia.nombre).split()

    if not partes:
        return None

    ultimo_token = partes[-1]
    token_previo = ROMANOS_PREVIOS.get(ultimo_token)

    if not token_previo:
        return None

    nombre_requerido = " ".join([*partes[:-1], token_previo])

    for candidata in db.query(Materia).all():
        if normalizar_texto(candidata.nombre) == nombre_requerido:
            return candidata

    return None


def materias_requeridas(db: Session, materia: Materia):
    prerrequisitos = (
        db.query(MateriaPrerrequisito)
        .options(joinedload(MateriaPrerrequisito.materia_requerida))
        .filter(
            MateriaPrerrequisito.id_materia == materia.id_materia,
            MateriaPrerrequisito.tipo == "OBLIGATORIO",
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
    materia_anterior = materia_anterior_por_nombre(db, materia)

    if (
        materia_anterior
        and materia_anterior.id_materia not in ids_requeridas
    ):
        requeridas.append(materia_anterior)

    return requeridas


def materia_aprobada(db: Session, alumno_id: int, materia_id: int):
    historial_aprobado = (
        db.query(HistorialAcademico.id_historial)
        .filter(
            HistorialAcademico.id_alumno == alumno_id,
            HistorialAcademico.id_materia == materia_id,
            HistorialAcademico.resultado == "APROBADO",
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
            CargaAcademica.estatus == "APROBADA",
        )
        .first()
    )

    return bool(carga_aprobada)


def ultimo_resultado_materia(db: Session, alumno_id: int, materia_id: int):
    return (
        db.query(HistorialAcademico)
        .filter(
            HistorialAcademico.id_alumno == alumno_id,
            HistorialAcademico.id_materia == materia_id,
        )
        .order_by(
            HistorialAcademico.fecha_cierre.desc(),
            HistorialAcademico.id_historial.desc(),
        )
        .first()
    )


def validar_prerrequisitos(db: Session, alumno_id: int, grupo_materia: GrupoMateria):
    materia = grupo_materia.materia

    if not materia:
        return

    for requerida in materias_requeridas(db, materia):
        if materia_aprobada(db, alumno_id, requerida.id_materia):
            continue

        ultimo_resultado = ultimo_resultado_materia(
            db,
            alumno_id,
            requerida.id_materia,
        )
        motivo = (
            f"reprobo {requerida.nombre}"
            if ultimo_resultado
            and ultimo_resultado.resultado == "REPROBADO"
            else f"debe acreditar primero {requerida.nombre}"
        )

        raise ValueError(
            f"No puede inscribirse a {materia.nombre} porque {motivo}."
        )
