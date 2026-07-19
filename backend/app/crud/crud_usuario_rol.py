from sqlalchemy import and_, delete, insert, select
from sqlalchemy.orm import Session

from app.models.usuario_rol import usuario_roles


def get_usuarios_roles(db: Session):
    return db.execute(select(usuario_roles)).mappings().all()


def get_usuario_rol(db: Session, usuario_id: int, rol_id: int):
    return (
        db.execute(
            select(usuario_roles).where(
                and_(
                    usuario_roles.c.id_usuario == usuario_id,
                    usuario_roles.c.id_rol == rol_id
                )
            )
        )
        .mappings()
        .first()
    )


def create_usuario_rol(db: Session, usuario_id: int, rol_id: int):
    relacion = get_usuario_rol(db, usuario_id, rol_id)

    if relacion:
        return relacion

    db.execute(
        insert(usuario_roles).values(
            id_usuario=usuario_id,
            id_rol=rol_id
        )
    )
    db.commit()

    return get_usuario_rol(db, usuario_id, rol_id)


def delete_usuario_rol(db: Session, usuario_id: int, rol_id: int):
    result = db.execute(
        delete(usuario_roles).where(
            and_(
                usuario_roles.c.id_usuario == usuario_id,
                usuario_roles.c.id_rol == rol_id
            )
        )
    )
    db.commit()

    return result.rowcount > 0
