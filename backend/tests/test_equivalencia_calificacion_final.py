"""Compara la formula del modulo esquema_evaluacion con la que tenia
routers/calificaciones.py (copiada aqui tal cual como referencia).

Resultado esperado: identicas, salvo en empates exactos de redondeo
(p. ej. 80.125), donde la anterior usaba round() de flotantes y la nueva usa
"mitad hacia arriba".
"""

import random
import unittest
from decimal import Decimal
from types import SimpleNamespace

from app.services.esquema_evaluacion import (
    calcular_calificacion_final,
    es_aprobatoria
)


def formula_anterior(calificaciones, parciales_por_id):
    calificaciones_validas = [
        c for c in calificaciones if c.calificacion is not None
    ]

    if not calificaciones_validas:
        return None

    total = 0
    peso_total = 0

    for c in calificaciones_validas:
        parcial = parciales_por_id.get(c.id_parcial)
        peso = (
            float(parcial.porcentaje)
            if parcial and parcial.porcentaje is not None
            else 0
        )
        total += float(c.calificacion) * peso
        peso_total += peso

    if peso_total > 0:
        return round(total / peso_total, 2)

    promedio = sum(
        float(c.calificacion) for c in calificaciones_validas
    ) / len(calificaciones_validas)

    return round(promedio, 2)


def formula_nueva(calificaciones, pesos):
    """Igual que _calcular_calificacion_final del router."""
    final = calcular_calificacion_final(
        {c.id_parcial: c.calificacion for c in calificaciones},
        pesos
    )

    return float(final) if final is not None else None


PARCIALES = {
    1: SimpleNamespace(id_parcial=1, porcentaje=Decimal("25")),
    2: SimpleNamespace(id_parcial=2, porcentaje=Decimal("25")),
    3: SimpleNamespace(id_parcial=3, porcentaje=Decimal("50")),
    4: SimpleNamespace(id_parcial=4, porcentaje=Decimal("100")),
}
PESOS = {i: p.porcentaje for i, p in PARCIALES.items()}


def _cal(id_parcial, valor):
    return SimpleNamespace(id_parcial=id_parcial, calificacion=valor)


def _es_empate_exacto(calificaciones):
    """True si el resultado exacto cae justo en medio de dos centesimas."""
    validas = {
        c.id_parcial: Decimal(str(c.calificacion))
        for c in calificaciones if c.calificacion is not None
    }

    if not validas:
        return False

    peso = sum(PESOS[i] for i in validas)
    exacto = sum(v * PESOS[i] for i, v in validas.items()) / peso

    return (exacto * 1000) % 10 == 5 and exacto * 1000 == int(exacto * 1000)


class EquivalenciaCalificacionFinal(unittest.TestCase):
    def test_casos_conocidos(self):
        casos = [
            [_cal(1, 80), _cal(2, 90), _cal(3, 100)],
            [_cal(1, 70), _cal(2, 70), _cal(3, 70)],
            [_cal(1, 100), _cal(2, None), _cal(3, 60)],
            [_cal(1, None), _cal(2, None), _cal(3, None)],
            [],
            [_cal(1, 0), _cal(2, 0), _cal(3, 0)],
            [_cal(3, 85.5)],
        ]

        for calificaciones in casos:
            with self.subTest(calificaciones=calificaciones):
                self.assertEqual(
                    formula_anterior(calificaciones, PARCIALES),
                    formula_nueva(calificaciones, PESOS)
                )

    def test_aleatorio_20000_casos(self):
        azar = random.Random(2026)
        diferencias = 0
        empates = 0

        for _ in range(20000):
            calificaciones = []

            for id_parcial in (1, 2, 3):
                if azar.random() < 0.2:
                    valor = None
                else:
                    valor = round(azar.uniform(0, 100), azar.choice([0, 1, 2]))

                calificaciones.append(_cal(id_parcial, valor))

            anterior = formula_anterior(calificaciones, PARCIALES)
            nueva = formula_nueva(calificaciones, PESOS)

            if _es_empate_exacto(calificaciones):
                empates += 1

            if anterior != nueva:
                diferencias += 1
                self.assertTrue(
                    _es_empate_exacto(calificaciones),
                    f"Diferencia fuera de un empate: {calificaciones} "
                    f"anterior={anterior} nueva={nueva}"
                )
                self.assertAlmostEqual(anterior, nueva, delta=0.0100001)

        print(
            f"\n  20000 casos: {diferencias} difieren, "
            f"todos empates exactos de redondeo ({empates} empates en total)"
        )

    def test_sabatina_un_solo_parcial_al_100(self):
        for valor in (0, 59.99, 70, 85.5, 100):
            with self.subTest(valor=valor):
                self.assertEqual(
                    formula_nueva([_cal(4, valor)], PESOS),
                    float(Decimal(str(valor)).quantize(Decimal("0.01")))
                )

    def test_calificacion_de_parcial_desconocido_pesa_cero(self):
        calificaciones = [_cal(1, 80), _cal(99, 10)]

        self.assertEqual(
            formula_anterior(calificaciones, PARCIALES),
            formula_nueva(calificaciones, PESOS)
        )

    def test_aprobatoria_igual_que_el_70_anterior(self):
        for valor in (69.99, 70, 70.01, 100, 0):
            self.assertEqual(es_aprobatoria(valor), valor >= 70)


if __name__ == "__main__":
    unittest.main()