from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Boolean,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base

class PlanEstudio(Base):
    __tablename__ = "planes_estudio"

    id_plan = Column(
        Integer,
        primary_key=True,
        index=True
    )

    id_carrera = Column(
        Integer,
        ForeignKey("carreras.id_carrera"),
        nullable=False
    )

    nombre_plan = Column(
        String(100),
        nullable=False
    )

    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)

    vigente = Column(
        Boolean,
        default=True
    )

    carrera = relationship(
        "Carrera",
        back_populates="planes"
    )

    materias = relationship(
        "PlanMateria",
        back_populates="plan",
        cascade="all, delete-orphan"
    )
