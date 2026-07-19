from sqlalchemy import (
    Column,
    Integer,
    String
)

from app.database import Base

class Cuatrimestre(Base):
    __tablename__ = "cuatrimestres"

    id_cuatrimestre = Column(
        Integer,
        primary_key=True,
        index=True
    )

    numero = Column(
        Integer,
        nullable=False
    )

    nombre = Column(
        String(50),
        nullable=False
    )