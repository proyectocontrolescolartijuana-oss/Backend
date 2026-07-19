from typing import Optional

from pydantic import BaseModel


class ConstanciaEditable(BaseModel):
    alumno_id: Optional[int] = None
    sexo: Optional[str] = "M"
    nombre_completo: str
    matricula: Optional[str] = None
    numero_control: Optional[str] = None
    carrera: str
    plan: Optional[str] = None
    cuatrimestre: Optional[str] = None
    grupo: Optional[str] = None
    horario: str
    periodo_vacacional: str
    fecha_emision: str
    director: str
    cargo_director: str


class ConstanciaContextoResponse(ConstanciaEditable):
    departamento: str
    asunto: str
