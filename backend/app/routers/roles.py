# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session

# from app.database import get_db
# from app.schemas.rol import (
#     RolCreate,
#     RolResponse,
#     RolUpdate
# )
# from app.crud.crud_rol import (
#     get_roles,
#     get_rol,
#     create_rol,
#     update_rol,
#     delete_rol
# )

# router = APIRouter(
#     prefix="/roles",
#     tags=["Roles"]
# )

# @router.get(
#     "/",
#     response_model=list[RolResponse]
# )
# def listar_roles(
#     db: Session = Depends(get_db)
# ):
#     return get_roles(db)

# @router.get(
#     "/{rol_id}",
#     response_model=RolResponse
# )
# def obtener_rol(
#     rol_id: int,
#     db: Session = Depends(get_db)
# ):
#     rol = get_rol(db, rol_id)

#     if not rol:
#         raise HTTPException(
#             status_code=404,
#             detail="Rol no encontrado"
#         )

#     return rol

# @router.post(
#     "/",
#     response_model=RolResponse
# )
# def crear_rol(
#     rol: RolCreate,
#     db: Session = Depends(get_db)
# ):
#     return create_rol(db, rol)

# @router.patch(
#     "/{rol_id}",
#     response_model=RolResponse
# )
# def actualizar_rol(
#     rol_id: int,
#     rol: RolUpdate,
#     db: Session = Depends(get_db)
# ):
#     rol_actualizado = update_rol(
#         db,
#         rol_id,
#         rol
#     )

#     if not rol_actualizado:
#         raise HTTPException(
#             status_code=404,
#             detail="Rol no encontrado"
#         )

#     return rol_actualizado

# @router.delete(
#     "/{rol_id}",
#     status_code=status.HTTP_204_NO_CONTENT
# )
# def eliminar_rol(
#     rol_id: int,
#     db: Session = Depends(get_db)
# ):
#     eliminado = delete_rol(db, rol_id)

#     if not eliminado:
#         raise HTTPException(
#             status_code=404,
#             detail="Rol no encontrado"
#         )
