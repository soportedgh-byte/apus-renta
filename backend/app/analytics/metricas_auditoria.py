"""
CecilIA v2 — Metricas de auditoria
Contraloria General de la Republica de Colombia

Archivo: app/analytics/metricas_auditoria.py
Proposito: Auditorias por estado, hallazgos por connotacion, tiempo por fase,
           formatos generados.
Sprint: 10
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auditoria import Auditoria
from app.models.hallazgo import Hallazgo
from app.models.formato_generado import FormatoGenerado

logger = logging.getLogger("cecilia.analytics.auditoria")


async def obtener_metricas_auditoria(
    db: AsyncSession,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    direccion: Optional[str] = None,
) -> dict[str, Any]:
    """Obtiene metricas de auditorias, hallazgos y formatos."""
    ahora = datetime.now(timezone.utc)
    inicio = fecha_inicio or (ahora - timedelta(days=365))
    fin = fecha_fin or ahora

    filtros_aud = [Auditoria.created_at >= inicio, Auditoria.created_at < fin]
    filtros_hall = [Hallazgo.created_at >= inicio, Hallazgo.created_at < fin]
    filtros_fmt = [FormatoGenerado.created_at >= inicio, FormatoGenerado.created_at < fin]
    if direccion:
        filtros_aud.append(Auditoria.direccion == direccion)

    # Auditorias por estado/fase
    fases_q = await db.execute(
        select(
            Auditoria.fase_actual,
            func.count(Auditoria.id),
        ).where(and_(*filtros_aud)).group_by(Auditoria.fase_actual)
    )
    auditorias_por_fase = {}
    total_auditorias = 0
    for row in fases_q.all():
        auditorias_por_fase[row[0]] = row[1]
        total_auditorias += row[1]

    # Auditorias por tipo
    tipos_q = await db.execute(
        select(
            Auditoria.tipo_auditoria,
            func.count(Auditoria.id),
        ).where(and_(*filtros_aud)).group_by(Auditoria.tipo_auditoria)
    )
    auditorias_por_tipo = {row[0]: row[1] for row in tipos_q.all()}

    # Total hallazgos
    total_hall_q = await db.execute(
        select(func.count(Hallazgo.id)).where(and_(*filtros_hall))
    )
    total_hallazgos = total_hall_q.scalar() or 0

    # Hallazgos por estado
    estados_h_q = await db.execute(
        select(
            Hallazgo.estado,
            func.count(Hallazgo.id),
        ).where(and_(*filtros_hall)).group_by(Hallazgo.estado)
    )
    hallazgos_por_estado = {row[0]: row[1] for row in estados_h_q.all()}

    # Hallazgos por connotacion (extraer de JSONB)
    hallazgos_por_connotacion = {
        "administrativo": 0, "fiscal": 0, "disciplinario": 0, "penal": 0,
    }
    # Consulta simplificada: contar hallazgos que tienen connotaciones
    connotacion_q = await db.execute(
        select(Hallazgo.connotaciones).where(
            and_(*filtros_hall, Hallazgo.connotaciones.isnot(None))
        )
    )
    for row in connotacion_q.all():
        if row[0]:
            for c in row[0]:
                tipo = c.get("tipo", "").lower()
                if tipo in hallazgos_por_connotacion:
                    hallazgos_por_connotacion[tipo] += 1

    # Hallazgos generados con IA
    ia_q = await db.execute(
        select(func.count(Hallazgo.id)).where(
            and_(*filtros_hall, Hallazgo.generado_por_ia == True)
        )
    )
    hallazgos_ia = ia_q.scalar() or 0

    # Hallazgos validados (Circular 023)
    validados_q = await db.execute(
        select(func.count(Hallazgo.id)).where(
            and_(*filtros_hall, Hallazgo.redaccion_validada_humano == True)
        )
    )
    hallazgos_validados = validados_q.scalar() or 0

    # Cuantia total presunto dano
    cuantia_q = await db.execute(
        select(func.sum(Hallazgo.cuantia_presunto_dano)).where(
            and_(*filtros_hall, Hallazgo.cuantia_presunto_dano.isnot(None))
        )
    )
    cuantia_total = float(cuantia_q.scalar() or 0)

    # Formatos generados
    total_fmt_q = await db.execute(
        select(func.count(FormatoGenerado.id)).where(and_(*filtros_fmt))
    )
    total_formatos = total_fmt_q.scalar() or 0

    fmt_ia_q = await db.execute(
        select(func.count(FormatoGenerado.id)).where(
            and_(*filtros_fmt, FormatoGenerado.generado_con_ia == True)
        )
    )
    formatos_ia = fmt_ia_q.scalar() or 0

    return {
        "total_auditorias": total_auditorias,
        "auditorias_por_fase": auditorias_por_fase,
        "auditorias_por_tipo": auditorias_por_tipo,
        "total_hallazgos": total_hallazgos,
        "hallazgos_por_estado": hallazgos_por_estado,
        "hallazgos_por_connotacion": hallazgos_por_connotacion,
        "hallazgos_generados_ia": hallazgos_ia,
        "hallazgos_validados_humano": hallazgos_validados,
        "tasa_hallazgos_aprobados": round(
            hallazgos_por_estado.get("APROBADO", 0) / max(total_hallazgos, 1) * 100, 1
        ),
        "cuantia_total_presunto_dano": cuantia_total,
        "total_formatos": total_formatos,
        "formatos_generados_ia": formatos_ia,
        "periodo_inicio": inicio.isoformat(),
        "periodo_fin": fin.isoformat(),
    }
