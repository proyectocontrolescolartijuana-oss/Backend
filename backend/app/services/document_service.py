from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from app.utils.document_context import construir_contexto_documento
from app.utils.gramatica import articulo_alumno, egresado, inscrito, interesado

APP_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = APP_DIR.parent
TEMPLATES_DIR = APP_DIR / "templates"
TMP_DIR = BACKEND_DIR / "tmp"

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR))
)


def obtener_contexto_constancia(alumno):
    contexto = construir_contexto_documento(alumno)
    documento = contexto["documento"]

    return {
        "alumno_id": alumno.id_alumno,
        "sexo": getattr(alumno, "sexo", "M"),
        "nombre_completo": contexto["nombre_completo"],
        "matricula": getattr(alumno, "matricula", None),
        "numero_control": getattr(alumno, "numero_control", None),
        "carrera": contexto["nombre_carrera"],
        "plan": contexto["nombre_plan"],
        "cuatrimestre": None,
        "grupo": None,
        "horario": documento["horario"],
        "periodo_vacacional": documento["periodo_vacacional"],
        "fecha_emision": datetime.now().strftime("%d/%m/%Y"),
        "director": documento["director"],
        "cargo_director": documento["cargo_director"],
        "departamento": documento["departamento"],
        "asunto": documento["asunto"]
    }


def _contexto_constancia_desde_datos(datos):
    sexo = (datos.get("sexo") or "M").upper()

    documento = {
        "departamento": datos.get("departamento") or "Control Escolar",
        "asunto": datos.get("asunto") or "Constancia de Estudios",
        "director": datos["director"],
        "cargo_director": datos["cargo_director"],
        "horario": datos["horario"],
        "periodo_vacacional": datos["periodo_vacacional"],
        "ciudad": "Tijuana",
        "estado": "Baja California",
        "campus": "Campus Tijuana",
        "telefono": "+52 (664) 660.1989",
        "correo": "contacto@unifront.mx",
        "direccion": "Blvd. O'Higgins # 6050 Zona Rio III Etapa",
        "sitio_web": "WWW.UNIFRONT.MX"
    }

    return {
        "alumno": {
            "id_alumno": datos.get("alumno_id"),
            "sexo": sexo,
            "matricula": datos.get("matricula"),
            "numero_control": datos.get("numero_control"),
            "nombre_completo": datos["nombre_completo"],
            "carrera": datos["carrera"]
        },
        "nombre_completo": datos["nombre_completo"],
        "nombre_carrera": datos["carrera"],
        "nombre_plan": datos.get("plan"),
        "documento": documento,
        "director": datos["director"],
        "cargo_director": datos["cargo_director"],
        "fecha": datos["fecha_emision"],
        "static_url": "/static",
        "txt": {
            "alumno": articulo_alumno(sexo),
            "inscrito": inscrito(sexo),
            "egresado": egresado(sexo),
            "interesado": interesado(sexo),
        }
    }


def renderizar_constancia_html(datos):
    template = env.get_template(
        "certificados/constancia_estudios.html"
    )

    return template.render(
        **_contexto_constancia_desde_datos(datos)
    )


def renderizar_constancia_alumno_html(alumno):
    contexto = obtener_contexto_constancia(alumno)

    return renderizar_constancia_html(contexto)


def generar_constancia(alumno):
    from weasyprint import HTML

    template = env.get_template(
        "certificados/constancia_estudios.html"
    )

    contexto = construir_contexto_documento(alumno)

    html = template.render(
        **contexto,
        fecha=datetime.now().strftime("%d/%m/%Y"),
        static_url="static"
    )

    TMP_DIR.mkdir(parents=True, exist_ok=True)

    output = TMP_DIR / f"constancia_{alumno.id_alumno}.pdf"

    HTML(
        string=html,
        base_url=str(APP_DIR)
    ).write_pdf(output)

    return str(output)
