from pydantic import BaseModel, field_validator
from typing import Literal, Optional
from datetime import date

from app.utils.logo_url import construir_url_logo

Modalidad = Literal["CUATRIMESTRAL", "SABATINA"]

class CarreraBase(BaseModel):
    clave: str
    rvoe: Optional[str] = None
    nombre: str
    nivel: str
    modalidad: Modalidad = "CUATRIMESTRAL"
    duracion_cuatrimestres: int
    fecha_autorizacion: Optional[date] = None
    logo: Optional[str] = None

class CarreraCreate(CarreraBase):
    fecha_autorizacion: date

class CarreraUpdate(BaseModel):
    clave: Optional[str] = None
    rvoe: Optional[str] = None
    nombre: Optional[str] = None
    nivel: Optional[str] = None
    modalidad: Optional[Modalidad] = None
    duracion_cuatrimestres: Optional[int] = None
    fecha_autorizacion: Optional[date] = None
    estado: Optional[bool] = None
    logo: Optional[str] = None

    @field_validator("modalidad")
    @classmethod
    def modalidad_no_nula(cls, valor: Optional[str]) -> Optional[str]:
        # La columna es NOT NULL: si se manda, no puede ser null.
        if valor is None:
            raise ValueError("La modalidad no puede ser nula")

        return valor

class CarreraResponse(CarreraBase):
    id_carrera: int
    estado: bool
    
    @field_validator("logo")
    @classmethod
    def construir_url_logo_carrera(cls, valor: Optional[str]) -> Optional[str]:
        return construir_url_logo(valor)

    class Config:
        from_attributes = True

class CarreraSimple(BaseModel):
    id_carrera: int
    clave: Optional[str] = None
    rvoe: Optional[str] = None
    nombre: str
    modalidad: Optional[Modalidad] = None
    fecha_autorizacion: Optional[date] = None
    logo: Optional[str] = None

    @field_validator("logo")
    @classmethod
    def construir_url_logo_carrera(cls, valor: Optional[str]) -> Optional[str]:
        return construir_url_logo(valor)

    class Config:
        from_attributes = True