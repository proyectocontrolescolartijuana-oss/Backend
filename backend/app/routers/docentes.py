from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.docente import (
    DocenteCreate,
    DocenteResponse,
    DocenteUpdate
)

from app.crud.crud_docente import (
    get_docentes,
    get_docente,
    create_docente,
    update_docente,
    delete_docente
)

router = APIRouter(
    prefix="/docentes",
    tags=["Docentes"]
)



@router.get(
    "/",
    response_model=list[DocenteResponse]
)
def listar_docentes(
    db: Session = Depends(get_db)
):
    return get_docentes(db)

@router.get(
    "/{docente_id}",
    response_model=DocenteResponse
)
def obtener_docente(
    docente_id: int,
    db: Session = Depends(get_db)
):
    docente = get_docente(db, docente_id)

    if not docente:
        raise HTTPException(
            status_code=404,
            detail="Docente no encontrado"
        )

    return docente

@router.post(
    "/",
    response_model=DocenteResponse
)
def crear_docente(
    docente: DocenteCreate,
    db: Session = Depends(get_db)
):
    return create_docente(
        db,
        docente
    )

@router.patch(
    "/{docente_id}",
    response_model=DocenteResponse
)
def actualizar_docente(
    docente_id: int,
    docente: DocenteUpdate,
    db: Session = Depends(get_db)
):
    docente_actualizado = update_docente(
        db,
        docente_id,
        docente
    )

    if not docente_actualizado:
        raise HTTPException(
            status_code=404,
            detail="Docente no encontrado"
        )

    return docente_actualizado

@router.delete(
    "/{docente_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_docente(
    docente_id: int,
    db: Session = Depends(get_db)
):
    eliminado = delete_docente(db, docente_id)

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="Docente no encontrado"
        )
