"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: __init__.py
Proposito: Paquete de herramientas (tools) LangChain para el proceso auditor
           y consultas a APIs externas
Sprint: 7
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
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
from app.tools.consultar_secop import consultar_secop
from app.tools.verificar_norma import verificar_norma
from app.tools.obtener_datos_dane import obtener_datos_dane

TODAS_LAS_HERRAMIENTAS: list = [
    buscar_normativa,
    calcular_materialidad,
    calcular_muestra,
    analizar_benford,
    analisis_financiero,
    analisis_contratacion,
    generar_formato,
    acceder_workspace_local,
    consultar_secop,
    verificar_norma,
    obtener_datos_dane,
]

# Herramientas de integraciones externas (subconjunto)
HERRAMIENTAS_INTEGRACION: list = [
    consultar_secop,
    verificar_norma,
    obtener_datos_dane,
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
    "consultar_secop",
    "verificar_norma",
    "obtener_datos_dane",
    "TODAS_LAS_HERRAMIENTAS",
    "HERRAMIENTAS_INTEGRACION",
]
