"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: buscar_normativa.py
Propósito: Herramienta LangChain para búsqueda en el corpus normativo de control fiscal
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from typing import Optional

from langchain_core.tools import tool

logger = logging.getLogger("cecilia.tools.buscar_normativa")

# Colecciones normativas disponibles en la base vectorial
COLECCIONES_NORMATIVAS: list[str] = [
    "leyes",
    "decretos",
    "resoluciones_organicas",
    "jurisprudencia",
    "guias_auditoria",
    "conceptos_cgr",
    "normativa_contable",
]


@tool
def buscar_normativa(
    consulta: str,
    tipo_norma: Optional[str] = None,
    top_k: int = 5,
) -> str:
    """Busca en el corpus normativo de control fiscal colombiano.

    Realiza búsqueda semántica en la base de conocimiento normativo
    que incluye leyes, decretos, resoluciones orgánicas, jurisprudencia
    y guías de auditoría de la CGR.

    Args:
        consulta: Texto de la búsqueda normativa (ej: 'responsabilidad fiscal
                  del gestor público', 'materialidad en auditoría financiera').
        tipo_norma: Filtro opcional por tipo de norma: leyes, decretos,
                    resoluciones_organicas, jurisprudencia, guias_auditoria,
                    conceptos_cgr, normativa_contable. Si es None, busca en todas.
        top_k: Número máximo de resultados (default: 5).

    Returns:
        Texto con los fragmentos normativos relevantes y sus fuentes.
    """
    from backend.app.rag.retriever import buscar_similares, ResultadoBusqueda
    from backend.app.rag.reranker import reordenar_resultados
    import asyncio

    logger.info(
        "Búsqueda normativa: '%s' (tipo=%s, top_k=%d)",
        consulta[:100], tipo_norma, top_k,
    )

    coleccion: str = tipo_norma if tipo_norma in COLECCIONES_NORMATIVAS else "normativa"

    try:
        # Ejecutar búsqueda asíncrona
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                resultados: list[ResultadoBusqueda] = pool.submit(
                    asyncio.run,
                    buscar_similares(consulta, coleccion=coleccion, top_k=top_k * 2),
                ).result()
        else:
            resultados = asyncio.run(
                buscar_similares(consulta, coleccion=coleccion, top_k=top_k * 2)
            )

        # Re-ranking
        resultados = reordenar_resultados(
            resultados, consulta, top_k=top_k, coleccion_preferida=coleccion
        )

    except Exception:
        logger.exception("Error en búsqueda normativa.")
        return (
            "No fue posible realizar la búsqueda normativa en este momento. "
            "Por favor consulte directamente las fuentes normativas oficiales."
        )

    if not resultados:
        return (
            f"No se encontraron resultados normativos para: '{consulta}'. "
            f"Sugerencia: reformule la consulta o consulte directamente "
            f"las leyes 42/1993, 610/2000 y el Decreto 403/2020."
        )

    # Formatear resultados
    secciones: list[str] = [f"Resultados normativos para: '{consulta}'\n"]

    for i, resultado in enumerate(resultados, 1):
        fuente: str = resultado.metadata.get("nombre_archivo", "Fuente no identificada")
        norma: str = resultado.metadata.get("norma", "")
        articulo: str = resultado.metadata.get("articulo", "")

        referencia: str = f"{norma} {articulo}".strip() if norma else fuente

        secciones.append(
            f"--- Resultado {i} (relevancia: {resultado.score:.2f}) ---\n"
            f"Fuente: {referencia}\n"
            f"{resultado.contenido}\n"
        )

    secciones.append(
        "\nNota: Verifique siempre la vigencia de las normas citadas "
        "en las fuentes oficiales (Diario Oficial, SUIN-Juriscol)."
    )

    return "\n".join(secciones)
