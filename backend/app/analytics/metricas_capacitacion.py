"""
CecilIA v2 — Metricas de capacitacion
Contraloria General de la Republica de Colombia

Archivo: app/analytics/metricas_capacitacion.py
Proposito: Funcionarios capacitados, rutas completadas, quizzes aprobados.
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

from app.models.capacitacion import (
    RutaAprendizaje,
    Leccion,
    ProgresoUsuario,
    QuizResultado,
)

logger = logging.getLogger("cecilia.analytics.capacitacion")


async def obtener_metricas_capacitacion(
    db: AsyncSession,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
) -> dict[str, Any]:
    """Obtiene metricas del modulo de capacitacion."""
    ahora = datetime.now(timezone.utc)
    inicio = fecha_inicio or (ahora - timedelta(days=90))
    fin = fecha_fin or ahora

    # Total funcionarios capacitados (usuarios unicos con progreso)
    capacitados_q = await db.execute(
        select(func.count(func.distinct(ProgresoUsuario.usuario_id))).where(
            and_(ProgresoUsuario.created_at >= inicio, ProgresoUsuario.created_at < fin)
        )
    )
    total_capacitados = capacitados_q.scalar() or 0

    # Lecciones completadas
    completadas_q = await db.execute(
        select(func.count(ProgresoUsuario.id)).where(
            and_(
                ProgresoUsuario.created_at >= inicio,
                ProgresoUsuario.created_at < fin,
                ProgresoUsuario.completada == True,
            )
        )
    )
    lecciones_completadas = completadas_q.scalar() or 0

    # Total quizzes realizados y aprobados
    quizzes_q = await db.execute(
        select(func.count(QuizResultado.id)).where(
            and_(QuizResultado.created_at >= inicio, QuizResultado.created_at < fin)
        )
    )
    total_quizzes = quizzes_q.scalar() or 0

    aprobados_q = await db.execute(
        select(func.count(QuizResultado.id)).where(
            and_(
                QuizResultado.created_at >= inicio,
                QuizResultado.created_at < fin,
                QuizResultado.aprobado == True,
            )
        )
    )
    quizzes_aprobados = aprobados_q.scalar() or 0

    # Promedio puntaje quizzes
    puntaje_q = await db.execute(
        select(func.avg(QuizResultado.puntaje)).where(
            and_(QuizResultado.created_at >= inicio, QuizResultado.created_at < fin)
        )
    )
    promedio_puntaje = round(float(puntaje_q.scalar() or 0), 1)

    tasa_aprobacion = round(
        (quizzes_aprobados / max(total_quizzes, 1)) * 100, 1
    )

    # Rutas activas
    rutas_q = await db.execute(
        select(func.count(RutaAprendizaje.id)).where(RutaAprendizaje.activa == True)
    )
    rutas_activas = rutas_q.scalar() or 0

    # Detalle por ruta
    por_ruta = []
    rutas_detalle_q = await db.execute(
        select(
            RutaAprendizaje.id,
            RutaAprendizaje.nombre,
            RutaAprendizaje.total_lecciones,
        ).where(RutaAprendizaje.activa == True)
    )
    for ruta in rutas_detalle_q.all():
        # Aprendices en esta ruta
        aprendices_q = await db.execute(
            select(func.count(func.distinct(ProgresoUsuario.usuario_id))).where(
                and_(
                    ProgresoUsuario.ruta_id == ruta.id,
                    ProgresoUsuario.created_at >= inicio,
                )
            )
        )
        n_aprendices = aprendices_q.scalar() or 0

        # Promedio avance
        completadas_ruta_q = await db.execute(
            select(func.count(ProgresoUsuario.id)).where(
                and_(
                    ProgresoUsuario.ruta_id == ruta.id,
                    ProgresoUsuario.completada == True,
                )
            )
        )
        completadas_ruta = completadas_ruta_q.scalar() or 0
        total_posible = max(n_aprendices * (ruta.total_lecciones or 1), 1)
        promedio_avance = round((completadas_ruta / total_posible) * 100, 1)

        # Quiz promedio
        quiz_ruta_q = await db.execute(
            select(func.avg(QuizResultado.puntaje)).where(QuizResultado.ruta_id == ruta.id)
        )
        quiz_prom = round(float(quiz_ruta_q.scalar() or 0), 1)

        por_ruta.append({
            "ruta_id": ruta.id,
            "ruta_nombre": ruta.nombre,
            "aprendices": n_aprendices,
            "promedio_avance": promedio_avance,
            "promedio_quiz": quiz_prom,
        })

    return {
        "total_funcionarios_capacitados": total_capacitados,
        "lecciones_completadas": lecciones_completadas,
        "total_quizzes": total_quizzes,
        "quizzes_aprobados": quizzes_aprobados,
        "tasa_aprobacion_quizzes": tasa_aprobacion,
        "promedio_puntaje": promedio_puntaje,
        "rutas_activas": rutas_activas,
        "por_ruta": por_ruta,
        "periodo_inicio": inicio.isoformat(),
        "periodo_fin": fin.isoformat(),
    }
