"""Pruebas del esquema de evaluacion (no necesitan base de datos).

Ejecutar desde la carpeta backend:
    python -m unittest discover -s tests -t . -v
"""

import unittest
from decimal import Decimal
from types import SimpleNamespace

from app.services.esquema_evaluacion import (
    EsquemaEvaluacionError,
    calcular_calificacion_final,
    construir_esquema,
    es_aprobatoria,
)


def parcial(id_parcial, nombre, porcentaje, modalidad="CUATRIMESTRAL"):
    return SimpleNamespace(
        id_parcial=id_parcial,
        nombre=nombre,
        porcentaje=porcentaje,
        modalidad=modalidad,
    )


def cuatrimestral():
    return construir_esquema(
        "CUATRIMESTRAL",
        [
            parcial(1, "Primer Parcial", 25),
            parcial(2, "Segundo Parcial", 25),
            parcial(3, "Tercer Parcial", 50),
        ],
    )


def sabatina():
    return construir_esquema(
        "SABATINA", [parcial(7, "Calificación final", 100, "SABATINA")]
    )


class ConstruccionDelEsquema(unittest.TestCase):
    def test_cuatrimestral_valido(self):
        esquema = cuatrimestral()
        self.assertEqual(esquema.ids_parciales, (1, 2, 3))
        self.assertFalse(esquema.evaluacion_unica)

    def test_sabatina_valida(self):
        esquema = sabatina()
        self.assertEqual(esquema.ids_parciales, (7,))
        self.assertTrue(esquema.evaluacion_unica)

    def test_los_pesos_deben_sumar_100(self):
        with self.assertRaises(EsquemaEvaluacionError):
            construir_esquema(
                "CUATRIMESTRAL",
                [parcial(1, "P1", 25), parcial(2, "P2", 25), parcial(3, "P3", 40)],
            )

    def test_sin_parciales_es_error(self):
        with self.assertRaises(EsquemaEvaluacionError):
            construir_esquema("SABATINA", [])

    def test_modalidad_invalida(self):
        with self.assertRaises(EsquemaEvaluacionError):
            construir_esquema("NOCTURNA", [parcial(1, "P1", 100)])

    def test_ordena_por_id(self):
        esquema = construir_esquema(
            "CUATRIMESTRAL",
            [parcial(3, "P3", 50), parcial(1, "P1", 25), parcial(2, "P2", 25)],
        )
        self.assertEqual(esquema.ids_parciales, (1, 2, 3))


class PertenenciaYDesglose(unittest.TestCase):
    def test_un_parcial_ajeno_se_rechaza(self):
        # No se puede guardar una calificacion sabatina bajo un parcial
        # cuatrimestral, ni al reves.
        with self.assertRaises(EsquemaEvaluacionError):
            sabatina().validar_parcial(1)
        with self.assertRaises(EsquemaEvaluacionError):
            cuatrimestral().validar_parcial(7)

    def test_un_parcial_propio_se_acepta(self):
        cuatrimestral().validar_parcial(2)
        sabatina().validar_parcial(7)

    def test_desglose_cuatrimestral_solo_primero_y_segundo(self):
        esquema = cuatrimestral()
        self.assertTrue(esquema.admite_desglose(1))
        self.assertTrue(esquema.admite_desglose(2))
        self.assertFalse(esquema.admite_desglose(3))

    def test_la_sabatina_no_admite_desglose(self):
        self.assertFalse(sabatina().admite_desglose(7))


class CalificacionFinal(unittest.TestCase):
    def test_ponderada_con_los_tres_parciales(self):
        # 80*25% + 90*25% + 70*50% = 77.5
        final = cuatrimestral().calificacion_final({1: 80, 2: 90, 3: 70})
        self.assertEqual(final, Decimal("77.50"))

    def test_con_dos_parciales_pondera_solo_lo_capturado(self):
        final = cuatrimestral().calificacion_final({1: 80, 2: 90, 3: None})
        self.assertEqual(final, Decimal("85.00"))

    def test_sin_calificaciones_es_none(self):
        self.assertIsNone(cuatrimestral().calificacion_final({}))
        self.assertIsNone(
            cuatrimestral().calificacion_final({1: None, 2: None, 3: None})
        )

    def test_la_sabatina_es_la_misma_calificacion(self):
        self.assertEqual(sabatina().calificacion_final({7: 92}), Decimal("92.00"))
        self.assertEqual(
            sabatina().calificacion_final({7: Decimal("87.5")}), Decimal("87.50")
        )

    def test_pesos_en_cero_usa_promedio_simple(self):
        final = calcular_calificacion_final({1: 80, 2: 90}, {1: 0, 2: 0})
        self.assertEqual(final, Decimal("85.00"))

    def test_redondeo_mitad_hacia_arriba(self):
        # (80.5*25 + 80*25 + 80*50) / 100 = 80.125 -> 80.13
        final = cuatrimestral().calificacion_final({1: 80.5, 2: 80, 3: 80})
        self.assertEqual(final, Decimal("80.13"))

    def test_acepta_decimal_float_y_entero(self):
        final = cuatrimestral().calificacion_final(
            {1: Decimal("80"), 2: 90.0, 3: 70}
        )
        self.assertEqual(final, Decimal("77.50"))


class Aprobacion(unittest.TestCase):
    def test_limite_de_aprobacion(self):
        self.assertFalse(es_aprobatoria(69.99))
        self.assertTrue(es_aprobatoria(70))
        self.assertTrue(es_aprobatoria("70"))
        self.assertTrue(es_aprobatoria(Decimal("100")))

    def test_none_no_aprueba(self):
        self.assertFalse(es_aprobatoria(None))


if __name__ == "__main__":
    unittest.main()