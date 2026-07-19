def articulo_alumno(sexo: str):
    sexo = (sexo or "M").upper()

    return "el alumno" if sexo == "M" else "la alumna"


def pronombre(sexo: str):
    sexo = (sexo or "M").upper()

    return "el" if sexo == "M" else "ella"


def inscrito(sexo: str):
    sexo = (sexo or "M").upper()

    return "inscrito" if sexo == "M" else "inscrita"


def egresado(sexo: str):
    sexo = (sexo or "M").upper()

    return "egresado" if sexo == "M" else "egresada"


def interesado(sexo: str):
    sexo = (sexo or "M").upper()

    return "interesado" if sexo == "M" else "interesada"
