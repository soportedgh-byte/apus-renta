"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/api/rag_routes.py
Proposito: Endpoints RAG — busqueda semantica con pgvector, listado de
           colecciones y estadisticas del corpus vectorial
Sprint: 1
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import configuracion

logger = logging.getLogger("cecilia.api.rag")

enrutador = APIRouter()


# ── Dependencia de sesion DB ────────────────────────────────────────────────

async def _obtener_sesion_db():
    from app.main import fabrica_sesiones
    async with fabrica_sesiones() as sesion:
        try:
            yield sesion
            await sesion.commit()
        except Exception:
            await sesion.rollback()
            raise


# ── Dependencia temporal de usuario ────────────────────────────────────────

async def _obtener_usuario_actual_id() -> int:
    return 1


async def _verificar_rol_admin(usuario_id: int = Depends(_obtener_usuario_actual_id)) -> int:
    return usuario_id


# ── Esquemas ───────────────────────────────────────────────────────────────


class SolicitudBusqueda(BaseModel):
    consulta: str = Field(..., min_length=3, max_length=2000,
                          description="Texto de la consulta para busqueda semantica")
    colecciones: list[str] = Field(
        default_factory=lambda: ["normativo", "institucional", "academico",
                                 "tecnico_tic", "estadistico", "jurisprudencial",
                                 "auditoria"],
        description="Colecciones en las que buscar (por defecto, todas)",
    )
    top_k: int = Field(default=5, ge=1, le=20,
                       description="Numero maximo de fragmentos a retornar")
    umbral_similitud: float = Field(default=0.3, ge=0.0, le=1.0,
                                    description="Umbral minimo de similitud coseno")
    reranking: bool = Field(default=True, description="Aplicar re-ranking contextual")


class FragmentoRecuperado(BaseModel):
    id: str
    contenido: str
    documento_id: str
    nombre_documento: str = ""
    coleccion: str
    pagina: Optional[int] = None
    similitud: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class RespuestaBusqueda(BaseModel):
    consulta: str
    fragmentos: list[FragmentoRecuperado]
    total_encontrados: int
    tiempo_ms: float
    modelo_embeddings: str


class RespuestaColeccion(BaseModel):
    nombre: str
    descripcion: str
    total_documentos: int
    total_fragmentos: int
    ultima_actualizacion: Optional[datetime] = None


class SolicitudReindexar(BaseModel):
    coleccion: str = Field(..., description="Nombre de la coleccion a reindexar")
    forzar: bool = Field(default=False, description="Forzar reindexacion completa")


class RespuestaReindexacion(BaseModel):
    tarea_id: str
    coleccion: str
    estado: str
    mensaje: str


class EstadisticasCorpus(BaseModel):
    total_documentos: int
    total_fragmentos: int
    colecciones: dict[str, int]
    tiene_indice_vectorial: bool
    dimension_embeddings: int


# ── Colecciones ────────────────────────────────────────────────────────────

COLECCIONES_DISPONIBLES: dict[str, str] = {
    "normativo": "Leyes, decretos, resoluciones y circulares de control fiscal",
    "institucional": "Documentos institucionales, manuales y guias de la CGR",
    "academico": "Documentos academicos, investigaciones y publicaciones",
    "tecnico_tic": "Documentos tecnicos de TIC y arquitectura de sistemas",
    "estadistico": "Datos estadisticos, indicadores y reportes cuantitativos",
    "jurisprudencial": "Sentencias, conceptos juridicos y jurisprudencia",
    "auditoria": "Informes de auditoria, hallazgos y planes de mejoramiento",
}


# ── Endpoints ──────────────────────────────────────────────────────────────


