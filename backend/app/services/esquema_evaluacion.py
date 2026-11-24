"""Esquema de evaluacion: UNICO lugar que decide como se evalua un grupo.

Toda pantalla, endpoint o reporte que necesite saber que parciales le tocan a
un grupo, si admite desglose o como se calcula la calificacion final le
pregunta a este modulo. Nadie decide por su cuenta.

Contrato por modalidad de la carrera:

    | | CUATRIMESTRAL | SABATINA |
    |---|---|---|
    | Evaluaciones | Primer, Segundo y Tercer Parcial (25/25/50) | Calificacion final (100) |
    | Desglose por criterios | Primer y Segundo parcial | No |
    | Calificacion final | Promedio ponderado | La misma calificacion capturada |
    | Asistencia | Por parcial y total | Solo total |

La modalidad vive unicamente en `carreras.modalidad`.

Nota de diseno: las funciones puras (calculo y validaciones) no importan
SQLAlchemy ni los modelos a nivel de modulo, para poder probarse sin base de
datos. Las consultas importan los modelos dentro de cada funcion.
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Mapping, Optional, Sequence

MODALIDADES = ("CUATRIMESTRAL", "SABATINA")

# Modalidad que se asume si el grupo no tiene carrera asignada (comportamiento
# historico del sistema).
MODALIDAD_POR_DEFECTO = "CUATRIMESTRAL"

# Calificacion minima para acreditar. Unico lugar donde se define.
CALIFICACION_APROBATORIA = Decimal("70")

# Cuantos de los primeros parciales de cada modalidad admiten desglose.
PARCIALES_CON_DESGLOSE = {"CUATRIMESTRAL": 2, "SABATINA": 0}

SUMA_PESOS = Decimal("100")
_DOS_DECIMALES = Decimal("0.01")


class EsquemaEvaluacionError(ValueError):
    """La configuracion o el uso del esquema de evaluacion no es valido."""


def _decimal(valor) -> Decimal:
    return valor if isinstance(valor, Decimal) else Decimal(str(valor))


# --------------------------------------------------------------- calculos

def calcular_calificacion_final(
    calificaciones: Mapping[int, Optional[object]],
    pesos: Mapping[int, object]
) -> Optional[Decimal]:
    """Promedio ponderado de los parciales capturados, con 2 decimales.

    Los parciales sin calificacion (None) no cuentan. Si ninguno esta
    capturado devuelve None. Si los pesos capturados suman 0 usa el promedio
    simple. El redondeo es "mitad hacia arriba".
    """
    capturadas = {
        id_parcial: _decimal(valor)
        for id_parcial, valor in calificaciones.items()
        if valor is not None
    }

    if not capturadas:
        return None

    peso_total = sum(
        (_decimal(pesos.get(id_parcial, 0)) for id_parcial in capturadas),
        Decimal("0")
    )

    if peso_total > 0:
        total = sum(
            (
                valor * _decimal(pesos.get(id_parcial, 0))
                for id_parcial, valor in capturadas.items()
            ),
            Decimal("0")
        )
        resultado = total / peso_total
    else:
        resultado = sum(capturadas.values(), Decimal("0")) / len(capturadas)

    return resultado.quantize(_DOS_DECIMALES, rounding=ROUND_HALF_UP)


def es_aprobatoria(calificacion) -> bool:
    if calificacion is None:
        return False

    return _decimal(calificacion) >= CALIFICACION_APROBATORIA


# ---------------------------------------------------------------- esquema

@dataclass(frozen=True)
class EsquemaEvaluacion:
    modalidad: str
    parciales: tuple  # filas de `parciales` de la modalidad, ordenadas por id

    @property
    def ids_parciales(self) -> tuple:
        return tuple(parcial.id_parcial for parcial in self.parciales)

    @property
    def pesos(self) -> dict:
        return {
            parcial.id_parcial: _decimal(parcial.porcentaje)
            for parcial in self.parciales
        }

    @property
    def evaluacion_unica(self) -> bool:
        """True cuando la modalidad tiene una sola evaluacion (sabatina)."""
        return len(self.parciales) == 1

    def contiene(self, id_parcial: int) -> bool:
        return id_parcial in self.ids_parciales

    def validar_parcial(self, id_parcial: int) -> None:
        if not self.contiene(id_parcial):
            raise EsquemaEvaluacionError(
                f"El parcial {id_parcial} no pertenece a la modalidad "
                f"{self.modalidad}"
            )

    def admite_desglose(self, id_parcial: int) -> bool:
        limite = PARCIALES_CON_DESGLOSE.get(self.modalidad, 0)

        return id_parcial in self.ids_parciales[:limite]

    def calificacion_final(
        self,
        calificaciones: Mapping[int, Optional[object]]
    ) -> Optional[Decimal]:
        return calcular_calificacion_final(calificaciones, self.pesos)


def construir_esquema(
    modalidad: str,
    parciales: Sequence
) -> EsquemaEvaluacion:
    """Valida y arma el esquema de una modalidad a partir de sus parciales."""
    if modalidad not in MODALIDADES:
        raise EsquemaEvaluacionError(f"Modalidad no valida: {modalidad}")

    if not parciales:
        raise EsquemaEvaluacionError(
            f"No hay parciales configurados para la modalidad {modalidad}"
        )

    suma = sum(
        (_decimal(parcial.porcentaje) for parcial in parciales),
        Decimal("0")
    )

    if suma != SUMA_PESOS:
        raise EsquemaEvaluacionError(
            f"Los parciales de la modalidad {modalidad} suman {suma}% "
            f"y deben sumar {SUMA_PESOS}%"
        )

    ordenados = tuple(sorted(parciales, key=lambda p: p.id_parcial))

    return EsquemaEvaluacion(modalidad=modalidad, parciales=ordenados)


# ------------------------------------------------------ consultas (con BD)

def obtener_catalogo(db) -> dict:
    """{modalidad: EsquemaEvaluacion} de las modalidades con parciales."""
    from app.models.parcial import Parcial

    por_modalidad = {}

    for parcial in db.query(Parcial).order_by(Parcial.id_parcial).all():
        por_modalidad.setdefault(parcial.modalidad, []).append(parcial)

    return {
        modalidad: construir_esquema(modalidad, parciales)
        for modalidad, parciales in por_modalidad.items()
    }


def obtener_pesos(db) -> dict:
    """{id_parcial: peso} de todos los parciales, de cualquier modalidad.

    Sirve para calcular la calificacion final de calificaciones ya guardadas
    (boleta, cuadro de honor): cada calificacion pertenece a un parcial y cada
    parcial a una sola modalidad, asi que no hace falta conocer la modalidad
    de la carga para ponderar. No valida la suma de pesos: leer una boleta no
    debe fallar por una configuracion a medio editar.
    """
    from app.models.parcial import Parcial

    return {
        id_parcial: (porcentaje if porcentaje is not None else 0)
        for id_parcial, porcentaje in db.query(
            Parcial.id_parcial,
            Parcial.porcentaje
        ).all()
    }


def obtener_esquema(db, modalidad: str) -> EsquemaEvaluacion:
    catalogo = obtener_catalogo(db)

    if modalidad not in catalogo:
        raise EsquemaEvaluacionError(
            f"No hay parciales configurados para la modalidad {modalidad}"
        )

    return catalogo[modalidad]


def modalidades_de_grupos_materias(db, ids_grupo_materia) -> dict:
    """{id_grupo_materia: modalidad} con una sola consulta."""
    from app.models.carrera import Carrera
    from app.models.grupo import Grupo
    from app.models.grupo_materia import GrupoMateria

    ids = list(set(ids_grupo_materia))

    if not ids:
        return {}

    filas = (
        db.query(GrupoMateria.id_grupo_materia, Carrera.modalidad)
        .join(Grupo, Grupo.id_grupo == GrupoMateria.id_grupo)
        .outerjoin(Carrera, Carrera.id_carrera == Grupo.id_carrera)
        .filter(GrupoMateria.id_grupo_materia.in_(ids))
        .all()
    )
    resultado = {
        id_grupo_materia: modalidad or MODALIDAD_POR_DEFECTO
        for id_grupo_materia, modalidad in filas
    }

    return resultado


def modalidad_de_grupo_materia(db, id_grupo_materia: int) -> str:
    modalidades = modalidades_de_grupos_materias(db, [id_grupo_materia])

    if id_grupo_materia not in modalidades:
        raise EsquemaEvaluacionError("Grupo-materia no encontrado")

    return modalidades[id_grupo_materia]


def modalidad_de_grupo(db, id_grupo: int) -> str:
    from app.models.carrera import Carrera
    from app.models.grupo import Grupo

    fila = (
        db.query(Grupo.id_grupo, Carrera.modalidad)
        .outerjoin(Carrera, Carrera.id_carrera == Grupo.id_carrera)
        .filter(Grupo.id_grupo == id_grupo)
        .first()
    )

    if not fila:
        raise EsquemaEvaluacionError("Grupo no encontrado")

    return fila[1] or MODALIDAD_POR_DEFECTO


def esquema_de_grupo_materia(db, id_grupo_materia: int) -> EsquemaEvaluacion:
    return obtener_esquema(
        db,
        modalidad_de_grupo_materia(db, id_grupo_materia)
    )


def esquema_de_grupo(db, id_grupo: int) -> EsquemaEvaluacion:
    return obtener_esquema(db, modalidad_de_grupo(db, id_grupo))