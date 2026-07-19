from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    Boolean,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base

class PlanMateria(Base):
    __tablename__ = "plan_materias"

    id_plan_materia = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    id_plan = Column(
        Integer,
        ForeignKey("planes_estudio.id_plan"),
        nullable=False
    )

    id_materia = Column(
        BigInteger,
        ForeignKey("materias.id_materia"),
        nullable=False
    )

    id_cuatrimestre = Column(
        Integer,
        ForeignKey("cuatrimestres.id_cuatrimestre"),
        nullable=False
    )

    obligatoria = Column(
        Boolean,
        default=True
    )

    plan = relationship(
        "PlanEstudio",
        back_populates="materias"
    )

    materia = relationship(
        "Materia",
        back_populates="planes"
    )

    cuatrimestre = relationship(
        "Cuatrimestre"
    )