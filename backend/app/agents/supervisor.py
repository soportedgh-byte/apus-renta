"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: supervisor.py
Propósito: Nodo supervisor/enrutador del grafo LangGraph — determina qué agente invocar
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel

from app.agents.state import AuditState

logger = logging.getLogger("cecilia.agents.supervisor")

# ---------------------------------------------------------------------------
# Rutas de enrutamiento válidas
# ---------------------------------------------------------------------------
NODOS_FASE: dict[str, str] = {
    "preplaneacion": "fase_0_preplaneacion",
    "planeacion": "fase_1_planeacion",
    "ejecucion": "fase_2_ejecucion",
    "informe": "fase_3_informe",
    "seguimiento": "fase_4_seguimiento",
}

NODOS_TRANSVERSALES: set[str] = {
    "analista_financiero",
    "normativo_juridico",
    "generador_formatos",
    "detector_fraude",
    "tutor",
}

RUTA_PROMPT = Path(__file__).parent / "prompts" / "supervisor.txt"


def _cargar_prompt_sistema() -> str:
    """Carga el prompt del sistema desde el archivo de texto."""
    try:
        return RUTA_PROMPT.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("Prompt del supervisor no encontrado en %s; usando prompt base.", RUTA_PROMPT)
        return (
            "Eres el supervisor de CecilIA v2, sistema de IA de la Contraloría General "
            "de la República de Colombia. Tu tarea es determinar a qué agente especializado "
            "derivar la consulta del auditor."
        )


def _construir_contexto(state: AuditState) -> str:
    """Genera un resumen del contexto actual para ayudar al LLM a decidir."""
    lineas: list[str] = [
        f"Dirección: {state.get('direccion', 'NO DEFINIDA')}",
        f"Fase actual: {state.get('fase_actual', 'NO DEFINIDA')}",
        f"Rol: {state.get('rol', 'NO DEFINIDO')}",
        f"Proyecto auditoría: {state.get('proyecto_auditoria_id', 'Ninguno')}",
    ]
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# Función principal de enrutamiento
# ---------------------------------------------------------------------------

def enrutar_consulta(state: AuditState, llm: BaseChatModel | None = None) -> str:
    """Determina el nodo destino en el grafo según la consulta del usuario.

    Estrategia de enrutamiento:
    1. Si la consulta es claramente de una fase, se envía al agente de fase.
    2. Si requiere análisis financiero, normativo, formatos o detección de
       fraude, se envía al agente transversal correspondiente.
    3. Si el LLM está disponible, se le pide que clasifique.
    4. Por defecto, se envía al agente de la fase actual del proyecto.

    Args:
        state: Estado actual del grafo.
        llm: Modelo de lenguaje opcional para clasificación inteligente.

    Returns:
        Nombre del nodo destino en el grafo.
    """
    fase_actual: str = state.get("fase_actual", "planeacion")
    direccion: str = state.get("direccion", "DES")
    rol: str = state.get("rol", "")
    mensajes: list = state.get("messages", [])

    # ── APRENDIZ siempre va al tutor ─────────────────────────────────────
    if rol.lower() == "aprendiz":
        logger.info("Rol APRENDIZ detectado — enrutando a tutor")
        return "tutor"

    if not mensajes:
        logger.info("Sin mensajes — enrutando a fase actual: %s", fase_actual)
        return NODOS_FASE.get(fase_actual, "fase_1_planeacion")

    ultimo_mensaje: str = ""
    for msg in reversed(mensajes):
        if isinstance(msg, HumanMessage):
            ultimo_mensaje = msg.content
            break
        elif isinstance(msg, dict) and msg.get("role") == "user":
            ultimo_mensaje = msg.get("content", "")
            break

    if not ultimo_mensaje:
        return NODOS_FASE.get(fase_actual, "fase_1_planeacion")

    # ------------------------------------------------------------------
    # Heurísticas rápidas basadas en palabras clave
    # ------------------------------------------------------------------
    texto_lower: str = ultimo_mensaje.lower()

    palabras_fase: dict[str, list[str]] = {
        "preplaneacion": ["universo auditable", "preplaneación", "pre-planeación", "plan de vigilancia"],
        "planeacion": ["materialidad", "muestra", "programa de auditoría", "planeación"],
        "ejecucion": ["hallazgo", "evidencia", "papeles de trabajo", "ejecución", "benford"],
        "informe": ["informe", "formato cgr", "conclusiones", "dictamen"],
        "seguimiento": ["plan de mejoramiento", "seguimiento", "acción correctiva"],
    }

    for fase, palabras in palabras_fase.items():
        if any(p in texto_lower for p in palabras):
            nodo: str = NODOS_FASE[fase]
            logger.info("Heurística de palabras clave → %s", nodo)
            return nodo

    # Transversales
    if any(p in texto_lower for p in ["ratio", "indicador financiero", "análisis financiero", "estado financiero"]):
        return "analista_financiero"
    if any(p in texto_lower for p in ["ley ", "decreto", "resolución", "normativa", "jurídico", "concepto jurídico"]):
        return "normativo_juridico"
    if any(p in texto_lower for p in ["formato", "formato cgr", "generar formato"]):
        return "generador_formatos"
    if any(p in texto_lower for p in ["fraude", "benford", "anomalía", "irregular"]):
        return "detector_fraude"
    if any(p in texto_lower for p in ["capacitacion", "capacitación", "tutor", "aprendiz", "leccion", "lección", "ruta de aprendizaje", "quiz"]):
        return "tutor"

    # ------------------------------------------------------------------
    # Clasificación con LLM (si está disponible)
    # ------------------------------------------------------------------
    if llm is not None:
        try:
            destinos_validos: str = ", ".join(
                list(NODOS_FASE.values()) + list(NODOS_TRANSVERSALES)
            )
            prompt_clasificacion: str = (
                f"Contexto:\n{_construir_contexto(state)}\n\n"
                f"Consulta del auditor: {ultimo_mensaje}\n\n"
                f"Responde SOLO con el nombre del nodo destino. "
                f"Opciones válidas: {destinos_validos}"
            )
            respuesta: Any = llm.invoke([
                SystemMessage(content=_cargar_prompt_sistema()),
                HumanMessage(content=prompt_clasificacion),
            ])
            nodo_llm: str = respuesta.content.strip().lower().replace(" ", "_")

            if nodo_llm in NODOS_FASE.values() or nodo_llm in NODOS_TRANSVERSALES:
                logger.info("LLM clasificó consulta → %s", nodo_llm)
                return nodo_llm
        except Exception:
            logger.exception("Error al clasificar con LLM; usando heurística por defecto.")

    # ------------------------------------------------------------------
    # Fallback: fase actual
    # ------------------------------------------------------------------
    nodo_default: str = NODOS_FASE.get(fase_actual, "fase_1_planeacion")
    logger.info("Fallback → %s", nodo_default)
    return nodo_default
