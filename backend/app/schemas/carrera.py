from pydantic import BaseModel, field_validator
from typing import Optional

class CarreraBase(BaseModel):
    clave: str
    rvoe: Optional[str] = None
    nombre: str
    nivel: str
    duracion_cuatrimestres: int
    logo: Optional[str] = None

class CarreraCreate(CarreraBase):
    pass

class CarreraUpdate(BaseModel):
    clave: Optional[str] = None
    rvoe: Optional[str] = None
    nombre: Optional[str] = None
    nivel: Optional[str] = None
    duracion_cuatrimestres: Optional[int] = None
    estado: Optional[bool] = None
    logo: Optional[str] = None

class CarreraResponse(CarreraBase):
    id_carrera: int
    estado: bool
    
    @field_validator("logo")
    @classmethod
    def construir_url_logo(cls, valor: Optional[str]) -> Optional[str]:
        if not valor:
            return None
        return f"http://localhost:8000/static/logos/{valor}"

    class Config:
        from_attributes = True

class CarreraSimple(BaseModel):
    id_carrera: int
    clave: Optional[str] = None
    rvoe: Optional[str] = None
    nombre: str
    logo: Optional[str] = None

    class Config:
        from_attributes = True
