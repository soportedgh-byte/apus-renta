"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/tools/consultar_secop.py
Proposito: Herramienta LangGraph para consultar contratos y contratistas en SECOP II
Sprint: 7
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from langchain_core.tools import tool

logger = logging.getLogger("cecilia.tools.consultar_secop")


@tool
async def consultar_secop(
    query: str,
    tipo_consulta: str = "contratos",
    entidad: Optional[str] = None,
    contratista: Optional[str] = None,
    numero_proceso: Optional[str] = None,
    valor_minimo: Optional[float] = None,
    valor_maximo: Optional[float] = None,
    region: Optional[str] = None,
    limite: int = 20,
) -> dict[str, Any]:
    """Consulta contratos publicos en SECOP II (Sistema Electronico de Contratacion Publica).

    Tipos de consulta disponibles:
    - contratos: Busca contratos por entidad, contratista, proceso o valor
    - contratista: Busca todos los contratos de un contratista por NIT o nombre
    - detalle: Obtiene detalle completo de un contrato por numero de proceso
    - precios: Analiza precios de mercado para un tipo de objeto contractual

    Args:
        query: Termino de busqueda principal o descripcion de la consulta.
        tipo_consulta: Tipo de consulta (contratos, contratista, detalle, precios).
        entidad: Nombre de la entidad compradora (para tipo=contratos).
        contratista: Nombre o NIT del contratista (para tipo=contratos o contratista).
        numero_proceso: Numero del proceso contractual (para tipo=detalle).
        valor_minimo: Valor minimo del contrato en pesos.
        valor_maximo: Valor maximo del contrato en pesos.
        region: Departamento o region para filtrar (para tipo=precios).
        limite: Numero maximo de resultados.

    Returns:
        Resultados de la consulta SECOP con contratos, estadisticas o analisis.
    """
    from app.integraciones.secop import ClienteSECOP

    try:
        async with ClienteSECOP() as cliente:
            if tipo_consulta == "contratista":
                nit_nombre = contratista or query
                resultado = await cliente.buscar_contratista(nit_o_nombre=nit_nombre, limite=limite)
                return {
                    "tipo": "contratista",
                    "busqueda": nit_nombre,
                    "resultado": resultado,
                }

            elif tipo_consulta == "detalle":
                proceso = numero_proceso or query
                resultado = await cliente.obtener_detalle_contrato(numero_proceso=proceso)
                return {
                    "tipo": "detalle_contrato",
                    "proceso": proceso,
                    "resultado": resultado,
                }

            elif tipo_consulta == "precios":
                resultado = await cliente.analizar_precios_mercado(
                    objeto_contractual=query,
                    region=region,
                    limite=limite,
                )
                return {
                    "tipo": "analisis_precios",
                    "objeto": query,
                    "resultado": resultado,
                }

            else:
                # Busqueda general de contratos
                resultado = await cliente.buscar_contratos(
                    entidad=entidad or (query if not contratista else None),
                    contratista=contratista,
                    numero_proceso=numero_proceso,
                    valor_minimo=valor_minimo,
                    valor_maximo=valor_maximo,
                    limite=limite,
                )
                return {
                    "tipo": "contratos",
                    "total": len(resultado),
                    "contratos": resultado,
                }

    except Exception as error:
        logger.exception("Error en herramienta consultar_secop.")
        return {
            "tipo": tipo_consulta,
            "error": True,
            "mensaje": f"Error al consultar SECOP: {error}",
        }
