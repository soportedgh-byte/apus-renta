"""
Tests de permisos para hallazgos — Sprint 5.
Verifica restricciones de rol y estado para cada accion.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.hallazgo_service import (
    HallazgoService,
    FASE_REQUERIDA,
    TRANSICIONES_VALIDAS,
)


def _mock_db():
    """Crea mock de AsyncSession."""
    db = AsyncMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    return db


def _mock_hallazgo(**kwargs):
    """Crea mock de Hallazgo."""
    h = MagicMock()
    h.id = kwargs.get("id", "h-001")
    h.auditoria_id = "aud-001"
    h.numero_hallazgo = 1
    h.titulo = "Test"
    h.condicion = "Test condicion"
    h.criterio = "Test criterio"
    h.causa = "Test causa"
    h.efecto = "Test efecto"
    h.recomendacion = None
    h.connotaciones = kwargs.get("connotaciones", [])
    h.cuantia_presunto_dano = None
    h.presuntos_responsables = []
    h.evidencias = []
    h.estado = kwargs.get("estado", "BORRADOR")
    h.fase_actual_workflow = kwargs.get("fase_actual_workflow", "auditor")
    h.historial_workflow = kwargs.get("historial_workflow", [])
    h.redaccion_validada_humano = kwargs.get("redaccion_validada_humano", False)
    h.generado_por_ia = kwargs.get("generado_por_ia", False)
    h.validado_por = None
    h.fecha_validacion = None
    h.created_by = 1
    h.updated_by = 1
    return h


class TestPermisosActualizacion:
    """Tests de permisos para actualizacion de hallazgos."""

    @pytest.mark.asyncio
    async def test_actualizar_en_borrador_permitido(self):
        """Se puede actualizar un hallazgo en BORRADOR."""
        db = _mock_db()
        h = _mock_hallazgo(estado="BORRADOR")

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = h
        db.execute.return_value = result_mock

        servicio = HallazgoService(db)
        resultado = await servicio.actualizar_hallazgo("h-001", {"titulo": "Nuevo"}, 1)
        assert resultado is not None

    @pytest.mark.asyncio
    async def test_actualizar_en_revision_permitido(self):
        """Se puede actualizar un hallazgo en EN_REVISION."""
        db = _mock_db()
        h = _mock_hallazgo(estado="EN_REVISION")

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = h
        db.execute.return_value = result_mock

        servicio = HallazgoService(db)
        resultado = await servicio.actualizar_hallazgo("h-001", {"titulo": "Editado"}, 1)
        assert resultado is not None

    @pytest.mark.asyncio
    async def test_actualizar_en_aprobado_prohibido(self):
        """NO se puede actualizar un hallazgo APROBADO."""
        db = _mock_db()
        h = _mock_hallazgo(estado="APROBADO")

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = h
        db.execute.return_value = result_mock

        servicio = HallazgoService(db)
        with pytest.raises(ValueError, match="No se puede editar"):
            await servicio.actualizar_hallazgo("h-001", {"titulo": "Intento"}, 1)

    @pytest.mark.asyncio
    async def test_actualizar_en_trasladado_prohibido(self):
        """NO se puede actualizar un hallazgo TRASLADADO."""
        db = _mock_db()
        h = _mock_hallazgo(estado="TRASLADADO")

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = h
        db.execute.return_value = result_mock

        servicio = HallazgoService(db)
        with pytest.raises(ValueError, match="No se puede editar"):
            await servicio.actualizar_hallazgo("h-001", {"titulo": "Intento"}, 1)


class TestPermisosAprobacion:
    """Tests de permisos para aprobacion."""

    @pytest.mark.asyncio
    async def test_no_director_no_puede_aprobar(self):
        """Solo el director puede aprobar."""
        db = _mock_db()
        h = _mock_hallazgo(
            estado="HALLAZGO_CONFIGURADO",
            redaccion_validada_humano=True,
        )

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = h
        db.execute.return_value = result_mock

        servicio = HallazgoService(db)
        with pytest.raises(PermissionError, match="Solo el Director DVF"):
            await servicio.aprobar_hallazgo("h-001", 1, rol_usuario="auditor")

    @pytest.mark.asyncio
    async def test_director_puede_aprobar_si_validado(self):
        """El director puede aprobar si la redaccion esta validada."""
        db = _mock_db()
        h = _mock_hallazgo(
            estado="HALLAZGO_CONFIGURADO",
            redaccion_validada_humano=True,
            historial_workflow=[],
        )

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = h
        db.execute.return_value = result_mock

        servicio = HallazgoService(db)
        resultado = await servicio.aprobar_hallazgo(
            "h-001", 1, rol_usuario="director_dvf"
        )
        assert resultado is not None

    @pytest.mark.asyncio
    async def test_aprobar_estado_incorrecto(self):
        """No se puede aprobar un hallazgo que no este en HALLAZGO_CONFIGURADO."""
        db = _mock_db()
        h = _mock_hallazgo(
            estado="EN_REVISION",
            redaccion_validada_humano=True,
        )

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = h
        db.execute.return_value = result_mock

        servicio = HallazgoService(db)
        with pytest.raises(ValueError, match="HALLAZGO_CONFIGURADO"):
            await servicio.aprobar_hallazgo("h-001", 1, rol_usuario="director_dvf")


class TestPermisosTransicion:
    """Tests para transiciones invalidas."""

    @pytest.mark.asyncio
    async def test_borrador_no_puede_ir_a_aprobado(self):
        """BORRADOR -> APROBADO no es valido."""
        db = _mock_db()
        h = _mock_hallazgo(estado="BORRADOR")

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = h
        db.execute.return_value = result_mock

        servicio = HallazgoService(db)
        with pytest.raises(ValueError, match="Transicion invalida"):
            await servicio.cambiar_estado("h-001", "APROBADO", 1)

    @pytest.mark.asyncio
    async def test_trasladado_no_puede_cambiar(self):
        """TRASLADADO no tiene transiciones salientes."""
        db = _mock_db()
        h = _mock_hallazgo(estado="TRASLADADO")

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = h
        db.execute.return_value = result_mock

        servicio = HallazgoService(db)
        with pytest.raises(ValueError, match="Transicion invalida"):
            await servicio.cambiar_estado("h-001", "EN_REVISION", 1)

    @pytest.mark.asyncio
    async def test_hallazgo_no_encontrado(self):
        """Operacion sobre hallazgo inexistente lanza error."""
        db = _mock_db()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        db.execute.return_value = result_mock

        servicio = HallazgoService(db)
        with pytest.raises(ValueError, match="no encontrado"):
            await servicio.cambiar_estado("inexistente", "EN_REVISION", 1)
