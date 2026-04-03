"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: __init__.py
Propósito: Paquete de agentes transversales
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from backend.app.agents.transversales.analista_financiero import ejecutar_analisis_financiero
from backend.app.agents.transversales.normativo_juridico import ejecutar_analisis_normativo
from backend.app.agents.transversales.generador_formatos import ejecutar_generador_formatos
from backend.app.agents.transversales.detector_fraude import ejecutar_detector_fraude

__all__: list[str] = [
    "ejecutar_analisis_financiero",
    "ejecutar_analisis_normativo",
    "ejecutar_generador_formatos",
    "ejecutar_detector_fraude",
]
