"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: __init__.py
Propósito: Paquete de agentes transversales
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from app.agents.transversales.analista_financiero import ejecutar_analisis_financiero
from app.agents.transversales.normativo_juridico import ejecutar_analisis_normativo
from app.agents.transversales.generador_formatos import ejecutar_generador_formatos
from app.agents.transversales.detector_fraude import ejecutar_detector_fraude
from app.agents.transversales.tutor import ejecutar_tutor

__all__: list[str] = [
    "ejecutar_analisis_financiero",
    "ejecutar_analisis_normativo",
    "ejecutar_generador_formatos",
    "ejecutar_detector_fraude",
    "ejecutar_tutor",
]
