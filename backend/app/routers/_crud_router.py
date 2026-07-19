from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db


def create_crud_router(
    *,
    prefix,
    tags,
    response_schema,
    create_schema,
    update_schema,
    get_all,
    get_one,
    create_one,
    update_one,
    delete_one,
    not_found_detail
):
    router = APIRouter(
        prefix=prefix,
        tags=tags
    )

    @router.get(
        "/",
        response_model=list[response_schema]
    )
    def listar_items(
        db: Session = Depends(get_db)
    ):
        return get_all(db)

    @router.get(
        "/{item_id}",
        response_model=response_schema
    )
    def obtener_item(
        item_id: int,
        db: Session = Depends(get_db)
    ):
        item = get_one(db, item_id)

        if not item:
            raise HTTPException(
                status_code=404,
                detail=not_found_detail
            )

        return item

    @router.post(
        "/",
        response_model=response_schema
    )
    def crear_item(
        item: create_schema,
        db: Session = Depends(get_db)
    ):
        return create_one(db, item)

    @router.patch(
        "/{item_id}",
        response_model=response_schema
    )
    def actualizar_item(
        item_id: int,
        item: update_schema,
        db: Session = Depends(get_db)
    ):
        item_actualizado = update_one(db, item_id, item)

        if not item_actualizado:
            raise HTTPException(
                status_code=404,
                detail=not_found_detail
            )

        return item_actualizado

    @router.delete(
        "/{item_id}",
        status_code=status.HTTP_204_NO_CONTENT
    )
    def eliminar_item(
        item_id: int,
        db: Session = Depends(get_db)
    ):
        eliminado = delete_one(db, item_id)

        if not eliminado:
            raise HTTPException(
                status_code=404,
                detail=not_found_detail
            )

    return router
