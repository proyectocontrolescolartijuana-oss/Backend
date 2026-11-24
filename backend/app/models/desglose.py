from sqlalchemy import (
    Column,
    BigInteger,
    DECIMAL,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint
)

from sqlalchemy.orm import relationship

from app.database import Base


class DesgloseCriterio(Base):
    __tablename__ = "desglose_criterios"

    __table_args__ = (
        UniqueConstraint(
            "id_grupo_materia",
            "id_parcial",
            "clave",
            name="uq_desglose_criterio"
        ),
    )

    id_criterio = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    id_grupo_materia = Column(
        BigInteger,
        ForeignKey("grupos_materias.id_grupo_materia"),
        nullable=False
    )

    id_parcial = Column(
        Integer,
        ForeignKey("parciales.id_parcial"),
        nullable=False
    )

    clave = Column(
        Enum("C1", "C2", "C3", "C4", "C5", "EPA"),
        nullable=False
    )

    nombre = Column(String(100))

    porcentaje = Column(
        DECIMAL(5, 2),
        nullable=False
    )

    puntos_max = Column(
        DECIMAL(7, 2),
        nullable=False
    )

    puntajes = relationship(
        "DesglosePuntaje",
        back_populates="criterio",
        cascade="all, delete-orphan"
    )


class DesglosePuntaje(Base):
    __tablename__ = "desglose_puntajes"

    __table_args__ = (
        UniqueConstraint(
            "id_criterio",
            "id_carga",
            name="uq_desglose_puntaje"
        ),
    )

    id_puntaje = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    id_criterio = Column(
        BigInteger,
        ForeignKey(
            "desglose_criterios.id_criterio",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    id_carga = Column(
        BigInteger,
        ForeignKey("carga_academica.id_carga"),
        nullable=False
    )

    puntaje = Column(
        DECIMAL(7, 2),
        nullable=False
    )

    criterio = relationship(
        "DesgloseCriterio",
        back_populates="puntajes"
    )