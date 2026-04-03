"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: __init__.py
Propósito: Paquete de herramientas (tools) LangChain para el proceso auditor
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from app.tools.buscar_normativa import buscar_normativa
from app.tools.calcular_materialidad import calcular_materialidad
from app.tools.calcular_muestra import calcular_muestra
from app.tools.analizar_benford import analizar_benford
from app.tools.analisis_financiero import analisis_financiero
from app.tools.analisis_contratacion import analisis_contratacion
from app.tools.generar_formato import generar_formato
from app.tools.acceder_workspace_local import acceder_workspace_local

TODAS_LAS_HERRAMIENTAS: list = [
    buscar_normativa,
    calcular_materialidad,
    calcular_muestra,
    analizar_benford,
    analisis_financiero,
    analisis_contratacion,
    generar_formato,
    acceder_workspace_local,
]

__all__: list[str] = [
    "buscar_normativa",
    "calcular_materialidad",
    "calcular_muestra",
    "analizar_benford",
    "analisis_financiero",
    "analisis_contratacion",
    "generar_formato",
    "acceder_workspace_local",
    "TODAS_LAS_HERRAMIENTAS",
]