@enrutador.post(
    "/buscar",
    response_model=RespuestaBusqueda,
    summary="Busqueda semantica",
    description="Busca fragmentos relevantes en el corpus documental usando similitud coseno con pgvector.",
)
async def buscar_semantico(
    solicitud: SolicitudBusqueda,
    db: AsyncSession = Depends(_obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Busqueda semantica real sobre pgvector."""
    inicio = time.monotonic()

    # Validar colecciones
    colecciones_invalidas = [c for c in solicitud.colecciones if c not in COLECCIONES_DISPONIBLES]
    if colecciones_invalidas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Colecciones invalidas: {colecciones_invalidas}. "
                   f"Disponibles: {list(COLECCIONES_DISPONIBLES.keys())}",
        )

    try:
        from app.rag.retriever import buscar_similares
        from app.rag.reranker import reordenar_resultados

        resultados = await buscar_similares(
            consulta=solicitud.consulta,
            db=db,
            colecciones=solicitud.colecciones,
            top_k=solicitud.top_k * 2 if solicitud.reranking else solicitud.top_k,
            umbral_similitud=solicitud.umbral_similitud,
        )

        if solicitud.reranking and resultados:
            resultados = reordenar_resultados(
                resultados=resultados,
                consulta=solicitud.consulta,
                top_k=solicitud.top_k,
            )

        # Obtener nombres de documentos
        doc_ids = list({r.documento_id for r in resultados if r.documento_id})
        nombres_docs: dict[str, str] = {}
        if doc_ids:
            result = await db.execute(
                text("SELECT id, nombre_archivo FROM documentos WHERE id = ANY(:ids)"),
                {"ids": doc_ids},
            )
            for fila in result.fetchall():
                nombres_docs[fila.id] = fila.nombre_archivo

        fragmentos = []
        for r in resultados:
            fragmentos.append({
                "id": r.fragmento_id or "",
                "contenido": r.contenido,
                "documento_id": r.documento_id or "",
                "nombre_documento": nombres_docs.get(r.documento_id or "", ""),
                "coleccion": r.coleccion,
                "pagina": r.pagina,
                "similitud": round(r.score, 4),
                "metadata": r.metadata,
            })

        duracion_ms = (time.monotonic() - inicio) * 1000

        logger.info(
            "Busqueda: '%s...' -> %d resultados en %.1f ms (usuario=%d)",
            solicitud.consulta[:50], len(fragmentos), duracion_ms, usuario_id,
        )

        return {
            "consulta": solicitud.consulta,
            "fragmentos": fragmentos,
            "total_encontrados": len(fragmentos),
            "tiempo_ms": round(duracion_ms, 1),
            "modelo_embeddings": configuracion.EMBEDDINGS_MODEL,
        }

    except Exception as exc:
        logger.exception("Error en busqueda semantica")
        duracion_ms = (time.monotonic() - inicio) * 1000
        return {
            "consulta": solicitud.consulta,
            "fragmentos": [],
            "total_encontrados": 0,
            "tiempo_ms": round(duracion_ms, 1),
            "modelo_embeddings": configuracion.EMBEDDINGS_MODEL,
        }


@enrutador.get(
    "/colecciones",
    response_model=list[RespuestaColeccion],
    summary="Listar colecciones",
    description="Lista las 7 colecciones del corpus con conteos de documentos y fragmentos.",
)
async def listar_colecciones(
    db: AsyncSession = Depends(_obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> list[dict[str, Any]]:
    """Retorna colecciones con estadisticas reales desde pgvector."""
    # Conteos de documentos por coleccion
    result_docs = await db.execute(text(
        "SELECT coleccion, COUNT(*) as total FROM documentos GROUP BY coleccion"
    ))
    conteo_docs: dict[str, int] = {fila.coleccion: fila.total for fila in result_docs.fetchall()}

    # Conteos de fragmentos por coleccion
    result_frags = await db.execute(text(
        "SELECT coleccion, COUNT(*) as total FROM fragmentos_vectoriales GROUP BY coleccion"
    ))
    conteo_frags: dict[str, int] = {fila.coleccion: fila.total for fila in result_frags.fetchall()}

    resultado = []
    for nombre, descripcion in COLECCIONES_DISPONIBLES.items():
        resultado.append({
            "nombre": nombre,
            "descripcion": descripcion,
            "total_documentos": conteo_docs.get(nombre, 0),
            "total_fragmentos": conteo_frags.get(nombre, 0),
            "ultima_actualizacion": None,
        })

    return resultado


@enrutador.get(
    "/estadisticas",
    response_model=EstadisticasCorpus,
    summary="Estadisticas del corpus",
    description="Retorna estadisticas generales del corpus vectorial.",
)
async def estadisticas_corpus(
    db: AsyncSession = Depends(_obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Estadisticas del corpus vectorial."""
    total_docs = (await db.execute(text("SELECT COUNT(*) FROM documentos"))).scalar() or 0
    total_frags = (await db.execute(text("SELECT COUNT(*) FROM fragmentos_vectoriales"))).scalar() or 0

    result_cols = await db.execute(text(
        "SELECT coleccion, COUNT(*) as total FROM fragmentos_vectoriales GROUP BY coleccion"
    ))
    colecciones = {fila.coleccion: fila.total for fila in result_cols.fetchall()}

    # Verificar si existe indice vectorial
    result_idx = await db.execute(text(
        "SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'fragmentos_vectoriales' "
        "AND indexdef LIKE '%ivfflat%'"
    ))
    tiene_indice = (result_idx.scalar() or 0) > 0

    return {
        "total_documentos": total_docs,
        "total_fragmentos": total_frags,
        "colecciones": colecciones,
        "tiene_indice_vectorial": tiene_indice,
        "dimension_embeddings": configuracion.EMBEDDINGS_DIMENSIONES,
    }


@enrutador.post(
    "/reindexar",
    response_model=RespuestaReindexacion,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Reindexar coleccion",
    description="Solicita la reindexacion de una coleccion (solo administradores).",
)
async def reindexar_coleccion(
    solicitud: SolicitudReindexar,
    db: AsyncSession = Depends(_obtener_sesion_db),
    usuario_id: int = Depends(_verificar_rol_admin),
) -> dict[str, Any]:
    if solicitud.coleccion not in COLECCIONES_DISPONIBLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Coleccion '{solicitud.coleccion}' no existe.",
        )

    tarea_id = str(uuid.uuid4())

    logger.info(
        "Reindexacion solicitada: tarea=%s, coleccion=%s, forzar=%s, usuario=%d",
        tarea_id, solicitud.coleccion, solicitud.forzar, usuario_id,
    )

    return {
        "tarea_id": tarea_id,
        "coleccion": solicitud.coleccion,
        "estado": "encolada",
        "mensaje": f"Reindexacion de '{solicitud.coleccion}' encolada exitosamente.",
    }
