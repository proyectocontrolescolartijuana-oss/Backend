from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Date,
    Text,
    Enum,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base

class Alumno(Base):
    __tablename__ = "alumnos"

    id_alumno = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    matricula = Column(
        String(20),
        unique=True,
        nullable=False
    )

    numero_control = Column(
        String(30),
        unique=True
    )

    id_usuario = Column(
        BigInteger,
        ForeignKey("usuarios.id_usuario"),
        nullable=False
    )

    id_carrera = Column(
        Integer,
        ForeignKey("carreras.id_carrera"),
        nullable=False
    )

    id_plan = Column(
        Integer,
        ForeignKey("planes_estudio.id_plan"),
        nullable=False
    )

    fecha_nacimiento = Column(Date)

    ciudad_nacimiento = Column(String(100))
    municipio_nacimiento = Column(String(100))
    nacionalidad = Column(String(100))

    sexo = Column(
        Enum("M", "F")
    )

    curp = Column(String(18))

    direccion = Column(Text)

    ciudad = Column(String(100))
    estado = Column(String(100))

    correo_contacto = Column(String(150))

    fecha_ingreso = Column(Date)

    estatus = Column(
        Enum(
            "ACTIVO",
            "BAJA",
            "EGRESADO",
            "TITULADO"
        ),
        default="ACTIVO"
    )

    foto = Column(String(255))

    usuario = relationship("Usuario")

    carrera = relationship("Carrera")

    plan = relationship("PlanEstudio")

    contactos = relationship(
        "ContactoEmergencia",
        back_populates="alumno"
    )

    seguros = relationship(
        "SeguroMedico",
        back_populates="alumno"
    )

    procedencia = relationship(
        "ProcedenciaAcademica",
        back_populates="alumno",
        uselist=False
    )
