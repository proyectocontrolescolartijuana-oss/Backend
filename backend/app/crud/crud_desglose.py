from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.calificacion import Calificacion
from app.models.carga_academica import CargaAcademica
from app.models.desglose import DesgloseCriterio, DesglosePuntaje
from app.models.parcial import Parcial
from app.models.usuario import Usuario
from app.schemas.desglose import DesgloseGuardar
from app.services.esquema_evaluacion import (
    EsquemaEvaluacionError,
    esquema_de_grupo_materia
)
from app.utils.desglose import CLAVES, calcular_resumen

EPA_PORCENTAJE_INICIAL = 30.0
EPA_PUNTOS_INICIALES = 100.0

DOS_DECIMALES = Decimal("0.01")


def _error(codigo: int, detalle: str):
    return HTTPException(status_code=codigo, detail=detalle)


def _a_float(valor):
    return float(valor) if valor is not None else None


# ---------------------------------------------------------------- parciales

def validar_parcial_existe(db: Session, parcial_id: int):
    existe = (
        db.query(Parcial.id_parcial)
        .filter(Parcial.id_parcial == parcial_id)
        .first()
    )

    if not existe:
        raise _error(status.HTTP_404_NOT_FOUND, "Parcial no encontrado")


def _esquema_del_grupo(db: Session, grupo_materia_id: int):
    try:
        return esquema_de_grupo_materia(db, grupo_materia_id)
    except EsquemaEvaluacionError as error:
        raise _error(status.HTTP_409_CONFLICT, str(error))


def validar_parcial_del_grupo(
    db: Session,
    grupo_materia_id: int,
    parcial_id: int
):
    """El parcial debe existir y pertenecer a la modalidad del grupo."""
    validar_parcial_existe(db, parcial_id)
    esquema = _esquema_del_grupo(db, grupo_materia_id)

    try:
        esquema.validar_parcial(parcial_id)
    except EsquemaEvaluacionError as error:
        raise _error(status.HTTP_400_BAD_REQUEST, str(error))

    return esquema


def validar_parcial_con_desglose(
    db: Session,
    grupo_materia_id: int,
    parcial_id: int
):
    """Ademas de pertenecer al grupo, el parcial debe admitir desglose."""
    esquema = validar_parcial_del_grupo(db, grupo_materia_id, parcial_id)

    if not esquema.admite_desglose(parcial_id):
        raise _error(
            status.HTTP_400_BAD_REQUEST,
            "Este parcial no se captura con desglose en la modalidad "
            f"{esquema.modalidad}"
        )


def get_parciales_con_desglose(db: Session, grupo_materia_id: int):
    filas = (
        db.query(DesgloseCriterio.id_parcial)
        .filter(DesgloseCriterio.id_grupo_materia == grupo_materia_id)
        .distinct()
        .all()
    )

    return sorted(id_parcial for (id_parcial,) in filas)


# ------------------------------------------------------------------ lectura

def _ids_cargas_grupo(db: Session, grupo_materia_id: int):
    return [
        id_carga
        for (id_carga,) in (
            db.query(CargaAcademica.id_carga)
            .filter(CargaAcademica.id_grupo_materia == grupo_materia_id)
            .order_by(CargaAcademica.id_carga)
            .all()
        )
    ]


def _criterios_guardados(
    db: Session,
    grupo_materia_id: int,
    parcial_id: int
):
    criterios = (
        db.query(DesgloseCriterio)
        .filter(
            DesgloseCriterio.id_grupo_materia == grupo_materia_id,
            DesgloseCriterio.id_parcial == parcial_id
        )
        .all()
    )

    return sorted(criterios, key=lambda criterio: CLAVES.index(criterio.clave))


def _calcular_alumnos(
    db: Session,
    grupo_materia_id: int,
    criterios
):
    """{id_carga: (puntajes, resumen)} para todos los alumnos del grupo."""
    configuracion = {
        criterio.clave: (criterio.porcentaje, criterio.puntos_max)
        for criterio in criterios
    }
    clave_por_criterio = {
        criterio.id_criterio: criterio.clave
        for criterio in criterios
    }
    puntajes_por_carga = {}

    if clave_por_criterio:
        filas = (
            db.query(DesglosePuntaje)
            .filter(
                DesglosePuntaje.id_criterio.in_(list(clave_por_criterio))
            )
            .all()
        )

        for fila in filas:
            puntajes_por_carga.setdefault(fila.id_carga, {})[
                clave_por_criterio[fila.id_criterio]
            ] = fila.puntaje

    resultado = {}

    for id_carga in _ids_cargas_grupo(db, grupo_materia_id):
        puntajes = puntajes_por_carga.get(id_carga, {})
        resultado[id_carga] = (
            puntajes,
            calcular_resumen(configuracion, puntajes)
        )

    return resultado


