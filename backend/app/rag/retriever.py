"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: retriever.py
Proposito: Busqueda por similitud coseno en pgvector sobre tabla fragmentos_vectoriales
           con filtrado por coleccion y soporte async via SQLAlchemy
Sprint: 1
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.embeddings import generar_embedding_consulta

logger = logging.getLogger("cecilia.rag.retriever")

TABLA_FRAGMENTOS = "fragmentos_vectoriales"


@dataclass
class ResultadoBusqueda:
    """Resultado individual de una busqueda por similitud."""

    contenido: str
    metadata: dict[str, Any] = field(default_factory=dict)
    score: float = 0.0
    fragmento_id: str | None = None
    documento_id: str | None = None
    coleccion: str = ""
    pagina: int | None = None

    @property
    def fuente(self) -> str:
        return self.metadata.get("nombre_archivo", "desconocido")


async def buscar_similares(
    consulta: str,
    db: AsyncSession,
    colecciones: list[str] | None = None,
    top_k: int = 5,
    umbral_similitud: float = 0.3,
    filtros: dict[str, Any] | None = None,
) -> list[ResultadoBusqueda]:
    """Busca fragmentos similares a la consulta en pgvector.

    Realiza busqueda por similitud coseno en la tabla fragmentos_vectoriales,
    con filtrado por colecciones y metadatos.

    Args:
        consulta: Texto de la consulta del usuario.
        db: Sesion asincrona de SQLAlchemy.
        colecciones: Lista de colecciones a buscar (None para todas).
        top_k: Numero maximo de resultados.
        umbral_similitud: Score minimo de similitud (0-1).
        filtros: Filtros adicionales de metadatos.

    Returns:
        Lista de resultados ordenados por similitud descendente.
    """
    inicio = time.monotonic()

    try:
        # Generar embedding de la consulta
        embedding_consulta = generar_embedding_consulta(consulta)
        embedding_str = "[" + ",".join(str(v) for v in embedding_consulta) + "]"

        # Construir query con filtros
        condiciones: list[str] = []
        parametros: dict[str, Any] = {
            "embedding": embedding_str,
            "top_k": top_k,
            "umbral": 1.0 - umbral_similitud,  # cosine distance threshold
        }

        if colecciones:
            condiciones.append("fv.coleccion = ANY(:colecciones)")
            parametros["colecciones"] = colecciones

        if filtros:
            for i, (clave, valor) in enumerate(filtros.items()):
                param_name = f"filtro_{i}"
                condiciones.append(f"fv.metadata_extra->>'{clave}' = :{param_name}")
                parametros[param_name] = str(valor)

        clausula_where = ""
        if condiciones:
            clausula_where = "WHERE " + " AND ".join(condiciones)

        query = text(f"""
            SELECT
                fv.id,
                fv.documento_id,
                fv.contenido,
                fv.coleccion,
                fv.pagina,
                fv.posicion_fragmento,
                fv.metadata_extra,
                1 - (fv.embedding <=> CAST(:embedding AS vector)) AS similitud
            FROM {TABLA_FRAGMENTOS} fv
            {clausula_where}
            ORDER BY fv.embedding <=> CAST(:embedding AS vector)
            LIMIT :top_k
        """)

        resultado = await db.execute(query, parametros)
        filas = resultado.fetchall()

        resultados: list[ResultadoBusqueda] = []
        for fila in filas:
            score = float(fila.similitud)
            if score >= umbral_similitud:
                metadata = dict(fila.metadata_extra) if fila.metadata_extra else {}
                resultados.append(
                    ResultadoBusqueda(
                        contenido=fila.contenido,
                        metadata=metadata,
                        score=score,
                        fragmento_id=str(fila.id),
                        documento_id=str(fila.documento_id),
                        coleccion=fila.coleccion,
                        pagina=fila.pagina,
                    )
                )

        duracion_ms = (time.monotonic() - inicio) * 1000
        logger.info(
            "Busqueda semantica: %d resultados en %.1f ms (consulta='%s...', colecciones=%s)",
            len(resultados), duracion_ms, consulta[:50], colecciones,
        )

        return resultados

    except Exception:
        logger.exception("Error en busqueda por similitud.")
        return []
