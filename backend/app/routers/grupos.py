from app.crud.crud_grupo import (
    create_grupo,
    delete_grupo,
    get_grupo,
    get_grupos,
    update_grupo
)
from app.routers._crud_router import create_crud_router
from app.schemas.grupo import GrupoCreate, GrupoResponse, GrupoUpdate


router = create_crud_router(
    prefix="/grupos",
    tags=["Grupos"],
    response_schema=GrupoResponse,
    create_schema=GrupoCreate,
    update_schema=GrupoUpdate,
    get_all=get_grupos,
    get_one=get_grupo,
    create_one=create_grupo,
    update_one=update_grupo,
    delete_one=delete_grupo,
    not_found_detail="Grupo no encontrado"
)
