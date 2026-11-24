from decimal import Decimal
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, BeforeValidator, Field

Clave = Literal["C1", "C2", "C3", "C4", "C5", "EPA"]


def _vacio_a_none(valor):
    if isinstance(valor, str) and valor.strip() == "":
        return None

    return valor


NumeroOpcional = Annotated[Optional[Decimal], BeforeValidator(_vacio_a_none)]


class CriterioDesglose(BaseModel):
    clave: Clave
    nombre: Optional[str] = None
    porcentaje: NumeroOpcional = None
    puntos_max: NumeroOpcional = None


class DesgloseGuardar(BaseModel):
    criterios: list[CriterioDesglose]
    puntajes: dict[int, dict[Clave, NumeroOpcional]] = Field(
        default_factory=dict
    )


class CriterioDesgloseResponse(BaseModel):
    clave: Clave
    nombre: Optional[str] = None
    porcentaje: Optional[float] = None
    puntos_max: Optional[float] = None


class ResumenDesglose(BaseModel):
    C1: Optional[float] = None
    C2: Optional[float] = None
    C3: Optional[float] = None
    C4: Optional[float] = None
    C5: Optional[float] = None
    EPA: Optional[float] = None
    cpf: Optional[int] = None
    cpfl: Optional[str] = None
    completo: bool = False


class AlumnoDesgloseResponse(BaseModel):
    id_carga: int
    puntajes: dict[str, Optional[float]] = Field(default_factory=dict)
    resumen: ResumenDesglose


class DesgloseResponse(BaseModel):
    criterios: list[CriterioDesgloseResponse]
    alumnos: list[AlumnoDesgloseResponse] = Field(default_factory=list)