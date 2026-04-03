"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: analista_financiero.py
Propósito: Agente transversal de análisis financiero (ratios, indicadores, estados financieros)
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

logger = logging.getLogger("cecilia.agents.transversales.financiero")

RUTA_PROMPT: Path = Path(__file__).resolve().parent.parent / "prompts" / "analista_financiero.txt"

INDICADORES_FINANCIEROS: dict[str, str] = {
    "razon_corriente": "Activo Corriente / Pasivo Corriente",
    "prueba_acida": "(Activo Corriente - Inventarios) / Pasivo Corriente",
    "endeudamiento": "Pasivo Total / Activo Total",
    "rotacion_cartera": "Ingresos / Cuentas por Cobrar",
    "margen_operacional": "Resultado Operacional / Ingresos Operacionales",
    "rentabilidad_patrimonio": "Resultado del Ejercicio / Patrimonio",
    "capital_trabajo": "Activo Corriente - Pasivo Corriente",
    "solvencia": "Activo Total / Pasivo Total",
}


def _cargar_prompt() -> str:
    """Carga el prompt del sistema para el analista financiero."""
    try:
        return RUTA_PROMPT.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("Prompt de analista financiero no encontrado; usando prompt base.")
        return (
            "Eres un analista financiero experto al servicio de la Contraloría "
            "General de la República de Colombia."
        )


def ejecutar_analisis_financiero(
    state: AuditState,
    llm: BaseChatModel | None = None,
) -> AuditState:
    """Ejecuta el agente de análisis financiero.

    Responsabilidades:
    - Cálculo e interpretación de indicadores financieros.
    - Análisis horizontal y vertical de estados financieros.
    - Evaluación de la situación financiera de sujetos de control.
    - Identificación de tendencias y riesgos financieros.
    - Análisis bajo el Marco Normativo Contable colombiano (NICSP/NIIF).

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
    ) if contexto_rag else "No se encontraron documentos financieros relevantes."

    indicadores_str: str = "\n".join(
        f"  - {k}: {v}" for k, v in INDICADORES_FINANCIEROS.items()
    )

    prompt_sistema: str = _cargar_prompt()
    prompt_enriquecido: str = (
        f"{prompt_sistema}\n\n"
        f"Indicadores financieros disponibles:\n{indicadores_str}\n\n"
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
            "\n\n---\n⚠️ *Análisis financiero generado por IA. Los cálculos e "
            "interpretaciones deben ser validados por el equipo auditor con base "
            "en los estados financieros oficiales del sujeto de control.*"
        )
        contenido += disclaimer

        state["respuesta_final"] = contenido
        state["messages"] = mensajes + [AIMessage(content=contenido)]
        state["fuentes"] = _extraer_fuentes(contenido)

    except Exception:
        logger.exception("Error en analista financiero.")
        state["respuesta_final"] = "Error al procesar el análisis financiero."
        state["fuentes"] = []

    return state


def _extraer_fuentes(texto: str) -> list[str]:
    """Extrae referencias normativas del texto."""
    import re

    patrones: list[str] = [
        r"Ley\s+\d+\s*(?:de|/)\s*\d{4}",
        r"Decreto\s+\d+\s*(?:de|/)\s*\d{4}",
        r"Resolución\s+(?:Orgánica\s+)?\d+\s*(?:de|/)\s*\d{4}",
        r"NIC(?:SP)?\s+\d+",
        r"NIIF\s+\d+",
    ]
    fuentes: list[str] = []
    for patron in patrones:
        fuentes.extend(re.findall(patron, texto, re.IGNORECASE))
    return list(dict.fromkeys(fuentes))
