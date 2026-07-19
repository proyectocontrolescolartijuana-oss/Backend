from datetime import (
    datetime,
    timedelta,
    timezone
)

from jose import jwt, JWTError

import bcrypt

from fastapi import (
    Depends,
    HTTPException,
    status
)

from fastapi.security import (
    OAuth2PasswordBearer
)

from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.models import init as _models_init
from app.models.usuario import Usuario

from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

def hash_password(password: str):

    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

def verify_password(
    plain_password,
    hashed_password
):

    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except (TypeError, ValueError):
        return False

# OAUTH2

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

# DATABASE

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

# CREATE TOKEN

def create_access_token(
    data: dict
):

    to_encode = data.copy()

    expire = datetime.now(
        timezone.utc
    ) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

# GET CURRENT USER

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        correo: str = payload.get("sub")

        if correo is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    usuario = (
        db.query(Usuario)
        .filter(
            Usuario.correo == correo
        )
        .first()
    )

    if usuario is None:
        raise credentials_exception

    return usuario
