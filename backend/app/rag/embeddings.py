"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: embeddings.py
Proposito: Generacion de embeddings vectoriales mediante API compatible con OpenAI
           (soporta OpenAI, Ollama, vLLM, LiteLLM y cualquier API OpenAI-compatible)
Sprint: 1
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger("cecilia.rag.embeddings")


def _obtener_config() -> dict[str, Any]:
    """Lee la configuracion de embeddings desde variables de entorno."""
    return {
        "base_url": os.environ.get("EMBEDDINGS_BASE_URL", "http://localhost:11434/v1"),
        "api_key": os.environ.get("EMBEDDINGS_API_KEY", "ollama"),
        "model": os.environ.get("EMBEDDINGS_MODEL", "nomic-embed-text"),
        "dimensiones": int(os.environ.get("EMBEDDINGS_DIMENSIONES", "768")),
    }


def _crear_cliente():
    """Crea un cliente OpenAI apuntando al proveedor configurado."""
    from openai import OpenAI

    config = _obtener_config()
    return OpenAI(
        base_url=config["base_url"],
        api_key=config["api_key"],
    )


def generar_embeddings(
    textos: list[str],
    modelo: str | None = None,
    batch_size: int = 64,
) -> list[list[float]]:
    """Genera embeddings para una lista de textos.

    Usa la API compatible con OpenAI, por lo que funciona con:
    - OpenAI directamente (text-embedding-3-small, text-embedding-3-large)
    - Ollama (nomic-embed-text, mxbai-embed-large, etc.)
    - vLLM, LiteLLM, y otros servidores compatibles

    Args:
        textos: Lista de textos a vectorizar.
        modelo: Modelo de embeddings (override). Si es None, usa EMBEDDINGS_MODEL.
        batch_size: Tamano de lote para procesamiento.

    Returns:
        Lista de vectores de embeddings.
    """
    if not textos:
        return []

    config = _obtener_config()
    modelo = modelo or config["model"]
    cliente = _crear_cliente()

    todos_embeddings: list[list[float]] = []

    for i in range(0, len(textos), batch_size):
        lote = textos[i: i + batch_size]
        # Limpiar textos vacios (la API los rechaza)
        lote_limpio = [t if t.strip() else " " for t in lote]

        try:
            respuesta = cliente.embeddings.create(
                input=lote_limpio,
                model=modelo,
            )
            embeddings_lote = [item.embedding for item in respuesta.data]
            todos_embeddings.extend(embeddings_lote)

            logger.debug(
                "Embeddings generados: lote %d-%d de %d (dim=%d)",
                i, min(i + batch_size, len(textos)), len(textos),
                len(embeddings_lote[0]) if embeddings_lote else 0,
            )
        except Exception:
            logger.exception("Error al generar embeddings para lote %d.", i)
            raise

    logger.info(
        "Generados %d embeddings (modelo=%s, dim=%d).",
        len(todos_embeddings),
        modelo,
        len(todos_embeddings[0]) if todos_embeddings else 0,
    )

    return todos_embeddings


def generar_embedding_consulta(
    consulta: str,
    modelo: str | None = None,
) -> list[float]:
    """Genera el embedding para una consulta de busqueda.

    Args:
        consulta: Texto de la consulta.
        modelo: Modelo de embeddings (override).

    Returns:
        Vector de embedding de la consulta.
    """
    resultados = generar_embeddings([consulta], modelo=modelo, batch_size=1)
    return resultados[0]


def obtener_dimension() -> int:
    """Retorna la dimension configurada para los embeddings."""
    return _obtener_config()["dimensiones"]
