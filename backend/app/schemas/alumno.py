from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date

from app.utils.logo_url import construir_url_logo

class AlumnoBase(BaseModel):
    matricula: Optional[str] = None
    numero_control: Optional[str] = None
    id_usuario: int
    id_carrera: int
    id_plan: int
    fecha_nacimiento: Optional[date] = None
    ciudad_nacimiento: Optional[str] = None
    municipio_nacimiento: Optional[str] = None
    nacionalidad: Optional[str] = None
    sexo: Optional[str] = None
    curp: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    estado: Optional[str] = None
    correo_contacto: Optional[str] = None
    fecha_ingreso: Optional[date] = None
    foto: Optional[str] = None

class AlumnoCreate(AlumnoBase):
    id_grupo: Optional[int] = None
    id_periodo: Optional[int] = None

class AlumnoResponse(AlumnoBase):
    id_alumno: int
    estatus: str

    class Config:
        from_attributes = True


class AlumnoCarreraDetalle(BaseModel):
    id_carrera: int
    clave: Optional[str] = None
    rvoe: Optional[str] = None
    nombre: Optional[str] = None
    logo: Optional[str] = None

    @field_validator("logo")
    @classmethod
    def construir_url_logo_carrera(cls, valor: Optional[str]) -> Optional[str]:
        return construir_url_logo(valor)
    


class AlumnoPlanDetalle(BaseModel):
    id_plan: int
    nombre_plan: Optional[str] = None


class AlumnoGrupoDetalle(BaseModel):
    id_grupo: int
    nombre: Optional[str] = None
    turno: Optional[str] = None
    id_carrera: Optional[int] = None
    estatus: Optional[str] = None


class AlumnoDetalleResponse(BaseModel):
    id_alumno: int
    matricula: Optional[str] = None
    numero_control: Optional[str] = None
    id_usuario: Optional[int] = None
    nombre: Optional[str] = None
    nombres: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    estatus: Optional[str] = None
    id_carrera: Optional[int] = None
    id_plan: Optional[int] = None
    fecha_nacimiento: Optional[date] = None
    ciudad_nacimiento: Optional[str] = None
    municipio_nacimiento: Optional[str] = None
    nacionalidad: Optional[str] = None
    sexo: Optional[str] = None
    curp: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    estado: Optional[str] = None
    correo_contacto: Optional[str] = None
    fecha_ingreso: Optional[date] = None
    foto: Optional[str] = None
    carrera: Optional[AlumnoCarreraDetalle] = None
    plan: Optional[AlumnoPlanDetalle] = None
    grupo: Optional[AlumnoGrupoDetalle] = None

    class Config:
        from_attributes = True

class AlumnoUpdate(BaseModel):
    matricula: Optional[str] = None
    numero_control: Optional[str] = None
    id_usuario: Optional[int] = None
    id_carrera: Optional[int] = None
    id_plan: Optional[int] = None
    fecha_nacimiento: Optional[date] = None
    ciudad_nacimiento: Optional[str] = None
    municipio_nacimiento: Optional[str] = None
    nacionalidad: Optional[str] = None
    sexo: Optional[str] = None
    curp: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    estado: Optional[str] = None
    correo_contacto: Optional[str] = None
    fecha_ingreso: Optional[date] = None
    estatus: Optional[str] = None
    foto: Optional[str] = None

    class Config:
        from_attributes = True
