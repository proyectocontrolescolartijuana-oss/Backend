from sqlalchemy import (
    Table,
    Column,
    BigInteger,
    Integer,
    ForeignKey
)

from app.database import Base

usuario_roles = Table(
    "usuario_roles",
    Base.metadata,

    Column(
        "id_usuario",
        BigInteger,
        ForeignKey("usuarios.id_usuario"),
        primary_key=True
    ),

    Column(
        "id_rol",
        Integer,
        ForeignKey("roles.id_rol"),
        primary_key=True
    )
)