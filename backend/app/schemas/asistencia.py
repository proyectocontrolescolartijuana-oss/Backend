from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.schemas.detalles import (
    AlumnoDetalle,
    GrupoMateriaDetalleResponse
)


class AsistenciaBase(BaseModel):
    id_carga: int
    id_parcial: Optional[int] = None
    fecha: date
    asistencia: bool
    retardo: bool = False

    @model_validator(mode="after")
    def retardo_requiere_asistencia(self):

        if not self.asistencia:
            self.retardo = False

        return self


class AsistenciaCreate(AsistenciaBase):
    pass


class AsistenciaUpdate(BaseModel):
    id_carga: Optional[int] = None
    id_parcial: Optional[int] = None
    fecha: Optional[date] = None
    asistencia: Optional[bool] = None
    retardo: Optional[bool] = None


class AsistenciaResponse(AsistenciaBase):
    id_asistencia: int

    class Config:
        from_attributes = True


class CapturaAsistenciaItem(BaseModel):
    id_carga: int
    fecha: Optional[date] = None
    asistencia: bool
    retardo: bool = False

    @model_validator(mode="after")
    def retardo_requiere_asistencia(self):
        if not self.asistencia:
            self.retardo = False

        return self


class CapturaAsistenciasBatch(BaseModel):
    grupo_materia_id: int
    id_parcial: int
    fecha: Optional[date] = None
    asistencias: list[CapturaAsistenciaItem] = Field(default_factory=list)


class CapturaAlumnoAsistenciaResponse(BaseModel):
    id_asistencia: Optional[int] = None
    id_carga: int
    fecha: date
    id_parcial: Optional[int] = None
    asistencia: bool = False
    retardo: bool = False


class CapturaParcialAsistenciaResponse(BaseModel):
    id_parcial: int
    nombre: Optional[str] = None
    porcentaje: Optional[float] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    fechas: list[date] = Field(default_factory=list)


class CapturaAlumnoAsistenciaResumen(BaseModel):
    id_carga: int
    estatus: Optional[str] = None
    alumno: Optional[AlumnoDetalle] = None
    asistencias: list[CapturaAlumnoAsistenciaResponse] = Field(
        default_factory=list
    )
    total_asistencias: int = 0
    total_retardos: int = 0
    total_clases: int = 0
    porcentaje_asistencia: Optional[float] = None


class CapturaAsistenciasResumen(BaseModel):
    total_alumnos: int = 0
    total_clases: int = 0
    alumnos_en_riesgo: int = 0


class CapturaAsistenciasResponse(BaseModel):
    grupo_materia: GrupoMateriaDetalleResponse
    parcial_seleccionado_id: Optional[int] = None
    fecha_seleccionada: Optional[date] = None
    retardos_por_falta: Optional[int] = None
    fechas: list[date] = Field(default_factory=list)
    parciales: list[CapturaParcialAsistenciaResponse] = Field(
        default_factory=list
    )
    resumen: CapturaAsistenciasResumen
    alumnos: list[CapturaAlumnoAsistenciaResumen] = Field(
        default_factory=list
    )