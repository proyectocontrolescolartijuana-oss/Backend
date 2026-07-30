from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.carrera import (
    CarreraCreate,
    CarreraResponse,
    CarreraUpdate
)

from app.crud.crud_carrera import (
    get_carreras,
    get_carrera,
    create_carrera,
    update_carrera,
    delete_carrera
)

router = APIRouter(
    prefix="/carreras",
    tags=["Carreras"]
)

LOGOS_DIR = Path(__file__).resolve().parents[1] / "static" / "logos"
EXTENSIONES_LOGO_PERMITIDAS = {".png", ".jpg", ".jpeg", ".webp", ".svg"}


def _validar_archivo_logo(archivo: UploadFile):
    nombre_original = archivo.filename or ""
    extension = Path(nombre_original).suffix.lower()

    if extension not in EXTENSIONES_LOGO_PERMITIDAS:
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten imagenes PNG, JPG, WEBP o SVG"
        )

    if archivo.content_type and not archivo.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser una imagen"
        )

    return extension


@router.post("/logos")
def subir_logo_carrera(
    archivo: UploadFile = File(...)
):
    extension = _validar_archivo_logo(archivo)
    LOGOS_DIR.mkdir(parents=True, exist_ok=True)

    nombre_archivo = f"carrera_{uuid4().hex}{extension}"
    destino = (LOGOS_DIR / nombre_archivo).resolve()

    try:
        destino.relative_to(LOGOS_DIR.resolve())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Nombre de archivo invalido"
        )

    with destino.open("wb") as salida:
        salida.write(archivo.file.read())

    return {
        "logo": nombre_archivo,
        "url": f"http://localhost:8000/static/logos/{nombre_archivo}"
    }

@router.get(
    "/",
    response_model=list[CarreraResponse]
)
def listar_carreras(
    db: Session = Depends(get_db)
):
    return get_carreras(db)

@router.get(
    "/{carrera_id}",
    response_model=CarreraResponse
)
def obtener_carrera(
    carrera_id: int,
    db: Session = Depends(get_db)
):
    carrera = get_carrera(db, carrera_id)

    if not carrera:
        raise HTTPException(
            status_code=404,
            detail="Carrera no encontrada"
        )

    return carrera

@router.post(
    "/",
    response_model=CarreraResponse
)
def crear_carrera(
    carrera: CarreraCreate,
    db: Session = Depends(get_db)
):
    return create_carrera(db, carrera)

@router.patch(
    "/{carrera_id}",
    response_model=CarreraResponse
)
def actualizar_carrera(
    carrera_id: int,
    carrera: CarreraUpdate,
    db: Session = Depends(get_db)
):
    carrera_actualizada = update_carrera(
        db,
        carrera_id,
        carrera
    )

    if not carrera_actualizada:
        raise HTTPException(
            status_code=404,
            detail="Carrera no encontrada"
        )

    return carrera_actualizada

@router.delete(
    "/{carrera_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_carrera(
    carrera_id: int,
    db: Session = Depends(get_db)
):
    try:
        eliminada = delete_carrera(db, carrera_id)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    if not eliminada:
        raise HTTPException(
            status_code=404,
            detail="Carrera no encontrada"
        )
