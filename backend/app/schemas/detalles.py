from datetime import date
from typing import Optional 

from pydantic import BaseModel, field_validator


class UsuarioNombre(BaseModel):
    id_usuario: int
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    correo: Optional[str] = None


class AlumnoDetalle(BaseModel):
    id_alumno: int
    matricula: Optional[str] = None
    numero_control: Optional[str] = None
    nombre: Optional[str] = None


class DocenteDetalle(BaseModel):
    id_docente: int
    numero_empleado: Optional[str] = None
    nombre: Optional[str] = None


class MateriaDetalle(BaseModel):
    id_materia: int
    clave: Optional[str] = None
    nombre: Optional[str] = None
    creditos: Optional[float] = None


class CuatrimestreDetalle(BaseModel):
    id_cuatrimestre: int
    numero: Optional[int] = None
    nombre: Optional[str] = None


class GrupoDetalle(BaseModel):
    id_grupo: int
    nombre: Optional[str] = None
    turno: Optional[str] = None
    id_carrera: Optional[int] = None
    id_plan: Optional[int] = None
    estatus: Optional[str] = None
    cuatrimestre: Optional[CuatrimestreDetalle] = None


class PeriodoDetalle(BaseModel):
    id_periodo: int
    nombre: Optional[str] = None
    estado: Optional[str] = None


class CarreraDetalle(BaseModel):
    id_carrera: int
    clave: Optional[str] = None
    rvoe: Optional[str] = None
    nombre: Optional[str] = None
    logo: Optional[str] = None
    
    @field_validator("logo")
    @classmethod
    def construir_url_logo(cls, valor: Optional[str]) -> Optional[str]:
        if not valor:
            return None
        return f"http://localhost:8000/static/logos/{valor}"


class EmpresaDetalle(BaseModel):
    id_empresa: int
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None


class TutorDetalle(BaseModel):
    id_tutor: int
    nombre: str
    parentesco: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None


class RolDetalle(BaseModel):
    id_rol: int
    nombre: str


class TipoDocumentoDetalle(BaseModel):
    id_tipo_documento: int
    nombre: Optional[str] = None


class GrupoMateriaDetalleResponse(BaseModel):
    id_grupo_materia: int
    aula: Optional[str] = None
    cupo_maximo: Optional[int] = None
    grupo: Optional[GrupoDetalle] = None
    materia: Optional[MateriaDetalle] = None
    docente: Optional[DocenteDetalle] = None
    periodo: Optional[PeriodoDetalle] = None


class CargaAcademicaDetalleResponse(BaseModel):
    id_carga: int
    oportunidad: Optional[str] = None
    intento: Optional[int] = None
    estatus: Optional[str] = None
    fecha_inscripcion: Optional[date] = None
    alumno: Optional[AlumnoDetalle] = None
    grupo_materia: Optional[GrupoMateriaDetalleResponse] = None


class AsistenciaDetalleResponse(BaseModel):
    id_asistencia: int
    fecha: Optional[date] = None
    asistencia: Optional[bool] = None
    alumno: Optional[AlumnoDetalle] = None
    materia: Optional[MateriaDetalle] = None
    grupo: Optional[GrupoDetalle] = None
    periodo: Optional[PeriodoDetalle] = None


class InscripcionDetalleResponse(BaseModel):
    id_inscripcion: int
    fecha_inscripcion: Optional[date] = None
    estado: Optional[str] = None
    alumno: Optional[AlumnoDetalle] = None
    grupo: Optional[GrupoDetalle] = None
    carrera: Optional[CarreraDetalle] = None
    cuatrimestre: Optional[CuatrimestreDetalle] = None
    periodo: Optional[PeriodoDetalle] = None


