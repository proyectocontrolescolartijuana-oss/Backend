from app.crud.crud_cuatrimestre import (
    create_cuatrimestre,
    delete_cuatrimestre,
    get_cuatrimestre,
    get_cuatrimestres,
    update_cuatrimestre
)
from app.routers._crud_router import create_crud_router
from app.schemas.cuatrimestre import (
    CuatrimestreCreate,
    CuatrimestreResponse,
    CuatrimestreUpdate
)


router = create_crud_router(
    prefix="/cuatrimestres",
    tags=["Cuatrimestres"],
    response_schema=CuatrimestreResponse,
    create_schema=CuatrimestreCreate,
    update_schema=CuatrimestreUpdate,
    get_all=get_cuatrimestres,
    get_one=get_cuatrimestre,
    create_one=create_cuatrimestre,
    update_one=update_cuatrimestre,
    delete_one=delete_cuatrimestre,
    not_found_detail="Cuatrimestre no encontrado"
)
