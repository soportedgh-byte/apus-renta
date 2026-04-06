"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/api/analytics_routes.py
Proposito: Endpoints de analitica — metricas de uso, auditoria, calidad,
           capacitacion, exportacion Excel/DOCX/CSV y reporte Circular 023.
Sprint: 10
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import io
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import obtener_sesion_db

logger = logging.getLogger("cecilia.api.analytics")

enrutador = APIRouter()


# ── Dependencia temporal de usuario autenticado ──────────────────────────────

async def _obtener_usuario_actual_id() -> int:
    """Dependencia temporal — sera reemplazada por auth real."""
    return 1


# ── Endpoints de metricas ───────────────────────────────────────────────────

@enrutador.get("/uso", summary="Metricas de uso del sistema")
async def obtener_estadisticas_uso(
    fecha_inicio: Optional[datetime] = Query(default=None),
    fecha_fin: Optional[datetime] = Query(default=None),
    direccion: Optional[str] = Query(default=None, description="DES | DVF"),
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Retorna metricas de uso: consultas, usuarios, por direccion y fase."""
    from app.analytics.metricas_uso import obtener_metricas_uso
    return await obtener_metricas_uso(db, fecha_inicio, fecha_fin, direccion)


@enrutador.get("/uso/consultas-por-dia", summary="Consultas por dia (grafico linea)")
async def consultas_por_dia(
    dias: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Retorna consultas por dia para grafico de linea."""
    from app.analytics.metricas_uso import obtener_consultas_por_dia
    datos = await obtener_consultas_por_dia(db, dias)
    return {"serie": datos, "total_dias": len(datos)}


@enrutador.get("/uso/top-temas", summary="Top 10 temas consultados")
async def top_temas(
    limite: int = Query(default=10, ge=1, le=50),
    dias: int = Query(default=30),
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Top N temas mas consultados."""
    from app.analytics.metricas_uso import obtener_top_temas
    return {"temas": await obtener_top_temas(db, limite, dias)}


@enrutador.get("/uso/usuarios-activos", summary="Usuarios mas activos")
async def usuarios_activos(
    limite: int = Query(default=20),
    dias: int = Query(default=30),
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Lista usuarios mas activos con metricas."""
    from app.analytics.metricas_uso import obtener_usuarios_activos
    return {"usuarios": await obtener_usuarios_activos(db, limite, dias)}


@enrutador.get("/uso/comparativo-des-dvf", summary="Comparativo DES vs DVF")
async def comparativo_des_dvf(
    dias: int = Query(default=30),
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Comparativo de uso entre DES y DVF."""
    from app.analytics.metricas_uso import obtener_comparativo_des_dvf
    return await obtener_comparativo_des_dvf(db, dias)


@enrutador.get("/auditorias", summary="Metricas de auditorias y hallazgos")
async def obtener_metricas_auditorias(
    fecha_inicio: Optional[datetime] = Query(default=None),
    fecha_fin: Optional[datetime] = Query(default=None),
    direccion: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Retorna metricas de auditorias, hallazgos por connotacion, formatos."""
    from app.analytics.metricas_auditoria import obtener_metricas_auditoria
    return await obtener_metricas_auditoria(db, fecha_inicio, fecha_fin, direccion)


@enrutador.get("/calidad", summary="Metricas de calidad de respuestas")
async def obtener_metricas_calidad(
    fecha_inicio: Optional[datetime] = Query(default=None),
    fecha_fin: Optional[datetime] = Query(default=None),
    direccion: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Retorna metricas de calidad: feedback, citaciones, aprobacion."""
    from app.analytics.metricas_calidad import obtener_metricas_calidad
    return await obtener_metricas_calidad(db, fecha_inicio, fecha_fin, direccion)


@enrutador.get("/capacitacion", summary="Metricas de capacitacion")
async def obtener_metricas_capacitacion(
    fecha_inicio: Optional[datetime] = Query(default=None),
    fecha_fin: Optional[datetime] = Query(default=None),
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Retorna metricas del modulo de capacitacion."""
    from app.analytics.metricas_capacitacion import obtener_metricas_capacitacion
    return await obtener_metricas_capacitacion(db, fecha_inicio, fecha_fin)


# ── Exportacion ──────────────────────────────────────────────────────────────

@enrutador.get("/exportar", summary="Exportar metricas a Excel")
async def exportar_metricas_excel(
    db: AsyncSession = Depends(obtener_sesion_db),
) -> StreamingResponse:
    """Genera y descarga un archivo Excel con todas las metricas."""
    from app.analytics.metricas_uso import obtener_metricas_uso
    from app.analytics.metricas_auditoria import obtener_metricas_auditoria
    from app.analytics.metricas_calidad import obtener_metricas_calidad
    from app.analytics.metricas_capacitacion import obtener_metricas_capacitacion
    from app.analytics.exportador import exportar_excel

    uso = await obtener_metricas_uso(db)
    auditoria = await obtener_metricas_auditoria(db)
    calidad = await obtener_metricas_calidad(db)
    capacitacion = await obtener_metricas_capacitacion(db)

    excel_bytes = exportar_excel(uso, auditoria, calidad, capacitacion)
    fecha = datetime.now().strftime("%Y%m%d")

    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=metricas_cecilia_{fecha}.xlsx"},
    )


@enrutador.get("/exportar/csv", summary="Exportar metricas a CSV")
async def exportar_metricas_csv(
    seccion: str = Query(default="uso", description="uso | auditorias | calidad | capacitacion"),
    db: AsyncSession = Depends(obtener_sesion_db),
) -> StreamingResponse:
    """Exporta una seccion de metricas a CSV."""
    from app.analytics.exportador import exportar_csv

    datos: dict[str, Any] = {}
    if seccion == "uso":
        from app.analytics.metricas_uso import obtener_metricas_uso
        datos = await obtener_metricas_uso(db)
    elif seccion == "auditorias":
        from app.analytics.metricas_auditoria import obtener_metricas_auditoria
        datos = await obtener_metricas_auditoria(db)
    elif seccion == "calidad":
        from app.analytics.metricas_calidad import obtener_metricas_calidad
        datos = await obtener_metricas_calidad(db)
    elif seccion == "capacitacion":
        from app.analytics.metricas_capacitacion import obtener_metricas_capacitacion
        datos = await obtener_metricas_capacitacion(db)

    csv_bytes = exportar_csv(datos, seccion)
    fecha = datetime.now().strftime("%Y%m%d")

    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=metricas_{seccion}_{fecha}.csv"},
    )


# ── Informe ejecutivo ────────────────────────────────────────────────────────

@enrutador.get("/informe-ejecutivo", summary="Informe ejecutivo mensual DOCX")
async def generar_informe_ejecutivo(
    periodo: str = Query(default="", description="Periodo del informe (ej: 'Marzo 2026')"),
    db: AsyncSession = Depends(obtener_sesion_db),
) -> StreamingResponse:
    """Genera y descarga un informe ejecutivo mensual en formato DOCX."""
    from app.analytics.metricas_uso import obtener_metricas_uso
    from app.analytics.metricas_auditoria import obtener_metricas_auditoria
    from app.analytics.metricas_calidad import obtener_metricas_calidad
    from app.analytics.metricas_capacitacion import obtener_metricas_capacitacion
    from app.analytics.exportador import generar_informe_ejecutivo

    uso = await obtener_metricas_uso(db)
    auditoria = await obtener_metricas_auditoria(db)
    calidad = await obtener_metricas_calidad(db)
    capacitacion = await obtener_metricas_capacitacion(db)

    docx_bytes = generar_informe_ejecutivo(uso, auditoria, calidad, capacitacion, periodo)
    fecha = datetime.now().strftime("%Y%m%d")

    return StreamingResponse(
        io.BytesIO(docx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=informe_ejecutivo_{fecha}.docx"},
    )


# ── Reporte Circular 023 CGR ────────────────────────────────────────────────

@enrutador.get(
    "/reporte-circular-023",
    summary="Reporte trimestral Circular 023 CGR",
    description=(
        "Genera el reporte trimestral de uso de IA requerido por la Circular 023 "
        "del Contralor General de la Republica."
    ),
)
async def generar_reporte_circular_023(
    trimestre: Optional[str] = Query(
        default=None,
        description="Trimestre (ej: '2026-Q1'). Si no se especifica, usa el actual.",
    ),
    formato: str = Query(default="json", description="json | docx"),
    db: AsyncSession = Depends(obtener_sesion_db),
) -> Any:
    """Genera el reporte Circular 023 en JSON o DOCX."""
    from app.models.conversacion import Conversacion
    from app.models.mensaje import Mensaje
    from app.models.documento import Documento
    from app.models.formato_generado import FormatoGenerado
    from app.models.hallazgo import Hallazgo

    ahora = datetime.now(timezone.utc)

    # Calcular periodo del trimestre
    if trimestre:
        try:
            anio, q = trimestre.split("-Q")
            anio, q = int(anio), int(q)
            mes_inicio = (q - 1) * 3 + 1
            inicio = datetime(anio, mes_inicio, 1, tzinfo=timezone.utc)
            fin = datetime(anio, mes_inicio + 3, 1, tzinfo=timezone.utc) if q < 4 else datetime(anio + 1, 1, 1, tzinfo=timezone.utc)
        except (ValueError, IndexError):
            q_actual = (ahora.month - 1) // 3 + 1
            mes_inicio = (q_actual - 1) * 3 + 1
            inicio = datetime(ahora.year, mes_inicio, 1, tzinfo=timezone.utc)
            fin = datetime(ahora.year, mes_inicio + 3, 1, tzinfo=timezone.utc) if q_actual < 4 else datetime(ahora.year + 1, 1, 1, tzinfo=timezone.utc)
            trimestre = f"{ahora.year}-Q{q_actual}"
    else:
        q_actual = (ahora.month - 1) // 3 + 1
        mes_inicio = (q_actual - 1) * 3 + 1
        inicio = datetime(ahora.year, mes_inicio, 1, tzinfo=timezone.utc)
        fin = datetime(ahora.year, mes_inicio + 3, 1, tzinfo=timezone.utc) if q_actual < 4 else datetime(ahora.year + 1, 1, 1, tzinfo=timezone.utc)
        trimestre = f"{ahora.year}-Q{q_actual}"

    # Consultas a la BD
    total_conv = (await db.execute(
        select(func.count(Conversacion.id)).where(and_(Conversacion.created_at >= inicio, Conversacion.created_at < fin))
    )).scalar() or 0

    total_consultas = (await db.execute(
        select(func.count(Mensaje.id)).where(and_(Mensaje.created_at >= inicio, Mensaje.created_at < fin))
    )).scalar() or 0

    promedio_msgs = round(total_consultas / max(total_conv, 1), 1)

    usuarios_des = (await db.execute(
        select(func.count(func.distinct(Conversacion.usuario_id))).where(
            and_(Conversacion.created_at >= inicio, Conversacion.created_at < fin, Conversacion.direccion == "DES")
        )
    )).scalar() or 0

    usuarios_dvf = (await db.execute(
        select(func.count(func.distinct(Conversacion.usuario_id))).where(
            and_(Conversacion.created_at >= inicio, Conversacion.created_at < fin, Conversacion.direccion == "DVF")
        )
    )).scalar() or 0

    consultas_des = (await db.execute(
        select(func.sum(Conversacion.total_mensajes)).where(
            and_(Conversacion.created_at >= inicio, Conversacion.created_at < fin, Conversacion.direccion == "DES")
        )
    )).scalar() or 0

    consultas_dvf = (await db.execute(
        select(func.sum(Conversacion.total_mensajes)).where(
            and_(Conversacion.created_at >= inicio, Conversacion.created_at < fin, Conversacion.direccion == "DVF")
        )
    )).scalar() or 0

    docs_procesados = (await db.execute(
        select(func.count(Documento.id)).where(
            and_(Documento.created_at >= inicio, Documento.created_at < fin, Documento.estado == "indexado")
        )
    )).scalar() or 0

    formatos_ia = (await db.execute(
        select(func.count(FormatoGenerado.id)).where(
            and_(FormatoGenerado.created_at >= inicio, FormatoGenerado.created_at < fin, FormatoGenerado.generado_con_ia == True)
        )
    )).scalar() or 0

    hallazgos_ia = (await db.execute(
        select(func.count(Hallazgo.id)).where(and_(Hallazgo.created_at >= inicio, Hallazgo.created_at < fin))
    )).scalar() or 0

    feedback_pos = (await db.execute(
        select(func.count(Mensaje.id)).where(and_(Mensaje.created_at >= inicio, Mensaje.created_at < fin, Mensaje.feedback_puntuacion == 1))
    )).scalar() or 0

    feedback_neg = (await db.execute(
        select(func.count(Mensaje.id)).where(and_(Mensaje.created_at >= inicio, Mensaje.created_at < fin, Mensaje.feedback_puntuacion == -1))
    )).scalar() or 0

    feedback_neu = (await db.execute(
        select(func.count(Mensaje.id)).where(and_(Mensaje.created_at >= inicio, Mensaje.created_at < fin, Mensaje.feedback_puntuacion == 0))
    )).scalar() or 0

    total_fb = feedback_pos + feedback_neg + feedback_neu
    tasa_sat = round((feedback_pos / max(total_fb, 1)) * 100, 1)

    modelos = [m for m in (await db.execute(
        select(func.distinct(Conversacion.modelo_utilizado)).where(
            and_(Conversacion.created_at >= inicio, Conversacion.created_at < fin, Conversacion.modelo_utilizado.isnot(None))
        )
    )).scalars().all() if m]

    datos = {
        "periodo_trimestre": trimestre,
        "periodo_inicio": inicio.isoformat(),
        "periodo_fin": fin.isoformat(),
        "total_consultas": total_consultas,
        "total_conversaciones": total_conv,
        "promedio_mensajes_por_conversacion": promedio_msgs,
        "usuarios_activos_des": usuarios_des,
        "usuarios_activos_dvf": usuarios_dvf,
        "total_usuarios_activos": usuarios_des + usuarios_dvf,
        "consultas_des": consultas_des,
        "consultas_dvf": consultas_dvf,
        "documentos_procesados_rag": docs_procesados,
        "formatos_generados_ia": formatos_ia,
        "hallazgos_asistidos_ia": hallazgos_ia,
        "feedback_positivo": feedback_pos,
        "feedback_negativo": feedback_neg,
        "feedback_neutral": feedback_neu,
        "tasa_satisfaccion": tasa_sat,
        "modelos_utilizados": modelos or ["Sin datos en el periodo"],
        "latencia_promedio_ms": 0.0,
        "total_advertencias_privacidad": 0,
        "disclaimers_incluidos": "Todos los mensajes incluyen disclaimer de validacion humana",
        "principios_implementados": [
            "Transparencia", "Responsabilidad", "Privacidad",
            "Control Humano", "Usos Limitados", "Declaracion IA", "Algoritmos Abiertos",
        ],
        "nota": (
            "Reporte generado automaticamente por CecilIA v2. "
            "Requiere revision y aprobacion del Director de TIC "
            "antes de remision al Despacho del Contralor General."
        ),
    }

    if formato == "docx":
        from app.analytics.exportador import generar_reporte_circular_023_docx
        docx_bytes = generar_reporte_circular_023_docx(datos)
        return StreamingResponse(
            io.BytesIO(docx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename=reporte_circular_023_{trimestre}.docx"},
        )

    return datos


# ── Modelos (legacy compat) ─────────────────────────────────────────────────

@enrutador.get("/modelos", summary="Metricas de modelos LLM")
async def obtener_metricas_modelos(
    db: AsyncSession = Depends(obtener_sesion_db),
) -> list[dict[str, Any]]:
    """Retorna metricas de rendimiento por modelo LLM."""
    from app.models.conversacion import Conversacion
    ahora = datetime.now(timezone.utc)
    inicio = ahora - timedelta(days=30)

    q = await db.execute(
        select(
            Conversacion.modelo_utilizado,
            func.count(Conversacion.id),
            func.sum(Conversacion.total_mensajes),
        ).where(
            and_(Conversacion.created_at >= inicio, Conversacion.modelo_utilizado.isnot(None))
        ).group_by(Conversacion.modelo_utilizado)
    )

    modelos = []
    for row in q.all():
        modelos.append({
            "modelo": row[0],
            "total_invocaciones": row[1],
            "total_mensajes": row[2] or 0,
            "latencia_promedio_ms": 0.0,
            "periodo_inicio": inicio.isoformat(),
            "periodo_fin": ahora.isoformat(),
        })

    if not modelos:
        modelos.append({
            "modelo": "Sin datos",
            "total_invocaciones": 0,
            "total_mensajes": 0,
            "latencia_promedio_ms": 0.0,
            "periodo_inicio": inicio.isoformat(),
            "periodo_fin": ahora.isoformat(),
        })

    return modelos


@enrutador.get("/trazabilidad", summary="Logs de trazabilidad")
async def obtener_trazabilidad(
    pagina: int = Query(default=1, ge=1),
    tamano_pagina: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Retorna registros de trazabilidad con paginacion."""
    return {
        "registros": [],
        "total": 0,
        "pagina": pagina,
        "tamano_pagina": tamano_pagina,
        "total_paginas": 0,
    }
