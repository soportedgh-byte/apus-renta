"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: analisis_contratacion.py
Propósito: Herramienta LangChain para análisis de contratación pública (SECOP)
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional

from langchain_core.tools import tool

logger = logging.getLogger("cecilia.tools.contratacion")

# Modalidades de contratación según Ley 80/1993 y Ley 1150/2007
MODALIDADES_CONTRATACION: dict[str, str] = {
    "licitacion_publica": "Licitación Pública (Art. 30, Ley 80/1993)",
    "seleccion_abreviada": "Selección Abreviada (Art. 2, Ley 1150/2007)",
    "concurso_meritos": "Concurso de Méritos (Art. 2, num. 3, Ley 1150/2007)",
    "contratacion_directa": "Contratación Directa (Art. 2, num. 4, Ley 1150/2007)",
    "minima_cuantia": "Mínima Cuantía (Art. 94, Ley 1474/2011)",
}

# Umbrales de contratación directa por presupuesto (simplificados)
# Los umbrales reales dependen del presupuesto anual de cada entidad
UMBRAL_MINIMA_CUANTIA_SMLV: int = 28  # Hasta 28 SMLV


@tool
def analisis_contratacion(
    contratos: list[dict[str, Any]],
    nombre_entidad: str = "Sujeto de Control",
    vigencia: str = "2025",
    smlv: float = 1_423_500.0,
) -> str:
    """Analiza un conjunto de contratos públicos para detectar irregularidades.

    Realiza análisis de contratación pública conforme a Ley 80/1993,
    Ley 1150/2007 y Ley 1474/2011. Detecta banderas rojas como
    fraccionamiento contractual, concentración en proveedores,
    adiciones excesivas y contratación directa injustificada.

    Args:
        contratos: Lista de diccionarios con datos de contratos. Cada contrato
                   debe tener: numero, objeto, valor, modalidad, contratista,
                   fecha_inicio, fecha_fin, adiciones (opcional), nit_contratista.
        nombre_entidad: Nombre de la entidad contratante.
        vigencia: Vigencia fiscal del análisis.
        smlv: Salario Mínimo Legal Mensual Vigente (COP).

    Returns:
        Informe de análisis de contratación con banderas rojas detectadas.
    """
    logger.info(
        "Análisis de contratación: %s (%d contratos, vigencia %s)",
        nombre_entidad, len(contratos), vigencia,
    )

    if not contratos:
        return "No se proporcionaron contratos para analizar."

    banderas_rojas: list[str] = []
    estadisticas: dict[str, Any] = {
        "total_contratos": len(contratos),
        "valor_total": 0.0,
        "por_modalidad": {},
        "por_contratista": {},
    }

    def fmt(valor: float) -> str:
        return f"${valor:,.0f}"

    # --- Procesar cada contrato ---
    for contrato in contratos:
        valor: float = float(contrato.get("valor", 0))
        modalidad: str = contrato.get("modalidad", "no_especificada")
        contratista: str = contrato.get("contratista", "No identificado")
        nit: str = contrato.get("nit_contratista", "No identificado")
        numero: str = contrato.get("numero", "S/N")
        adiciones: float = float(contrato.get("adiciones", 0))

        estadisticas["valor_total"] += valor

        # Estadísticas por modalidad
        if modalidad not in estadisticas["por_modalidad"]:
            estadisticas["por_modalidad"][modalidad] = {"cantidad": 0, "valor": 0.0}
        estadisticas["por_modalidad"][modalidad]["cantidad"] += 1
        estadisticas["por_modalidad"][modalidad]["valor"] += valor

        # Estadísticas por contratista
        clave_contratista: str = f"{contratista} ({nit})"
        if clave_contratista not in estadisticas["por_contratista"]:
            estadisticas["por_contratista"][clave_contratista] = {"cantidad": 0, "valor": 0.0}
        estadisticas["por_contratista"][clave_contratista]["cantidad"] += 1
        estadisticas["por_contratista"][clave_contratista]["valor"] += valor

        # --- Banderas rojas por contrato ---

        # 1. Adiciones superiores al 50%
        if adiciones > 0 and valor > 0:
            porcentaje_adicion: float = adiciones / valor
            if porcentaje_adicion > 0.5:
                banderas_rojas.append(
                    f"⚑ Contrato {numero}: Adición del {porcentaje_adicion * 100:.0f}% "
                    f"({fmt(adiciones)}) supera el 50% del valor inicial ({fmt(valor)}). "
                    f"Posible violación del Art. 40, Ley 80/1993."
                )

    # --- Análisis de fraccionamiento contractual ---
    for modalidad_key, datos_mod in estadisticas["por_modalidad"].items():
        if modalidad_key in ("contratacion_directa", "minima_cuantia"):
            valor_promedio: float = datos_mod["valor"] / datos_mod["cantidad"] if datos_mod["cantidad"] > 0 else 0
            umbral_cuantia: float = smlv * UMBRAL_MINIMA_CUANTIA_SMLV

            if datos_mod["cantidad"] > 5 and datos_mod["valor"] > umbral_cuantia * 3:
                banderas_rojas.append(
                    f"⚑ Posible FRACCIONAMIENTO CONTRACTUAL: {datos_mod['cantidad']} contratos "
                    f"por {modalidad_key} con valor total {fmt(datos_mod['valor'])}. "
                    f"Valor promedio: {fmt(valor_promedio)}. "
                    f"Verificar si debió utilizarse otra modalidad de selección."
                )

    # --- Concentración en proveedores ---
    for contratista_key, datos_contr in estadisticas["por_contratista"].items():
        if datos_contr["cantidad"] >= 3:
            porcentaje_valor: float = (
                datos_contr["valor"] / estadisticas["valor_total"] * 100
                if estadisticas["valor_total"] > 0 else 0
            )
            if porcentaje_valor > 30:
                banderas_rojas.append(
                    f"⚑ CONCENTRACIÓN: {contratista_key} tiene {datos_contr['cantidad']} "
                    f"contratos ({porcentaje_valor:.1f}% del valor total: {fmt(datos_contr['valor'])}). "
                    f"Verificar principio de selección objetiva (Art. 5, Ley 1150/2007)."
                )

    # --- Contratación directa excesiva ---
    directa: dict[str, Any] = estadisticas["por_modalidad"].get("contratacion_directa", {"cantidad": 0, "valor": 0})
    if estadisticas["total_contratos"] > 0:
        porcentaje_directa: float = directa["cantidad"] / estadisticas["total_contratos"] * 100
        if porcentaje_directa > 60:
            banderas_rojas.append(
                f"⚑ El {porcentaje_directa:.0f}% de los contratos ({directa['cantidad']}/{estadisticas['total_contratos']}) "
                f"se celebraron por contratación directa. Verificar causal de Ley 1150/2007, Art. 2, num. 4."
            )

    # --- Construir informe ---
    secciones: list[str] = [
        f"=== ANÁLISIS DE CONTRATACIÓN PÚBLICA ===",
        f"Entidad: {nombre_entidad}",
        f"Vigencia: {vigencia}",
        f"SMLV vigente: {fmt(smlv)}",
        f"",
        f"--- Resumen general ---",
        f"Total contratos: {estadisticas['total_contratos']}",
        f"Valor total contratado: {fmt(estadisticas['valor_total'])}",
        f"",
        f"--- Por modalidad de contratación ---",
    ]

    for mod, datos in sorted(estadisticas["por_modalidad"].items()):
        nombre_mod: str = MODALIDADES_CONTRATACION.get(mod, mod)
        secciones.append(
            f"  {nombre_mod}: {datos['cantidad']} contratos — {fmt(datos['valor'])}"
        )

    secciones.append("")
    secciones.append(f"--- Principales contratistas ---")

    contratistas_ordenados = sorted(
        estadisticas["por_contratista"].items(),
        key=lambda x: x[1]["valor"],
        reverse=True,
    )
    for contr, datos in contratistas_ordenados[:10]:
        secciones.append(f"  {contr}: {datos['cantidad']} contratos — {fmt(datos['valor'])}")

    secciones.append("")
    if banderas_rojas:
        secciones.append(f"--- BANDERAS ROJAS DETECTADAS ({len(banderas_rojas)}) ---")
        for br in banderas_rojas:
            secciones.append(f"  {br}")
    else:
        secciones.append("--- No se detectaron banderas rojas automáticas ---")

    secciones.extend([
        "",
        "--- Fundamentación normativa ---",
        "- Ley 80/1993: Estatuto General de Contratación.",
        "- Ley 1150/2007: Eficiencia y transparencia en contratación.",
        "- Ley 1474/2011: Estatuto Anticorrupción.",
        "- Ley 1882/2018: Normas complementarias.",
        "- Decreto 1082/2015: Reglamento del sector administrativo de planeación.",
        "",
        "⚠️ Las banderas rojas son indicios que requieren verificación.",
        "Consulte SECOP I/II para validar la información contractual.",
    ])

    return "\n".join(secciones)
