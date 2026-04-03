"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: fase_0_preplaneacion.py
Propósito: Agente de Fase 0 — Pre-planeación (universo auditable, análisis de riesgos)
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

logger = logging.getLogger("cecilia.agents.fase_0")

RUTA_PROMPT: Path = Path(__file__).parent / "prompts" / "fase_0_preplaneacion.txt"


def _cargar_prompt() -> str:
    """Carga el prompt del sistema para el agente de pre-planeación."""
    try:
        return RUTA_PROMPT.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("Prompt de pre-planeación no encontrado; usando prompt base.")
        return (
            "Eres un asistente experto en la fase de pre-planeación del proceso "
            "auditor de la Contraloría General de la República de Colombia."
        )


def ejecutar_preplaneacion(
    state: AuditState,
    llm: BaseChatModel | None = None,
) -> AuditState:
    """Ejecuta el agente de pre-planeación.

    Responsabilidades:
    - Identificación del universo auditable.
    - Análisis de riesgos (inherente, de control, de detección).
    - Priorización de sujetos de vigilancia y control fiscal.
    - Construcción de la matriz de riesgos.
    - Selección de sujetos para el Plan de Vigilancia y Control Fiscal.

    Args:
        state: Estado actual del grafo de auditoría.
        llm: Modelo de lenguaje para generación de respuestas.

    Returns:
        Estado actualizado con la respuesta del agente.
    """
    mensajes: list = state.get("messages", [])
    contexto_rag: list = state.get("contexto_rag", [])

    # Construir contexto enriquecido
    fragmentos_contexto: str = "\n---\n".join(
        doc if isinstance(doc, str) else str(doc) for doc in contexto_rag
    ) if contexto_rag else "No se encontraron documentos relevantes en la base de conocimiento."

    prompt_sistema: str = _cargar_prompt()
    prompt_enriquecido: str = (
        f"{prompt_sistema}\n\n"
        f"--- CONTEXTO RECUPERADO (RAG) ---\n{fragmentos_contexto}\n"
        f"--- FIN CONTEXTO ---"
    )

    if llm is None:
        logger.warning("LLM no proporcionado al agente de pre-planeación.")
        state["respuesta_final"] = (
            "El modelo de lenguaje no está disponible en este momento. "
            "Por favor intente más tarde."
        )
        state["fuentes"] = []
        return state

    try:
        mensajes_llm: list = [SystemMessage(content=prompt_enriquecido)] + mensajes
        respuesta: Any = llm.invoke(mensajes_llm)

        contenido_respuesta: str = (
            respuesta.content if hasattr(respuesta, "content") else str(respuesta)
        )

        # Agregar disclaimer obligatorio
        disclaimer: str = (
            "\n\n---\n⚠️ *Esta respuesta es una asistencia generada por IA y requiere "
            "validación por parte del equipo auditor. No reemplaza el criterio profesional "
            "del auditor ni constituye concepto oficial de la CGR.*"
        )
        contenido_respuesta += disclaimer

        # Actualizar estado
        state["respuesta_final"] = contenido_respuesta
        state["messages"] = mensajes + [AIMessage(content=contenido_respuesta)]
        state["fuentes"] = _extraer_fuentes(contenido_respuesta)

    except Exception:
        logger.exception("Error en agente de pre-planeación.")
        state["respuesta_final"] = (
            "Ocurrió un error al procesar su consulta de pre-planeación. "
            "Por favor intente nuevamente."
        )
        state["fuentes"] = []

    return state


def _extraer_fuentes(texto: str) -> list[str]:
    """Extrae referencias normativas mencionadas en la respuesta.

    Busca patrones comunes como 'Ley X/YYYY', 'Decreto X/YYYY',
    'Resolución X/YYYY', 'Artículo X'.
    """
    import re

    patrones: list[str] = [
        r"Ley\s+\d+\s*(?:de|/)\s*\d{4}",
        r"Decreto\s+\d+\s*(?:de|/)\s*\d{4}",
        r"Resolución\s+(?:Orgánica\s+)?\d+\s*(?:de|/)\s*\d{4}",
        r"Artículo\s+\d+",
        r"GAO[-\s]\d+",
        r"ISSAI\s+\d+",
        r"NIA\s+\d+",
    ]

    fuentes: list[str] = []
    for patron in patrones:
        coincidencias: list[str] = re.findall(patron, texto, re.IGNORECASE)
        fuentes.extend(coincidencias)

    return list(dict.fromkeys(fuentes))  # Eliminar duplicados preservando orden
