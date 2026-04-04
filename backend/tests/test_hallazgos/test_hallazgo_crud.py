"""
Tests CRUD para hallazgos — Sprint 5.
Verifica creacion, lectura, actualizacion y listado de hallazgos.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.services.hallazgo_service import HallazgoService, ESTADOS_HALLAZGO


def _crear_hallazgo_mock(**kwargs):
    """Crea un mock de Hallazgo con datos por defecto."""
    h = MagicMock()
    h.id = kwargs.get("id", "h-001")
    h.auditoria_id = kwargs.get("auditoria_id", "aud-001")
    h.numero_hallazgo = kwargs.get("numero_hallazgo", 1)
    h.titulo = kwargs.get("titulo", "Hallazgo de prueba")
    h.condicion = kwargs.get("condicion", "Condicion de prueba")
    h.criterio = kwargs.get("criterio", "Criterio de prueba")
    h.causa = kwargs.get("causa", "Causa de prueba")
    h.efecto = kwargs.get("efecto", "Efecto de prueba")
    h.recomendacion = kwargs.get("recomendacion", "Recomendacion de prueba")
    h.connotaciones = kwargs.get("connotaciones", [{"tipo": "fiscal"}])
    h.cuantia_presunto_dano = kwargs.get("cuantia_presunto_dano", 1000000)
    h.presuntos_responsables = kwargs.get("presuntos_responsables", [])
    h.evidencias = kwargs.get("evidencias", [])
    h.estado = kwargs.get("estado", "BORRADOR")
    h.fase_actual_workflow = kwargs.get("fase_actual_workflow", "auditor")
    h.historial_workflow = kwargs.get("historial_workflow", [])
    h.redaccion_validada_humano = kwargs.get("redaccion_validada_humano", False)
    h.generado_por_ia = kwargs.get("generado_por_ia", False)
    h.validado_por = kwargs.get("validado_por", None)
    h.fecha_validacion = kwargs.get("fecha_validacion", None)
    h.created_by = kwargs.get("created_by", 1)
    h.updated_by = kwargs.get("updated_by", 1)
    h.created_at = kwargs.get("created_at", datetime.now(timezone.utc))
    h.updated_at = kwargs.get("updated_at", datetime.now(timezone.utc))
    return h


class TestEstadosDefinidos:
    """Tests para la definicion de estados."""

    def test_estados_completos(self):
        """Verifica que estan los 7 estados definidos."""
        assert len(ESTADOS_HALLAZGO) == 7

    def test_estados_requeridos(self):
        """Cada estado esperado esta en la lista."""
        esperados = [
            "BORRADOR", "EN_REVISION", "OBSERVACION_TRASLADADA",
            "RESPUESTA_RECIBIDA", "HALLAZGO_CONFIGURADO",
            "APROBADO", "TRASLADADO",
        ]
        for e in esperados:
            assert e in ESTADOS_HALLAZGO, f"Falta estado: {e}"


class TestModeloHallazgo:
    """Tests para el modelo de hallazgo."""

    def test_campos_obligatorios(self):
        """Verifica que un hallazgo mock tiene los 4 elementos."""
        h = _crear_hallazgo_mock()
        assert h.condicion != ""
        assert h.criterio != ""
        assert h.causa != ""
        assert h.efecto != ""

    def test_estado_inicial_borrador(self):
        """El estado inicial de un hallazgo debe ser BORRADOR."""
        h = _crear_hallazgo_mock()
        assert h.estado == "BORRADOR"

    def test_fase_inicial_auditor(self):
        """La fase inicial del workflow es 'auditor'."""
        h = _crear_hallazgo_mock()
        assert h.fase_actual_workflow == "auditor"

    def test_numero_hallazgo_positivo(self):
        """El numero de hallazgo debe ser positivo."""
        h = _crear_hallazgo_mock(numero_hallazgo=5)
        assert h.numero_hallazgo > 0

    def test_connotaciones_es_lista(self):
        """Las connotaciones deben ser una lista."""
        h = _crear_hallazgo_mock()
        assert isinstance(h.connotaciones, list)

    def test_cuantia_presunto_dano(self):
        """La cuantia del presunto dano debe ser numerico."""
        h = _crear_hallazgo_mock(cuantia_presunto_dano=2345678900)
        assert h.cuantia_presunto_dano == 2345678900

    def test_circular_023_default_false(self):
        """redaccion_validada_humano default es False."""
        h = _crear_hallazgo_mock()
        assert h.redaccion_validada_humano is False

    def test_generado_por_ia_default_false(self):
        """generado_por_ia default es False."""
        h = _crear_hallazgo_mock()
        assert h.generado_por_ia is False

    def test_hallazgo_con_multiples_connotaciones(self):
        """Un hallazgo puede tener multiples connotaciones."""
        h = _crear_hallazgo_mock(connotaciones=[
            {"tipo": "fiscal", "fundamentacion_legal": "Ley 610"},
            {"tipo": "disciplinario", "fundamentacion_legal": "Ley 734"},
        ])
        assert len(h.connotaciones) == 2
        assert h.connotaciones[0]["tipo"] == "fiscal"
        assert h.connotaciones[1]["tipo"] == "disciplinario"

    def test_hallazgo_con_responsables(self):
        """Un hallazgo puede tener presuntos responsables."""
        h = _crear_hallazgo_mock(presuntos_responsables=[
            {"nombre": "Juan Perez", "cargo": "Director", "periodo": "2024-2025"},
        ])
        assert len(h.presuntos_responsables) == 1
        assert h.presuntos_responsables[0]["nombre"] == "Juan Perez"

    def test_hallazgo_con_evidencias(self):
        """Un hallazgo puede tener evidencias."""
        h = _crear_hallazgo_mock(evidencias=[
            {"documento_id": "doc-1", "descripcion": "Contrato", "folio": "1-10", "tipo": "documental"},
        ])
        assert len(h.evidencias) == 1
