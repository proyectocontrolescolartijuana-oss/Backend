from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import (
    BLOB_READ_WRITE_TOKEN,
    BLOB_STORE_ID,
    VERCEL_OIDC_TOKEN,
)
from app.core.security import get_current_user
from app.crud.crud_alumno import get_alumno
from app.crud.crud_detalles import get_documentos_alumno_detalle
from app.crud.crud_documento_alumno import (
    create_documento_alumno,
    delete_documento_alumno,
    get_documento_alumno,
    update_documento_alumno
)
from app.database import get_db
from app.models.alumno import Alumno
from app.models.usuario import Usuario
from app.schemas.detalles import DocumentoAlumnoDetalleResponse
from app.schemas.documento_alumno import DocumentoAlumnoCreate, DocumentoAlumnoUpdate
from app.services.blob_service import (
    BlobStorageError,
    delete_blob,
    download_blob,
    upload_blob
)


STATIC_DIR = Path(__file__).resolve().parents[1] / "static"
DOCUMENTOS_DIR = STATIC_DIR / "documentos-alumno"
EXTENSIONES_PERMITIDAS = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}
BLOB_OBJECT_PREFIX = "documentos-alumno"


if not BLOB_STORE_ID and not BLOB_READ_WRITE_TOKEN:
    raise RuntimeError(
        "Faltan variables de entorno para Vercel Blob: configure BLOB_READ_WRITE_TOKEN localmente o BLOB_STORE_ID + VERCEL_OIDC_TOKEN en Vercel."
    )

router = APIRouter(
    prefix="/documentos-alumno",
    tags=["Documentos alumno"]
)


def _detalle_documento(db: Session, documento_id: int):
    documento = next(
        item for item in get_documentos_alumno_detalle(db)
        if item["id_documento"] == documento_id
    )

    return _map_documento_ruta(documento)


def _obtener_documentos_con_permisos(
    db: Session,
    usuario: Usuario,
    alumno_id: Optional[int] = None,
    tipo_documento_id: Optional[int] = None,
    validado: Optional[bool] = None,
):
    if _usuario_es_admin(usuario):
        documentos = get_documentos_alumno_detalle(
            db,
            alumno_id=alumno_id,
            tipo_documento_id=tipo_documento_id,
            validado=validado
        )
    else:
        alumno_actual = _obtener_alumno_actual(db, usuario)

        if not alumno_actual:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para acceder a estos documentos"
            )

        if alumno_id is not None and alumno_actual.id_alumno != alumno_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para acceder a este alumno"
            )

        documentos = get_documentos_alumno_detalle(
            db,
            alumno_id=alumno_actual.id_alumno,
            tipo_documento_id=tipo_documento_id,
            validado=validado
        )

    return [_map_documento_ruta(item) for item in documentos]


def _eliminar_archivo_estatico(ruta_archivo: Optional[str]):
    if not ruta_archivo or not ruta_archivo.startswith("/static/documentos-alumno/"):
        return

    archivo = (STATIC_DIR / ruta_archivo.removeprefix("/static/")).resolve()
    raiz_documentos = DOCUMENTOS_DIR.resolve()

    try:
        archivo.relative_to(raiz_documentos)
    except ValueError:
        return

    if archivo.is_file():
        archivo.unlink()


def _build_blob_key(id_alumno: int, extension: str) -> str:
    return f"{BLOB_OBJECT_PREFIX}/{id_alumno}/{uuid4().hex}{extension}"


def _build_download_route(documento_id: int) -> str:
    return f"/documentos-alumno/{documento_id}/download"


def _build_static_file_response(ruta_archivo: str, nombre_archivo: Optional[str] = None):
    archivo = (STATIC_DIR / ruta_archivo.removeprefix("/static/")).resolve()
    raiz_documentos = DOCUMENTOS_DIR.resolve()

    try:
        archivo.relative_to(raiz_documentos)
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Ruta de documento no válida"
        )

    if not archivo.is_file():
        raise HTTPException(
            status_code=404,
            detail="Archivo no encontrado"
        )

    return FileResponse(
        path=archivo,
        media_type=None,
        filename=nombre_archivo,
    )


def _usuario_es_admin(usuario: Usuario) -> bool:
    if not usuario:
        return False

    return any(
        rol.nombre in {"ADMIN", "CONTROL_ESCOLAR"}
        for rol in usuario.roles
    )


def _obtener_alumno_actual(db: Session, usuario: Usuario) -> Alumno | None:
    if not usuario:
        return None

    return (
        db.query(Alumno)
        .filter(
            Alumno.id_usuario == usuario.id_usuario,
            Alumno.estatus != "BAJA"
        )
        .first()
    )


def _usuario_tiene_acceso(documento, usuario: Usuario) -> bool:
    if not usuario or not documento:
        return False

    if documento.alumno and documento.alumno.id_usuario == usuario.id_usuario:
        return True

    return _usuario_es_admin(usuario)


