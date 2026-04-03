"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: retriever.py
Propósito: Búsqueda por similitud en pgvector con filtrado por colección
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from backend.app.rag.embeddings import generar_embedding_consulta

logger = logging.getLogger("cecilia.rag.retriever")


@dataclass
class ResultadoBusqueda:
    """Resultado individual de una búsqueda por similitud."""

    contenido: str
    metadata: dict[str, Any] = field(default_factory=dict)
    score: float = 0.0
    fragmento_id: Optional[str] = None

    @property
    def fuente(self) -> str:
        """Nombre del archivo fuente."""
        return self.metadata.get("nombre_archivo", "desconocido")


@dataclass
class ConfiguracionRetriever:
    """Configuración del retriever pgvector."""

    connection_string: str = "postgresql://cecilia:cecilia@localhost:5432/cecilia_v2"
    nombre_tabla: str = "embeddings_documentos"
    top_k: int = 5
    score_minimo: float = 0.3
    coleccion_default: str = "general"


async def buscar_similares(
    consulta: str,
    coleccion: Optional[str] = None,
    top_k: int = 5,
    filtros: Optional[dict[str, Any]] = None,
    config: Optional[ConfiguracionRetriever] = None,
) -> list[ResultadoBusqueda]:
    """Busca fragmentos similares a la consulta en pgvector.

    Realiza una búsqueda por similitud coseno en la base de datos vectorial,
    con filtrado opcional por colección y metadatos.

    Args:
        consulta: Texto de la consulta del usuario.
        coleccion: Nombre de la colección a buscar (None para todas).
        top_k: Número máximo de resultados a retornar.
        filtros: Filtros adicionales de metadatos.
        config: Configuración de conexión.

    Returns:
        Lista de resultados ordenados por similitud descendente.
    """
    if config is None:
        config = ConfiguracionRetriever()

    coleccion = coleccion or config.coleccion_default

    try:
        # Generar embedding de la consulta
        embedding_consulta: list[float] = generar_embedding_consulta(consulta)

        # Construir query SQL con pgvector
        condiciones: list[str] = []
        parametros: list[Any] = [embedding_consulta, top_k]

        if coleccion != "todas":
            condiciones.append("coleccion = %s")
            parametros.insert(-1, coleccion)

        if filtros:
            for clave, valor in filtros.items():
                condiciones.append(f"metadata->>'{clave}' = %s")
                parametros.insert(-1, str(valor))

        clausula_where: str = ""
        if condiciones:
            clausula_where = "WHERE " + " AND ".join(condiciones)

        query: str = f"""
            SELECT
                id,
                contenido,
                metadata,
                coleccion,
                1 - (embedding <=> %s::vector) AS score
            FROM {config.nombre_tabla}
            {clausula_where}
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """

        # Ejecutar búsqueda
        import asyncpg

        conexion = await asyncpg.connect(config.connection_string)
        try:
            # Ajustar parámetros para la query con doble referencia al embedding
            params_query: list[Any] = [
                str(embedding_consulta),
                *([coleccion] if coleccion != "todas" else []),
                *([str(v) for v in filtros.values()] if filtros else []),
                str(embedding_consulta),
                top_k,
            ]

            filas = await conexion.fetch(query, *params_query)

            resultados: list[ResultadoBusqueda] = []
            for fila in filas:
                score: float = float(fila["score"])
                if score >= config.score_minimo:
                    resultados.append(
                        ResultadoBusqueda(
                            contenido=fila["contenido"],
                            metadata=dict(fila["metadata"]) if fila["metadata"] else {},
                            score=score,
                            fragmento_id=str(fila["id"]),
                        )
                    )

            logger.info(
                "Búsqueda en '%s': %d resultados (top_k=%d, score_min=%.2f).",
                coleccion, len(resultados), top_k, config.score_minimo,
            )

            return resultados

        finally:
            await conexion.close()

    except ImportError:
        logger.error("asyncpg no disponible. Instale: pip install asyncpg")
        return _buscar_similares_sync_fallback(consulta, coleccion, top_k, config)

    except Exception:
        logger.exception("Error en búsqueda por similitud.")
        return []


def _buscar_similares_sync_fallback(
    consulta: str,
    coleccion: str,
    top_k: int,
    config: ConfiguracionRetriever,
) -> list[ResultadoBusqueda]:
    """Fallback síncrono usando psycopg2 cuando asyncpg no está disponible.

    Args:
        consulta: Texto de la consulta.
        coleccion: Colección a buscar.
        top_k: Número máximo de resultados.
        config: Configuración.

    Returns:
        Lista de resultados.
    """
    try:
        import psycopg2
        import json

        embedding_consulta: list[float] = generar_embedding_consulta(consulta)

        conexion = psycopg2.connect(config.connection_string)
        cursor = conexion.cursor()

        query: str = f"""
            SELECT
                id,
                contenido,
                metadata,
                1 - (embedding <=> %s::vector) AS score
            FROM {config.nombre_tabla}
            WHERE coleccion = %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """

        embedding_str: str = str(embedding_consulta)
        cursor.execute(query, (embedding_str, coleccion, embedding_str, top_k))
        filas = cursor.fetchall()

        resultados: list[ResultadoBusqueda] = []
        for fila in filas:
            score: float = float(fila[3])
            if score >= config.score_minimo:
                metadata_raw = fila[2]
                metadata: dict[str, Any] = (
                    json.loads(metadata_raw) if isinstance(metadata_raw, str) else dict(metadata_raw or {})
                )
                resultados.append(
                    ResultadoBusqueda(
                        contenido=fila[1],
                        metadata=metadata,
                        score=score,
                        fragmento_id=str(fila[0]),
                    )
                )

        cursor.close()
        conexion.close()

        return resultados

    except Exception:
        logger.exception("Error en fallback síncrono de búsqueda.")
        return []
