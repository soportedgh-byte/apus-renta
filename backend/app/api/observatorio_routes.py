"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/api/observatorio_routes.py
Proposito: Endpoints REST para el Observatorio TIC — alertas inteligentes,
           ejecucion de crawlers y estadisticas.
Sprint: 8
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from pydantic import BaseModel, Field
from sqlalchemy import case, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_handler import verificar_token
from app.main import obtener_sesion_db
from app.models.alerta_observatorio import AlertaObservatorio

logger = logging.getLogger("cecilia.api.observatorio")

enrutador = APIRouter()
esquema_bearer = HTTPBearer(auto_error=True)


# ── Dependencia de autenticacion ─────────────────────────────────────────────

async def _obtener_usuario_id(
    credenciales: HTTPAuthorizationCredentials = Depends(esquema_bearer),
) -> int:
    """Extrae el usuario_id del token JWT."""
    try:
        payload = verificar_token(credenciales.credentials)
        return int(payload.get("sub", 0))
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalido o expirado.")


# ── Schemas ──────────────────────────────────────────────────────────────────

class AsignarAlertaRequest(BaseModel):
    alerta_id: str
    usuario_id: Optional[int] = None


class CambiarEstadoRequest(BaseModel):
    estado: str = Field(..., pattern="^(NUEVA|VISTA|EN_ANALISIS|ARCHIVADA)$")


# ── GET /alertas — Listar alertas ────────────────────────────────────────────

@enrutador.get("/alertas")
async def listar_alertas(
    tipo: Optional[str] = Query(None, description="REGULATORIA|LEGISLATIVA|NOTICIA|INDICADOR"),
    relevancia: Optional[str] = Query(None, description="ALTA|MEDIA|BAJA"),
    estado: Optional[str] = Query(None, description="NUEVA|VISTA|EN_ANALISIS|ARCHIVADA"),
    fuente: Optional[str] = Query(None, description="MinTIC|CRC|ANE|Congreso|Noticias"),
    entidad: Optional[str] = Query(None, description="Filtrar por entidad afectada"),
    limite: int = Query(default=50, ge=1, le=200),
    desplazamiento: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_id),
) -> list[dict[str, Any]]:
    """Lista alertas del Observatorio TIC con filtros."""
    query = select(AlertaObservatorio)

    if tipo:
        query = query.where(AlertaObservatorio.tipo == tipo)
    if relevancia:
        query = query.where(AlertaObservatorio.relevancia == relevancia)
    if estado:
        query = query.where(AlertaObservatorio.estado == estado)
    if fuente:
        query = query.where(AlertaObservatorio.fuente_nombre.ilike(f"%{fuente}%"))
    if entidad:
        # JSONB contains check
        query = query.where(
            AlertaObservatorio.entidades_afectadas.cast(str).ilike(f"%{entidad}%")
        )

    query = query.order_by(
        # Nuevas primero, luego por relevancia, luego por fecha
        case(
            (AlertaObservatorio.estado == "NUEVA", 0),
            (AlertaObservatorio.estado == "EN_ANALISIS", 1),
            (AlertaObservatorio.estado == "VISTA", 2),
            else_=3,
        ),
        case(
            (AlertaObservatorio.relevancia == "ALTA", 0),
            (AlertaObservatorio.relevancia == "MEDIA", 1),
            else_=2,
        ),
        AlertaObservatorio.fecha_deteccion.desc(),
    ).offset(desplazamiento).limit(limite)

    resultado = await db.execute(query)
    alertas = resultado.scalars().all()
    return [a.a_dict() for a in alertas]


# ── GET /alertas/contadores — Resumen de contadores ──────────────────────────

@enrutador.get("/alertas/contadores")
async def obtener_contadores(
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_id),
) -> dict[str, Any]:
    """Contadores agregados de alertas para el dashboard."""

    # Total por estado
    resultado_estado = await db.execute(
        select(
            AlertaObservatorio.estado,
            func.count(AlertaObservatorio.id),
        ).group_by(AlertaObservatorio.estado)
    )
    por_estado = {row[0]: row[1] for row in resultado_estado.all()}

    # Total por tipo
    resultado_tipo = await db.execute(
        select(
            AlertaObservatorio.tipo,
            func.count(AlertaObservatorio.id),
        ).group_by(AlertaObservatorio.tipo)
    )
    por_tipo = {row[0]: row[1] for row in resultado_tipo.all()}

    # Total por relevancia
    resultado_relevancia = await db.execute(
        select(
            AlertaObservatorio.relevancia,
            func.count(AlertaObservatorio.id),
        ).group_by(AlertaObservatorio.relevancia)
    )
    por_relevancia = {row[0]: row[1] for row in resultado_relevancia.all()}

    # Total por fuente
    resultado_fuente = await db.execute(
        select(
            AlertaObservatorio.fuente_nombre,
            func.count(AlertaObservatorio.id),
        ).group_by(AlertaObservatorio.fuente_nombre)
    )
    por_fuente = {row[0]: row[1] for row in resultado_fuente.all()}

    total = sum(por_estado.values())

    return {
        "total": total,
        "por_estado": por_estado,
        "por_tipo": por_tipo,
        "por_relevancia": por_relevancia,
        "por_fuente": por_fuente,
        "nuevas": por_estado.get("NUEVA", 0),
        "en_analisis": por_estado.get("EN_ANALISIS", 0),
    }