class HistorialAcademicoDetalleResponse(BaseModel):
    id_historial: int
    tipo_evaluacion: Optional[str] = None
    oportunidad: Optional[int] = None
    calificacion_final: Optional[float] = None
    resultado: Optional[str] = None
    fecha_cierre: Optional[date] = None
    alumno: Optional[AlumnoDetalle] = None
    carrera: Optional[CarreraDetalle] = None
    materia: Optional[MateriaDetalle] = None
    periodo: Optional[PeriodoDetalle] = None



class ParcialDetalle(BaseModel):
    id_parcial: int
    nombre: Optional[str] = None
    porcentaje: Optional[float] = None


class CalificacionDetalleResponse(BaseModel):
    id_calificacion: int
    calificacion: Optional[float] = None
    alumno: Optional[AlumnoDetalle] = None
    materia: Optional[MateriaDetalle] = None
    grupo: Optional[GrupoDetalle] = None
    periodo: Optional[PeriodoDetalle] = None
    parcial: Optional[ParcialDetalle] = None
    capturado_por: Optional[UsuarioNombre] = None


class DocumentoAlumnoDetalleResponse(BaseModel):
    id_documento: int
    nombre_archivo: Optional[str] = None
    ruta_archivo: Optional[str] = None
    validado: Optional[bool] = None
    observaciones: Optional[str] = None
    alumno: Optional[AlumnoDetalle] = None
    tipo_documento: Optional[TipoDocumentoDetalle] = None


class RecepcionDocumentoDetalleResponse(BaseModel):
    id_recepcion: int
    fecha_recepcion: Optional[date] = None
    ficha_inscripcion: Optional[bool] = None
    acta_original: Optional[bool] = None
    acta_copias: Optional[bool] = None
    certificado_original: Optional[bool] = None
    constancia_terminacion: Optional[bool] = None
    fotografias: Optional[bool] = None
    curp_documento: Optional[bool] = None
    observaciones: Optional[str] = None
    alumno: Optional[AlumnoDetalle] = None
    recibido_por: Optional[UsuarioNombre] = None


class ContactoEmergenciaDetalleResponse(BaseModel):
    id_contacto: int
    nombre: str
    parentesco: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None
    contacto_principal: Optional[bool] = None
    alumno: Optional[AlumnoDetalle] = None


class SeguroMedicoDetalleResponse(BaseModel):
    id_seguro: int
    tiene_seguro: Optional[bool] = None
    institucion: Optional[str] = None
    numero_poliza: Optional[str] = None
    alumno: Optional[AlumnoDetalle] = None


class ProcedenciaAcademicaDetalleResponse(BaseModel):
    id_procedencia: int
    escuela_procedencia: Optional[str] = None
    nivel_academico: Optional[str] = None
    estado_procedencia: Optional[str] = None
    promedio_general: Optional[float] = None
    fecha_egreso: Optional[date] = None
    alumno: Optional[AlumnoDetalle] = None


class ServicioSocialDetalleResponse(BaseModel):
    id_servicio: int
    horas_requeridas: Optional[int] = None
    horas_completadas: Optional[int] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: Optional[str] = None
    carta_unifront: bool = False
    carta_procedencia: bool = False
    alumno: Optional[AlumnoDetalle] = None
    empresa: Optional[EmpresaDetalle] = None


class PracticaProfesionalDetalleResponse(BaseModel):
    id_practica: int
    proyecto: Optional[str] = None
    asesor_empresa: Optional[str] = None
    asesor_universidad: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: Optional[str] = None
    oficio_campo: bool = False
    horas_campo: Optional[int] = None
    alumno: Optional[AlumnoDetalle] = None
    empresa: Optional[EmpresaDetalle] = None


class AlumnoTutorDetalleResponse(BaseModel):
    alumno: AlumnoDetalle
    tutor: TutorDetalle


class UsuarioRolDetalleResponse(BaseModel):
    usuario: UsuarioNombre
    rol: RolDetalle


class AlumnoRelacionadoResponse(BaseModel):
    alumno: AlumnoDetalle


class TutorRelacionadoResponse(BaseModel):
    tutor: TutorDetalle
