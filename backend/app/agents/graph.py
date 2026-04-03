"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: graph.py
Proposito: Grafo principal LangGraph — orquestacion de agentes de auditoria
           con inyeccion de LLM y checkpointing PostgreSQL
Sprint: 2
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from typing import Any

from langgraph.graph import END, StateGraph

from app.agents.state import AuditState
from app.agents.supervisor import enrutar_consulta
from app.agents.fase_0_preplaneacion import ejecutar_preplaneacion
from app.agents.fase_1_planeacion import ejecutar_planeacion
from app.agents.fase_2_ejecucion import ejecutar_ejecucion
from app.agents.fase_3_informe import ejecutar_informe
from app.agents.fase_4_seguimiento import ejecutar_seguimiento
from app.agents.transversales.analista_financiero import ejecutar_analisis_financiero
from app.agents.transversales.normativo_juridico import ejecutar_analisis_normativo
from app.agents.transversales.generador_formatos import ejecutar_generador_formatos
from app.agents.transversales.detector_fraude import ejecutar_detector_fraude

logger = logging.getLogger("cecilia.agents.graph")

# ---------------------------------------------------------------------------
# Wrappers que inyectan el LLM a cada agente
# ---------------------------------------------------------------------------

_llm_instance = None


def _obtener_llm():
    """Obtiene o crea la instancia del LLM (lazy singleton)."""
    global _llm_instance
    if _llm_instance is None:
        from app.llm import obtener_llm
        _llm_instance = obtener_llm()
        logger.info("LLM inicializado para el grafo: %s", type(_llm_instance).__name__)
    return _llm_instance


def _nodo_supervisor(state: AuditState) -> AuditState:
    """Nodo supervisor: determina la ruta usando el LLM si es necesario."""
    return state


def _decidir_ruta(state: AuditState) -> str:
    """Funcion de decision condicional para las aristas del grafo."""
    llm = _obtener_llm()
    destino: str = enrutar_consulta(state, llm=llm)
    logger.info("Supervisor enruta a: %s", destino)
    return destino


# Wrappers para cada agente que inyectan el LLM
def _nodo_fase_0(state: AuditState) -> AuditState:
    return ejecutar_preplaneacion(state, llm=_obtener_llm())


def _nodo_fase_1(state: AuditState) -> AuditState:
    return ejecutar_planeacion(state, llm=_obtener_llm())


def _nodo_fase_2(state: AuditState) -> AuditState:
    return ejecutar_ejecucion(state, llm=_obtener_llm())


def _nodo_fase_3(state: AuditState) -> AuditState:
    return ejecutar_informe(state, llm=_obtener_llm())


def _nodo_fase_4(state: AuditState) -> AuditState:
    return ejecutar_seguimiento(state, llm=_obtener_llm())


def _nodo_financiero(state: AuditState) -> AuditState:
    return ejecutar_analisis_financiero(state, llm=_obtener_llm())


def _nodo_normativo(state: AuditState) -> AuditState:
    return ejecutar_analisis_normativo(state, llm=_obtener_llm())


def _nodo_formatos(state: AuditState) -> AuditState:
    return ejecutar_generador_formatos(state, llm=_obtener_llm())


def _nodo_fraude(state: AuditState) -> AuditState:
    return ejecutar_detector_fraude(state, llm=_obtener_llm())


# ---------------------------------------------------------------------------
# Construccion del grafo
# ---------------------------------------------------------------------------

def construir_grafo() -> StateGraph:
    """Construye y retorna el grafo LangGraph.

    Estructura:
        supervisor --> (condicional) --> agente_fase_N / agente_transversal --> END
    """
    grafo = StateGraph(AuditState)

    # Agregar nodos
    grafo.add_node("supervisor", _nodo_supervisor)
    grafo.add_node("fase_0_preplaneacion", _nodo_fase_0)
    grafo.add_node("fase_1_planeacion", _nodo_fase_1)
    grafo.add_node("fase_2_ejecucion", _nodo_fase_2)
    grafo.add_node("fase_3_informe", _nodo_fase_3)
    grafo.add_node("fase_4_seguimiento", _nodo_fase_4)
    grafo.add_node("analista_financiero", _nodo_financiero)
    grafo.add_node("normativo_juridico", _nodo_normativo)
    grafo.add_node("generador_formatos", _nodo_formatos)
    grafo.add_node("detector_fraude", _nodo_fraude)

    # Punto de entrada
    grafo.set_entry_point("supervisor")

    # Aristas condicionales
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

    # Todos terminan en END
    for nodo in destinos.values():
        grafo.add_edge(nodo, END)

    return grafo


# Grafo compilado (singleton)
_grafo_compilado: Any | None = None


def obtener_grafo() -> Any:
    """Retorna el grafo compilado como singleton."""
    global _grafo_compilado
    if _grafo_compilado is None:
        _grafo_compilado = construir_grafo().compile()
        logger.info("Grafo LangGraph compilado exitosamente con LLM inyectado.")
    return _grafo_compilado


def ejecutar_grafo(state: AuditState) -> AuditState:
    """Ejecuta el grafo completo con el estado proporcionado."""
    grafo = obtener_grafo()
    try:
        resultado: AuditState = grafo.invoke(state)
        logger.info(
            "Grafo ejecutado. Fuentes: %d",
            len(resultado.get("fuentes", [])),
        )
        return resultado
    except Exception:
        logger.exception("Error al ejecutar el grafo LangGraph.")
        state["respuesta_final"] = (
            "Ocurrio un error interno al procesar su consulta. "
            "Por favor intente nuevamente o contacte al administrador."
        )
        state["fuentes"] = []
        return state


async def ejecutar_grafo_streaming(state: AuditState):
    """Ejecuta el grafo con streaming — yield eventos a medida que se generan."""
    grafo = obtener_grafo()
    try:
        async for evento in grafo.astream(state, stream_mode="values"):
            yield evento
    except Exception:
        logger.exception("Error en streaming del grafo.")
        state["respuesta_final"] = (
            "Error interno al procesar su consulta en modo streaming."
        )
        state["fuentes"] = []
        yield state
