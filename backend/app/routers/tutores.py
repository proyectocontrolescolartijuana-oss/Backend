from app.crud.crud_tutor import (
    create_tutor,
    delete_tutor,
    get_tutor,
    get_tutores,
    update_tutor
)
from app.routers._crud_router import create_crud_router
from app.schemas.tutor import TutorCreate, TutorResponse, TutorUpdate


router = create_crud_router(
    prefix="/tutores",
    tags=["Tutores"],
    response_schema=TutorResponse,
    create_schema=TutorCreate,
    update_schema=TutorUpdate,
    get_all=get_tutores,
    get_one=get_tutor,
    create_one=create_tutor,
    update_one=update_tutor,
    delete_one=delete_tutor,
    not_found_detail="Tutor no encontrado"
)
