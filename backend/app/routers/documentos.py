from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud.crud_alumno import get_alumno
from app.schemas.documento import ConstanciaContextoResponse, ConstanciaEditable
from app.services.document_service import (
    generar_constancia,
    obtener_contexto_constancia,
    renderizar_constancia_alumno_html,
    renderizar_constancia_html
)

router = APIRouter(
    prefix="/documentos",
    tags=["Documentos"]
)

@router.get("/constancia/{alumno_id}")
def generar_pdf(
    alumno_id: int,
    db: Session = Depends(get_db)
):

    alumno = get_alumno(db, alumno_id)

    if not alumno:
        raise HTTPException(
            status_code=404,
            detail="Alumno no encontrado"
        )

    ruta = generar_constancia(alumno)

    return FileResponse(
        path=ruta,
        media_type="application/pdf",
        filename="constancia.pdf"
    )


@router.get(
    "/constancia/{alumno_id}/contexto",
    response_model=ConstanciaContextoResponse
)
def obtener_contexto_constancia_endpoint(
    alumno_id: int,
    db: Session = Depends(get_db)
):
    alumno = get_alumno(db, alumno_id)

    if not alumno:
        raise HTTPException(
            status_code=404,
            detail="Alumno no encontrado"
        )

    return obtener_contexto_constancia(alumno)


@router.get(
    "/constancia/{alumno_id}/html",
    response_class=HTMLResponse
)
def previsualizar_constancia_alumno(
    alumno_id: int,
    db: Session = Depends(get_db)
):
    alumno = get_alumno(db, alumno_id)

    if not alumno:
        raise HTTPException(
            status_code=404,
            detail="Alumno no encontrado"
        )

    return renderizar_constancia_alumno_html(alumno)


@router.post(
    "/constancia/preview",
    response_class=HTMLResponse
)
def previsualizar_constancia_editada(
    datos: ConstanciaEditable
):
    return renderizar_constancia_html(datos.model_dump())
