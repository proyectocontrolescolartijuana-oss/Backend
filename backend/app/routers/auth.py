from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from fastapi.security import (
    OAuth2PasswordRequestForm
)

from sqlalchemy.orm import Session

from app.models.usuario import Usuario

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

from app.database import get_db
from app.crud.crud_usuario_expediente import get_usuario_expediente
from app.schemas.auth import PasswordUpdate
from app.schemas.usuario import UsuarioResponse

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    usuario = (
        db.query(Usuario)
        .filter(
            Usuario.correo == form_data.username
        )
        .first()
    )

    if not usuario:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo incorrecto"
        )

    if not verify_password(
        form_data.password,
        usuario.password
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password incorrecto"
        )

    access_token = create_access_token(
        data={
            "sub": usuario.correo
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",

        "user": {
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "roles": [
            {
                "id_rol": rol.id_rol,
                "nombre": rol.nombre
            }
            for rol in usuario.roles
        ]
    }
    }

@router.get(
    "/me",
    response_model=UsuarioResponse
)
def obtener_usuario_actual(
    usuario: Usuario = Depends(get_current_user)
):
    return usuario


@router.get("/me/expediente")
def obtener_expediente_usuario_actual(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    expediente = get_usuario_expediente(db, usuario.id_usuario)

    if not expediente:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    return expediente


@router.patch("/me/password")
def actualizar_password_usuario_actual(
    datos: PasswordUpdate,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(datos.password_actual, usuario.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual no es correcta"
        )

    usuario_db = (
        db.query(Usuario)
        .filter(Usuario.id_usuario == usuario.id_usuario)
        .first()
    )

    if not usuario_db:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    usuario_db.password = hash_password(datos.nueva_password)
    db.commit()

    return {
        "message": "Contraseña actualizada correctamente"
    }
