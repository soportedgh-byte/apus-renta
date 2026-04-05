"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/tools/verificar_norma.py
Proposito: Herramienta LangGraph para buscar y verificar vigencia de normas
           en la base de datos legislativa del Congreso
Sprint: 7
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from langchain_core.tools import tool

logger = logging.getLogger("cecilia.tools.verificar_norma")


@tool
async def verificar_norma(
    tipo: str = "ley",
    numero: Optional[int] = None,
    anio: Optional[int] = None,
    termino: Optional[str] = None,
    verificar_vigencia: bool = True,
) -> dict[str, Any]:
    """Busca y verifica la vigencia de normas colombianas (leyes, decretos, actos legislativos).

    Permite buscar normas especificas (ej: Ley 42 de 1993, Decreto 403 de 2020)
    o por termino libre, y verificar si siguen vigentes.

    Args:
        tipo: Tipo de norma (ley, decreto, acto_legislativo, resolucion, acuerdo).
        numero: Numero de la norma (ej: 42 para Ley 42).
        anio: Ano de la norma (ej: 1993 para Ley 42 de 1993).
        termino: Termino de busqueda adicional en el titulo.
        verificar_vigencia: Si True, verifica el estado de vigencia de la norma.

    Returns:
        Informacion de la norma con estado de vigencia y datos legislativos.
    """
    from app.integraciones.congreso import ClienteCongreso

    try:
        async with ClienteCongreso() as cliente:
            if verificar_vigencia and (numero or termino):
                # Verificar vigencia de una norma especifica
                resultado = await cliente.verificar_vigencia(
                    tipo=tipo,
                    numero=numero,
                    anio=anio,
                )

                if resultado.get("encontrada"):
                    return {
                        "accion": "verificar_vigencia",
                        "resultado": resultado,
                    }

            # Buscar normas por criterios
            normas = await cliente.buscar_norma(
                tipo=tipo,
                numero=numero,
                anio=anio,
                termino=termino,
                limite=10,
            )

            referencia = f"{tipo}"
            if numero:
                referencia += f" {numero}"
            if anio:
                referencia += f" de {anio}"

            return {
                "accion": "buscar_norma",
                "referencia": referencia,
                "total_encontradas": len(normas),
                "normas": normas,
                "nota": (
                    "Para verificacion definitiva de vigencia, consulte "
                    "SUIN-Juriscol: https://www.suin-juriscol.gov.co/"
                ),
            }

    except Exception as error:
        logger.exception("Error en herramienta verificar_norma.")
        return {
            "accion": "verificar_norma",
            "error": True,
            "mensaje": f"Error al verificar norma: {error}",
        }
