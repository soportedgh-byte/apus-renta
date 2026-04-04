"""
Tests para cumplimiento de Circular 023 — Sprint 5.
Verifica que la validacion humana es obligatoria antes de aprobar hallazgos
generados con asistencia de IA.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from app.services.hallazgo_service import HallazgoService


def _mock_db():
    """Crea mock de AsyncSession."""
    db = AsyncMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    return db


def _mock_hallazgo_ia(**kwargs):
    """Crea mock de hallazgo generado por IA."""
    h = MagicMock()
    h.id = kwargs.get("id", "h-ia-001")
    h.auditoria_id = "aud-001"
    h.numero_hallazgo = 1
    h.titulo = "Hallazgo generado por IA"
    h.condicion = "Condicion generada"
    h.criterio = "Criterio generado"
    h.causa = "Causa generada"
    h.efecto = "Efecto generado"
    h.recomendacion = "Recomendacion generada"
    h.connotaciones = [{"tipo": "fiscal"}]
    h.cuantia_presunto_dano = 1000000
    h.presuntos_responsables = []
    h.evidencias = []
    h.estado = kwargs.get("estado", "HALLAZGO_CONFIGURADO")
    h.fase_actual_workflow = "director"
    h.historial_workflow = kwargs.get("historial_workflow", [])
    h.redaccion_validada_humano = kwargs.get("redaccion_validada_humano", False)
    h.generado_por_ia = kwargs.get("generado_por_ia", True)
    h.validado_por = kwargs.get("validado_por", None)
    h.fecha_validacion = kwargs.get("fecha_validacion", None)
    h.created_by = 1
    h.updated_by = 1
    return h


class TestCircular023Validacion:
    """Tests de la Circular 023 — Validacion humana obligatoria."""

    @pytest.mark.asyncio
    async def test_no_aprobar_sin_validacion_humana(self):
        """NO se puede aprobar si redaccion_validada_humano = False."""
        db = _mock_db()
        h = _mock_hallazgo_ia(
            redaccion_validada_humano=False,
            generado_por_ia=True,
        )

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = h
        db.execute.return_value = result_mock

        servicio = HallazgoService(db)
        with pytest.raises(ValueError, match="Circular 023"):
            await servicio.aprobar_hallazgo("h-ia-001", 1, rol_usuario="director_dvf")

    @pytest.mark.asyncio
    async def test_aprobar_con_validacion_humana(self):
        """Se PUEDE aprobar si redaccion_validada_humano = True."""
        db = _mock_db()
        h = _mock_hallazgo_ia(
            redaccion_validada_humano=True,
            generado_por_ia=True,
            historial_workflow=[],
        )

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = h
        db.execute.return_value = result_mock

        servicio = HallazgoService(db)
        resultado = await servicio.aprobar_hallazgo(
            "h-ia-001", 1, rol_usuario="director_dvf",
        )
        assert resultado is not None

    @pytest.mark.asyncio
    async def test_validar_redaccion_marca_true(self):
        """validar_redaccion marca el hallazgo como validado."""
        db = _mock_db()
        h = _mock_hallazgo_ia(
            redaccion_validada_humano=False,
            historial_workflow=[],
        )

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = h
        db.execute.return_value = result_mock

        servicio = HallazgoService(db)
        resultado = await servicio.validar_redaccion("h-ia-001", usuario_id=2)

        assert resultado.redaccion_validada_humano is True
        assert resultado.validado_por == 2
        assert resultado.fecha_validacion is not None

    @pytest.mark.asyncio
    async def test_validar_redaccion_registra_historial(self):
        """validar_redaccion registra la accion en historial_workflow."""
        db = _mock_db()
        h = _mock_hallazgo_ia(
            redaccion_validada_humano=False,
            historial_workflow=[],
        )

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = h
        db.execute.return_value = result_mock

        servicio = HallazgoService(db)
        resultado = await servicio.validar_redaccion("h-ia-001", usuario_id=2)

        historial = resultado.historial_workflow
        assert len(historial) == 1
        assert "Circular 023" in historial[0]["accion"]

    @pytest.mark.asyncio
    async def test_hallazgo_no_ia_tambien_requiere_validacion(self):
        """Incluso hallazgos no-IA requieren validacion (campo es False por defecto)."""
        db = _mock_db()
        h = _mock_hallazgo_ia(
            generado_por_ia=False,
            redaccion_validada_humano=False,
        )

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = h
        db.execute.return_value = result_mock

        servicio = HallazgoService(db)
        # Circular 023 check aplica a TODOS los hallazgos
        with pytest.raises(ValueError, match="no ha sido validada"):
            await servicio.aprobar_hallazgo("h-ia-001", 1, rol_usuario="director_dvf")


class TestCircular023Mensaje:
    """Tests para mensajes de error de la Circular 023."""

    @pytest.mark.asyncio
    async def test_mensaje_error_incluye_referencia_circular(self):
        """El mensaje de error debe mencionar la Circular 023."""
        db = _mock_db()
        h = _mock_hallazgo_ia(redaccion_validada_humano=False)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = h
        db.execute.return_value = result_mock

        servicio = HallazgoService(db)
        try:
            await servicio.aprobar_hallazgo("h-ia-001", 1, rol_usuario="director_dvf")
            pytest.fail("Debio lanzar ValueError")
        except ValueError as e:
            msg = str(e)
            assert "Circular 023" in msg
            assert "VI.1.4" in msg or "IA" in msg

    @pytest.mark.asyncio
    async def test_mensaje_error_incluye_referencia_ia(self):
        """El mensaje menciona que la redaccion no puede basarse solo en IA."""
        db = _mock_db()
        h = _mock_hallazgo_ia(redaccion_validada_humano=False)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = h
        db.execute.return_value = result_mock

        servicio = HallazgoService(db)
        try:
            await servicio.aprobar_hallazgo("h-ia-001", 1, rol_usuario="director_dvf")
            pytest.fail("Debio lanzar ValueError")
        except ValueError as e:
            msg = str(e)
            assert "IA" in msg