def _map_documento_ruta(documento: dict) -> dict:
    documento = documento.copy()
    documento["ruta_archivo"] = _build_download_route(documento["id_documento"])
    return documento


def _is_blob_route(ruta_archivo: Optional[str]) -> bool:
    if not ruta_archivo:
        return False

    return not ruta_archivo.startswith("/static/")


def _extract_blob_key(ruta_archivo: str) -> str:
    return ruta_archivo


@router.get(
    "/",
    response_model=list[DocumentoAlumnoDetalleResponse]
)
def listar_documentos_alumno(
    usuario: Usuario = Depends(get_current_user),
    alumno_id: Optional[int] = None,
    tipo_documento_id: Optional[int] = None,
    validado: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    return _obtener_documentos_con_permisos(
        db,
        usuario,
        alumno_id=alumno_id,
        tipo_documento_id=tipo_documento_id,
        validado=validado
    )


@router.get(
    "/{documento_id}",
    response_model=DocumentoAlumnoDetalleResponse
)
def obtener_documento_alumno(
    documento_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    documento = next(
        (
            item for item in get_documentos_alumno_detalle(db)
            if item["id_documento"] == documento_id
        ),
        None
    )

    if not documento:
        raise HTTPException(
            status_code=404,
            detail="Documento de alumno no encontrado"
        )

    documento_obj = get_documento_alumno(db, documento_id)

    if not _usuario_tiene_acceso(documento_obj, usuario):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a este documento"
        )

    return _map_documento_ruta(documento)


@router.get("/{documento_id}/download")
def descargar_documento_alumno(
    documento_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    documento = get_documento_alumno(db, documento_id)

    if not documento:
        raise HTTPException(
            status_code=404,
            detail="Documento de alumno no encontrado"
        )

    if not _usuario_tiene_acceso(documento, usuario):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a este documento"
        )

    if not documento.ruta_archivo:
        raise HTTPException(
            status_code=404,
            detail="Ruta de documento no disponible"
        )

    if documento.ruta_archivo.startswith("/static/"):
        return _build_static_file_response(
            documento.ruta_archivo,
            documento.nombre_archivo,
        )

    try:
        content, content_type = download_blob(documento.ruta_archivo)
    except BlobStorageError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc

    headers = {}
    if documento.nombre_archivo:
        headers["Content-Disposition"] = (
            f'inline; filename="{documento.nombre_archivo}"'
        )

    return Response(
        content,
        media_type=content_type or "application/octet-stream",
        headers=headers,
    )


@router.post(
    "/",
    response_model=DocumentoAlumnoDetalleResponse
)
def crear_documento_alumno(
    documento: DocumentoAlumnoCreate,
    db: Session = Depends(get_db)
):
    nuevo_documento = create_documento_alumno(db, documento)

    return _detalle_documento(db, nuevo_documento.id_documento)


@router.post(
    "/upload",
    response_model=DocumentoAlumnoDetalleResponse
)
def subir_documento_alumno(
    id_alumno: int = Form(...),
    id_tipo_documento: int = Form(...),
    validado: bool = Form(True),
    observaciones: Optional[str] = Form(None),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    nombre_original = archivo.filename or "documento"
    extension = Path(nombre_original).suffix.lower()

    if extension not in EXTENSIONES_PERMITIDAS:
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten archivos PDF o imagenes"
        )

    object_key = _build_blob_key(id_alumno, extension)

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

    nuevo_documento = create_documento_alumno(
        db,
        DocumentoAlumnoCreate(
            id_alumno=id_alumno,
            id_tipo_documento=id_tipo_documento,
            nombre_archivo=nombre_original,
            ruta_archivo=object_key,
            validado=validado,
            observaciones=observaciones
        )
    )

    return _detalle_documento(db, nuevo_documento.id_documento)


@router.patch(
    "/{documento_id}",
    response_model=DocumentoAlumnoDetalleResponse
)
def actualizar_documento_alumno(
    documento_id: int,
    documento: DocumentoAlumnoUpdate,
    db: Session = Depends(get_db)
):
    documento_actualizado = update_documento_alumno(db, documento_id, documento)

    if not documento_actualizado:
        raise HTTPException(
            status_code=404,
            detail="Documento de alumno no encontrado"
        )

    return next(
        item for item in get_documentos_alumno_detalle(db)
        if item["id_documento"] == documento_id
    )


@router.delete(
    "/{documento_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_documento_alumno(
    documento_id: int,
    db: Session = Depends(get_db)
):
    documento = get_documento_alumno(db, documento_id)

    if not documento:
        raise HTTPException(
            status_code=404,
            detail="Documento de alumno no encontrado"
        )

    if _is_blob_route(documento.ruta_archivo):
        object_key = _extract_blob_key(documento.ruta_archivo)
        try:
            delete_blob(object_key)
        except BlobStorageError:
            pass
    else:
        _eliminar_archivo_estatico(documento.ruta_archivo)

    delete_documento_alumno(db, documento_id)
