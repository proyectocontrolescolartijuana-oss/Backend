from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.crud.crud_titulacion import (
    create_titulacion,
    delete_titulacion,
    get_titulacion,
    get_titulaciones,
    update_titulacion,
)
from app.database import get_db
from app.models.documento_titulacion import DocumentoTitulacion
from app.schemas.documento_titulacion import DocumentoTitulacionResponse
from app.schemas.titulacion import (
    TitulacionCreate,
    TitulacionResponse,
    TitulacionUpdate,
)
from app.services.blob_service import (
    BlobStorageError,
    delete_blob,
    download_blob,
    upload_blob,
)


router = APIRouter(
    prefix="/titulaciones",
    tags=["Titulacion"],
)

EXTENSIONES_PERMITIDAS = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}
BLOB_OBJECT_PREFIX = "titulaciones"
REQUISITOS_BOOLEANOS = {
    "servicio_social_liberado",
    "practicas_liberadas",
    "certificado_emitido",
    "pagos_titulacion_completos",
    "titulo_emitido",
}
REQUISITOS_TEXTO = {
    "numero_autorizacion",
    "acta_examen",
}
REQUISITOS_PERMITIDOS = REQUISITOS_BOOLEANOS | REQUISITOS_TEXTO


def _build_blob_key(id_titulacion: int, requisito: str, extension: str) -> str:
    return (
        f"{BLOB_OBJECT_PREFIX}/{id_titulacion}/{requisito}/"
        f"{uuid4().hex}{extension}"
    )


def _build_download_route(documento_id: int) -> str:
    return f"/titulaciones/documentos/{documento_id}/download"


def _map_documento(documento: DocumentoTitulacion) -> dict:
    return {
        "id_documento_titulacion": documento.id_documento_titulacion,
        "id_titulacion": documento.id_titulacion,
        "requisito": documento.requisito,
        "nombre_archivo": documento.nombre_archivo,
        "ruta_archivo": _build_download_route(documento.id_documento_titulacion),
        "observaciones": documento.observaciones,
        "fecha_subida": documento.fecha_subida,
    }


def _aplicar_requisito_titulacion(
    titulacion,
    requisito: str,
    entregado: bool,
    nombre_archivo: Optional[str] = None,
):
    if requisito in REQUISITOS_BOOLEANOS:
        setattr(titulacion, requisito, entregado)
        return

    if requisito in REQUISITOS_TEXTO:
        setattr(titulacion, requisito, nombre_archivo if entregado else "")


def _obtener_documento(db: Session, documento_id: int) -> DocumentoTitulacion:
    documento = (
        db.query(DocumentoTitulacion)
        .filter(DocumentoTitulacion.id_documento_titulacion == documento_id)
        .first()
    )

    if not documento:
        raise HTTPException(
            status_code=404,
            detail="Documento de titulación no encontrado",
        )

    return documento


@router.get(
    "/",
    response_model=list[TitulacionResponse],
)
def listar_titulaciones(db: Session = Depends(get_db)):
    return get_titulaciones(db)