def _criterios_iniciales():
    return [
        {
            "clave": clave,
            "nombre": "Examen parcial" if clave == "EPA" else None,
            "porcentaje": EPA_PORCENTAJE_INICIAL if clave == "EPA" else None,
            "puntos_max": EPA_PUNTOS_INICIALES if clave == "EPA" else None
        }
        for clave in CLAVES
    ]


def _resumen_a_json(resumen: dict):
    return {
        **{clave: _a_float(resumen[clave]) for clave in CLAVES},
        "cpf": resumen["cpf"],
        "cpfl": resumen["cpfl"],
        "completo": resumen["completo"]
    }


def _build_respuesta(db: Session, grupo_materia_id: int, parcial_id: int):
    criterios = _criterios_guardados(db, grupo_materia_id, parcial_id)

    if not criterios:
        return {"criterios": _criterios_iniciales(), "alumnos": []}

    por_clave = {criterio.clave: criterio for criterio in criterios}
    calculos = _calcular_alumnos(db, grupo_materia_id, criterios)

    return {
        "criterios": [
            {
                "clave": clave,
                "nombre": por_clave[clave].nombre if clave in por_clave else None,
                "porcentaje": (
                    _a_float(por_clave[clave].porcentaje)
                    if clave in por_clave else None
                ),
                "puntos_max": (
                    _a_float(por_clave[clave].puntos_max)
                    if clave in por_clave else None
                )
            }
            for clave in CLAVES
        ],
        "alumnos": [
            {
                "id_carga": id_carga,
                "puntajes": {
                    clave: _a_float(valor)
                    for clave, valor in puntajes.items()
                },
                "resumen": _resumen_a_json(resumen)
            }
            for id_carga, (puntajes, resumen) in calculos.items()
        ]
    }


def get_desglose(db: Session, grupo_materia_id: int, parcial_id: int):
    return _build_respuesta(db, grupo_materia_id, parcial_id)


#---------------------validaciones
def _validar_criterios(criterios):
    vistos = set()
    en_uso = {}

    for criterio in criterios:
        if criterio.clave in vistos:
            raise _error(
                status.HTTP_400_BAD_REQUEST,
                f"El criterio {criterio.clave} esta repetido"
            )

        vistos.add(criterio.clave)
        porcentaje = (criterio.porcentaje or Decimal("0")).quantize(
            DOS_DECIMALES
        )

        if porcentaje < 0 or porcentaje > 100:
            raise _error(
                status.HTTP_400_BAD_REQUEST,
                f"El porcentaje de {criterio.clave} debe estar entre 0 y 100"
            )

        if porcentaje == 0:
            continue

        puntos_max = criterio.puntos_max

        if puntos_max is None or puntos_max <= 0 or puntos_max > 10000:
            raise _error(
                status.HTTP_400_BAD_REQUEST,
                f"{criterio.clave} necesita puntos maximos mayores a 0"
            )

        nombre = (criterio.nombre or "").strip()

        if criterio.clave != "EPA" and not nombre:
            raise _error(
                status.HTTP_400_BAD_REQUEST,
                f"{criterio.clave} necesita un nombre"
            )

        if len(nombre) > 100:
            raise _error(
                status.HTTP_400_BAD_REQUEST,
                f"El nombre de {criterio.clave} es demasiado largo"
            )

        en_uso[criterio.clave] = (
            nombre or None,
            porcentaje,
            puntos_max.quantize(DOS_DECIMALES)
        )

    if not en_uso:
        raise _error(
            status.HTTP_400_BAD_REQUEST,
            "Define al menos un criterio con porcentaje"
        )

    total = sum(datos[1] for datos in en_uso.values())

    if total != Decimal("100"):
        raise _error(
            status.HTTP_400_BAD_REQUEST,
            f"Los criterios deben sumar 100% (hoy suman {total}%)"
        )

    return en_uso


