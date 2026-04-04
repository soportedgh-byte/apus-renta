"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: generar_formato.py
Proposito: Herramienta LangChain para generacion de formatos CGR (1-30).
           Integrada con el sistema de generacion DOCX profesional.
Sprint: 4
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import base64
import logging
from typing import Any, Optional

from langchain_core.tools import tool

from app.formatos.registro import CATALOGO_FORMATOS, FORMATOS_IMPLEMENTADOS, obtener_generador

logger = logging.getLogger("cecilia.tools.generar_formato")


@tool
def generar_formato(
    numero_formato: int,
    datos: Optional[dict[str, Any]] = None,
) -> str:
    """Genera un formato CGR oficial del proceso auditor (formatos 1 a 30) en DOCX.

    Genera documentos DOCX profesionales con encabezado institucional de la CGR,
    tablas formateadas, campos por completar y pie de pagina con disclaimer.
    Los campos con informacion disponible se pre-llenan; los faltantes
    se marcan como [COMPLETAR] en rojo.

    Args:
        numero_formato: Numero del formato CGR (1-30).
        datos: Diccionario con los datos para pre-llenar el formato.
               Las claves dependen del formato solicitado.

    Returns:
        Texto con informacion del formato generado y bytes en base64.
    """
    logger.info("Generando formato CGR F%02d via tool", numero_formato)

    if numero_formato < 1 or numero_formato > 30:
        return (
            f"Formato {numero_formato} no valido. "
            f"Los formatos CGR van del 1 al 30."
        )

    if datos is None:
        datos = {}

    info = CATALOGO_FORMATOS.get(numero_formato)
    if not info:
        return f"Formato {numero_formato} no encontrado en el catalogo."

    nombre = info["nombre"]
    fase = info["fase"]
    implementado = numero_formato in FORMATOS_IMPLEMENTADOS

    try:
        # Generar DOCX
        generador = obtener_generador(numero_formato, datos)
        docx_bytes = generador.generar_bytes()

        # Codificar en base64 para transmision
        docx_b64 = base64.b64encode(docx_bytes).decode("utf-8")

        resultado = (
            f"Formato F{numero_formato:02d} — {nombre}\n"
            f"Fase: {fase}\n"
            f"Estado: {'Implementado con tablas especificas' if implementado else 'Estructura basica'}\n"
            f"Tamano: {len(docx_bytes):,} bytes\n\n"
            f"El documento DOCX ha sido generado exitosamente con:\n"
            f"- Encabezado institucional de la CGR\n"
            f"- Tablas profesionales con formato\n"
            f"- Campos [COMPLETAR] en rojo para datos pendientes\n"
            f"- Pie de pagina con disclaimer Circular 023\n\n"
        )

        if implementado:
            resultado += (
                f"Este formato cuenta con estructura completa implementada.\n"
            )
        else:
            resultado += (
                f"Este formato usa estructura generica. "
                f"Se implementara con tablas especificas en proximas versiones.\n"
            )

        resultado += (
            f"\n⚠ NOTA: Este documento fue generado con asistencia de IA. "
            f"Debe ser revisado y validado por el equipo auditor antes de "
            f"su uso oficial (Circular 023 CGR).\n\n"
            f"[DOCX_BASE64:{docx_b64[:100]}...]"
        )

        return resultado

    except Exception as exc:
        logger.error("Error generando formato F%02d: %s", numero_formato, exc)
        return (
            f"Error al generar el formato F{numero_formato:02d}: {str(exc)}. "
            f"Puede intentar nuevamente o contactar al equipo tecnico."
        )


@tool
def listar_formatos_disponibles() -> str:
    """Lista todos los formatos CGR disponibles (1-30) con su estado de implementacion.

    Retorna la lista completa de formatos organizados por fase del proceso auditor.
    """
    fases = {
        "pre-planeacion": [],
        "planeacion": [],
        "ejecucion": [],
    }

    for numero, info in sorted(CATALOGO_FORMATOS.items()):
        estado = "Implementado" if numero in FORMATOS_IMPLEMENTADOS else "Proximamente"
        fases[info["fase"]].append(
            f"  F{numero:02d} — {info['nombre']} [{estado}]"
        )

    resultado = "CATALOGO DE FORMATOS CGR (1-30)\n"
    resultado += "=" * 50 + "\n\n"

    for fase, formatos in fases.items():
        resultado += f"📋 {fase.upper().replace('-', ' ')}\n"
        resultado += "\n".join(formatos) + "\n\n"

    resultado += (
        f"\nTotal: {len(CATALOGO_FORMATOS)} formatos\n"
        f"Implementados con DOCX: {len(FORMATOS_IMPLEMENTADOS)}\n"
        f"Formatos implementados: {sorted(FORMATOS_IMPLEMENTADOS)}\n"
    )

    return resultado
