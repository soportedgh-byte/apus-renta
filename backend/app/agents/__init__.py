"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: __init__.py
Propósito: Paquete de agentes del sistema de auditoría
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from app.agents.state import AuditState
from app.agents.graph import ejecutar_grafo, obtener_grafo
from app.agents.supervisor import enrutar_consulta

__all__: list[str] = [
    "AuditState",
    "ejecutar_grafo",
    "obtener_grafo",
    "enrutar_consulta",
]
