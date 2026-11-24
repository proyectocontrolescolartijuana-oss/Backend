"""Regla de asistencia con retardos.

PENDIENTE DE DEFINIR con el cliente. Se cambia solo aqui:

    None -> el retardo cuenta como asistencia completa (opcion a, vigente)
    1    -> el retardo cuenta como falta
    N    -> cada N retardos equivalen a una falta (por ejemplo 3)

El valor se envia al frontend en la captura, para que el porcentaje que se ve
mientras se captura use exactamente la misma regla.
"""

RETARDOS_POR_FALTA = None


def asistencias_efectivas(total_asistencias: int, total_retardos: int) -> int:
    """Asistencias que cuentan para el porcentaje.

    `total_asistencias` ya incluye los retardos (un retardo es una asistencia).
    """
    if not RETARDOS_POR_FALTA:
        return total_asistencias

    return max(0, total_asistencias - total_retardos // RETARDOS_POR_FALTA)