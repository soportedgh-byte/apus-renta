"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: embeddings.py
Propósito: Generación de embeddings vectoriales mediante API configurable
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("cecilia.rag.embeddings")


class ConfiguracionEmbeddings(BaseModel):
    """Configuración para el proveedor de embeddings."""

    proveedor: str = Field(default="openai", description="Proveedor: openai | azure | local")
    modelo: str = Field(default="text-embedding-3-small", description="Nombre del modelo")
    dimension: int = Field(default=1536, description="Dimensión del vector de salida")
    batch_size: int = Field(default=100, description="Tamaño de lote para procesamiento")
    api_key: Optional[str] = Field(default=None, description="API key (si no usa variable de entorno)")
    api_base: Optional[str] = Field(default=None, description="URL base de la API")
    api_version: Optional[str] = Field(default=None, description="Versión de la API (Azure)")


def _obtener_modelo_embeddings(config: ConfiguracionEmbeddings) -> Any:
    """Instancia el modelo de embeddings según la configuración.

    Args:
        config: Configuración del proveedor.

    Returns:
        Instancia del modelo de embeddings de LangChain.

    Raises:
        ValueError: Si el proveedor no está soportado.
    """
    if config.proveedor == "openai":
        from langchain_openai import OpenAIEmbeddings

        kwargs: dict[str, Any] = {"model": config.modelo}
        if config.api_key:
            kwargs["openai_api_key"] = config.api_key
        return OpenAIEmbeddings(**kwargs)

    elif config.proveedor == "azure":
        from langchain_openai import AzureOpenAIEmbeddings

        kwargs = {
            "model": config.modelo,
            "azure_deployment": config.modelo,
        }
        if config.api_key:
            kwargs["openai_api_key"] = config.api_key
        if config.api_base:
            kwargs["azure_endpoint"] = config.api_base
        if config.api_version:
            kwargs["openai_api_version"] = config.api_version
        return AzureOpenAIEmbeddings(**kwargs)

    elif config.proveedor == "local":
        from langchain_community.embeddings import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(
            model_name=config.modelo,
            model_kwargs={"device": "cpu"},
        )

    else:
        raise ValueError(f"Proveedor de embeddings no soportado: '{config.proveedor}'")


# Singleton del modelo de embeddings
_modelo_singleton: Any | None = None
_config_singleton: ConfiguracionEmbeddings | None = None


def inicializar_embeddings(config: ConfiguracionEmbeddings | None = None) -> Any:
    """Inicializa (o reinicializa) el modelo de embeddings.

    Args:
        config: Configuración del proveedor. Si es None, usa valores por defecto.

    Returns:
        Instancia del modelo de embeddings.
    """
    global _modelo_singleton, _config_singleton

    if config is None:
        config = ConfiguracionEmbeddings()

    _modelo_singleton = _obtener_modelo_embeddings(config)
    _config_singleton = config

    logger.info(
        "Modelo de embeddings inicializado: proveedor=%s, modelo=%s, dim=%d",
        config.proveedor, config.modelo, config.dimension,
    )

    return _modelo_singleton


def obtener_modelo_embeddings() -> Any:
    """Obtiene el modelo de embeddings singleton.

    Returns:
        Instancia del modelo de embeddings.
    """
    if _modelo_singleton is None:
        return inicializar_embeddings()
    return _modelo_singleton


def generar_embeddings(
    textos: list[str],
    config: ConfiguracionEmbeddings | None = None,
) -> list[list[float]]:
    """Genera embeddings para una lista de textos.

    Args:
        textos: Lista de textos a vectorizar.
        config: Configuración opcional (usa singleton si no se proporciona).

    Returns:
        Lista de vectores de embeddings.
    """
    if not textos:
        logger.warning("Lista vacía proporcionada para generar embeddings.")
        return []

    if config is not None:
        modelo = _obtener_modelo_embeddings(config)
    else:
        modelo = obtener_modelo_embeddings()

    batch_size: int = (config or _config_singleton or ConfiguracionEmbeddings()).batch_size
    todos_embeddings: list[list[float]] = []

    for i in range(0, len(textos), batch_size):
        lote: list[str] = textos[i : i + batch_size]
        try:
            embeddings_lote: list[list[float]] = modelo.embed_documents(lote)
            todos_embeddings.extend(embeddings_lote)
            logger.debug(
                "Embeddings generados para lote %d-%d de %d textos.",
                i, min(i + batch_size, len(textos)), len(textos),
            )
        except Exception:
            logger.exception("Error al generar embeddings para lote %d.", i)
            raise

    logger.info(
        "Generados %d embeddings (dim=%d).",
        len(todos_embeddings),
        len(todos_embeddings[0]) if todos_embeddings else 0,
    )

    return todos_embeddings


def generar_embedding_consulta(
    consulta: str,
    config: ConfiguracionEmbeddings | None = None,
) -> list[float]:
    """Genera el embedding para una consulta de búsqueda.

    Args:
        consulta: Texto de la consulta.
        config: Configuración opcional.

    Returns:
        Vector de embedding de la consulta.
    """
    if config is not None:
        modelo = _obtener_modelo_embeddings(config)
    else:
        modelo = obtener_modelo_embeddings()

    return modelo.embed_query(consulta)
