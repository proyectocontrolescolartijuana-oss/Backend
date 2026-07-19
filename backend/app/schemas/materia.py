from pydantic import BaseModel
from typing import Optional

class MateriaBase(BaseModel):
    clave: str
    nombre: str
    creditos: float

class MateriaCreate(MateriaBase):
    pass

class MateriaUpdate(BaseModel):
    clave: Optional[str] = None
    nombre: Optional[str] = None
    creditos: Optional[float] = None
    estado: Optional[bool] = None

class MateriaResponse(MateriaBase):
    id_materia: int
    estado: bool

    class Config:
        from_attributes = True

class MateriaSimple(BaseModel):
    id_materia: int
    clave: str | None = None
    nombre: str
    creditos: float

    class Config:
        from_attributes = True