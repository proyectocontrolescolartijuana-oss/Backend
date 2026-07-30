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

from app.database import get_db
from app.models.alumno import Alumno
from app.models.documento_egresado import DocumentoEgresado
from app.models.practica_profesional import PracticaProfesional
from app.models.servicio_social import ServicioSocial
from app.schemas.documento_egresado import DocumentoEgresadoResponse
from app.services.blob_service import (
    BlobStorageError,
    delete_blob,
    download_blob,
    upload_blob,
)


router = APIRouter(
    prefix="/documentos-egresado",
    tags=["Documentos de egresados"],
)

EXTENSIONES_PERMITIDAS = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}
TIPOS_PERMITIDOS = {
    "OFICIO_CAMPO",
    "CARTA_UNIFRONT",
    "CARTA_PROCEDENCIA",
}
BLOB_OBJECT_PREFIX = "egresados"


def _ruta_descarga(documento_id: int) -> str:
    return f"/documentos-egresado/{documento_id}/download"


def _map_documento(documento: DocumentoEgresado) -> dict:
    return {
        "id_documento": documento.id_documento,
        "id_alumno": documento.id_alumno,
        "tipo": documento.tipo,
        "nombre_archivo": documento.nombre_archivo,
        "ruta_archivo": _ruta_descarga(documento.id_documento),
        "fecha_subida": documento.fecha_subida,
    }


def _obtener_documento(db: Session, documento_id: int) -> DocumentoEgresado:
    documento = (
        db.query(DocumentoEgresado)
        .filter(DocumentoEgresado.id_documento == documento_id)
        .first()
    )
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return documento


def _sincronizar_booleano(
    db: Session,
    alumno_id: int,
    tipo: str,
    existe: bool,
):
    if tipo == "OFICIO_CAMPO":
        registro = (
            db.query(PracticaProfesional)
            .filter(PracticaProfesional.id_alumno == alumno_id)
            .first()
        )
        if registro is None:
            registro = PracticaProfesional(id_alumno=alumno_id)
            db.add(registro)
        registro.oficio_campo = existe
        return

    registro = (
        db.query(ServicioSocial)
        .filter(ServicioSocial.id_alumno == alumno_id)
        .first()
    )
    if registro is None:
        registro = ServicioSocial(id_alumno=alumno_id)
        db.add(registro)

    if tipo == "CARTA_UNIFRONT":
        registro.carta_unifront = existe
    elif tipo == "CARTA_PROCEDENCIA":
        registro.carta_procedencia = existe


@router.get("/", response_model=list[DocumentoEgresadoResponse])
def listar_documentos(
    alumno_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(DocumentoEgresado)
    if alumno_id is not None:
        query = query.filter(DocumentoEgresado.id_alumno == alumno_id)
    documentos = query.order_by(DocumentoEgresado.fecha_subida.desc()).all()
    return [_map_documento(documento) for documento in documentos]


@router.get("/{documento_id}/download")
def descargar_documento(
    documento_id: int,
    db: Session = Depends(get_db),
):
    documento = _obtener_documento(db, documento_id)
    try:
        contenido, content_type = download_blob(documento.ruta_archivo)
    except BlobStorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return Response(
        contenido,
        media_type=content_type or "application/octet-stream",
        headers={
            "Content-Disposition": (
                f'inline; filename="{documento.nombre_archivo}"'
            )
        },
    )


@router.post("/upload", response_model=DocumentoEgresadoResponse)
def subir_documento(
    alumno_id: int = Form(...),
    tipo: str = Form(...),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if tipo not in TIPOS_PERMITIDOS:
        raise HTTPException(status_code=400, detail="Tipo de documento no válido")

    if not db.query(Alumno).filter(Alumno.id_alumno == alumno_id).first():
        raise HTTPException(status_code=404, detail="Alumno no encontrado")

    nombre_original = archivo.filename or "documento"
    extension = Path(nombre_original).suffix.lower()
    if extension not in EXTENSIONES_PERMITIDAS:
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten archivos PDF o imágenes",
        )

    anterior = (
        db.query(DocumentoEgresado)
        .filter(
            DocumentoEgresado.id_alumno == alumno_id,
            DocumentoEgresado.tipo == tipo,
        )
        .first()
    )
    object_key = (
        f"{BLOB_OBJECT_PREFIX}/{alumno_id}/{tipo}/"
        f"{uuid4().hex}{extension}"
    )

    try:
        upload_blob(object_key, archivo.file.read(), archivo.content_type)
    except BlobStorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if anterior:
        try:
            delete_blob(anterior.ruta_archivo)
        except BlobStorageError:
            pass
        anterior.nombre_archivo = nombre_original
        anterior.ruta_archivo = object_key
        documento = anterior
    else:
        documento = DocumentoEgresado(
            id_alumno=alumno_id,
            tipo=tipo,
            nombre_archivo=nombre_original,
            ruta_archivo=object_key,
        )
        db.add(documento)

    _sincronizar_booleano(db, alumno_id, tipo, True)
    db.commit()
    db.refresh(documento)
    return _map_documento(documento)


@router.delete("/{documento_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_documento(
    documento_id: int,
    db: Session = Depends(get_db),
):
    documento = _obtener_documento(db, documento_id)
    alumno_id = documento.id_alumno
    tipo = documento.tipo

    try:
        delete_blob(documento.ruta_archivo)
    except BlobStorageError:
        pass

    db.delete(documento)
    _sincronizar_booleano(db, alumno_id, tipo, False)
    db.commit()
