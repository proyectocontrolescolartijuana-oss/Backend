import mimetypes
from typing import Any

from vercel.blob import delete, get, put

from app.core.config import (
    BLOB_READ_WRITE_TOKEN,
)


class BlobStorageError(Exception):
    pass


if not BLOB_READ_WRITE_TOKEN:
    raise BlobStorageError(
        "BLOB_READ_WRITE_TOKEN no está configurado."
    )


def _normalize_blob_response(result: Any) -> bytes:
    if result is None:
        raise BlobStorageError("No se obtuvo contenido del blob.")

    if isinstance(result, (bytes, bytearray)):
        return bytes(result)

    if hasattr(result, "content"):
        return result.content

    if hasattr(result, "read"):
        return result.read()

    if hasattr(result, "raw") and hasattr(result.raw, "read"):
        return result.raw.read()

    raise BlobStorageError(
        "Respuesta de blob no compatible con el servidor."
    )


def upload_blob(
    object_key: str,
    content: bytes,
    content_type: str | None = None,
) -> Any:
    if not object_key:
        raise BlobStorageError("Object key is required.")

    if not content_type:
        content_type, _ = mimetypes.guess_type(object_key)
        content_type = content_type or "application/octet-stream"

    try:
        result = put(
            object_key,
            content,
            access="private",
            content_type=content_type,
            token=BLOB_READ_WRITE_TOKEN,
            add_random_suffix=False,
            overwrite=True,
        )

        return result

    except Exception as exc:
        raise BlobStorageError(
            f"Failed to upload object to Vercel Blob: {exc}"
        ) from exc


def download_blob(object_key: str) -> tuple[bytes, str | None]:
    if not object_key:
        raise BlobStorageError("Object key is required.")

    try:
        result = get(
            object_key,
            access="private",
            token=BLOB_READ_WRITE_TOKEN,
            use_cache=False,
        )

        content_type = None
        if hasattr(result, "content_type"):
            content_type = getattr(result, "content_type")
        elif hasattr(result, "headers"):
            headers = getattr(result, "headers")
            if hasattr(headers, "get"):
                content_type = headers.get("content-type")

        return _normalize_blob_response(result), content_type
    except Exception as exc:
        raise BlobStorageError(
            f"Failed to download object from Vercel Blob: {exc}"
        ) from exc


def delete_blob(object_key: str) -> None:
    if not object_key:
        return

    try:
        delete(
            object_key,
            token=BLOB_READ_WRITE_TOKEN,
        )

    except Exception as exc:
        raise BlobStorageError(
            f"Failed to delete object from Vercel Blob: {exc}"
        ) from exc