def _validar_puntajes(puntajes, en_uso, cargas_validas):
    for id_carga, por_clave in puntajes.items():
        if id_carga not in cargas_validas:
            raise _error(
                status.HTTP_403_FORBIDDEN,
                "La carga academica no pertenece al grupo indicado"
            )

        for clave, valor in por_clave.items():
            if valor is None or clave not in en_uso:
                continue

            maximo = en_uso[clave][2]

            if valor < 0 or valor > maximo:
                raise _error(
                    status.HTTP_400_BAD_REQUEST,
                    f"El puntaje de {clave} debe estar entre 0 y {maximo}"
                )


# ----------------------------------------------------------------- escritura

def _sincronizar_calificaciones(
    db: Session,
    parcial_id: int,
    calculos,
    usuario: Usuario
):
   
    ids_carga = list(calculos)

    if not ids_carga:
        return

    existentes = {
        calificacion.id_carga: calificacion
        for calificacion in (
            db.query(Calificacion)
            .filter(
                Calificacion.id_parcial == parcial_id,
                Calificacion.id_carga.in_(ids_carga)
            )
            .all()
        )
    }

    for id_carga, (puntajes, resumen) in calculos.items():
        if not puntajes:
            continue

        cpf = resumen["cpf"]
        calificacion = existentes.get(id_carga)

        if calificacion:
            calificacion.calificacion = cpf
            calificacion.capturado_por = usuario.id_usuario
        elif cpf is not None:
            db.add(
                Calificacion(
                    id_carga=id_carga,
                    id_parcial=parcial_id,
                    calificacion=cpf,
                    capturado_por=usuario.id_usuario
                )
            )


def guardar_desglose(
    db: Session,
    grupo_materia_id: int,
    parcial_id: int,
    datos: DesgloseGuardar,
    usuario: Usuario
):
    en_uso = _validar_criterios(datos.criterios)
    cargas_validas = set(_ids_cargas_grupo(db, grupo_materia_id))
    _validar_puntajes(datos.puntajes, en_uso, cargas_validas)

    try:
        existentes = {
            criterio.clave: criterio
            for criterio in _criterios_guardados(
                db, grupo_materia_id, parcial_id
            )
        }

        for clave in CLAVES:
            fila = existentes.get(clave)

            if clave not in en_uso:
                if fila:
                    db.delete(fila)
                    del existentes[clave]
                continue

            nombre, porcentaje, puntos_max = en_uso[clave]

            if fila:
                fila.nombre = nombre
                fila.porcentaje = porcentaje
                fila.puntos_max = puntos_max
                continue

            fila = DesgloseCriterio(
                id_grupo_materia=grupo_materia_id,
                id_parcial=parcial_id,
                clave=clave,
                nombre=nombre,
                porcentaje=porcentaje,
                puntos_max=puntos_max
            )
            db.add(fila)
            existentes[clave] = fila

        # La sesion usa autoflush=False: se necesita para tener los ids.
        db.flush()

        ids_criterio = [fila.id_criterio for fila in existentes.values()]
        puntajes_guardados = {}

        if ids_criterio:
            puntajes_guardados = {
                (fila.id_criterio, fila.id_carga): fila
                for fila in (
                    db.query(DesglosePuntaje)
                    .filter(DesglosePuntaje.id_criterio.in_(ids_criterio))
                    .all()
                )
            }

        for id_carga, por_clave in datos.puntajes.items():
            for clave, valor in por_clave.items():
                if clave not in en_uso:
                    continue

                id_criterio = existentes[clave].id_criterio
                fila = puntajes_guardados.get((id_criterio, id_carga))

                if valor is None:
                    if fila:
                        db.delete(fila)
                    continue

                valor = valor.quantize(DOS_DECIMALES)

                if fila:
                    fila.puntaje = valor
                else:
                    db.add(
                        DesglosePuntaje(
                            id_criterio=id_criterio,
                            id_carga=id_carga,
                            puntaje=valor
                        )
                    )

        db.flush()

        criterios = _criterios_guardados(db, grupo_materia_id, parcial_id)
        calculos = _calcular_alumnos(db, grupo_materia_id, criterios)
        _sincronizar_calificaciones(db, parcial_id, calculos, usuario)

        db.commit()
    except Exception:
        db.rollback()
        raise

    return _build_respuesta(db, grupo_materia_id, parcial_id)