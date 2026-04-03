"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: fase_3_informe.py
Propósito: Agente de Fase 3 — Informe (redacción de informes, generación de formatos CGR)
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

logger = logging.getLogger("cecilia.agents.fase_3")

RUTA_PROMPT: Path = Path(__file__).parent / "prompts" / "fase_3_informe.txt"

HERRAMIENTAS_FASE: list[str] = [
    "generar_formato",
    "buscar_normativa",
]

# Formatos CGR relevantes para la fase de informe
FORMATOS_INFORME: dict[str, str] = {
    "F1": "Carta de presentación del informe",
    "F2": "Informe de auditoría",
    "F3": "Dictamen sobre estados financieros",
    "F4": "Concepto sobre gestión y resultados",
    "F5": "Tabla de hallazgos",
    "F6": "Tabla resumen de hallazgos fiscales",
    "F7": "Beneficios del control fiscal",
}


def _cargar_prompt() -> str:
    """Carga el prompt del sistema para el agente de informe."""
    try:
        return RUTA_PROMPT.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("Prompt de informe no encontrado; usando prompt base.")
        return (
            "Eres un asistente experto en la fase de informe del proceso "
            "auditor de la Contraloría General de la República de Colombia."
        )


def ejecutar_informe(
    state: AuditState,
    llm: BaseChatModel | None = None,
) -> AuditState:
    """Ejecuta el agente de informe.

    Responsabilidades:
    - Redacción de borradores de informe de auditoría.
    - Generación de formatos CGR (1 a 30).
    - Estructuración del dictamen (financiera) o concepto (desempeño).
    - Resumen ejecutivo y conclusiones.
    - Verificación de coherencia entre hallazgos y conclusiones.

    Args:
        state: Estado actual del grafo de auditoría.
        llm: Modelo de lenguaje para generación de respuestas.

    Returns:
        Estado actualizado con la respuesta del agente.
    """
    mensajes: list = state.get("messages", [])
    contexto_rag: list = state.get("contexto_rag", [])
    direccion: str = state.get("direccion", "DES")

    fragmentos_contexto: str = "\n---\n".join(
        doc if isinstance(doc, str) else str(doc) for doc in contexto_rag
    ) if contexto_rag else "No se encontraron documentos relevantes."

    formatos_str: str = "\n".join(f"  - {k}: {v}" for k, v in FORMATOS_INFORME.items())

    prompt_sistema: str = _cargar_prompt()
    prompt_enriquecido: str = (
        f"{prompt_sistema}\n\n"
        f"Dirección: {direccion}\n"
        f"Formatos disponibles:\n{formatos_str}\n\n"
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
            "\n\n---\n⚠️ *Este borrador de informe es una asistencia generada por IA. "
            "Debe ser revisado, ajustado y aprobado por el equipo auditor y el "
            "supervisor antes de su emisión oficial.*"
        )
        contenido_respuesta += disclaimer

        state["respuesta_final"] = contenido_respuesta
        state["messages"] = mensajes + [AIMessage(content=contenido_respuesta)]
        state["fuentes"] = _extraer_fuentes(contenido_respuesta)
        state["herramientas_disponibles"] = HERRAMIENTAS_FASE

    except Exception:
        logger.exception("Error en agente de informe.")
        state["respuesta_final"] = "Ocurrió un error al procesar su consulta de informe."
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
