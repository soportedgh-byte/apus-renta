"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: fase_2_ejecucion.py
Propósito: Agente de Fase 2 — Ejecución (análisis de evidencia, estructuración de hallazgos)
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

logger = logging.getLogger("cecilia.agents.fase_2")

RUTA_PROMPT: Path = Path(__file__).parent / "prompts" / "fase_2_ejecucion.txt"

HERRAMIENTAS_FASE: list[str] = [
    "analizar_benford",
    "buscar_normativa",
    "analisis_financiero",
    "analisis_contratacion",
    "acceder_workspace_local",
]

# Los 5 elementos del hallazgo fiscal según la CGR
ELEMENTOS_HALLAZGO: list[str] = [
    "Condición (lo que se encontró)",
    "Criterio (la norma o estándar aplicable)",
    "Causa (por qué ocurrió)",
    "Efecto (impacto o consecuencia)",
    "Recomendación (acción correctiva propuesta)",
]


def _cargar_prompt() -> str:
    """Carga el prompt del sistema para el agente de ejecución."""
    try:
        return RUTA_PROMPT.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("Prompt de ejecución no encontrado; usando prompt base.")
        return (
            "Eres un asistente experto en la fase de ejecución del proceso "
            "auditor de la Contraloría General de la República de Colombia."
        )


def ejecutar_ejecucion(
    state: AuditState,
    llm: BaseChatModel | None = None,
) -> AuditState:
    """Ejecuta el agente de ejecución.

    Responsabilidades:
    - Análisis de evidencia documental.
    - Estructuración de hallazgos con los 5 elementos (condición, criterio,
      causa, efecto, recomendación).
    - Soporte para análisis de Ley de Benford.
    - Clasificación de hallazgos (administrativo, fiscal, disciplinario, penal).
    - Cuantificación del presunto detrimento patrimonial.
    - Referencia cruzada con papeles de trabajo.

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

    elementos_str: str = "\n".join(f"  {i+1}. {e}" for i, e in enumerate(ELEMENTOS_HALLAZGO))

    prompt_sistema: str = _cargar_prompt()
    prompt_enriquecido: str = (
        f"{prompt_sistema}\n\n"
        f"Herramientas disponibles: {', '.join(HERRAMIENTAS_FASE)}\n\n"
        f"Recuerda que todo hallazgo debe estructurarse con los 5 elementos:\n"
        f"{elementos_str}\n\n"
        f"--- CONTEXTO RECUPERADO (RAG) ---\n{fragmentos_contexto}\n"
        f"--- FIN CONTEXTO ---"
    )

    if llm is None:
        logger.warning("LLM no proporcionado al agente de ejecución.")
        state["respuesta_final"] = (
            "El modelo de lenguaje no está disponible en este momento."
        )
        state["fuentes"] = []
        return state

    try:
        mensajes_llm: list = [SystemMessage(content=prompt_enriquecido)] + mensajes
        respuesta: Any = llm.invoke(mensajes_llm)

        contenido_respuesta: str = (
            respuesta.content if hasattr(respuesta, "content") else str(respuesta)
        )

        disclaimer: str = (
            "\n\n---\n⚠️ *Esta respuesta es una asistencia generada por IA y requiere "
            "validación por parte del equipo auditor. La estructuración de hallazgos "
            "debe ser revisada y soportada con evidencia suficiente, pertinente y "
            "competente conforme a la Ley 610 de 2000.*"
        )
        contenido_respuesta += disclaimer

        state["respuesta_final"] = contenido_respuesta
        state["messages"] = mensajes + [AIMessage(content=contenido_respuesta)]
        state["fuentes"] = _extraer_fuentes(contenido_respuesta)
        state["herramientas_disponibles"] = HERRAMIENTAS_FASE

    except Exception:
        logger.exception("Error en agente de ejecución.")
        state["respuesta_final"] = (
            "Ocurrió un error al procesar su consulta de ejecución."
        )
        state["fuentes"] = []

    return state


def _extraer_fuentes(texto: str) -> list[str]:
    """Extrae referencias normativas mencionadas en la respuesta."""
    import re

    patrones: list[str] = [
        r"Ley\s+\d+\s*(?:de|/)\s*\d{4}",
        r"Decreto\s+\d+\s*(?:de|/)\s*\d{4}",
        r"Resolución\s+(?:Orgánica\s+)?\d+\s*(?:de|/)\s*\d{4}",
        r"Artículo\s+\d+",
        r"NIA\s+\d+",
        r"ISSAI\s+\d+",
    ]

    fuentes: list[str] = []
    for patron in patrones:
        fuentes.extend(re.findall(patron, texto, re.IGNORECASE))
    return list(dict.fromkeys(fuentes))
