"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: graph.py
Propósito: Grafo principal LangGraph — orquestación de agentes de auditoría
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from typing import Any

from langgraph.graph import END, StateGraph

from backend.app.agents.state import AuditState
from backend.app.agents.supervisor import enrutar_consulta
from backend.app.agents.fase_0_preplaneacion import ejecutar_preplaneacion
from backend.app.agents.fase_1_planeacion import ejecutar_planeacion
from backend.app.agents.fase_2_ejecucion import ejecutar_ejecucion
from backend.app.agents.fase_3_informe import ejecutar_informe
from backend.app.agents.fase_4_seguimiento import ejecutar_seguimiento
from backend.app.agents.transversales.analista_financiero import ejecutar_analisis_financiero
from backend.app.agents.transversales.normativo_juridico import ejecutar_analisis_normativo
from backend.app.agents.transversales.generador_formatos import ejecutar_generador_formatos
from backend.app.agents.transversales.detector_fraude import ejecutar_detector_fraude

logger = logging.getLogger("cecilia.agents.graph")

# ---------------------------------------------------------------------------
# Construcción del grafo
# ---------------------------------------------------------------------------

def _nodo_supervisor(state: AuditState) -> AuditState:
    """Nodo supervisor: solo determina la ruta, no modifica el estado."""
    return state


def _decidir_ruta(state: AuditState) -> str:
    """Función de decisión condicional para las aristas del grafo."""
    destino: str = enrutar_consulta(state)
    logger.info("Supervisor enruta a: %s", destino)
    return destino


def construir_grafo() -> StateGraph:
    """Construye y retorna el grafo LangGraph compilado.

    Estructura del grafo:
        supervisor --> (condicional) --> agente_fase_N / agente_transversal --> END

    Returns:
        Grafo LangGraph compilado y listo para ejecutar.
    """
    grafo = StateGraph(AuditState)

    # --- Agregar nodos ---
    grafo.add_node("supervisor", _nodo_supervisor)

    # Nodos de fase
    grafo.add_node("fase_0_preplaneacion", ejecutar_preplaneacion)
    grafo.add_node("fase_1_planeacion", ejecutar_planeacion)
    grafo.add_node("fase_2_ejecucion", ejecutar_ejecucion)
    grafo.add_node("fase_3_informe", ejecutar_informe)
    grafo.add_node("fase_4_seguimiento", ejecutar_seguimiento)

    # Nodos transversales
    grafo.add_node("analista_financiero", ejecutar_analisis_financiero)
    grafo.add_node("normativo_juridico", ejecutar_analisis_normativo)
    grafo.add_node("generador_formatos", ejecutar_generador_formatos)
    grafo.add_node("detector_fraude", ejecutar_detector_fraude)

    # --- Punto de entrada ---
    grafo.set_entry_point("supervisor")

    # --- Aristas condicionales desde el supervisor ---
    destinos: dict[str, str] = {
        "fase_0_preplaneacion": "fase_0_preplaneacion",
        "fase_1_planeacion": "fase_1_planeacion",
        "fase_2_ejecucion": "fase_2_ejecucion",
        "fase_3_informe": "fase_3_informe",
        "fase_4_seguimiento": "fase_4_seguimiento",
        "analista_financiero": "analista_financiero",
        "normativo_juridico": "normativo_juridico",
        "generador_formatos": "generador_formatos",
        "detector_fraude": "detector_fraude",
    }

    grafo.add_conditional_edges("supervisor", _decidir_ruta, destinos)

    # --- Todas las fases y transversales terminan en END ---
    for nodo in destinos.values():
        grafo.add_edge(nodo, END)

    return grafo


# Grafo compilado (singleton)
_grafo_compilado: Any | None = None


def obtener_grafo() -> Any:
    """Retorna el grafo compilado como singleton.

    Returns:
        Instancia compilada del grafo LangGraph.
    """
    global _grafo_compilado
    if _grafo_compilado is None:
        _grafo_compilado = construir_grafo().compile()
        logger.info("Grafo LangGraph compilado exitosamente.")
    return _grafo_compilado


def ejecutar_grafo(state: AuditState) -> AuditState:
    """Ejecuta el grafo completo con el estado proporcionado.

    Args:
        state: Estado inicial con mensajes del usuario y contexto.

    Returns:
        Estado final con la respuesta generada y metadatos.
    """
    grafo = obtener_grafo()
    try:
        resultado: AuditState = grafo.invoke(state)
        logger.info(
            "Grafo ejecutado exitosamente. Fuentes: %d",
            len(resultado.get("fuentes", [])),
        )
        return resultado
    except Exception:
        logger.exception("Error al ejecutar el grafo LangGraph.")
        state["respuesta_final"] = (
            "Ocurrió un error interno al procesar su consulta. "
            "Por favor intente nuevamente o contacte al administrador."
        )
        state["fuentes"] = []
        return state
