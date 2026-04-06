"""
CecilIA v2 — Clasificador LLM para alertas del Observatorio TIC
Contraloria General de la Republica de Colombia

Proposito: Clasifica contenido detectado usando el LLM para determinar
           relevancia, entidades afectadas y tipo de impacto.
Sprint: 8
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Optional

from langchain_core.messages import HumanMessage, SystemMessage

from app.observatorio.fuentes.base_monitor import ContenidoDetectado

logger = logging.getLogger("cecilia.observatorio.clasificador")

PROMPT_SISTEMA = """Eres un analista experto de la Contraloria General de la Republica de Colombia,
especializado en el sector de Tecnologias de la Informacion y las Comunicaciones (TIC).

Tu tarea es clasificar noticias, regulaciones y legislacion del sector TIC colombiano
segun su relevancia para el control fiscal.

Responde SIEMPRE en formato JSON valido con esta estructura exacta:
{
    "relevancia": "ALTA" | "MEDIA" | "BAJA",
    "tipo_impacto": "presupuestal" | "regulatorio" | "contractual",
    "entidades_afectadas": ["lista de entidades del sector TIC potencialmente afectadas"],
    "resumen_ejecutivo": "Resumen en exactamente 3 lineas cortas para un director de la CGR"
}

Criterios de relevancia para control fiscal:
- ALTA: Afecta directamente presupuestos publicos, contratacion estatal TIC, o genera riesgo fiscal
- MEDIA: Cambio regulatorio que impacta entidades bajo vigilancia de la CGR, o tendencia que requiere seguimiento
- BAJA: Informativa, sin impacto fiscal directo inmediato

Entidades tipicas del sector TIC colombiano:
MinTIC, CRC, ANE, RTVC, Fondo de las TIC, Colombia TIC, ETB, EMCALI Telecomunicaciones,
operadores moviles (Claro, Movistar, Tigo, WOM), DNP, SIC, Colciencias/Minciencias
"""


@dataclass
class ClasificacionAlerta:
    """Resultado de la clasificacion LLM de un contenido."""

    relevancia: str  # ALTA | MEDIA | BAJA
    tipo_impacto: str  # presupuestal | regulatorio | contractual
    entidades_afectadas: list[str]
    resumen_ejecutivo: str
    exito: bool = True
    error: Optional[str] = None


async def clasificar_contenido(contenido: ContenidoDetectado) -> ClasificacionAlerta:
    """Clasifica un contenido detectado usando el LLM.

    Solo genera alerta si relevancia >= MEDIA.
    """
    try:
        from app.llm import obtener_llm

        llm = obtener_llm()

        texto_a_clasificar = f"""TITULO: {contenido.titulo}

FUENTE: {contenido.fuente_nombre}
TIPO: {contenido.tipo}
URL: {contenido.url}

RESUMEN/CONTEXTO:
{contenido.resumen or contenido.contenido_completo or 'No disponible'}
"""

        mensajes = [
            SystemMessage(content=PROMPT_SISTEMA),
            HumanMessage(content=f"Clasifica el siguiente contenido del sector TIC:\n\n{texto_a_clasificar}"),
        ]

        respuesta = llm.invoke(mensajes)
        texto_respuesta = respuesta.content if hasattr(respuesta, "content") else str(respuesta)

        # Extraer JSON de la respuesta
        clasificacion = _parsear_json_respuesta(texto_respuesta)

        return ClasificacionAlerta(
            relevancia=clasificacion.get("relevancia", "BAJA"),
            tipo_impacto=clasificacion.get("tipo_impacto", "regulatorio"),
            entidades_afectadas=clasificacion.get("entidades_afectadas", []),
            resumen_ejecutivo=clasificacion.get("resumen_ejecutivo", contenido.titulo),
        )

    except Exception as e:
        logger.error("Error al clasificar contenido '%s': %s", contenido.titulo[:50], e)
        # Fallback: clasificacion basica por palabras clave
        return _clasificacion_fallback(contenido)


def _parsear_json_respuesta(texto: str) -> dict[str, Any]:
    """Extrae JSON de la respuesta del LLM, tolerando texto adicional."""
    # Intentar parsear directamente
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        pass

    # Buscar bloque JSON en la respuesta
    import re
    patron = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', texto, re.DOTALL)
    if patron:
        try:
            return json.loads(patron.group())
        except json.JSONDecodeError:
            pass

    # Buscar entre ```json ... ```
    patron_code = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', texto, re.DOTALL)
    if patron_code:
        try:
            return json.loads(patron_code.group(1))
        except json.JSONDecodeError:
            pass

    logger.warning("No se pudo parsear JSON de la respuesta LLM: %s", texto[:200])
    return {"relevancia": "BAJA", "tipo_impacto": "regulatorio", "entidades_afectadas": [], "resumen_ejecutivo": texto[:200]}


def _clasificacion_fallback(contenido: ContenidoDetectado) -> ClasificacionAlerta:
    """Clasificacion basica sin LLM usando heuristicas de palabras clave."""
    titulo_lower = contenido.titulo.lower()

    # Determinar relevancia
    alta = ["presupuesto", "contrato", "licitacion", "detrimento", "hallazgo",
            "adjudicacion", "adicion", "irregularidad", "sancion", "multa"]
    media = ["resolucion", "regulacion", "decreto", "proyecto de ley",
             "conectividad", "espectro", "5g", "banda ancha"]

    relevancia = "BAJA"
    if any(p in titulo_lower for p in alta):
        relevancia = "ALTA"
    elif any(p in titulo_lower for p in media):
        relevancia = "MEDIA"

    # Tipo de impacto
    if any(p in titulo_lower for p in ["presupuesto", "contrato", "licitacion", "adjudicacion"]):
        tipo = "contractual"
    elif any(p in titulo_lower for p in ["resolucion", "regulacion", "decreto", "ley"]):
        tipo = "regulatorio"
    else:
        tipo = "presupuestal"

    # Entidades
    entidades = []
    if "mintic" in titulo_lower:
        entidades.append("MinTIC")
    if "crc" in titulo_lower or "crcom" in titulo_lower:
        entidades.append("CRC")
    if "ane" in titulo_lower or "espectro" in titulo_lower:
        entidades.append("ANE")
    if not entidades:
        entidades = ["Sector TIC"]

    return ClasificacionAlerta(
        relevancia=relevancia,
        tipo_impacto=tipo,
        entidades_afectadas=entidades,
        resumen_ejecutivo=contenido.titulo[:200],
        exito=True,
        error="Clasificacion por heuristica (LLM no disponible)",
    )
