"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: normativo_juridico.py
Propósito: Agente transversal normativo/jurídico (consulta de leyes, decretos, jurisprudencia)
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

logger = logging.getLogger("cecilia.agents.transversales.normativo")

RUTA_PROMPT: Path = Path(__file__).resolve().parent.parent / "prompts" / "normativo_juridico.txt"

# Marco normativo principal del control fiscal colombiano
MARCO_NORMATIVO: dict[str, str] = {
    "Constitución Política 1991": "Arts. 267-274 — Control fiscal",
    "Ley 42/1993": "Organización del control fiscal financiero",
    "Ley 610/2000": "Proceso de responsabilidad fiscal",
    "Ley 1474/2011": "Estatuto Anticorrupción",
    "Decreto 403/2020": "Régimen del Control Fiscal Colombiano",
    "Decreto 768/2022": "Estructura de la CGR",
    "Resolución Orgánica REG-ORG-0012-2023": "Guía de Auditoría Financiera",
    "Resolución Orgánica REG-ORG-0017-2023": "Guía de Auditoría de Desempeño",
    "Ley 1581/2012": "Protección de datos personales",
    "Ley 80/1993": "Estatuto General de Contratación",
    "Ley 1150/2007": "Medidas de eficiencia en contratación",
}


def _cargar_prompt() -> str:
    """Carga el prompt del sistema para el agente normativo/jurídico."""
    try:
        return RUTA_PROMPT.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("Prompt normativo no encontrado; usando prompt base.")
        return (
            "Eres un experto en derecho público y control fiscal colombiano "
            "al servicio de la Contraloría General de la República de Colombia."
        )


def ejecutar_analisis_normativo(
    state: AuditState,
    llm: BaseChatModel | None = None,
) -> AuditState:
    """Ejecuta el agente normativo/jurídico.

    Responsabilidades:
    - Consulta de normativa aplicable al control fiscal.
    - Interpretación de leyes, decretos y resoluciones.
    - Identificación de criterios normativos para hallazgos.
    - Análisis de tipicidad fiscal (Ley 610/2000).
    - Referencia a jurisprudencia de la Corte Constitucional y Consejo de Estado.

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
    ) if contexto_rag else "No se encontraron documentos normativos relevantes."

    marco_str: str = "\n".join(
        f"  - {k}: {v}" for k, v in MARCO_NORMATIVO.items()
    )

    prompt_sistema: str = _cargar_prompt()
    prompt_enriquecido: str = (
        f"{prompt_sistema}\n\n"
        f"Marco normativo principal:\n{marco_str}\n\n"
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
            "\n\n---\n⚠️ *Esta consulta normativa es generada por IA y NO constituye "
            "concepto jurídico vinculante. Debe ser validada por el equipo jurídico "
            "de la CGR. Para conceptos oficiales, consulte la Oficina Jurídica.*"
        )
        contenido += disclaimer

        state["respuesta_final"] = contenido
        state["messages"] = mensajes + [AIMessage(content=contenido)]
        state["fuentes"] = _extraer_fuentes(contenido)

    except Exception:
        logger.exception("Error en agente normativo.")
        state["respuesta_final"] = "Error al procesar la consulta normativa."
        state["fuentes"] = []

    return state


def _extraer_fuentes(texto: str) -> list[str]:
    """Extrae referencias normativas del texto."""
    import re

    patrones: list[str] = [
        r"Ley\s+\d+\s*(?:de|/)\s*\d{4}",
        r"Decreto\s+\d+\s*(?:de|/)\s*\d{4}",
        r"Resolución\s+(?:Orgánica\s+)?(?:REG-ORG-)?\d+[-/]\d{4}",
        r"Artículo\s+\d+",
        r"Sentencia\s+[A-Z]-\d+/\d{2,4}",
        r"Constitución\s+Política.*?(?:Art(?:ículo)?\.?\s*\d+)",
    ]
    fuentes: list[str] = []
    for patron in patrones:
        fuentes.extend(re.findall(patron, texto, re.IGNORECASE))
    return list(dict.fromkeys(fuentes))
