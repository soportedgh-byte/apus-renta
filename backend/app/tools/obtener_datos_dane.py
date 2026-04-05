"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/tools/obtener_datos_dane.py
Proposito: Herramienta LangGraph para consultar indicadores economicos del DANE
           (IPC, PIB, desempleo, TIC, etc.)
Sprint: 7
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from langchain_core.tools import tool

logger = logging.getLogger("cecilia.tools.obtener_datos_dane")


@tool
async def obtener_datos_dane(
    indicador: str = "ipc",
    periodo: Optional[str] = None,
    departamento: Optional[str] = None,
    sector: Optional[str] = None,
    limite: int = 12,
) -> dict[str, Any]:
    """Consulta indicadores economicos y estadisticos del DANE (Departamento Nacional de Estadistica).

    Indicadores disponibles:
    - ipc: Indice de Precios al Consumidor (inflacion)
    - pib: Producto Interno Bruto (crecimiento economico)
    - desempleo: Tasa de desempleo
    - pobreza: Pobreza monetaria
    - poblacion: Proyecciones de poblacion
    - tic: Indicadores de Tecnologias de Informacion y Comunicaciones

    Para PIB sectorial, use indicador="pib" y especifique el sector.
    Sectores disponibles: agricultura, mineria, manufactura, energia, construccion,
    comercio, transporte, informacion, financiero, administracion_publica, educacion, salud.

    Args:
        indicador: Codigo del indicador DANE (ipc, pib, desempleo, pobreza, poblacion, tic).
        periodo: Ano o periodo de consulta (ej: '2025', '2025-Q1').
        departamento: Codigo DIVIPOLA del departamento para filtrado.
        sector: Sector economico para PIB sectorial (solo cuando indicador=pib).
        limite: Numero maximo de registros a retornar.

    Returns:
        Datos del indicador con valores, estadisticas y fuente DANE.
    """
    from app.integraciones.dane import ClienteDANE

    try:
        async with ClienteDANE() as cliente:
            indicador_lower = indicador.lower()

            if indicador_lower == "ipc":
                resultado = await cliente.obtener_ipc(
                    periodo=periodo,
                    departamento=departamento,
                    limite=limite,
                )
                return {"indicador": "ipc", "resultado": resultado}

            elif indicador_lower == "pib" and sector:
                resultado = await cliente.obtener_pib_sectorial(
                    sector=sector,
                    periodo=periodo,
                    limite=limite,
                )
                return {"indicador": "pib_sectorial", "sector": sector, "resultado": resultado}

            elif indicador_lower == "tic":
                resultado = await cliente.obtener_estadisticas_tic(
                    periodo=periodo,
                    departamento=departamento,
                    limite=limite,
                )
                return {"indicador": "tic", "resultado": resultado}

            else:
                # Consulta generica del indicador
                registros = await cliente.obtener_indicador(
                    codigo_indicador=indicador_lower,
                    periodo=periodo,
                    departamento=departamento,
                    limite=limite,
                )
                return {
                    "indicador": indicador_lower,
                    "total_registros": len(registros),
                    "registros": registros,
                }

    except Exception as error:
        logger.exception("Error en herramienta obtener_datos_dane.")
        return {
            "indicador": indicador,
            "error": True,
            "mensaje": f"Error al consultar DANE: {error}",
            "indicadores_disponibles": ["ipc", "pib", "desempleo", "pobreza", "poblacion", "tic"],
        }
