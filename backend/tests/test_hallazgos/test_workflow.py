"""
Tests del workflow de hallazgos — Sprint 5.
Verifica las transiciones de estado validas e invalidas.
"""

import pytest

from app.services.hallazgo_service import (
    ESTADOS_HALLAZGO,
    TRANSICIONES_VALIDAS,
    FASE_REQUERIDA,
    TIPOS_CONNOTACION,
)


class TestTransicionesWorkflow:
    """Tests para la maquina de estados del workflow."""

    def test_borrador_puede_ir_a_en_revision(self):
        """BORRADOR -> EN_REVISION es valido."""
        assert "EN_REVISION" in TRANSICIONES_VALIDAS["BORRADOR"]

    def test_borrador_no_puede_ir_a_aprobado(self):
        """BORRADOR -> APROBADO no es valido (debe pasar por el workflow)."""
        assert "APROBADO" not in TRANSICIONES_VALIDAS["BORRADOR"]

    def test_en_revision_puede_devolver_a_borrador(self):
        """EN_REVISION -> BORRADOR (devolucion) es valido."""
        assert "BORRADOR" in TRANSICIONES_VALIDAS["EN_REVISION"]

    def test_en_revision_puede_trasladar_observacion(self):
        """EN_REVISION -> OBSERVACION_TRASLADADA es valido."""
        assert "OBSERVACION_TRASLADADA" in TRANSICIONES_VALIDAS["EN_REVISION"]

    def test_en_revision_puede_configurar(self):
        """EN_REVISION -> HALLAZGO_CONFIGURADO (sin observacion) es valido."""
        assert "HALLAZGO_CONFIGURADO" in TRANSICIONES_VALIDAS["EN_REVISION"]

    def test_observacion_trasladada_espera_respuesta(self):
        """OBSERVACION_TRASLADADA -> RESPUESTA_RECIBIDA es valido."""
        assert "RESPUESTA_RECIBIDA" in TRANSICIONES_VALIDAS["OBSERVACION_TRASLADADA"]

    def test_respuesta_puede_configurar_o_devolver(self):
        """RESPUESTA_RECIBIDA puede ir a HALLAZGO_CONFIGURADO o EN_REVISION."""
        trans = TRANSICIONES_VALIDAS["RESPUESTA_RECIBIDA"]
        assert "HALLAZGO_CONFIGURADO" in trans
        assert "EN_REVISION" in trans

    def test_configurado_puede_aprobar(self):
        """HALLAZGO_CONFIGURADO -> APROBADO es valido."""
        assert "APROBADO" in TRANSICIONES_VALIDAS["HALLAZGO_CONFIGURADO"]

    def test_configurado_puede_devolver(self):
        """HALLAZGO_CONFIGURADO -> EN_REVISION (devolucion) es valido."""
        assert "EN_REVISION" in TRANSICIONES_VALIDAS["HALLAZGO_CONFIGURADO"]

    def test_aprobado_puede_trasladar(self):
        """APROBADO -> TRASLADADO es valido."""
        assert "TRASLADADO" in TRANSICIONES_VALIDAS["APROBADO"]

    def test_trasladado_es_estado_final(self):
        """TRASLADADO no tiene transiciones salientes."""
        assert TRANSICIONES_VALIDAS["TRASLADADO"] == []

    def test_todos_los_estados_tienen_transiciones(self):
        """Todos los estados deben estar en el diccionario de transiciones."""
        for estado in ESTADOS_HALLAZGO:
            assert estado in TRANSICIONES_VALIDAS, f"{estado} no esta en TRANSICIONES_VALIDAS"

    def test_no_hay_transiciones_reflexivas(self):
        """Un estado no puede transicionar a si mismo."""
        for estado, destinos in TRANSICIONES_VALIDAS.items():
            assert estado not in destinos, f"{estado} tiene transicion reflexiva"

    def test_transiciones_destino_validas(self):
        """Todos los destinos de transicion son estados validos."""
        for estado, destinos in TRANSICIONES_VALIDAS.items():
            for destino in destinos:
                assert destino in ESTADOS_HALLAZGO, (
                    f"Transicion {estado} -> {destino}: destino no es estado valido"
                )


class TestFasesWorkflow:
    """Tests para las fases del workflow (auditor/supervisor/coordinador/director)."""

    def test_en_revision_requiere_auditor(self):
        """La fase para EN_REVISION es 'auditor'."""
        assert FASE_REQUERIDA.get("EN_REVISION") == "auditor"

    def test_observacion_requiere_supervisor(self):
        """La fase para OBSERVACION_TRASLADADA es 'supervisor'."""
        assert FASE_REQUERIDA.get("OBSERVACION_TRASLADADA") == "supervisor"

    def test_configurado_requiere_coordinador(self):
        """La fase para HALLAZGO_CONFIGURADO es 'coordinador'."""
        assert FASE_REQUERIDA.get("HALLAZGO_CONFIGURADO") == "coordinador"

    def test_aprobado_requiere_director(self):
        """La fase para APROBADO es 'director'."""
        assert FASE_REQUERIDA.get("APROBADO") == "director"

    def test_trasladado_requiere_director(self):
        """La fase para TRASLADADO es 'director'."""
        assert FASE_REQUERIDA.get("TRASLADADO") == "director"


class TestTiposConnotacion:
    """Tests para los tipos de connotacion."""

    def test_4_tipos_connotacion(self):
        """Hay exactamente 4 tipos de connotacion."""
        assert len(TIPOS_CONNOTACION) == 4

    def test_tipos_esperados(self):
        """Verifica que estan los 4 tipos esperados."""
        esperados = {"administrativo", "fiscal", "disciplinario", "penal"}
        assert TIPOS_CONNOTACION == esperados


class TestFlujoCamino:
    """Tests para verificar caminos completos del workflow."""

    def test_camino_directo_sin_observacion(self):
        """Camino: BORRADOR -> EN_REVISION -> HALLAZGO_CONFIGURADO -> APROBADO -> TRASLADADO."""
        camino = ["BORRADOR", "EN_REVISION", "HALLAZGO_CONFIGURADO", "APROBADO", "TRASLADADO"]
        for i in range(len(camino) - 1):
            actual = camino[i]
            siguiente = camino[i + 1]
            assert siguiente in TRANSICIONES_VALIDAS[actual], (
                f"Transicion {actual} -> {siguiente} no valida"
            )

    def test_camino_con_observacion(self):
        """Camino con observacion trasladada y respuesta."""
        camino = [
            "BORRADOR", "EN_REVISION", "OBSERVACION_TRASLADADA",
            "RESPUESTA_RECIBIDA", "HALLAZGO_CONFIGURADO", "APROBADO", "TRASLADADO",
        ]
        for i in range(len(camino) - 1):
            actual = camino[i]
            siguiente = camino[i + 1]
            assert siguiente in TRANSICIONES_VALIDAS[actual], (
                f"Transicion {actual} -> {siguiente} no valida en camino con observacion"
            )

    def test_camino_con_devolucion(self):
        """Camino con devolucion de EN_REVISION a BORRADOR."""
        assert "BORRADOR" in TRANSICIONES_VALIDAS["EN_REVISION"]
        assert "EN_REVISION" in TRANSICIONES_VALIDAS["BORRADOR"]
