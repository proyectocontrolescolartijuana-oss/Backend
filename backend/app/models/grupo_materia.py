from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base

class GrupoMateria(Base):
    __tablename__ = "grupos_materias"

    id_grupo_materia = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    id_grupo = Column(
        BigInteger,
        ForeignKey("grupos.id_grupo")
    )

    id_materia = Column(
        BigInteger,
        ForeignKey("materias.id_materia")
    )

    id_docente = Column(
        BigInteger,
        ForeignKey("docentes.id_docente")
    )

    id_periodo = Column(
        Integer,
        ForeignKey("periodos.id_periodo")
    )

    aula = Column(String(20))

    cupo_maximo = Column(Integer)

    grupo = relationship(
        "Grupo",
        back_populates="materias"
    )

    materia = relationship("Materia")

    docente = relationship(
        "Docente",
        back_populates="grupos_materia"
    )

    periodo = relationship(
        "Periodo",
        back_populates="grupos_materia"
    )

    cargas = relationship(
        "CargaAcademica",
        back_populates="grupo_materia"
    )