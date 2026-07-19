from sqlalchemy import (
    Table,
    Column,
    BigInteger,
    ForeignKey
)

from app.database import Base

alumno_tutor = Table(
    "alumno_tutor",
    Base.metadata,

    Column(
        "id_alumno",
        BigInteger,
        ForeignKey("alumnos.id_alumno"),
        primary_key=True
    ),

    Column(
        "id_tutor",
        BigInteger,
        ForeignKey("tutores.id_tutor"),
        primary_key=True
    )
)