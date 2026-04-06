"""
CecilIA v2 — Metricas de calidad de respuestas
Contraloria General de la Republica de Colombia

Archivo: app/analytics/metricas_calidad.py
Proposito: Precision de citaciones, feedback thumbs up/down,
           tasa de hallazgos aprobados, satisfaccion de usuario.
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

from app.models.mensaje import Mensaje
from app.models.hallazgo import Hallazgo

logger = logging.getLogger("cecilia.analytics.calidad")


async def obtener_metricas_calidad(
    db: AsyncSession,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    direccion: Optional[str] = None,
) -> dict[str, Any]:
    """Obtiene metricas de calidad del sistema."""
    ahora = datetime.now(timezone.utc)
    inicio = fecha_inicio or (ahora - timedelta(days=30))
    fin = fecha_fin or ahora

    filtros = [Mensaje.created_at >= inicio, Mensaje.created_at < fin]

    # Feedback positivo
    pos_q = await db.execute(
        select(func.count(Mensaje.id)).where(
            and_(*filtros, Mensaje.feedback_puntuacion == 1)
        )
    )
    feedback_positivo = pos_q.scalar() or 0

    # Feedback negativo
    neg_q = await db.execute(
        select(func.count(Mensaje.id)).where(
            and_(*filtros, Mensaje.feedback_puntuacion == -1)
        )
    )
    feedback_negativo = neg_q.scalar() or 0

    # Feedback neutral
    neu_q = await db.execute(
        select(func.count(Mensaje.id)).where(
            and_(*filtros, Mensaje.feedback_puntuacion == 0)
        )
    )
    feedback_neutral = neu_q.scalar() or 0

    total_con_feedback = feedback_positivo + feedback_negativo + feedback_neutral
    tasa_satisfaccion = round(
        (feedback_positivo / max(total_con_feedback, 1)) * 100, 1
    )

    # Respuestas con fuentes (citaciones)
    total_asistente_q = await db.execute(
        select(func.count(Mensaje.id)).where(
            and_(*filtros, Mensaje.rol == "assistant")
        )
    )
    total_respuestas = total_asistente_q.scalar() or 0

    con_fuentes_q = await db.execute(
        select(func.count(Mensaje.id)).where(
            and_(*filtros, Mensaje.rol == "assistant", Mensaje.fuentes.isnot(None))
        )
    )
    con_fuentes = con_fuentes_q.scalar() or 0

    cobertura_fuentes = round(
        (con_fuentes / max(total_respuestas, 1)) * 100, 1
    )

    # Hallazgos: tasa de aprobacion
    filtros_hall = [Hallazgo.created_at >= inicio, Hallazgo.created_at < fin]
    total_hall_q = await db.execute(
        select(func.count(Hallazgo.id)).where(and_(*filtros_hall))
    )
    total_hallazgos = total_hall_q.scalar() or 0

    aprobados_q = await db.execute(
        select(func.count(Hallazgo.id)).where(
            and_(*filtros_hall, Hallazgo.estado == "APROBADO")
        )
    )
    aprobados = aprobados_q.scalar() or 0

    tasa_aprobacion = round(
        (aprobados / max(total_hallazgos, 1)) * 100, 1
    )

    # Comentarios de feedback negativos recientes
    comentarios_q = await db.execute(
        select(
            Mensaje.id,
            Mensaje.feedback_comentario,
            Mensaje.feedback_puntuacion,
            Mensaje.created_at,
        ).where(
            and_(
                *filtros,
                Mensaje.feedback_puntuacion == -1,
                Mensaje.feedback_comentario.isnot(None),
            )
        ).order_by(Mensaje.created_at.desc()).limit(20)
    )
    comentarios_negativos = [
        {
            "mensaje_id": row.id,
            "comentario": row.feedback_comentario,
            "fecha": row.created_at.isoformat() if row.created_at else "",
        }
        for row in comentarios_q.all()
    ]

    return {
        "feedback_positivo": feedback_positivo,
        "feedback_negativo": feedback_negativo,
        "feedback_neutral": feedback_neutral,
        "total_con_feedback": total_con_feedback,
        "tasa_satisfaccion": tasa_satisfaccion,
        "total_respuestas": total_respuestas,
        "respuestas_con_fuentes": con_fuentes,
        "cobertura_fuentes": cobertura_fuentes,
        "precision_citaciones_estimada": cobertura_fuentes,  # Proxy
        "total_hallazgos": total_hallazgos,
        "hallazgos_aprobados": aprobados,
        "tasa_hallazgos_aprobados": tasa_aprobacion,
        "comentarios_negativos_recientes": comentarios_negativos,
        "periodo_inicio": inicio.isoformat(),
        "periodo_fin": fin.isoformat(),
    }
