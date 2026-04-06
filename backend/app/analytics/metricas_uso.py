"""
CecilIA v2 — Metricas de uso del sistema
Contraloria General de la Republica de Colombia

Archivo: app/analytics/metricas_uso.py
Proposito: Consultas/dia/semana/mes, tokens consumidos, top 10 temas,
           distribucion por fase, comparativo DES vs DVF.
Sprint: 10
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import and_, case, cast, func, select, Date
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversacion import Conversacion
from app.models.mensaje import Mensaje
from app.models.usuario import Usuario

logger = logging.getLogger("cecilia.analytics.uso")


async def obtener_metricas_uso(
    db: AsyncSession,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    direccion: Optional[str] = None,
) -> dict[str, Any]:
    """Obtiene metricas completas de uso del sistema.

    Returns:
        Dict con todas las metricas de uso.
    """
    ahora = datetime.now(timezone.utc)
    inicio = fecha_inicio or (ahora - timedelta(days=30))
    fin = fecha_fin or ahora

    filtros_conv = [Conversacion.created_at >= inicio, Conversacion.created_at < fin]
    filtros_msg = [Mensaje.created_at >= inicio, Mensaje.created_at < fin]
    if direccion:
        filtros_conv.append(Conversacion.direccion == direccion)

    # Total consultas (mensajes de usuario)
    total_q = await db.execute(
        select(func.count(Mensaje.id)).where(and_(*filtros_msg, Mensaje.rol == "user"))
    )
    total_consultas = total_q.scalar() or 0

    # Total mensajes (ambos roles)
    total_all_q = await db.execute(
        select(func.count(Mensaje.id)).where(and_(*filtros_msg))
    )
    total_mensajes = total_all_q.scalar() or 0

    # Usuarios activos
    usuarios_q = await db.execute(
        select(func.count(func.distinct(Conversacion.usuario_id))).where(and_(*filtros_conv))
    )
    total_usuarios_activos = usuarios_q.scalar() or 0

    # Consultas por direccion
    dir_q = await db.execute(
        select(
            Conversacion.direccion,
            func.sum(Conversacion.total_mensajes),
        ).where(and_(*filtros_conv)).group_by(Conversacion.direccion)
    )
    consultas_por_direccion = {"DES": 0, "DVF": 0}
    for row in dir_q.all():
        if row[0] in consultas_por_direccion:
            consultas_por_direccion[row[0]] = row[1] or 0

    # Consultas por fase
    fase_q = await db.execute(
        select(
            Conversacion.fase,
            func.count(Conversacion.id),
        ).where(and_(*filtros_conv, Conversacion.fase.isnot(None))).group_by(Conversacion.fase)
    )
    consultas_por_fase = {
        "preplaneacion": 0, "planeacion": 0, "ejecucion": 0,
        "informe": 0, "seguimiento": 0,
    }
    for row in fase_q.all():
        if row[0] in consultas_por_fase:
            consultas_por_fase[row[0]] = row[1] or 0

    # Consultas hoy/semana/mes
    hoy = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    semana = hoy - timedelta(days=7)
    mes = hoy - timedelta(days=30)

    hoy_q = await db.execute(
        select(func.count(Mensaje.id)).where(
            and_(Mensaje.created_at >= hoy, Mensaje.rol == "user")
        )
    )
    consultas_hoy = hoy_q.scalar() or 0

    semana_q = await db.execute(
        select(func.count(Mensaje.id)).where(
            and_(Mensaje.created_at >= semana, Mensaje.rol == "user")
        )
    )
    consultas_semana = semana_q.scalar() or 0

    mes_q = await db.execute(
        select(func.count(Mensaje.id)).where(
            and_(Mensaje.created_at >= mes, Mensaje.rol == "user")
        )
    )
    consultas_mes = mes_q.scalar() or 0

    return {
        "total_consultas": total_consultas,
        "total_mensajes": total_mensajes,
        "total_usuarios_activos": total_usuarios_activos,
        "consultas_por_direccion": consultas_por_direccion,
        "consultas_por_fase": consultas_por_fase,
        "consultas_hoy": consultas_hoy,
        "consultas_semana": consultas_semana,
        "consultas_mes": consultas_mes,
        "periodo_inicio": inicio.isoformat(),
        "periodo_fin": fin.isoformat(),
    }


async def obtener_consultas_por_dia(
    db: AsyncSession,
    dias: int = 30,
) -> list[dict[str, Any]]:
    """Obtiene consultas por dia para grafico de linea."""
    ahora = datetime.now(timezone.utc)
    inicio = ahora - timedelta(days=dias)

    q = await db.execute(
        select(
            cast(Mensaje.created_at, Date).label("fecha"),
            func.count(Mensaje.id).label("total"),
        ).where(
            and_(Mensaje.created_at >= inicio, Mensaje.rol == "user")
        ).group_by(cast(Mensaje.created_at, Date)).order_by(cast(Mensaje.created_at, Date))
    )

    resultado = []
    for row in q.all():
        resultado.append({
            "fecha": row.fecha.isoformat() if row.fecha else "",
            "consultas": row.total,
        })

    return resultado


async def obtener_top_temas(
    db: AsyncSession,
    limite: int = 10,
    dias: int = 30,
) -> list[dict[str, Any]]:
    """Obtiene los top N temas mas consultados (basado en titulos de conversacion)."""
    ahora = datetime.now(timezone.utc)
    inicio = ahora - timedelta(days=dias)

    q = await db.execute(
        select(
            Conversacion.titulo,
            func.count(Conversacion.id).label("total"),
            func.sum(Conversacion.total_mensajes).label("mensajes"),
        ).where(
            and_(Conversacion.created_at >= inicio)
        ).group_by(Conversacion.titulo).order_by(func.count(Conversacion.id).desc()).limit(limite)
    )

    return [
        {"tema": row.titulo, "conversaciones": row.total, "mensajes": row.mensajes or 0}
        for row in q.all()
    ]


async def obtener_usuarios_activos(
    db: AsyncSession,
    limite: int = 20,
    dias: int = 30,
) -> list[dict[str, Any]]:
    """Obtiene los usuarios mas activos con sus metricas."""
    ahora = datetime.now(timezone.utc)
    inicio = ahora - timedelta(days=dias)

    q = await db.execute(
        select(
            Usuario.id,
            Usuario.nombre_completo,
            Usuario.rol,
            Usuario.direccion,
            func.count(func.distinct(Conversacion.id)).label("conversaciones"),
            func.sum(Conversacion.total_mensajes).label("mensajes"),
        ).join(Conversacion, Conversacion.usuario_id == Usuario.id).where(
            Conversacion.created_at >= inicio
        ).group_by(
            Usuario.id, Usuario.nombre_completo, Usuario.rol, Usuario.direccion
        ).order_by(func.sum(Conversacion.total_mensajes).desc()).limit(limite)
    )

    return [
        {
            "id": row.id,
            "nombre": row.nombre_completo,
            "rol": row.rol,
            "direccion": row.direccion,
            "conversaciones": row.conversaciones,
            "mensajes": row.mensajes or 0,
        }
        for row in q.all()
    ]


async def obtener_comparativo_des_dvf(
    db: AsyncSession,
    dias: int = 30,
) -> dict[str, Any]:
    """Comparativo de uso entre DES y DVF."""
    ahora = datetime.now(timezone.utc)
    inicio = ahora - timedelta(days=dias)

    resultado = {"DES": {}, "DVF": {}}
    for dir_val in ("DES", "DVF"):
        conv_q = await db.execute(
            select(func.count(Conversacion.id)).where(
                and_(Conversacion.created_at >= inicio, Conversacion.direccion == dir_val)
            )
        )
        usr_q = await db.execute(
            select(func.count(func.distinct(Conversacion.usuario_id))).where(
                and_(Conversacion.created_at >= inicio, Conversacion.direccion == dir_val)
            )
        )
        msgs_q = await db.execute(
            select(func.sum(Conversacion.total_mensajes)).where(
                and_(Conversacion.created_at >= inicio, Conversacion.direccion == dir_val)
            )
        )
        resultado[dir_val] = {
            "conversaciones": conv_q.scalar() or 0,
            "usuarios_activos": usr_q.scalar() or 0,
            "mensajes": msgs_q.scalar() or 0,
        }

    return resultado
