from sqlalchemy import (
    Column,
    BigInteger,
    String,
    DECIMAL,
    Boolean
)

from sqlalchemy.orm import relationship

from app.database import Base

class Materia(Base):
    __tablename__ = "materias"

    id_materia = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    clave = Column(
        String(20),
        unique=True
    )

    nombre = Column(
        String(150),
        nullable=False
    )

    creditos = Column(
        DECIMAL(5,2),
        nullable=False
    )

    estado = Column(
        Boolean,
        default=True
    )

    planes = relationship(
        "PlanMateria",
        back_populates="materia"
    )

    prerrequisitos = relationship(
        "MateriaPrerrequisito",
        foreign_keys="MateriaPrerrequisito.id_materia",
        back_populates="materia"
    )
