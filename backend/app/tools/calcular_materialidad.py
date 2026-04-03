"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: calcular_materialidad.py
Propósito: Herramienta LangChain para cálculo de materialidad en auditoría
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from typing import Optional

from langchain_core.tools import tool

logger = logging.getLogger("cecilia.tools.materialidad")

# Porcentajes de referencia según guías de auditoría (NIA 320, ISSAI 1320)
PORCENTAJES_MATERIALIDAD: dict[str, dict[str, float]] = {
    "activos_totales": {"minimo": 0.005, "maximo": 0.02, "tipico": 0.01},
    "ingresos_totales": {"minimo": 0.005, "maximo": 0.02, "tipico": 0.01},
    "gastos_totales": {"minimo": 0.005, "maximo": 0.02, "tipico": 0.01},
    "patrimonio": {"minimo": 0.01, "maximo": 0.05, "tipico": 0.02},
    "presupuesto_ejecutado": {"minimo": 0.005, "maximo": 0.02, "tipico": 0.01},
}

# Porcentaje para materialidad de ejecución (performance materiality)
FACTOR_MATERIALIDAD_EJECUCION: float = 0.75  # 75% de la materialidad global

# Porcentaje para errores claramente insignificantes
FACTOR_ERRORES_INSIGNIFICANTES: float = 0.05  # 5% de la materialidad global


@tool
def calcular_materialidad(
    base_calculo: str,
    valor_base: float,
    porcentaje: Optional[float] = None,
    tipo_auditoria: str = "financiera",
    moneda: str = "COP",
) -> str:
    """Calcula la materialidad para auditoría financiera o de desempeño.

    Calcula tres niveles de materialidad conforme a NIA 320 e ISSAI 1320:
    1. Materialidad global.
    2. Materialidad de ejecución (performance materiality).
    3. Umbral de errores claramente insignificantes.

    Args:
        base_calculo: Base para el cálculo. Opciones: activos_totales,
                      ingresos_totales, gastos_totales, patrimonio,
                      presupuesto_ejecutado.
        valor_base: Valor monetario de la base de cálculo (en la moneda indicada).
        porcentaje: Porcentaje a aplicar (ej: 0.01 para 1%). Si es None,
                    usa el porcentaje típico para la base seleccionada.
        tipo_auditoria: Tipo de auditoría: financiera o desempeno.
        moneda: Moneda (default: COP — pesos colombianos).

    Returns:
        Texto con el cálculo detallado de materialidad.
    """
    logger.info(
        "Cálculo de materialidad: base=%s, valor=%.2f, tipo=%s",
        base_calculo, valor_base, tipo_auditoria,
    )

    # Validaciones
    if base_calculo not in PORCENTAJES_MATERIALIDAD:
        bases_validas: str = ", ".join(PORCENTAJES_MATERIALIDAD.keys())
        return (
            f"Base de cálculo '{base_calculo}' no válida. "
            f"Opciones: {bases_validas}"
        )

    if valor_base <= 0:
        return "El valor base debe ser un número positivo mayor que cero."

    rangos: dict[str, float] = PORCENTAJES_MATERIALIDAD[base_calculo]

    if porcentaje is None:
        porcentaje = rangos["tipico"]
    elif not (rangos["minimo"] <= porcentaje <= rangos["maximo"] * 2):
        logger.warning(
            "Porcentaje %.4f fuera del rango típico [%.4f - %.4f] para %s.",
            porcentaje, rangos["minimo"], rangos["maximo"], base_calculo,
        )

    # Cálculos
    materialidad_global: float = valor_base * porcentaje
    materialidad_ejecucion: float = materialidad_global * FACTOR_MATERIALIDAD_EJECUCION
    errores_insignificantes: float = materialidad_global * FACTOR_ERRORES_INSIGNIFICANTES

    # Formatear valores en moneda colombiana
    def fmt(valor: float) -> str:
        if moneda == "COP":
            return f"${valor:,.0f} COP"
        return f"{valor:,.2f} {moneda}"

    resultado: str = f"""
=== CÁLCULO DE MATERIALIDAD ===
Tipo de auditoría: {tipo_auditoria.capitalize()}
Base de cálculo: {base_calculo.replace('_', ' ').title()}
Valor de la base: {fmt(valor_base)}
Porcentaje aplicado: {porcentaje * 100:.2f}%

--- Resultados ---

1. MATERIALIDAD GLOBAL
   Fórmula: {base_calculo.replace('_', ' ')} x {porcentaje * 100:.2f}%
   Valor: {fmt(materialidad_global)}

2. MATERIALIDAD DE EJECUCIÓN (Performance Materiality)
   Fórmula: Materialidad global x {FACTOR_MATERIALIDAD_EJECUCION * 100:.0f}%
   Valor: {fmt(materialidad_ejecucion)}

3. UMBRAL DE ERRORES CLARAMENTE INSIGNIFICANTES
   Fórmula: Materialidad global x {FACTOR_ERRORES_INSIGNIFICANTES * 100:.0f}%
   Valor: {fmt(errores_insignificantes)}

--- Rango de referencia para {base_calculo.replace('_', ' ')} ---
   Mínimo: {rangos['minimo'] * 100:.2f}% → {fmt(valor_base * rangos['minimo'])}
   Típico: {rangos['tipico'] * 100:.2f}% → {fmt(valor_base * rangos['tipico'])}
   Máximo: {rangos['maximo'] * 100:.2f}% → {fmt(valor_base * rangos['maximo'])}

--- Fundamentación normativa ---
- NIA 320: Materialidad en la planificación y ejecución de una auditoría.
- NIA 450: Evaluación de las incorrecciones identificadas durante la auditoría.
- ISSAI 1320: Materialidad en la planificación y ejecución de auditorías del sector público.
- Guía de Auditoría Financiera de la CGR (Resolución Orgánica vigente).

⚠️ Este cálculo es una asistencia. La determinación final de materialidad
requiere el juicio profesional del auditor y la aprobación del supervisor.
""".strip()

    return resultado
