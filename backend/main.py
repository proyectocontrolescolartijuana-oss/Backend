from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware

from app.models import init as _models_init

from app.routers import (
    alumnos_tutores,
    asistencias,
    usuarios,
    usuarios_roles,
    carreras,
    cargas_academicas,
    alumnos,
    contactos_emergencia,
    cuatrimestres,
    docentes,
    documentos_alumno,
    empresas,
    extraordinarios,
    grupos,
    grupos_materias,
    historiales_academicos,
    inscripciones,
    materias,
    periodos,
    parciales,
    practicas_profesionales,
    procedencias_academicas,
    recepciones_documento,
    calificaciones,
    seguros_medicos,
    servicios_sociales,
    tipos_documento,
    titulaciones,
    tutores,
    roles,
    auth,
    documentos,
    plan_estudio,
    reportes,
    kardex,
)


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Unifront API",
    version="1.0.0"
)

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "app" / "static")),
    name="static"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

@app.get("/")
def root():
    return {"message": "API funcionando"}

# ROUTERS

app.include_router(usuarios.router)
app.include_router(usuarios_roles.router)
app.include_router(carreras.router)
app.include_router(alumnos.router)
app.include_router(alumnos_tutores.router)
app.include_router(asistencias.router)
app.include_router(cargas_academicas.router)
app.include_router(contactos_emergencia.router)
app.include_router(cuatrimestres.router)
app.include_router(docentes.router)
app.include_router(documentos_alumno.router)
app.include_router(empresas.router)
app.include_router(extraordinarios.router)
app.include_router(grupos.router)
app.include_router(grupos_materias.router)
app.include_router(historiales_academicos.router)
app.include_router(inscripciones.router)
app.include_router(materias.router)
app.include_router(periodos.router)
app.include_router(parciales.router)
app.include_router(practicas_profesionales.router)
app.include_router(procedencias_academicas.router)
app.include_router(recepciones_documento.router)
app.include_router(calificaciones.router)
app.include_router(seguros_medicos.router)
app.include_router(servicios_sociales.router)
app.include_router(tipos_documento.router)
app.include_router(titulaciones.router)
app.include_router(tutores.router)
# app.include_router(roles.router)
app.include_router(auth.router)
app.include_router(documentos.router)
app.include_router(plan_estudio.router)
app.include_router(reportes.router)
app.include_router(kardex.router)