# ── GET /alertas/{alerta_id} — Detalle de alerta ────────────────────────────

@enrutador.get("/alertas/{alerta_id}")
async def obtener_alerta(
    alerta_id: str,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_id),
) -> dict[str, Any]:
    """Obtiene el detalle de una alerta."""
    resultado = await db.execute(
        select(AlertaObservatorio).where(AlertaObservatorio.id == alerta_id)
    )
    alerta = resultado.scalar_one_or_none()
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada.")
    return alerta.a_dict()


# ── PUT /alertas/{alerta_id}/estado — Cambiar estado ────────────────────────

@enrutador.put("/alertas/{alerta_id}/estado")
async def cambiar_estado_alerta(
    alerta_id: str,
    datos: CambiarEstadoRequest,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_id),
) -> dict[str, Any]:
    """Cambia el estado de una alerta (NUEVA -> VISTA -> EN_ANALISIS -> ARCHIVADA)."""
    resultado = await db.execute(
        select(AlertaObservatorio).where(AlertaObservatorio.id == alerta_id)
    )
    alerta = resultado.scalar_one_or_none()
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada.")

    alerta.estado = datos.estado
    if datos.estado == "EN_ANALISIS" and not alerta.asignada_a:
        alerta.asignada_a = usuario_id

    await db.commit()
    await db.refresh(alerta)
    return alerta.a_dict()


# ── PUT /alertas/{alerta_id}/asignar — Asignar alerta ───────────────────────

@enrutador.put("/alertas/{alerta_id}/asignar")
async def asignar_alerta(
    alerta_id: str,
    datos: AsignarAlertaRequest,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_id),
) -> dict[str, Any]:
    """Asigna una alerta a un usuario para analisis."""
    resultado = await db.execute(
        select(AlertaObservatorio).where(AlertaObservatorio.id == alerta_id)
    )
    alerta = resultado.scalar_one_or_none()
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada.")

    alerta.asignada_a = datos.usuario_id or usuario_id
    alerta.estado = "EN_ANALISIS"
    await db.commit()
    await db.refresh(alerta)
    return alerta.a_dict()


# ── POST /crawl — Ejecutar crawl manual ──────────────────────────────────────

@enrutador.post("/crawl")
async def ejecutar_crawl_manual(
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_id),
) -> dict[str, Any]:
    """Ejecuta un ciclo de crawl manual (solo admin/director)."""
    from app.observatorio.scheduler import ejecutar_crawl

    logger.info("Crawl manual iniciado por usuario %d", usuario_id)
    resumen = await ejecutar_crawl(db)
    return resumen


# ── GET /estadisticas — Estadisticas del observatorio ────────────────────────

@enrutador.get("/estadisticas")
async def obtener_estadisticas(
    dias: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_id),
) -> dict[str, Any]:
    """Estadisticas del Observatorio TIC para graficos y tendencias."""
    from datetime import timedelta

    fecha_inicio = datetime.now(timezone.utc) - timedelta(days=dias)

    # Alertas por dia (timeline)
    resultado_timeline = await db.execute(
        select(
            func.date(AlertaObservatorio.fecha_deteccion).label("fecha"),
            func.count(AlertaObservatorio.id).label("total"),
        )
        .where(AlertaObservatorio.fecha_deteccion >= fecha_inicio)
        .group_by(func.date(AlertaObservatorio.fecha_deteccion))
        .order_by(func.date(AlertaObservatorio.fecha_deteccion))
    )
    timeline = [{"fecha": str(row[0]), "total": row[1]} for row in resultado_timeline.all()]

    # Top entidades afectadas
    resultado_entidades = await db.execute(
        select(AlertaObservatorio.entidades_afectadas)
        .where(AlertaObservatorio.fecha_deteccion >= fecha_inicio)
        .where(AlertaObservatorio.entidades_afectadas.isnot(None))
    )
    conteo_entidades: dict[str, int] = {}
    for (entidades,) in resultado_entidades.all():
        if isinstance(entidades, list):
            for e in entidades:
                conteo_entidades[e] = conteo_entidades.get(e, 0) + 1

    top_entidades = sorted(conteo_entidades.items(), key=lambda x: x[1], reverse=True)[:10]

    # Fuentes activas
    resultado_fuentes = await db.execute(
        select(
            AlertaObservatorio.fuente_nombre,
            func.count(AlertaObservatorio.id),
            func.max(AlertaObservatorio.fecha_deteccion),
        )
        .where(AlertaObservatorio.fecha_deteccion >= fecha_inicio)
        .group_by(AlertaObservatorio.fuente_nombre)
    )
    fuentes = [
        {
            "nombre": row[0],
            "alertas": row[1],
            "ultima_deteccion": row[2].isoformat() if row[2] else None,
        }
        for row in resultado_fuentes.all()
    ]

    return {
        "periodo_dias": dias,
        "timeline": timeline,
        "top_entidades": [{"nombre": e, "alertas": c} for e, c in top_entidades],
        "fuentes": fuentes,
    }
