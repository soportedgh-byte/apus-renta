"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: fase_4_seguimiento.py
Propósito: Agente de Fase 4 — Seguimiento (planes de mejoramiento, verificación de cumplimiento)
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

from backend.app.agents.state import AuditState

logger = logging.getLogger("cecilia.agents.fase_4")

RUTA_PROMPT: Path = Path(__file__).parent / "prompts" / "fase_4_seguimiento.txt"

HERRAMIENTAS_FASE: list[str] = [
    "buscar_normativa",
    "generar_formato",
]

ESTADOS_ACCION_CORRECTIVA: list[str] = [
    "pendiente",
    "en_progreso",
    "cumplida",
    "cumplida_parcialmente",
    "incumplida",
    "no_aplicable",
]


def _cargar_prompt() -> str:
    """Carga el prompt del sistema para el agente de seguimiento."""
    try:
        return RUTA_PROMPT.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("Prompt de seguimiento no encontrado; usando prompt base.")
        return (
            "Eres un asistente experto en la fase de seguimiento del proceso "
            "auditor de la Contraloría General de la República de Colombia."
        )


def ejecutar_seguimiento(
    state: AuditState,
    llm: BaseChatModel | None = None,
) -> AuditState:
    """Ejecuta el agente de seguimiento.

    Responsabilidades:
    - Seguimiento a planes de mejoramiento suscritos por sujetos de control.
    - Verificación de cumplimiento de acciones correctivas.
    - Cálculo de porcentaje de cumplimiento.
    - Identificación de acciones vencidas o con riesgo de incumplimiento.
    - Generación de informes de seguimiento.

    Args:
        state: Estado actual del grafo de auditoría.
        llm: Modelo de lenguaje para generación de respuestas.

    Returns:
        Estado actualizado con la respuesta del agente.
    """
    mensajes: list = state.get("messages", [])
    contexto_rag: list = state.get("contexto_rag", [])

    fragmentos_contexto: str = "\n---\n".join(
        doc if isinstance(doc, str) else str(doc) for doc in contexto_rag
    ) if contexto_rag else "No se encontraron documentos relevantes."

    estados_str: str = ", ".join(ESTADOS_ACCION_CORRECTIVA)

    prompt_sistema: str = _cargar_prompt()
    prompt_enriquecido: str = (
        f"{prompt_sistema}\n\n"
        f"Estados posibles de acciones correctivas: {estados_str}\n\n"
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

        contenido_respuesta: str = (
            respuesta.content if hasattr(respuesta, "content") else str(respuesta)
        )

        disclaimer: str = (
            "\n\n---\n⚠️ *Esta respuesta es una asistencia generada por IA. "
            "La verificación de cumplimiento de planes de mejoramiento requiere "
            "validación del equipo auditor con base en la evidencia presentada "
            "por el sujeto de control.*"
        )
        contenido_respuesta += disclaimer

        state["respuesta_final"] = contenido_respuesta
        state["messages"] = mensajes + [AIMessage(content=contenido_respuesta)]
        state["fuentes"] = _extraer_fuentes(contenido_respuesta)
        state["herramientas_disponibles"] = HERRAMIENTAS_FASE

    except Exception:
        logger.exception("Error en agente de seguimiento.")
        state["respuesta_final"] = "Ocurrió un error al procesar su consulta de seguimiento."
        state["fuentes"] = []

    return state


def _extraer_fuentes(texto: str) -> list[str]:
    """Extrae referencias normativas mencionadas en la respuesta."""
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
