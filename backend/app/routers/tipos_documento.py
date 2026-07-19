from app.crud.crud_tipo_documento import (
    create_tipo_documento,
    delete_tipo_documento,
    get_tipo_documento,
    get_tipos_documento,
    update_tipo_documento
)
from app.routers._crud_router import create_crud_router
from app.schemas.tipo_documento import (
    TipoDocumentoCreate,
    TipoDocumentoResponse,
    TipoDocumentoUpdate
)


router = create_crud_router(
    prefix="/tipos-documento",
    tags=["Tipos documento"],
    response_schema=TipoDocumentoResponse,
    create_schema=TipoDocumentoCreate,
    update_schema=TipoDocumentoUpdate,
    get_all=get_tipos_documento,
    get_one=get_tipo_documento,
    create_one=create_tipo_documento,
    update_one=update_tipo_documento,
    delete_one=delete_tipo_documento,
    not_found_detail="Tipo de documento no encontrado"
)
