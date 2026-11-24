from decimal import Decimal

CLAVES = ("C1", "C2", "C3", "C4", "C5", "EPA")

MINIMA_APROBATORIA = 70

_DOS_DECIMALES = Decimal("0.01")

_ESPECIALES = [
    "cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete",
    "ocho", "nueve", "diez", "once", "doce", "trece", "catorce", "quince",
    "dieciséis", "diecisiete", "dieciocho", "diecinueve", "veinte",
    "veintiuno", "veintidós", "veintitrés", "veinticuatro", "veinticinco",
    "veintiséis", "veintisiete", "veintiocho", "veintinueve",
]

_DECENAS = {
    3: "treinta", 4: "cuarenta", 5: "cincuenta",
    6: "sesenta", 7: "setenta", 8: "ochenta", 9: "noventa",
}


def redondear_calificacion(valor: Decimal) -> int:
    entero = int(valor)

    if valor - entero >= Decimal("0.6"):
        return entero + 1

    return entero


def numero_a_letras(numero: int) -> str:
    if numero < 0 or numero > 100:
        raise ValueError("La calificacion debe estar entre 0 y 100")

    if numero == 100:
        texto = "cien"
    elif numero < 30:
        texto = _ESPECIALES[numero]
    else:
        decena, unidad = divmod(numero, 10)
        texto = (
            _DECENAS[decena]
            if unidad == 0
            else f"{_DECENAS[decena]} y {_ESPECIALES[unidad]}"
        )

    return texto.capitalize()


def calcular_resumen(criterios, puntajes) -> dict:
    resumen = {clave: None for clave in CLAVES}
    suma = Decimal("0")
    en_uso = 0
    completo = True

    for clave in CLAVES:
        datos = criterios.get(clave)

        if not datos:
            continue

        porcentaje, puntos_max = datos
        en_uso += 1
        puntaje = puntajes.get(clave)

        if puntaje is None:
            completo = False
            continue

        aporte = Decimal(puntaje) / Decimal(puntos_max) * Decimal(porcentaje)
        resumen[clave] = aporte.quantize(_DOS_DECIMALES)
        suma += aporte

    listo = en_uso > 0 and completo
    cpf = redondear_calificacion(suma) if listo else None

    return {
        **resumen,
        "cpf": cpf,
        "cpfl": numero_a_letras(cpf) if listo else None,
        "completo": listo,
    }