from sqlalchemy import BigInteger, Column, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class MateriaPrerrequisito(Base):
    __tablename__ = "materias_prerrequisito"

    id_prerrequisito = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    id_materia = Column(
        BigInteger,
        ForeignKey("materias.id_materia"),
        nullable=False
    )

    id_materia_requerida = Column(
        BigInteger,
        ForeignKey("materias.id_materia"),
        nullable=False
    )

    tipo = Column(
        Enum("OBLIGATORIO", "RECOMENDADO"),
        nullable=False
    )

    materia = relationship(
        "Materia",
        foreign_keys=[id_materia],
        back_populates="prerrequisitos"
    )

    materia_requerida = relationship(
        "Materia",
        foreign_keys=[id_materia_requerida]
    )
