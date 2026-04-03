"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: analisis_financiero.py
Propósito: Herramienta LangChain para análisis de indicadores y ratios financieros
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from langchain_core.tools import tool

logger = logging.getLogger("cecilia.tools.analisis_financiero")


@tool
def analisis_financiero(
    activo_corriente: float = 0.0,
    activo_no_corriente: float = 0.0,
    pasivo_corriente: float = 0.0,
    pasivo_no_corriente: float = 0.0,
    patrimonio: float = 0.0,
    ingresos_operacionales: float = 0.0,
    gastos_operacionales: float = 0.0,
    resultado_ejercicio: float = 0.0,
    inventarios: float = 0.0,
    cuentas_por_cobrar: float = 0.0,
    nombre_entidad: str = "Sujeto de Control",
    vigencia: str = "2025",
) -> str:
    """Calcula y analiza indicadores financieros de una entidad pública.

    Calcula ratios de liquidez, endeudamiento, actividad y rentabilidad
    aplicables a entidades del sector público colombiano bajo el Marco
    Normativo Contable (NICSP/NIIF según corresponda).

    Args:
        activo_corriente: Total activos corrientes (COP).
        activo_no_corriente: Total activos no corrientes (COP).
        pasivo_corriente: Total pasivos corrientes (COP).
        pasivo_no_corriente: Total pasivos no corrientes (COP).
        patrimonio: Total patrimonio (COP).
        ingresos_operacionales: Total ingresos operacionales (COP).
        gastos_operacionales: Total gastos operacionales (COP).
        resultado_ejercicio: Resultado del ejercicio (COP).
        inventarios: Total inventarios (COP).
        cuentas_por_cobrar: Total cuentas por cobrar (COP).
        nombre_entidad: Nombre de la entidad analizada.
        vigencia: Vigencia fiscal del análisis.

    Returns:
        Informe con indicadores financieros calculados e interpretados.
    """
    logger.info("Análisis financiero: %s (vigencia %s)", nombre_entidad, vigencia)

    activo_total: float = activo_corriente + activo_no_corriente
    pasivo_total: float = pasivo_corriente + pasivo_no_corriente
    resultado_operacional: float = ingresos_operacionales - gastos_operacionales

    def fmt(valor: float) -> str:
        return f"${valor:,.0f}"

    def ratio_seguro(numerador: float, denominador: float) -> Optional[float]:
        if denominador == 0:
            return None
        return numerador / denominador

    # --- Cálculo de indicadores ---
    indicadores: list[dict[str, Any]] = []

    # Liquidez
    razon_corriente: Optional[float] = ratio_seguro(activo_corriente, pasivo_corriente)
    indicadores.append({
        "grupo": "LIQUIDEZ",
        "nombre": "Razón Corriente",
        "formula": "Activo Corriente / Pasivo Corriente",
        "valor": razon_corriente,
        "formato": f"{razon_corriente:.2f}" if razon_corriente else "N/A",
        "interpretacion": _interpretar_razon_corriente(razon_corriente),
    })

    prueba_acida: Optional[float] = ratio_seguro(activo_corriente - inventarios, pasivo_corriente)
    indicadores.append({
        "grupo": "LIQUIDEZ",
        "nombre": "Prueba Ácida",
        "formula": "(Activo Corriente - Inventarios) / Pasivo Corriente",
        "valor": prueba_acida,
        "formato": f"{prueba_acida:.2f}" if prueba_acida else "N/A",
        "interpretacion": _interpretar_prueba_acida(prueba_acida),
    })

    capital_trabajo: float = activo_corriente - pasivo_corriente
    indicadores.append({
        "grupo": "LIQUIDEZ",
        "nombre": "Capital de Trabajo",
        "formula": "Activo Corriente - Pasivo Corriente",
        "valor": capital_trabajo,
        "formato": fmt(capital_trabajo),
        "interpretacion": "Positivo: capacidad de cubrir obligaciones a corto plazo." if capital_trabajo > 0 else "Negativo: posible riesgo de liquidez.",
    })

    # Endeudamiento
    nivel_endeudamiento: Optional[float] = ratio_seguro(pasivo_total, activo_total)
    indicadores.append({
        "grupo": "ENDEUDAMIENTO",
        "nombre": "Nivel de Endeudamiento",
        "formula": "Pasivo Total / Activo Total",
        "valor": nivel_endeudamiento,
        "formato": f"{nivel_endeudamiento * 100:.1f}%" if nivel_endeudamiento else "N/A",
        "interpretacion": _interpretar_endeudamiento(nivel_endeudamiento),
    })

    concentracion_cp: Optional[float] = ratio_seguro(pasivo_corriente, pasivo_total)
    indicadores.append({
        "grupo": "ENDEUDAMIENTO",
        "nombre": "Concentración del Pasivo a Corto Plazo",
        "formula": "Pasivo Corriente / Pasivo Total",
        "valor": concentracion_cp,
        "formato": f"{concentracion_cp * 100:.1f}%" if concentracion_cp else "N/A",
        "interpretacion": "Alta concentración (>70%) indica presión financiera a corto plazo." if concentracion_cp and concentracion_cp > 0.7 else "Distribución razonable de obligaciones.",
    })

    solvencia: Optional[float] = ratio_seguro(activo_total, pasivo_total)
    indicadores.append({
        "grupo": "ENDEUDAMIENTO",
        "nombre": "Solvencia",
        "formula": "Activo Total / Pasivo Total",
        "valor": solvencia,
        "formato": f"{solvencia:.2f}" if solvencia else "N/A",
        "interpretacion": "Solvente (>1)." if solvencia and solvencia > 1 else "Riesgo de insolvencia (<1)." if solvencia else "N/A",
    })

    # Rentabilidad
    margen_operacional: Optional[float] = ratio_seguro(resultado_operacional, ingresos_operacionales)
    indicadores.append({
        "grupo": "RENTABILIDAD",
        "nombre": "Margen Operacional",
        "formula": "Resultado Operacional / Ingresos Operacionales",
        "valor": margen_operacional,
        "formato": f"{margen_operacional * 100:.1f}%" if margen_operacional else "N/A",
        "interpretacion": _interpretar_margen(margen_operacional),
    })

    roe: Optional[float] = ratio_seguro(resultado_ejercicio, patrimonio)
    indicadores.append({
        "grupo": "RENTABILIDAD",
        "nombre": "Rentabilidad del Patrimonio (ROE)",
        "formula": "Resultado del Ejercicio / Patrimonio",
        "valor": roe,
        "formato": f"{roe * 100:.1f}%" if roe else "N/A",
        "interpretacion": "Mide la rentabilidad generada sobre los recursos propios.",
    })

    roa: Optional[float] = ratio_seguro(resultado_ejercicio, activo_total)
    indicadores.append({
        "grupo": "RENTABILIDAD",
        "nombre": "Rentabilidad del Activo (ROA)",
        "formula": "Resultado del Ejercicio / Activo Total",
        "valor": roa,
        "formato": f"{roa * 100:.1f}%" if roa else "N/A",
        "interpretacion": "Mide la eficiencia en el uso de los activos totales.",
    })

    # Actividad
    rotacion_cartera: Optional[float] = ratio_seguro(ingresos_operacionales, cuentas_por_cobrar)
    indicadores.append({
        "grupo": "ACTIVIDAD",
        "nombre": "Rotación de Cartera",
        "formula": "Ingresos Operacionales / Cuentas por Cobrar",
        "valor": rotacion_cartera,
        "formato": f"{rotacion_cartera:.1f} veces" if rotacion_cartera else "N/A",
        "interpretacion": f"Días de cobro: {365 / rotacion_cartera:.0f} días" if rotacion_cartera and rotacion_cartera > 0 else "N/A",
    })

    # --- Formatear informe ---
    secciones: list[str] = [
        f"=== ANÁLISIS DE INDICADORES FINANCIEROS ===",
        f"Entidad: {nombre_entidad}",
        f"Vigencia: {vigencia}",
        f"",
        f"--- Resumen de cifras ---",
        f"Activo Total:    {fmt(activo_total)}",
        f"Pasivo Total:    {fmt(pasivo_total)}",
        f"Patrimonio:      {fmt(patrimonio)}",
        f"Ingresos Oper.:  {fmt(ingresos_operacionales)}",
        f"Resultado Ej.:   {fmt(resultado_ejercicio)}",
        f"",
    ]

    grupo_actual: str = ""
    for ind in indicadores:
        if ind["grupo"] != grupo_actual:
            grupo_actual = ind["grupo"]
            secciones.append(f"--- {grupo_actual} ---")

        secciones.append(f"  {ind['nombre']}: {ind['formato']}")
        secciones.append(f"    Fórmula: {ind['formula']}")
        secciones.append(f"    Interpretación: {ind['interpretacion']}")
        secciones.append("")

    secciones.extend([
        "--- Fundamentación normativa ---",
        "- Resolución 533/2015 CGN (Marco Normativo Entidades de Gobierno — NICSP).",
        "- NIA 520: Procedimientos analíticos.",
        "- Guía de Auditoría Financiera de la CGR.",
        "",
        "⚠️ Los indicadores deben validarse con los estados financieros",
        "oficiales del sujeto de control y el dictamen del auditor.",
    ])

    return "\n".join(secciones)


