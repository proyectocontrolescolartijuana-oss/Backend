from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.blob_service import (
    BlobStorageError,
    download_blob,
    upload_blob
)

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

EXTENSIONES_LOGO_PERMITIDAS = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
BLOB_OBJECT_PREFIX = "logos-carreras"


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


def _build_blob_key(extension: str) -> str:
    return f"{BLOB_OBJECT_PREFIX}/{uuid4().hex}{extension}"


@router.post("/logos")
def subir_logo_carrera(
    archivo: UploadFile = File(...)
):
    extension = _validar_archivo_logo(archivo)
    object_key = _build_blob_key(extension)

    try:
        upload_blob(
            object_key,
            archivo.file.read(),
            archivo.content_type
        )
    except BlobStorageError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc

    return {
        "logo": object_key,
        "url": f"/carreras/logos/{object_key}"
    }


@router.get("/logos/{logo_path:path}")
def descargar_logo_carrera(logo_path: str):
    if not logo_path.startswith(f"{BLOB_OBJECT_PREFIX}/"):
        logo_path = f"{BLOB_OBJECT_PREFIX}/{Path(logo_path).name}"

    try:
        content, content_type = download_blob(logo_path)
    except BlobStorageError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc

    return Response(
        content,
        media_type=content_type or "application/octet-stream",
    )

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
