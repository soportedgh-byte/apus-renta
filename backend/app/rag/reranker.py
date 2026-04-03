"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: reranker.py
Proposito: Re-ranking de resultados de busqueda por relevancia contextual
Sprint: 1
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional

from app.rag.retriever import ResultadoBusqueda

logger = logging.getLogger("cecilia.rag.reranker")

# Pesos para factores de re-ranking
PESO_SCORE_ORIGINAL: float = 0.4
PESO_RELEVANCIA_CONSULTA: float = 0.3
PESO_FRESCURA: float = 0.1
PESO_COLECCION: float = 0.2


def _calcular_relevancia_keywords(consulta: str, contenido: str) -> float:
    """Calcula un score de relevancia basado en presencia de palabras clave."""
    palabras_consulta = {
        p.lower()
        for p in re.findall(r"\b\w{3,}\b", consulta)
        if p.lower() not in _STOPWORDS_ES
    }

    if not palabras_consulta:
        return 0.0

    contenido_lower = contenido.lower()
    coincidencias = sum(1 for p in palabras_consulta if p in contenido_lower)
    return coincidencias / len(palabras_consulta)


def _calcular_bonus_coleccion(
    coleccion: str,
    coleccion_preferida: Optional[str] = None,
) -> float:
    """Calcula un bonus basado en la relevancia de la coleccion."""
    if coleccion_preferida and coleccion == coleccion_preferida:
        return 1.0

    # Colecciones normativas siempre tienen bonus alto
    if coleccion in {"normativo", "jurisprudencial"}:
        return 0.8

    if coleccion in {"institucional", "auditoria"}:
        return 0.6

    if coleccion_preferida is None:
        return 0.5

    return 0.3


def reordenar_resultados(
    resultados: list[ResultadoBusqueda],
    consulta: str,
    top_k: int = 5,
    coleccion_preferida: Optional[str] = None,
    score_minimo: float = 0.2,
) -> list[ResultadoBusqueda]:
    """Re-ordena los resultados de busqueda por relevancia compuesta.

    Combina el score de similitud vectorial con:
    - Relevancia de palabras clave
    - Pertenencia a coleccion preferida
    - Bonus para colecciones normativas/juridicas

    Args:
        resultados: Resultados de la busqueda vectorial.
        consulta: Consulta original del usuario.
        top_k: Numero maximo de resultados.
        coleccion_preferida: Coleccion con mayor prioridad.
        score_minimo: Score minimo compuesto para incluir.

    Returns:
        Lista re-ordenada y filtrada de resultados.
    """
    if not resultados:
        return []

    resultados_scored: list[tuple[float, ResultadoBusqueda]] = []

    for resultado in resultados:
        score_vectorial = min(max(resultado.score, 0.0), 1.0)
        score_keywords = _calcular_relevancia_keywords(consulta, resultado.contenido)
        score_coleccion = _calcular_bonus_coleccion(resultado.coleccion, coleccion_preferida)

        score_compuesto = (
            PESO_SCORE_ORIGINAL * score_vectorial
            + PESO_RELEVANCIA_CONSULTA * score_keywords
            + PESO_COLECCION * score_coleccion
            + PESO_FRESCURA * 0.5
        )

        if score_compuesto >= score_minimo:
            resultado.score = score_compuesto
            resultados_scored.append((score_compuesto, resultado))

    resultados_scored.sort(key=lambda x: x[0], reverse=True)
    resultados_finales = [r for _, r in resultados_scored[:top_k]]

    logger.info(
        "Re-ranking: %d -> %d resultados (consulta: '%s...')",
        len(resultados), len(resultados_finales), consulta[:50],
    )

    return resultados_finales


_STOPWORDS_ES: set[str] = {
    "que", "del", "los", "las", "una", "con", "para", "por", "como", "pero",
    "sus", "mas", "este", "esta", "son", "entre", "cuando", "muy", "sin",
    "sobre", "ser", "tambien", "fue", "hay", "desde", "estan", "ese", "eso",
    "esa", "estos", "estas", "unos", "unas", "nos", "les", "ella", "ellos",
    "ellas", "todo", "todos", "toda", "todas", "cada", "otro", "otra", "otros",
    "otras", "mismo", "misma", "antes", "despues", "cual", "donde", "puede",
    "pueden", "tiene", "tienen", "debe", "deben", "asi", "bien", "aqui",
}