@router.get(
    "/documentos",
    response_model=list[DocumentoTitulacionResponse],
)
def listar_documentos_titulacion(
    titulacion_id: Optional[int] = None,
    requisito: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(DocumentoTitulacion)

    if titulacion_id is not None:
        query = query.filter(DocumentoTitulacion.id_titulacion == titulacion_id)

    if requisito:
        query = query.filter(DocumentoTitulacion.requisito == requisito)

    documentos = query.order_by(
        DocumentoTitulacion.fecha_subida.desc(),
        DocumentoTitulacion.id_documento_titulacion.desc(),
    ).all()

    return [_map_documento(documento) for documento in documentos]


@router.get("/documentos/{documento_id}/download")
def descargar_documento_titulacion(
    documento_id: int,
    db: Session = Depends(get_db),
):
    documento = _obtener_documento(db, documento_id)

    try:
        content, content_type = download_blob(documento.ruta_archivo)
    except BlobStorageError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    headers = {
        "Content-Disposition": f'inline; filename="{documento.nombre_archivo}"'
    }

    return Response(
        content,
        media_type=content_type or "application/octet-stream",
        headers=headers,
    )


@router.get(
    "/{titulacion_id}",
    response_model=TitulacionResponse,
)
def obtener_titulacion(
    titulacion_id: int,
    db: Session = Depends(get_db),
):
    titulacion = get_titulacion(db, titulacion_id)

    if not titulacion:
        raise HTTPException(
            status_code=404,
            detail="Titulación no encontrada",
        )

    return titulacion


@router.post(
    "/",
    response_model=TitulacionResponse,
)
def crear_titulacion(
    titulacion: TitulacionCreate,
    db: Session = Depends(get_db),
):
    return create_titulacion(db, titulacion)


@router.post(
    "/{titulacion_id}/documentos/upload",
    response_model=DocumentoTitulacionResponse,
)
def subir_documento_titulacion(
    titulacion_id: int,
    requisito: str = Form(...),
    observaciones: Optional[str] = Form(None),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if requisito not in REQUISITOS_PERMITIDOS:
        raise HTTPException(
            status_code=400,
            detail="Requisito de titulación no válido",
        )

    titulacion = get_titulacion(db, titulacion_id)

    if not titulacion:
        raise HTTPException(
            status_code=404,
            detail="Titulación no encontrada",
        )

    nombre_original = archivo.filename or "documento"
    extension = Path(nombre_original).suffix.lower()

    if extension not in EXTENSIONES_PERMITIDAS:
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten archivos PDF o imágenes",
        )

    documento_anterior = (
        db.query(DocumentoTitulacion)
        .filter(
            DocumentoTitulacion.id_titulacion == titulacion_id,
            DocumentoTitulacion.requisito == requisito,
        )
        .order_by(DocumentoTitulacion.id_documento_titulacion.desc())
        .first()
    )
    object_key = _build_blob_key(titulacion_id, requisito, extension)

    try:
        upload_blob(
            object_key,
            archivo.file.read(),
            archivo.content_type,
        )
    except BlobStorageError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    nuevo_documento = DocumentoTitulacion(
        id_titulacion=titulacion_id,
        requisito=requisito,
        nombre_archivo=nombre_original,
        ruta_archivo=object_key,
        observaciones=observaciones,
    )

    db.add(nuevo_documento)
    _aplicar_requisito_titulacion(
        titulacion,
        requisito,
        True,
        nombre_original,
    )

    if documento_anterior:
        try:
            delete_blob(documento_anterior.ruta_archivo)
        except BlobStorageError:
            pass
        db.delete(documento_anterior)

    db.commit()
    db.refresh(nuevo_documento)

    return _map_documento(nuevo_documento)


@router.patch(
    "/{titulacion_id}",
    response_model=TitulacionResponse,
)
def actualizar_titulacion(
    titulacion_id: int,
    titulacion: TitulacionUpdate,
    db: Session = Depends(get_db),
):
    titulacion_actualizada = update_titulacion(
        db,
        titulacion_id,
        titulacion,
    )

    if not titulacion_actualizada:
        raise HTTPException(
            status_code=404,
            detail="Titulación no encontrada",
        )

    return titulacion_actualizada


@router.delete(
    "/documentos/{documento_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_documento_titulacion(
    documento_id: int,
    db: Session = Depends(get_db),
):
    documento = _obtener_documento(db, documento_id)
    titulacion = documento.titulacion
    requisito = documento.requisito

    try:
        delete_blob(documento.ruta_archivo)
    except BlobStorageError:
        pass

    db.delete(documento)
    _aplicar_requisito_titulacion(titulacion, requisito, False)
    db.commit()


@router.delete(
    "/{titulacion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_titulacion(
    titulacion_id: int,
    db: Session = Depends(get_db),
):
    titulacion = get_titulacion(db, titulacion_id)

    if not titulacion:
        raise HTTPException(
            status_code=404,
            detail="Titulación no encontrada",
        )

    for documento in titulacion.documentos:
        try:
            delete_blob(documento.ruta_archivo)
        except BlobStorageError:
            pass

    eliminada = delete_titulacion(db, titulacion_id)

    if not eliminada:
        raise HTTPException(
            status_code=404,
            detail="Titulación no encontrada",
        )
