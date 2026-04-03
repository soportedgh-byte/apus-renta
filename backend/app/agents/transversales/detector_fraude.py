"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: detector_fraude.py
Propósito: Agente transversal de detección de fraude (Benford, anomalías, patrones irregulares)
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.language_models import BaseChatModel

from app.agents.state import AuditState

logger = logging.getLogger("cecilia.agents.transversales.fraude")

RUTA_PROMPT: Path = Path(__file__).resolve().parent.parent / "prompts" / "detector_fraude.txt"

# Técnicas de detección de fraude soportadas
TECNICAS_FRAUDE: dict[str, str] = {
    "benford": "Análisis de la Ley de Benford (distribución del primer dígito)",
    "duplicados": "Detección de registros duplicados o cuasi-duplicados",
    "outliers": "Identificación de valores atípicos (Z-score, IQR)",
    "secuencias": "Análisis de secuencias numéricas (gaps, duplicados consecutivos)",
    "round_numbers": "Detección de cifras redondas sospechosas",
    "relaciones": "Análisis de relaciones entre proveedores y funcionarios",
    "temporalidad": "Patrones temporales anómalos (fines de semana, festivos, cierre fiscal)",
}


def _cargar_prompt() -> str:
    """Carga el prompt del sistema para el detector de fraude."""
    try:
        return RUTA_PROMPT.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("Prompt de detector de fraude no encontrado.")
        return (
            "Eres un experto en detección de fraude y análisis forense contable "
            "al servicio de la Contraloría General de la República de Colombia."
        )


def ejecutar_detector_fraude(
    state: AuditState,
    llm: BaseChatModel | None = None,
) -> AuditState:
    """Ejecuta el agente detector de fraude.

    Responsabilidades:
    - Análisis de Ley de Benford sobre conjuntos de datos financieros.
    - Detección de anomalías estadísticas en transacciones.
    - Identificación de patrones de fraccionamiento contractual.
    - Análisis de relaciones sospechosas (proveedores, funcionarios).
    - Generación de alertas y banderas rojas (red flags).

    Args:
        state: Estado actual del grafo.
        llm: Modelo de lenguaje.

    Returns:
        Estado actualizado.
    """
    mensajes: list = state.get("messages", [])
    contexto_rag: list = state.get("contexto_rag", [])

    fragmentos_contexto: str = "\n---\n".join(
        doc if isinstance(doc, str) else str(doc) for doc in contexto_rag
    ) if contexto_rag else "Sin datos para análisis de fraude."

    tecnicas_str: str = "\n".join(
        f"  - {k}: {v}" for k, v in TECNICAS_FRAUDE.items()
    )

    prompt_sistema: str = _cargar_prompt()
    prompt_enriquecido: str = (
        f"{prompt_sistema}\n\n"
        f"Técnicas de detección disponibles:\n{tecnicas_str}\n\n"
        f"--- CONTEXTO RECUPERADO (RAG) ---\n{fragmentos_contexto}\n"
        f"--- FIN CONTEXTO ---"
    )

    if llm is None:
        state["respuesta_final"] = "El modelo de lenguaje no está disponible."
        state["fuentes"] = []
        return state

    try:
        mensajes_llm: list = [SystemMessage(content=prompt_enriquecido)] + mensajes
        respuesta: Any = llm.invoke(mensajes_llm)

        contenido: str = (
            respuesta.content if hasattr(respuesta, "content") else str(respuesta)
        )

        disclaimer: str = (
            "\n\n---\n⚠️ *Los resultados de detección de fraude son indicios generados "
            "por IA y NO constituyen prueba de irregularidad. Todo hallazgo debe ser "
            "verificado con evidencia suficiente, pertinente y competente. Los traslados "
            "fiscales, disciplinarios o penales requieren el debido proceso (Ley 610/2000).*"
        )
        contenido += disclaimer

        state["respuesta_final"] = contenido
        state["messages"] = mensajes + [AIMessage(content=contenido)]
        state["fuentes"] = _extraer_fuentes(contenido)

    except Exception:
        logger.exception("Error en detector de fraude.")
        state["respuesta_final"] = "Error al procesar el análisis de fraude."
        state["fuentes"] = []

    return state


def _extraer_fuentes(texto: str) -> list[str]:
    """Extrae referencias normativas del texto."""
    import re

    patrones: list[str] = [
        r"Ley\s+\d+\s*(?:de|/)\s*\d{4}",
        r"Decreto\s+\d+\s*(?:de|/)\s*\d{4}",
        r"Resolución\s+(?:Orgánica\s+)?\d+\s*(?:de|/)\s*\d{4}",
    ]
    fuentes: list[str] = []
    for patron in patrones:
        fuentes.extend(re.findall(patron, texto, re.IGNORECASE))
    return list(dict.fromkeys(fuentes))
