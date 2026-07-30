from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

from app.utils.logo_url import construir_url_logo


class KardexMateria(BaseModel):
    clave: str = ""
    asignatura: str = ""
    creditos: float = 0
    calificacion_final: float = 0
    tipo_acreditacion: str = "OR"


class KardexCuatrimestre(BaseModel):
    cuatrimestre: int = 0
    periodo_escolar: str = ""
    grupo: str = ""
    materias: List[KardexMateria] = Field(default_factory=list)

class KardexResponse(BaseModel):
    matricula: str = ""
    numero_control: str = ""
    curp: str = ""
    primer_apellido: str = ""
    segundo_apellido: str = ""
    nombre: str = ""
    carrera: str = ""
    rvoe: str = ""
    logo: Optional[str] = None
    plan_estudios: str = ""
    historial: List[KardexCuatrimestre] = Field(default_factory=list)
    
    @field_validator("logo")
    @classmethod
    def construir_url_logo_carrera(cls, valor: Optional[str]) -> Optional[str]:
        return construir_url_logo(valor)
    
    


class KardexAlumnoBusqueda(BaseModel):
    id_alumno: int
    matricula: str = ""
    numero_control: str = ""
    nombre: str = ""
    carrera: str = ""
