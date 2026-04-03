"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: calcular_muestra.py
Propósito: Herramienta LangChain para diseño de muestreo estadístico en auditoría
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
import math
from typing import Optional

from langchain_core.tools import tool

logger = logging.getLogger("cecilia.tools.muestra")

# Valores Z para niveles de confianza comunes
VALORES_Z: dict[float, float] = {
    0.90: 1.645,
    0.95: 1.960,
    0.99: 2.576,
}

# Factores de confianza para MUS (Monetary Unit Sampling)
FACTORES_CONFIANZA_MUS: dict[float, dict[int, float]] = {
    0.95: {0: 3.00, 1: 4.75, 2: 6.30, 3: 7.76, 4: 9.16},
    0.90: {0: 2.31, 1: 3.89, 2: 5.33, 3: 6.69, 4: 8.00},
    0.99: {0: 4.61, 1: 6.64, 2: 8.41, 3: 10.05, 4: 11.61},
}


@tool
def calcular_muestra(
    metodo: str,
    poblacion: int,
    nivel_confianza: float = 0.95,
    tasa_error_esperada: float = 0.01,
    precision: float = 0.02,
    materialidad: Optional[float] = None,
    valor_poblacion: Optional[float] = None,
    errores_esperados: int = 0,
) -> str:
    """Calcula el tamaño de muestra para auditoría usando métodos estadísticos.

    Métodos soportados conforme a NIA 530 e ISSAI 1530:
    - MUS (Monetary Unit Sampling / Muestreo de Unidad Monetaria).
    - atributos (Muestreo por atributos para pruebas de cumplimiento).
    - variables (Muestreo por variables para pruebas sustantivas).

    Args:
        metodo: Método de muestreo: 'mus', 'atributos' o 'variables'.
        poblacion: Número de elementos en la población.
        nivel_confianza: Nivel de confianza (0.90, 0.95, 0.99). Default: 0.95.
        tasa_error_esperada: Tasa de error esperada en la población (0.0 a 1.0).
        precision: Precisión deseada (margen de error tolerable).
        materialidad: Materialidad global (requerida para MUS).
        valor_poblacion: Valor monetario total de la población (requerido para MUS).
        errores_esperados: Número de errores esperados (para MUS).

    Returns:
        Texto con el diseño de muestreo detallado.
    """
    metodo = metodo.lower().strip()

    logger.info(
        "Cálculo de muestra: método=%s, población=%d, confianza=%.2f",
        metodo, poblacion, nivel_confianza,
    )

    if metodo == "mus":
        return _calcular_mus(
            poblacion, nivel_confianza, materialidad, valor_poblacion, errores_esperados
        )
    elif metodo == "atributos":
        return _calcular_atributos(
            poblacion, nivel_confianza, tasa_error_esperada, precision
        )
    elif metodo == "variables":
        return _calcular_variables(
            poblacion, nivel_confianza, precision, valor_poblacion
        )
    else:
        return (
            f"Método '{metodo}' no soportado. "
            f"Opciones válidas: mus, atributos, variables."
        )


def _calcular_mus(
    poblacion: int,
    nivel_confianza: float,
    materialidad: Optional[float],
    valor_poblacion: Optional[float],
    errores_esperados: int,
) -> str:
    """Calcula muestreo MUS (Monetary Unit Sampling)."""
    if materialidad is None or materialidad <= 0:
        return "Para MUS se requiere el valor de materialidad (mayor que cero)."
    if valor_poblacion is None or valor_poblacion <= 0:
        return "Para MUS se requiere el valor monetario total de la población."

    factores: dict[int, float] | None = FACTORES_CONFIANZA_MUS.get(nivel_confianza)
    if factores is None:
        niveles_validos: str = ", ".join(str(n) for n in FACTORES_CONFIANZA_MUS.keys())
        return f"Nivel de confianza {nivel_confianza} no soportado para MUS. Opciones: {niveles_validos}"

    errores_clave: int = min(errores_esperados, max(factores.keys()))
    factor_confianza: float = factores[errores_clave]

    # Intervalo de muestreo
    intervalo_muestreo: float = materialidad / factor_confianza

    # Tamaño de muestra
    tamano_muestra: int = math.ceil(valor_poblacion / intervalo_muestreo)
    tamano_muestra = min(tamano_muestra, poblacion)  # No puede superar la población

    def fmt(valor: float) -> str:
        return f"${valor:,.0f} COP"

    resultado: str = f"""
=== DISEÑO DE MUESTREO — MUS (Muestreo de Unidad Monetaria) ===

--- Parámetros de entrada ---
Valor de la población: {fmt(valor_poblacion)}
Número de elementos: {poblacion:,}
Materialidad: {fmt(materialidad)}
Nivel de confianza: {nivel_confianza * 100:.0f}%
Errores esperados: {errores_esperados}

--- Cálculo ---
Factor de confianza (R): {factor_confianza:.2f}
Intervalo de muestreo: Materialidad / R = {fmt(materialidad)} / {factor_confianza:.2f} = {fmt(intervalo_muestreo)}
Tamaño de muestra: Valor población / Intervalo = {fmt(valor_poblacion)} / {fmt(intervalo_muestreo)} = {tamano_muestra}

--- Resultado ---
TAMAÑO DE MUESTRA: {tamano_muestra} unidades monetarias / elementos

--- Fundamentación normativa ---
- NIA 530: Muestreo de auditoría.
- ISSAI 1530: Muestreo en auditoría del sector público.
- Guía de Auditoría Financiera de la CGR.

⚠️ El diseño de muestreo requiere aprobación del supervisor de auditoría.
""".strip()

    return resultado


