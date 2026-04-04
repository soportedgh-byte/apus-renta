"""
Runner de tests para el modulo de capacitacion — Sprint 6.
Ejecuta los tests mockeando las dependencias de langchain/redis/pgvector.
"""

import sys
import types
from unittest.mock import MagicMock
from pathlib import Path

# ── Pre-mock de dependencias pesadas ─────────────────────────────────────────
common_attrs = [
    "END", "START", "StateGraph", "AuditState", "BaseChatModel",
    "ChatOpenAI", "PGVector", "HumanMessage", "AIMessage", "SystemMessage",
    "BaseMessage", "ToolMessage", "FunctionMessage",
    "ChatAnthropic", "ChatGoogleGenerativeAI",
    "RecursiveCharacterTextSplitter",
    "AsyncRedis", "Redis",
]

mock_modules = [
    "langchain_core", "langchain_core.messages", "langchain_core.language_models",
    "langchain_core.prompts", "langchain_core.output_parsers",
    "langchain_openai", "langchain_anthropic", "langchain_google_genai",
    "langchain_community", "langchain_community.vectorstores",
    "langchain_community.vectorstores.pgvector", "langchain_text_splitters",
    "langgraph", "langgraph.graph", "langgraph.checkpoint",
    "langgraph.checkpoint.postgres", "langgraph.checkpoint.postgres.aio",
    "redis", "redis.asyncio",
    "pgvector", "pgvector.sqlalchemy",
    "opentelemetry", "opentelemetry.instrumentation",
    "opentelemetry.instrumentation.fastapi",
    "jose", "jose.jwt",
    "passlib", "passlib.context", "passlib.hash",
    "bcrypt",
]

# Especiales: passlib.context necesita CryptContext
passlib_ctx = sys.modules.get("passlib.context") or types.ModuleType("passlib.context")
passlib_ctx.CryptContext = MagicMock()
sys.modules["passlib.context"] = passlib_ctx

# jose necesita JWTError y jwt
jose_mod = sys.modules.get("jose") or types.ModuleType("jose")
jose_mod.JWTError = type("JWTError", (Exception,), {})
jose_mod.jwt = MagicMock()
sys.modules["jose"] = jose_mod

for mod_name in mock_modules:
    if mod_name not in sys.modules:
        mock_mod = types.ModuleType(mod_name)
        for attr in common_attrs:
            setattr(mock_mod, attr, MagicMock())
        sys.modules[mod_name] = mock_mod

# Mock app.agents submodules
for mod_name in [
    "app.agents", "app.agents.state", "app.agents.supervisor", "app.agents.graph",
    "app.agents.fase_0_preplaneacion", "app.agents.fase_1_planeacion",
    "app.agents.fase_2_ejecucion", "app.agents.fase_3_informe",
    "app.agents.fase_4_seguimiento",
    "app.agents.transversales", "app.agents.transversales.analista_financiero",
    "app.agents.transversales.normativo_juridico",
    "app.agents.transversales.generador_formatos",
    "app.agents.transversales.detector_fraude",
    "app.agents.transversales.tutor",
    "app.services.chat_service", "app.services.memoria_service",
    "app.llm",
]:
    if mod_name not in sys.modules:
        mock_mod = types.ModuleType(mod_name)
        for attr in common_attrs + [
            "ejecutar_preplaneacion", "ejecutar_planeacion", "ejecutar_ejecucion",
            "ejecutar_informe", "ejecutar_seguimiento",
            "ejecutar_analisis_financiero", "ejecutar_analisis_normativo",
            "ejecutar_generador_formatos", "ejecutar_detector_fraude",
            "ejecutar_tutor", "enrutar_consulta", "construir_grafo",
            "obtener_grafo", "ejecutar_grafo", "obtener_llm",
            "ChatService", "MemoriaService",
        ]:
            setattr(mock_mod, attr, MagicMock())
        sys.modules[mod_name] = mock_mod

# ── Ejecutar pytest ──────────────────────────────────────────────────────────
import pytest

ruta_tests = str(Path(__file__).parent / "tests" / "test_capacitacion")
sys.exit(pytest.main([
    ruta_tests,
    "-v",
    "--tb=short",
    "-x",
]))
