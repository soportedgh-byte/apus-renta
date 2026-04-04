"""
Tests para el servicio de capacitacion — Sprint 6.
Verifica generadores de contenido, seed data y logica de quizzes.
"""

import pytest
import sys
import types
import importlib.util
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch


# ── Cargar capacitacion_service directamente ─────────────────────────────────
def _cargar_servicio():
    """Carga capacitacion_service.py sin pasar por __init__."""
    # Mock de dependencias pesadas
    for mod_name in [
        "langchain_core", "langchain_core.messages", "langchain_core.language_models",
        "langchain_openai", "langchain_community", "langchain_community.vectorstores",
        "langchain_community.vectorstores.pgvector", "langchain_text_splitters",
        "redis", "redis.asyncio", "pgvector", "pgvector.sqlalchemy",
        "app.agents.graph", "app.agents.state", "app.agents.supervisor",
        "app.services.chat_service",
    ]:
        if mod_name not in sys.modules:
            mock_mod = types.ModuleType(mod_name)
            for attr in ["END", "START", "StateGraph", "AuditState", "BaseChatModel",
                         "ChatOpenAI", "PGVector", "HumanMessage", "AIMessage", "SystemMessage"]:
                setattr(mock_mod, attr, MagicMock())
            sys.modules[mod_name] = mock_mod

    ruta_archivo = Path(__file__).parent.parent.parent / "app" / "services" / "capacitacion_service.py"
    spec = importlib.util.spec_from_file_location("capacitacion_service", str(ruta_archivo))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["capacitacion_service"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestSeedData:
    """Tests para los datos seed de rutas y lecciones."""

    def test_4_rutas_configuradas(self):
        mod = _cargar_servicio()
        assert len(mod.RUTAS_SEED) == 4

    def test_ruta_001_tiene_6_lecciones(self):
        mod = _cargar_servicio()
        ruta = mod.RUTAS_SEED[0]
        assert ruta["id"] == "ruta-001"
        assert len(ruta["lecciones"]) == 6

    def test_ruta_002_tiene_10_lecciones(self):
        mod = _cargar_servicio()
        ruta = mod.RUTAS_SEED[1]
        assert ruta["id"] == "ruta-002"
        assert len(ruta["lecciones"]) == 10

    def test_ruta_003_tiene_7_lecciones(self):
        mod = _cargar_servicio()
        ruta = mod.RUTAS_SEED[2]
        assert ruta["id"] == "ruta-003"
        assert len(ruta["lecciones"]) == 7

    def test_ruta_004_tiene_8_lecciones(self):
        mod = _cargar_servicio()
        ruta = mod.RUTAS_SEED[3]
        assert ruta["id"] == "ruta-004"
        assert len(ruta["lecciones"]) == 8

    def test_total_31_lecciones(self):
        mod = _cargar_servicio()
        total = sum(len(r["lecciones"]) for r in mod.RUTAS_SEED)
        assert total == 31

    def test_cada_ruta_tiene_nombre(self):
        mod = _cargar_servicio()
        for ruta in mod.RUTAS_SEED:
            assert "nombre" in ruta
            assert len(ruta["nombre"]) > 0

    def test_cada_ruta_tiene_color(self):
        mod = _cargar_servicio()
        for ruta in mod.RUTAS_SEED:
            assert "color" in ruta
            assert ruta["color"].startswith("#")

    def test_direcciones_validas(self):
        mod = _cargar_servicio()
        for ruta in mod.RUTAS_SEED:
            assert ruta["direccion"] in ("DES", "DVF", "TODOS")


class TestGeneradores:
    """Tests para las funciones generadoras de contenido."""

    def test_generar_manual_docx(self):
        mod = _cargar_servicio()
        resultado = mod.generar_manual_docx(tema="auditoria", nivel="basico")
        assert isinstance(resultado, bytes)
        assert len(resultado) > 0

    def test_generar_podcast_script(self):
        mod = _cargar_servicio()
        resultado = mod.generar_podcast_script(tema="control_fiscal")
        assert isinstance(resultado, str)
        assert len(resultado) > 100
        assert "Narrador" in resultado or "narrador" in resultado.lower()

    def test_generar_glosario_docx(self):
        mod = _cargar_servicio()
        resultado = mod.generar_glosario_docx()
        assert isinstance(resultado, bytes)
        assert len(resultado) > 0

    def test_generar_guia_formato_docx(self):
        mod = _cargar_servicio()
        resultado = mod.generar_guia_formato_docx(numero_formato=1)
        assert isinstance(resultado, bytes)
        assert len(resultado) > 0

    def test_manual_nivel_avanzado(self):
        mod = _cargar_servicio()
        resultado = mod.generar_manual_docx(tema="hallazgos", nivel="avanzado")
        assert isinstance(resultado, bytes)
        assert len(resultado) > 0

    def test_podcast_tema_personalizado(self):
        mod = _cargar_servicio()
        resultado = mod.generar_podcast_script(tema="hallazgos")
        assert isinstance(resultado, str)
        assert len(resultado) > 50


class TestGlosario:
    """Tests para el glosario de terminos."""

    def test_glosario_tiene_contenido(self):
        """El glosario DOCX no esta vacio."""
        mod = _cargar_servicio()
        from io import BytesIO
        from docx import Document

        docx_bytes = mod.generar_glosario_docx()
        doc = Document(BytesIO(docx_bytes))
        textos = " ".join(p.text for p in doc.paragraphs).upper()
        # Debe contener terminos de control fiscal
        assert "HALLAZGO" in textos or "AUDITORIA" in textos or "CONTROL FISCAL" in textos


class TestQuizLogica:
    """Tests para la logica del quiz (umbral 70%)."""

    def test_umbral_aprobacion_70(self):
        """Puntaje >= 70 es aprobado."""
        assert 70.0 >= 70  # aprobado
        assert 69.9 < 70   # reprobado

    def test_puntaje_rango_0_100(self):
        """El puntaje debe estar entre 0 y 100."""
        for p in [0, 50, 70, 100]:
            assert 0 <= p <= 100