def _calcular_atributos(
    poblacion: int,
    nivel_confianza: float,
    tasa_error_esperada: float,
    precision: float,
) -> str:
    """Calcula muestreo por atributos para pruebas de cumplimiento."""
    z: float | None = VALORES_Z.get(nivel_confianza)
    if z is None:
        return f"Nivel de confianza {nivel_confianza} no soportado. Opciones: 0.90, 0.95, 0.99"

    # Fórmula para población infinita
    p: float = tasa_error_esperada
    q: float = 1 - p
    e: float = precision

    if e <= 0:
        return "La precisión debe ser mayor que cero."

    n_infinita: float = (z ** 2 * p * q) / (e ** 2)

    # Corrección para población finita
    n_finita: int = math.ceil(n_infinita / (1 + (n_infinita - 1) / poblacion))
    n_finita = min(n_finita, poblacion)

    resultado: str = f"""
=== DISEÑO DE MUESTREO — ATRIBUTOS ===

--- Parámetros de entrada ---
Población: {poblacion:,} elementos
Nivel de confianza: {nivel_confianza * 100:.0f}% (Z = {z:.3f})
Tasa de error esperada: {tasa_error_esperada * 100:.2f}%
Precisión (margen de error): {precision * 100:.2f}%

--- Cálculo ---
Muestra (población infinita): n₀ = Z² × p × q / e²
  n₀ = {z:.3f}² × {p:.4f} × {q:.4f} / {e:.4f}² = {n_infinita:.1f}

Corrección para población finita: n = n₀ / (1 + (n₀ - 1) / N)
  n = {n_infinita:.1f} / (1 + ({n_infinita:.1f} - 1) / {poblacion:,}) = {n_finita}

--- Resultado ---
TAMAÑO DE MUESTRA: {n_finita} elementos

--- Fundamentación normativa ---
- NIA 530: Muestreo de auditoría.
- ISSAI 1530.

⚠️ El diseño de muestreo requiere aprobación del supervisor de auditoría.
""".strip()

    return resultado


def _calcular_variables(
    poblacion: int,
    nivel_confianza: float,
    precision: float,
    valor_poblacion: Optional[float],
) -> str:
    """Calcula muestreo por variables para pruebas sustantivas."""
    z: float | None = VALORES_Z.get(nivel_confianza)
    if z is None:
        return f"Nivel de confianza {nivel_confianza} no soportado. Opciones: 0.90, 0.95, 0.99"

    if precision <= 0:
        return "La precisión debe ser mayor que cero."

    # Estimación con coeficiente de variación asumido (0.5 como conservador)
    cv: float = 0.5
    e: float = precision

    n_infinita: float = (z * cv / e) ** 2

    # Corrección para población finita
    n_finita: int = math.ceil(n_infinita / (1 + (n_infinita - 1) / poblacion))
    n_finita = min(n_finita, poblacion)

    def fmt(valor: float) -> str:
        return f"${valor:,.0f} COP"

    valor_info: str = f"Valor de la población: {fmt(valor_poblacion)}" if valor_poblacion else ""

    resultado: str = f"""
=== DISEÑO DE MUESTREO — VARIABLES ===

--- Parámetros de entrada ---
Población: {poblacion:,} elementos
{valor_info}
Nivel de confianza: {nivel_confianza * 100:.0f}% (Z = {z:.3f})
Precisión relativa: {precision * 100:.2f}%
Coeficiente de variación estimado: {cv * 100:.0f}%

--- Cálculo ---
Muestra (población infinita): n₀ = (Z × CV / e)²
  n₀ = ({z:.3f} × {cv:.2f} / {e:.4f})² = {n_infinita:.1f}

Corrección para población finita: n = n₀ / (1 + (n₀ - 1) / N)
  n = {n_infinita:.1f} / (1 + ({n_infinita:.1f} - 1) / {poblacion:,}) = {n_finita}

--- Resultado ---
TAMAÑO DE MUESTRA: {n_finita} elementos

Nota: El coeficiente de variación se estimó en {cv * 100:.0f}%. Si dispone
del CV real de la población, proporcione ese valor para un cálculo más preciso.

--- Fundamentación normativa ---
- NIA 530: Muestreo de auditoría.
- ISSAI 1530.

⚠️ El diseño de muestreo requiere aprobación del supervisor de auditoría.
""".strip()

    return resultado
