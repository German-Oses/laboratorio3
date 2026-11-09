"""Comprobaciones complementarias a T1-T4: python -m unittest -v."""
import copy
import unittest

import numpy as np
import pandas as pd

import app
import motor


class PruebasMotor(unittest.TestCase):
    def setUp(self):
        self.recursos, self.usuarios, self.vectorizador, self.matriz = app.cargar_datos()

    def test_empates_por_id_y_solo_positivos(self):
        recursos = pd.DataFrame({
            "id": ["Z", "B", "A", "C"], "titulo": ["z", "b", "a", "c"],
            "etiquetas": ["python", "python", "python", "angular"],
        })
        vectorizador, matriz = motor.construir_indice(recursos)
        perfil = motor.crear_perfil("python", vectorizador)
        resultado = motor.recomendar(perfil, recursos, matriz, vectorizador)
        self.assertEqual([r["id"] for r in resultado], ["A", "B", "Z"])
        self.assertEqual(len(motor.recomendar(perfil, recursos, matriz, vectorizador, 2)), 2)
        self.assertEqual(motor.recomendar(perfil, recursos, matriz, vectorizador, 0), [])

    def test_id_desconocido_no_modifica_estado(self):
        estado = app.crear_estado(self.usuarios, self.vectorizador)
        historial = app.crear_historial(self.usuarios)
        anterior = copy.deepcopy(estado)
        with self.assertRaisesRegex(ValueError, "No existe el recurso"):
            app.registrar_interes(estado, "u1", "R99", self.recursos, self.matriz, historial)
        for usuario in estado:
            np.testing.assert_array_equal(estado[usuario], anterior[usuario])
            self.assertEqual(historial[usuario], [])

    def test_actualizaciones_sucesivas_y_entradas_intactas(self):
        perfil = motor.crear_perfil("python datos pandas", self.vectorizador)
        original = perfil.copy()
        recurso = self.matriz[3].copy()
        matriz_original = self.matriz.copy()
        primero = motor.actualizar_perfil(perfil, recurso)
        segundo = motor.actualizar_perfil(primero, recurso)
        self.assertEqual(primero.ndim, 1)
        self.assertAlmostEqual(np.linalg.norm(primero), 1)
        self.assertAlmostEqual(np.linalg.norm(segundo), 1)
        self.assertGreater(motor.calcular_puntuaciones(segundo, self.matriz)[3],
                           motor.calcular_puntuaciones(primero, self.matriz)[3])
        np.testing.assert_array_equal(perfil, original)
        np.testing.assert_array_equal(self.matriz, matriz_original)
        cero = np.zeros_like(perfil)
        np.testing.assert_array_equal(motor.actualizar_perfil(cero, cero), cero)


if __name__ == "__main__":
    unittest.main()
