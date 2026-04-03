"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: state.py
Propósito: Definición del estado tipado (AuditState) para el grafo LangGraph
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

from typing import Optional, TypedDict


class AuditState(TypedDict, total=False):
    """Estado compartido entre todos los nodos del grafo de auditoría.

    Cada campo representa un aspecto del contexto de la conversación
    y del proceso auditor en curso. Los campos opcionales (``total=False``)
    permiten que el estado se construya progresivamente a medida que
    el usuario interactúa con el sistema.
    """

    # --- Mensajes de la conversación (formato LangChain) ---
    messages: list

    # --- Identidad y permisos del usuario ---
    usuario_id: str
    rol: str  # auditor | supervisor | gerente | admin
    direccion: str  # DES (Estudios Sectoriales) | DVF (Vigilancia Fiscal)

    # --- Contexto del proceso auditor ---
    fase_actual: str  # preplaneacion | planeacion | ejecucion | informe | seguimiento
    proyecto_auditoria_id: Optional[str]

    # --- RAG ---
    contexto_rag: list  # Fragmentos recuperados por el retriever

    # --- Herramientas habilitadas para el turno ---
    herramientas_disponibles: list  # Nombres de herramientas activas

    # --- Respuesta generada ---
    respuesta_final: str
    fuentes: list  # Referencias normativas / documentales citadas

    # --- Configuración del modelo ---
    modelo: str  # Identificador del modelo LLM activo

    # --- Sesión ---
    session_id: str
