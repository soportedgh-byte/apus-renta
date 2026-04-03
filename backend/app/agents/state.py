"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: state.py
Proposito: Definicion del estado tipado (AuditState) para el grafo LangGraph
Sprint: 2
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

from typing import Optional, TypedDict


class AuditState(TypedDict, total=False):
    """Estado compartido entre todos los nodos del grafo de auditoria.

    Cada campo representa un aspecto del contexto de la conversacion
    y del proceso auditor en curso.
    """

    # --- Mensajes de la conversacion (formato LangChain) ---
    messages: list

    # --- Identidad y permisos del usuario ---
    usuario_id: str
    rol: str  # auditor | supervisor | gerente | admin
    direccion: str  # DES (Estudios Sectoriales) | DVF (Vigilancia Fiscal)

    # --- Contexto del proceso auditor ---
    fase_actual: str  # preplaneacion | planeacion | ejecucion | informe | seguimiento
    proyecto_auditoria_id: Optional[str]
    sujeto_control: Optional[str]
    vigencia: Optional[str]
    tipo_auditoria: Optional[str]  # financiera | desempeno | cumplimiento | especial

    # --- RAG ---
    contexto_rag: list  # Fragmentos recuperados por el retriever

    # --- Herramientas habilitadas para el turno ---
    herramientas_disponibles: list  # Nombres de herramientas activas

    # --- Respuesta generada ---
    respuesta_final: str
    fuentes: list  # Referencias normativas / documentales citadas

    # --- Configuracion del modelo ---
    modelo: str  # Identificador del modelo LLM activo

    # --- Sesion ---
    session_id: str

    # --- Campos adicionales Sprint 2 ---
    documentos_cargados: list
    hallazgos_en_progreso: list
    formatos_generados: list
    acciones_disponibles: list
    modulo: str  # supervisor | fase_N | transversal
