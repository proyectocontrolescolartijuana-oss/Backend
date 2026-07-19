from pydantic import BaseModel


class AlumnoTutorBase(BaseModel):
    id_alumno: int
    id_tutor: int


class AlumnoTutorCreate(AlumnoTutorBase):
    pass


class AlumnoTutorResponse(AlumnoTutorBase):
    pass
