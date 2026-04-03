"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: analizar_benford.py
Propósito: Herramienta LangChain para análisis de Ley de Benford (detección de fraude)
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
import math
from collections import Counter
from typing import Optional

from langchain_core.tools import tool

logger = logging.getLogger("cecilia.tools.benford")

# Distribución teórica de Benford para el primer dígito
BENFORD_PRIMER_DIGITO: dict[int, float] = {
    d: math.log10(1 + 1 / d) for d in range(1, 10)
}

# Distribución teórica para el segundo dígito
BENFORD_SEGUNDO_DIGITO: dict[int, float] = {
    d: sum(math.log10(1 + 1 / (10 * k + d)) for k in range(1, 10))
    for d in range(0, 10)
}


def _extraer_primer_digito(valor: float) -> Optional[int]:
    """Extrae el primer dígito significativo de un número.

    Args:
        valor: Número del cual extraer el primer dígito.

    Returns:
        Primer dígito (1-9) o None si no es válido.
    """
    if valor <= 0:
        return None
    cadena: str = f"{abs(valor):.10f}".lstrip("0").lstrip(".")
    for char in cadena:
        if char.isdigit() and char != "0":
            return int(char)
    return None


def _extraer_segundo_digito(valor: float) -> Optional[int]:
    """Extrae el segundo dígito significativo de un número.

    Args:
        valor: Número del cual extraer el segundo dígito.

    Returns:
        Segundo dígito (0-9) o None si no es válido.
    """
    if valor <= 0:
        return None
    cadena: str = f"{abs(valor):.10f}".lstrip("0").lstrip(".")
    digitos_significativos: list[str] = [c for c in cadena if c.isdigit() and c != "0" or (c == "0" and len([x for x in cadena[:cadena.index(c)] if x.isdigit() and x != "0"]) > 0)]

    # Extraer primeros dos dígitos significativos
    nums: str = ""
    encontro_primer: bool = False
    for c in cadena:
        if c == ".":
            continue
        if not encontro_primer and c == "0":
            continue
        if c.isdigit():
            encontro_primer = True
            nums += c
            if len(nums) == 2:
                return int(nums[1])
    return None


def _test_chi_cuadrado(
    frecuencias_observadas: dict[int, float],
    frecuencias_esperadas: dict[int, float],
    n: int,
) -> tuple[float, bool]:
    """Realiza el test Chi-cuadrado de bondad de ajuste.

    Args:
        frecuencias_observadas: Proporciones observadas por dígito.
        frecuencias_esperadas: Proporciones esperadas (Benford).
        n: Tamaño total de la muestra.

    Returns:
        Tupla (estadístico chi2, es_significativo al 5%).
    """
    chi2: float = 0.0
    grados_libertad: int = len(frecuencias_esperadas) - 1

    for digito, esperada in frecuencias_esperadas.items():
        observada: float = frecuencias_observadas.get(digito, 0.0)
        esperada_count: float = esperada * n
        observada_count: float = observada * n
        if esperada_count > 0:
            chi2 += (observada_count - esperada_count) ** 2 / esperada_count

    # Valor crítico Chi² al 5% para 8 grados de libertad (primer dígito)
    valores_criticos: dict[int, float] = {
        8: 15.507,  # primer dígito (9 categorías - 1)
        9: 16.919,  # segundo dígito (10 categorías - 1)
    }
    valor_critico: float = valores_criticos.get(grados_libertad, 15.507)

    return chi2, chi2 > valor_critico


