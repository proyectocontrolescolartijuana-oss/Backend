from app.crud.crud_extraordinario import (
    create_extraordinario,
    delete_extraordinario,
    get_extraordinario,
    get_extraordinarios,
    update_extraordinario
)
from app.routers._crud_router import create_crud_router
from app.schemas.extraordinario import (
    ExtraordinarioCreate,
    ExtraordinarioResponse,
    ExtraordinarioUpdate
)


router = create_crud_router(
    prefix="/extraordinarios",
    tags=["Extraordinarios"],
    response_schema=ExtraordinarioResponse,
    create_schema=ExtraordinarioCreate,
    update_schema=ExtraordinarioUpdate,
    get_all=get_extraordinarios,
    get_one=get_extraordinario,
    create_one=create_extraordinario,
    update_one=update_extraordinario,
    delete_one=delete_extraordinario,
    not_found_detail="Extraordinario no encontrado"
)
