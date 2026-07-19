from app.crud.crud_empresa import (
    create_empresa,
    delete_empresa,
    get_empresa,
    get_empresas,
    update_empresa
)
from app.routers._crud_router import create_crud_router
from app.schemas.empresa import EmpresaCreate, EmpresaResponse, EmpresaUpdate


router = create_crud_router(
    prefix="/empresas",
    tags=["Empresas"],
    response_schema=EmpresaResponse,
    create_schema=EmpresaCreate,
    update_schema=EmpresaUpdate,
    get_all=get_empresas,
    get_one=get_empresa,
    create_one=create_empresa,
    update_one=update_empresa,
    delete_one=delete_empresa,
    not_found_detail="Empresa no encontrada"
)
