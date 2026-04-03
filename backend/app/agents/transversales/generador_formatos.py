"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: generador_formatos.py
Propósito: Agente transversal para generación de formatos CGR (1-30)
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

logger = logging.getLogger("cecilia.agents.transversales.formatos")

RUTA_PROMPT: Path = Path(__file__).resolve().parent.parent / "prompts" / "generador_formatos.txt"

# Catálogo de formatos CGR del proceso auditor
CATALOGO_FORMATOS: dict[int, str] = {
    1: "Carta de presentación del informe de auditoría",
    2: "Plan de trabajo de auditoría",
    3: "Programa de auditoría",
    4: "Memorando de planeación",
    5: "Evaluación del sistema de control interno",
    6: "Cálculo de materialidad",
    7: "Diseño de muestreo",
    8: "Cédula sumaria",
    9: "Cédula analítica",
    10: "Papeles de trabajo — evidencia documental",
    11: "Hoja de hallazgo (5 elementos)",
    12: "Traslado de hallazgo fiscal",
    13: "Traslado de hallazgo disciplinario",
    14: "Traslado de hallazgo penal",
    15: "Informe preliminar de auditoría",
    16: "Acta de mesa de trabajo (respuesta al informe preliminar)",
    17: "Evaluación de la respuesta del sujeto",
    18: "Informe definitivo de auditoría",
    19: "Dictamen sobre estados financieros",
    20: "Concepto sobre gestión y resultados",
    21: "Tabla resumen de hallazgos",
    22: "Beneficios del control fiscal",
    23: "Plan de mejoramiento",
    24: "Seguimiento al plan de mejoramiento",
    25: "Acta de cierre de auditoría",
    26: "Informe de seguimiento a planes de mejoramiento",
    27: "Acta de visita fiscal",
    28: "Auto de apertura de indagación preliminar",
    29: "Informe de actuación especial",
    30: "Formato de control de calidad",
}


def _cargar_prompt() -> str:
    """Carga el prompt del sistema para el generador de formatos."""
    try:
        return RUTA_PROMPT.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("Prompt de generador de formatos no encontrado.")
        return (
            "Eres un experto en formatos oficiales del proceso auditor de la "
            "Contraloría General de la República de Colombia."
        )


def ejecutar_generador_formatos(
    state: AuditState,
    llm: BaseChatModel | None = None,
) -> AuditState:
    """Ejecuta el agente generador de formatos CGR.

    Responsabilidades:
    - Generación de borradores de formatos CGR (1 a 30).
    - Pre-llenado de campos con base en el contexto del proyecto.
    - Verificación de completitud de campos obligatorios.
    - Guía sobre el uso correcto de cada formato.

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
    ) if contexto_rag else "Sin contexto documental disponible."

    catalogo_str: str = "\n".join(
        f"  F{num:02d}: {desc}" for num, desc in CATALOGO_FORMATOS.items()
    )

    prompt_sistema: str = _cargar_prompt()
    prompt_enriquecido: str = (
        f"{prompt_sistema}\n\n"
        f"Catálogo de formatos CGR:\n{catalogo_str}\n\n"
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
            "\n\n---\n⚠️ *Formato generado por IA como borrador. Debe ser revisado, "
            "completado y aprobado por el equipo auditor antes de su uso oficial. "
            "Verifique que cumple con las guías de auditoría vigentes de la CGR.*"
        )
        contenido += disclaimer

        state["respuesta_final"] = contenido
        state["messages"] = mensajes + [AIMessage(content=contenido)]
        state["fuentes"] = []

    except Exception:
        logger.exception("Error en generador de formatos.")
        state["respuesta_final"] = "Error al generar el formato solicitado."
        state["fuentes"] = []

    return state