@tool
def analizar_benford(
    valores: list[float],
    nombre_dataset: str = "Conjunto de datos",
    analisis_segundo_digito: bool = False,
) -> str:
    """Aplica el análisis de la Ley de Benford a un conjunto de datos numéricos.

    La Ley de Benford establece que en muchos conjuntos de datos naturales,
    el primer dígito significativo sigue una distribución logarítmica
    específica. Desviaciones significativas pueden indicar manipulación de datos.

    Args:
        valores: Lista de valores numéricos a analizar (ej: montos de contratos,
                 pagos, facturas). Mínimo 100 valores recomendados.
        nombre_dataset: Nombre descriptivo del conjunto de datos para el informe.
        analisis_segundo_digito: Si True, incluye análisis del segundo dígito.

    Returns:
        Informe de análisis de Benford con resultados estadísticos.
    """
    logger.info(
        "Análisis de Benford: %s (%d valores)",
        nombre_dataset, len(valores),
    )

    if len(valores) < 10:
        return "Se requieren al menos 10 valores para el análisis de Benford. Se recomiendan mínimo 100."

    # --- Análisis del primer dígito ---
    primeros_digitos: list[int] = [d for v in valores if (d := _extraer_primer_digito(v)) is not None]

    if not primeros_digitos:
        return "No se pudieron extraer dígitos significativos de los valores proporcionados."

    n: int = len(primeros_digitos)
    conteo: Counter = Counter(primeros_digitos)

    frecuencias_obs: dict[int, float] = {
        d: conteo.get(d, 0) / n for d in range(1, 10)
    }

    chi2, es_significativo = _test_chi_cuadrado(frecuencias_obs, BENFORD_PRIMER_DIGITO, n)

    # Calcular MAD (Mean Absolute Deviation)
    mad: float = sum(
        abs(frecuencias_obs.get(d, 0) - BENFORD_PRIMER_DIGITO[d])
        for d in range(1, 10)
    ) / 9

    # Clasificación del MAD
    if mad < 0.006:
        clasificacion_mad: str = "CONFORMIDAD CERCANA"
    elif mad < 0.012:
        clasificacion_mad = "CONFORMIDAD ACEPTABLE"
    elif mad < 0.015:
        clasificacion_mad = "CONFORMIDAD MARGINAL"
    else:
        clasificacion_mad = "NO CONFORMIDAD — REQUIERE INVESTIGACIÓN"

    # Construir tabla de resultados
    lineas_tabla: list[str] = ["Dígito | Observado | Esperado | Diferencia"]
    lineas_tabla.append("-------|-----------|----------|----------")

    digitos_sospechosos: list[str] = []
    for d in range(1, 10):
        obs: float = frecuencias_obs.get(d, 0)
        esp: float = BENFORD_PRIMER_DIGITO[d]
        dif: float = obs - esp
        marca: str = " ⚑" if abs(dif) > 0.03 else ""
        if abs(dif) > 0.03:
            digitos_sospechosos.append(f"Dígito {d}: observado {obs * 100:.1f}% vs esperado {esp * 100:.1f}%")
        lineas_tabla.append(
            f"   {d}   | {obs * 100:7.2f}% | {esp * 100:6.2f}%  | {dif * 100:+6.2f}%{marca}"
        )

    tabla: str = "\n".join(lineas_tabla)

    alertas: str = ""
    if digitos_sospechosos:
        alertas = "\nDígitos con desviación significativa (> 3%):\n" + "\n".join(
            f"  ⚑ {s}" for s in digitos_sospechosos
        )

    resultado: str = f"""
=== ANÁLISIS DE LEY DE BENFORD ===
Dataset: {nombre_dataset}
Total de valores analizados: {n:,}
Valores originales proporcionados: {len(valores):,}

--- Distribución del Primer Dígito ---
{tabla}

--- Pruebas estadísticas ---
Test Chi-cuadrado: χ² = {chi2:.3f}
  Significativo al 5%: {'SÍ — la distribución NO se ajusta a Benford' if es_significativo else 'NO — la distribución se ajusta a Benford'}

MAD (Mean Absolute Deviation): {mad:.4f}
  Clasificación: {clasificacion_mad}
{alertas}

--- Interpretación ---
{'⚠️ Los datos muestran desviaciones significativas respecto a la Ley de Benford. '
 'Esto puede indicar manipulación, fabricación o errores en los datos. '
 'Se recomienda investigar los registros asociados a los dígitos con mayor desviación.'
 if es_significativo or mad >= 0.015
 else '✓ Los datos se ajustan razonablemente a la distribución de Benford. '
      'No se detectan indicios estadísticos de manipulación.'}

--- Fundamentación ---
- NIA 240: Responsabilidades del auditor respecto al fraude.
- NIA 520: Procedimientos analíticos.
- Benford, F. (1938). The Law of Anomalous Numbers. American Philosophical Society.
- Nigrini, M. J. (2012). Benford's Law. Wiley.

⚠️ Los resultados son indicios estadísticos, NO pruebas de fraude.
Requieren verificación con evidencia adicional por el equipo auditor.
""".strip()

    return resultado
