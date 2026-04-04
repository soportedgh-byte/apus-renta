"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/agents/transversales/tutor.py
Proposito: Agente tutor para capacitacion de nuevos funcionarios.
           Responde de forma didactica, paciente y con ejemplos ficticios.
Sprint: 6
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel

from app.agents.state import AuditState

logger = logging.getLogger("cecilia.agents.tutor")

RUTA_PROMPT = Path(__file__).parent.parent / "prompts" / "tutor.txt"


def _cargar_prompt_tutor(leccion_titulo: str = "", ruta_nombre: str = "") -> str:
    """Carga y personaliza el prompt del tutor."""
    try:
        plantilla = RUTA_PROMPT.read_text(encoding="utf-8")
    except FileNotFoundError:
        plantilla = (
            "Eres CecilIA en modo Tutor. Guia a nuevos funcionarios de la CGR "
            "con paciencia, ejemplos ficticios y estructura didactica."
        )

    return plantilla.replace(
        "{leccion_titulo}", leccion_titulo or "General"
    ).replace(
        "{ruta_nombre}", ruta_nombre or "Capacitacion general"
    )


def ejecutar_tutor(state: AuditState, llm: BaseChatModel | None = None) -> AuditState:
    """Nodo del agente tutor en el grafo LangGraph.

    Se activa cuando el usuario tiene rol APRENDIZ.
    Responde de forma didactica usando el prompt de tutor.
    """
    mensajes: list = state.get("messages", [])
    if not mensajes:
        state["respuesta_final"] = (
            "Hola! 👋 Soy CecilIA, tu tutora virtual de la Contraloria General. "
            "Estoy aqui para ayudarte a aprender sobre control fiscal, auditorias "
            "y todo lo que necesitas saber como nuevo funcionario.\n\n"
            "Por donde quieres empezar? Puedo:\n"
            "1. 🏛️ Explicarte que es la CGR y como funciona\n"
            "2. 🔍 Guiarte por el proceso de auditoria paso a paso\n"
            "3. 📋 Ensenarte los 30 formatos de la GAF\n"
            "4. ⚖️ Repasar la normativa esencial\n"
            "5. 🎮 Hacer un ejercicio de simulacion\n\n"
            "Dime que te interesa!"
        )
        state["fuentes"] = []
        return state

    # Obtener contexto de la leccion actual (si existe)
    leccion_titulo = state.get("leccion_titulo", "")
    ruta_nombre = state.get("ruta_nombre", "")

    prompt_sistema = _cargar_prompt_tutor(leccion_titulo, ruta_nombre)

    if llm is None:
        # Sin LLM — respuesta por defecto
        state["respuesta_final"] = (
            "Excelente pregunta! 📚 Lamentablemente no puedo procesar tu consulta "
            "en este momento porque el modelo de lenguaje no esta disponible. "
            "Intenta nuevamente en unos minutos."
        )
        state["fuentes"] = []
        return state

    try:
        # Construir mensajes para el LLM
        mensajes_llm = [SystemMessage(content=prompt_sistema)]

        for msg in mensajes:
            if isinstance(msg, HumanMessage):
                mensajes_llm.append(msg)
            elif isinstance(msg, AIMessage):
                mensajes_llm.append(msg)
            elif isinstance(msg, dict):
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    mensajes_llm.append(HumanMessage(content=content))
                elif role == "assistant":
                    mensajes_llm.append(AIMessage(content=content))

        respuesta = llm.invoke(mensajes_llm)
        contenido = respuesta.content if hasattr(respuesta, "content") else str(respuesta)

        # Agregar disclaimer educativo
        contenido += (
            "\n\n---\n*📚 Respuesta con fines educativos — Datos ficticios de ejemplo. "
            "CecilIA Modo Tutor — Circular 023 CGR*"
        )

        state["respuesta_final"] = contenido
        state["fuentes"] = []

    except Exception as exc:
        logger.error("Error en agente tutor: %s", exc)
        state["respuesta_final"] = (
            "Disculpa, tuve un problema al procesar tu pregunta. "
            "Puedes reformularla? Estoy aqui para ayudarte. 😊"
        )
        state["fuentes"] = []

    return state