def _interpretar_razon_corriente(valor: Optional[float]) -> str:
    """Interpreta la razón corriente."""
    if valor is None:
        return "No calculable (pasivo corriente = 0)."
    if valor >= 2.0:
        return "Alta liquidez. Posibles recursos ociosos."
    if valor >= 1.0:
        return "Liquidez adecuada para cubrir obligaciones a corto plazo."
    return "Liquidez insuficiente. Riesgo de no cubrir obligaciones a corto plazo."


def _interpretar_prueba_acida(valor: Optional[float]) -> str:
    """Interpreta la prueba ácida."""
    if valor is None:
        return "No calculable."
    if valor >= 1.0:
        return "Capacidad de pago inmediato sin depender de inventarios."
    return "Dependencia de inventarios para cubrir obligaciones a corto plazo."


def _interpretar_endeudamiento(valor: Optional[float]) -> str:
    """Interpreta el nivel de endeudamiento."""
    if valor is None:
        return "No calculable."
    if valor > 0.7:
        return "Alto endeudamiento (>70%). Riesgo financiero elevado."
    if valor > 0.5:
        return "Endeudamiento moderado (50-70%)."
    return "Endeudamiento bajo (<50%). Estructura financiera conservadora."


def _interpretar_margen(valor: Optional[float]) -> str:
    """Interpreta el margen operacional."""
    if valor is None:
        return "No calculable."
    if valor > 0:
        return f"Margen positivo. La operación genera excedentes."
    return "Margen negativo. Los gastos operacionales superan los ingresos."
