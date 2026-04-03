"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: reranker.py
Propósito: Re-ranking de resultados de búsqueda por relevancia contextual
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional

from backend.app.rag.retriever import ResultadoBusqueda

logger = logging.getLogger("cecilia.rag.reranker")

# Pesos para factores de re-ranking
PESO_SCORE_ORIGINAL: float = 0.4
PESO_RELEVANCIA_CONSULTA: float = 0.3
PESO_FRESCURA: float = 0.1
PESO_COLECCION: float = 0.2


def _calcular_relevancia_keywords(consulta: str, contenido: str) -> float:
    """Calcula un score de relevancia basado en presencia de palabras clave.

    Args:
        consulta: Texto de la consulta original del usuario.
        contenido: Contenido del fragmento a evaluar.

    Returns:
        Score entre 0.0 y 1.0.
    """
    # Tokenización básica
    palabras_consulta: set[str] = {
        p.lower()
        for p in re.findall(r"\b\w{3,}\b", consulta)
        if p.lower() not in _STOPWORDS_ES
    }

    if not palabras_consulta:
        return 0.0

    contenido_lower: str = contenido.lower()
    coincidencias: int = sum(1 for p in palabras_consulta if p in contenido_lower)

    return coincidencias / len(palabras_consulta)


def _calcular_bonus_coleccion(
    metadata: dict[str, Any],
    coleccion_preferida: Optional[str] = None,
) -> float:
    """Calcula un bonus basado en la relevancia de la colección.

    Args:
        metadata: Metadatos del fragmento.
        coleccion_preferida: Colección preferida por el contexto actual.

    Returns:
        Score entre 0.0 y 1.0.
    """
    if coleccion_preferida is None:
        return 0.5

    coleccion_fragmento: str = metadata.get("coleccion", "general")

    if coleccion_fragmento == coleccion_preferida:
        return 1.0

    # Colecciones normativas siempre tienen bonus alto
    if coleccion_fragmento in {"normativa", "leyes", "decretos", "resoluciones"}:
        return 0.8

    return 0.3


def reordenar_resultados(
    resultados: list[ResultadoBusqueda],
    consulta: str,
    top_k: int = 5,
    coleccion_preferida: Optional[str] = None,
    score_minimo: float = 0.2,
) -> list[ResultadoBusqueda]:
    """Re-ordena los resultados de búsqueda por relevancia compuesta.

    Combina el score de similitud vectorial con factores adicionales:
    - Relevancia de palabras clave.
    - Pertenencia a colección preferida.
    - Metadatos de calidad.

    Args:
        resultados: Resultados de la búsqueda vectorial.
        consulta: Consulta original del usuario.
        top_k: Número máximo de resultados a retornar.
        coleccion_preferida: Colección con mayor prioridad.
        score_minimo: Score mínimo compuesto para incluir.

    Returns:
        Lista re-ordenada y filtrada de resultados.
    """
    if not resultados:
        return []

    resultados_scored: list[tuple[float, ResultadoBusqueda]] = []

    for resultado in resultados:
        # Score original de similitud vectorial (normalizado 0-1)
        score_vectorial: float = min(max(resultado.score, 0.0), 1.0)

        # Relevancia de keywords
        score_keywords: float = _calcular_relevancia_keywords(consulta, resultado.contenido)

        # Bonus por colección
        score_coleccion: float = _calcular_bonus_coleccion(
            resultado.metadata, coleccion_preferida
        )

        # Score compuesto
        score_compuesto: float = (
            PESO_SCORE_ORIGINAL * score_vectorial
            + PESO_RELEVANCIA_CONSULTA * score_keywords
            + PESO_COLECCION * score_coleccion
            + PESO_FRESCURA * 0.5  # TODO: implementar score de frescura basado en fecha
        )

        if score_compuesto >= score_minimo:
            resultado.score = score_compuesto
            resultados_scored.append((score_compuesto, resultado))

    # Ordenar por score compuesto descendente
    resultados_scored.sort(key=lambda x: x[0], reverse=True)

    resultados_finales: list[ResultadoBusqueda] = [r for _, r in resultados_scored[:top_k]]

    logger.info(
        "Re-ranking: %d → %d resultados (consulta: '%s...')",
        len(resultados),
        len(resultados_finales),
        consulta[:50],
    )

    return resultados_finales


# Stopwords básicas del español para no considerar en keyword matching
_STOPWORDS_ES: set[str] = {
    "que", "del", "los", "las", "una", "con", "para", "por", "como", "pero",
    "sus", "más", "este", "esta", "son", "entre", "cuando", "muy", "sin",
    "sobre", "ser", "también", "fue", "hay", "desde", "están", "ese", "eso",
    "esa", "estos", "estas", "unos", "unas", "nos", "les", "ella", "ellos",
    "ellas", "todo", "todos", "toda", "todas", "cada", "otro", "otra", "otros",
    "otras", "mismo", "misma", "antes", "después", "cual", "donde", "puede",
    "pueden", "tiene", "tienen", "debe", "deben", "así", "bien", "aquí",
}
