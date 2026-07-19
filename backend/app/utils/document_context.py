from app.utils.gramatica import *


def construir_contexto_documento(alumno):
    usuario = getattr(alumno, "usuario", None)
    carrera = getattr(alumno, "carrera", None)
    plan = getattr(alumno, "plan", None)
    sexo = getattr(alumno, "sexo", "M")

    nombre_completo = getattr(alumno, "nombre_completo", None)

    if not nombre_completo and usuario:
        nombre_completo = " ".join(
            parte for parte in [
                getattr(usuario, "nombre", None),
                getattr(usuario, "apellido_paterno", None),
                getattr(usuario, "apellido_materno", None),
            ] if parte
        )

    return {
        "alumno": alumno,
        "nombre_completo": nombre_completo,
        "nombre_carrera": (
            getattr(carrera, "nombre", None)
            or getattr(alumno, "carrera", "")
        ),
        "nombre_plan": getattr(plan, "nombre_plan", None),
        "documento": {
            "departamento": "Control Escolar",
            "asunto": "Constancia de Estudios",
            "director": "ANGELICA QUIRIARTE FERNANDEZ",
            "cargo_director": "DIRECTORA DE LA LICENCIATURA",
            "horario": "3:00 a 8:20 p.m.",
            "periodo_vacacional": "20 de marzo al 03 de abril del 2026",
            "ciudad": "Tijuana",
            "estado": "Baja California",
            "campus": "Campus Tijuana",
            "telefono": "+52 (664) 660.1989",
            "correo": "contacto@unifront.mx",
            "direccion": "Blvd. O'Higgins # 6050 Zona Rio III Etapa",
            "sitio_web": "WWW.UNIFRONT.MX"
        },
        "txt": {
            "alumno": articulo_alumno(sexo),
            "inscrito": inscrito(sexo),
            "egresado": egresado(sexo),
            "interesado": interesado(sexo),
        }
    }
