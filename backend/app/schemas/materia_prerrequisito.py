from pydantic import BaseModel
from typing import Literal, Optional

from .materia import MateriaSimple


TipoPrerrequisito = Literal["OBLIGATORIO", "RECOMENDADO"]


class MateriaPrerrequisitoBase(BaseModel):
    id_materia_requerida: int
    tipo: TipoPrerrequisito = "OBLIGATORIO"


class MateriaPrerrequisitoCreate(MateriaPrerrequisitoBase):
    pass


class MateriaPrerrequisitoUpdate(BaseModel):
    id_materia_requerida: Optional[int] = None
    tipo: Optional[TipoPrerrequisito] = None


class MateriaPrerrequisitoResponse(MateriaPrerrequisitoBase):
    id_prerrequisito: int
    id_materia: int
    materia_requerida: MateriaSimple

    class Config:
        from_attributes = True
