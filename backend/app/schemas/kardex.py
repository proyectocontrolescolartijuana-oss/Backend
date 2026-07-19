from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class KardexMateria(BaseModel):
    clave: str = ""
    asignatura: str = ""
    creditos: float = 0
    calificacion_final: float = 0


class KardexCuatrimestre(BaseModel):
    cuatrimestre: int = 0
    periodo_escolar: str = ""
    grupo: str = ""
    materias: List[KardexMateria] = Field(default_factory=list)

class KardexResponse(BaseModel):
    matricula: str = ""
    primer_apellido: str = ""
    segundo_apellido: str = ""
    nombre: str = ""
    carrera: str = ""
    logo: Optional[str] = None
    plan_estudios: str = ""
    historial: List[KardexCuatrimestre] = Field(default_factory=list)
    
    @field_validator("logo")
    @classmethod
    def contruir_url_logo(cls, valor: Optional[str]) -> Optional[str]:
        if not valor:
            return None
        return f"http://localhost:8000/static/logos/{valor}"
    
    


class KardexAlumnoBusqueda(BaseModel):
    id_alumno: int
    matricula: str = ""
    nombre: str = ""
    carrera: str = ""
