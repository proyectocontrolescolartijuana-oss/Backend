import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "CAMBIAR_ESTA_CLAVE_EN_PRODUCCION"
)

ALGORITHM = os.getenv(
    "ALGORITHM",
    "HS256"
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        60
    )
)

BLOB_STORE_ID = os.getenv("BLOB_STORE_ID")
BLOB_READ_WRITE_TOKEN = os.getenv("BLOB_READ_WRITE_TOKEN")
VERCEL_OIDC_TOKEN = os.getenv("VERCEL_OIDC_TOKEN")
BLOB_API_BASE_URL = os.getenv(
    "BLOB_API_BASE_URL",
    "https://api.vercel.com/v1/blob/stores"
)
BLOB_STORE_URL = os.getenv("BLOB_STORE_URL")

if not BLOB_STORE_URL and BLOB_STORE_ID:
    host_store_id = BLOB_STORE_ID.replace("_", "-")
    BLOB_STORE_URL = f"https://{host_store_id}.private.blob.vercel-storage.com"
