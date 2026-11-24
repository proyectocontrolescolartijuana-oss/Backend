from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional

Modalidad = Literal["CUATRIMESTRAL", "SABATINA"]


class ParcialBase(BaseModel):
    nombre: str
    modalidad: Modalidad = "CUATRIMESTRAL"
    porcentaje: float


class ParcialCreate(ParcialBase):
    # Se valida solo al crear/editar, no al leer lo que ya existe.
    porcentaje: float = Field(gt=0, le=100)


class ParcialUpdate(BaseModel):
    nombre: Optional[str] = None
    modalidad: Optional[Modalidad] = None
    porcentaje: Optional[float] = Field(default=None, gt=0, le=100)

    @field_validator("modalidad")
    @classmethod
    def modalidad_no_nula(cls, valor: Optional[str]) -> Optional[str]:
        # La columna es NOT NULL: si se manda, no puede ser null.
        if valor is None:
            raise ValueError("La modalidad no puede ser nula")

        return valor


class ParcialResponse(ParcialBase):
    id_parcial: int

    class Config:
        from_attributes = True