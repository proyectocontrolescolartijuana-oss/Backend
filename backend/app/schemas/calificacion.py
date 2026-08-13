from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional

from app.schemas.detalles import (
    AlumnoDetalle,
    GrupoMateriaDetalleResponse,
    ParcialDetalle,
    PeriodoDetalle
)
from app.utils.logo_url import construir_url_logo

class CalificacionBase(BaseModel):
    id_carga: int
    id_parcial: int
    calificacion: float
    capturado_por: int

class CalificacionCreate(CalificacionBase):
    pass

class CalificacionUpdate(BaseModel):
    id_carga: Optional[int] = None
    id_parcial: Optional[int] = None
    calificacion: Optional[float] = None
    capturado_por: Optional[int] = None

class CalificacionResponse(CalificacionBase):
    id_calificacion: int
    fecha_captura: datetime

    class Config:
        from_attributes = True


class CapturaCalificacionItem(BaseModel):
    id_carga: int
    id_parcial: int
    calificacion: Optional[float] = Field(default=None, ge=0, le=100)


class CapturaCalificacionesBatch(BaseModel):
    grupo_materia_id: int
    calificaciones: list[CapturaCalificacionItem]


class CapturaAlumnoCalificacionResponse(BaseModel):
    id_calificacion: Optional[int] = None
    id_carga: int
    id_parcial: int
    calificacion: Optional[float] = None


class CapturaAlumnoResponse(BaseModel):
    id_carga: int
    estatus: Optional[str] = None
    alumno: Optional[AlumnoDetalle] = None
    calificaciones: list[CapturaAlumnoCalificacionResponse] = Field(
        default_factory=list
    )


class CapturaCalificacionesResponse(BaseModel):
    grupo_materia: GrupoMateriaDetalleResponse
    parciales: list[ParcialDetalle]
    alumnos: list[CapturaAlumnoResponse]


class MonitoreoCalificacionItemResponse(BaseModel):
    id_calificacion: Optional[int] = None
    id_carga: int
    id_parcial: int
    calificacion: Optional[float] = None


class MonitoreoAlumnoResponse(BaseModel):
    id_carga: int
    estatus: Optional[str] = None
    alumno: Optional[AlumnoDetalle] = None
    calificaciones: list[MonitoreoCalificacionItemResponse] = Field(
        default_factory=list
    )
    capturadas: int = 0
    pendientes: int = 0


class MonitoreoGrupoMateriaResponse(BaseModel):
    grupo_materia: GrupoMateriaDetalleResponse
    alumnos: list[MonitoreoAlumnoResponse] = Field(default_factory=list)
    total_alumnos: int = 0
    total_calificaciones: int = 0
    capturadas: int = 0
    pendientes: int = 0
    completo: bool = False


class MonitoreoPeriodoResponse(BaseModel):
    periodo: Optional[PeriodoDetalle] = None
    parciales: list[ParcialDetalle] = Field(default_factory=list)
    grupos_materia: list[MonitoreoGrupoMateriaResponse] = Field(
        default_factory=list
    )
    total_grupos_materia: int = 0
    total_alumnos: int = 0
    total_calificaciones: int = 0
    capturadas: int = 0
    pendientes: int = 0


class BoletaAlumnoResponse(BaseModel):
    id_alumno: int
    matricula: Optional[str] = None
    numero_control: Optional[str] = None
    nombre: Optional[str] = None


class BoletaCarreraResponse(BaseModel):
    id_carrera: Optional[int] = None
    clave: Optional[str] = None
    rvoe: Optional[str] = None
    nombre: Optional[str] = None
    logo: Optional[str] = None
    
    @field_validator("logo")
    @classmethod
    def construir_url_logo_carrera(cls, valor: Optional[str]) -> Optional[str]:
        return construir_url_logo(valor)


class BoletaPeriodoResponse(BaseModel):
    id_periodo: Optional[int] = None
    nombre: Optional[str] = None


class BoletaCuatrimestreResponse(BaseModel):
    numero: Optional[int] = None
    nombre: Optional[str] = None


class BoletaMateriaResponse(BaseModel):
    id_materia: Optional[int] = None
    nombre: Optional[str] = None
    clave: Optional[str] = None
    calificacion_final: Optional[float] = None


class BoletaFinalResponse(BaseModel):
    alumno: BoletaAlumnoResponse
    carrera: Optional[BoletaCarreraResponse] = None
    periodo: Optional[BoletaPeriodoResponse] = None
    cuatrimestre: Optional[BoletaCuatrimestreResponse] = None
    materias: list[BoletaMateriaResponse] = Field(default_factory=list)
    promedio_general: Optional[float] = None
    asignaturas_acreditadas: int = 0


class CuadroHonorAlumnoResponse(BaseModel):
    id_alumno: int
    matricula: Optional[str] = None
    numero_control: Optional[str] = None
    nombre: Optional[str] = None
    carrera: Optional[str] = None
    grupo: Optional[str] = None
    cuatrimestre: Optional[int] = None
    generacion: Optional[str] = None
    promedio: float
    materias: int
    cuatrimestres_evaluados: Optional[int] = None
    estatus: Optional[str] = None


class CuadroHonorResponse(BaseModel):
    tipo: str
    cuatrimestre: Optional[int] = None
    alumnos: list[CuadroHonorAlumnoResponse] = Field(default_factory=list)
