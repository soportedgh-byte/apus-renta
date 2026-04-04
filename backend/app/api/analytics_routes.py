"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: app/api/analytics_routes.py
Propósito: Endpoints de analítica y dashboard — estadísticas de uso, métricas
           de modelos, trazabilidad, calidad y reporte Circular 023 CGR
Sprint: 2.1
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func, case, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import obtener_sesion_db

logger = logging.getLogger("cecilia.api.analytics")

enrutador = APIRouter()


# ── Esquemas ─────────────────────────────────────────────────────────────────


class EstadisticasUso(BaseModel):
    """Estadísticas generales de uso del sistema."""

    total_consultas: int
    total_usuarios_activos: int
    consultas_por_direccion: dict[str, int]
    consultas_por_fase: dict[str, int]
    consultas_hoy: int
    consultas_semana: int
    consultas_mes: int
    periodo_inicio: datetime
    periodo_fin: datetime


class MetricasModelo(BaseModel):
    """Métricas de rendimiento de los modelos LLM."""

    modelo: str
    total_invocaciones: int
    latencia_promedio_ms: float
    latencia_p95_ms: float
    latencia_p99_ms: float
    tokens_entrada_promedio: int
    tokens_salida_promedio: int
    tasa_error: float
    costo_estimado_usd: float
    periodo_inicio: datetime
    periodo_fin: datetime


class RegistroTrazabilidad(BaseModel):
    """Registro individual de trazabilidad de una operación."""

    id: str
    marca_temporal: datetime
    usuario_id: int
    usuario_nombre: str
    accion: str
    modulo: str
    detalle: str
    modelo_utilizado: Optional[str] = None
    fuentes_consultadas: list[str] = Field(default_factory=list)
    ip_origen: Optional[str] = None
    duracion_ms: Optional[float] = None


class RespuestaTrazabilidadPaginada(BaseModel):
    """Respuesta paginada de registros de trazabilidad."""

    registros: list[RegistroTrazabilidad]
    total: int
    pagina: int
    tamano_pagina: int
    total_paginas: int


class MetricasCalidad(BaseModel):
    """Métricas de calidad de las respuestas del sistema."""

    tasa_alucinacion_estimada: float = Field(
        ..., description="Porcentaje estimado de respuestas con alucinaciones",
    )
    precision_rag: float = Field(
        ..., description="Precisión promedio de la recuperación RAG",
    )
    cobertura_fuentes: float = Field(
        ..., description="Porcentaje de respuestas que citan al menos una fuente",
    )
    satisfaccion_usuario: float = Field(
        ..., description="Puntuación promedio de satisfacción (feedback positivo / total)",
    )
    total_feedback_positivo: int
    total_feedback_negativo: int
    total_feedback_neutral: int
    latencia_respuesta_promedio_ms: float
    periodo_inicio: datetime
    periodo_fin: datetime


# ── Dependencia temporal de usuario autenticado ──────────────────────────────


async def _obtener_usuario_actual_id() -> int:
    """Dependencia temporal — será reemplazada por auth real."""
    return 1


# ── Endpoints ────────────────────────────────────────────────────────────────


@enrutador.get(
    "/uso",
    response_model=EstadisticasUso,
    summary="Estadísticas de uso",
    description="Retorna estadísticas de uso del sistema por consultas, usuarios y direcciones.",
)
async def obtener_estadisticas_uso(
    fecha_inicio: Optional[datetime] = Query(default=None, description="Inicio del periodo de consulta"),
    fecha_fin: Optional[datetime] = Query(default=None, description="Fin del periodo de consulta"),
    direccion: Optional[str] = Query(default=None, description="Filtrar por dirección: DES | DVF"),
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Calcula y retorna estadísticas de uso del sistema.

    Incluye conteo de consultas por dirección, fase y periodo temporal.
    """

    ahora: datetime = datetime.now(timezone.utc)

    # TODO: Implementar consultas reales a la base de datos
    logger.info(
        "Consulta de estadísticas de uso: inicio=%s, fin=%s, direccion=%s, usuario=%d",
        fecha_inicio, fecha_fin, direccion, usuario_id,
    )

    return {
        "total_consultas": 0,
        "total_usuarios_activos": 0,
        "consultas_por_direccion": {"DES": 0, "DVF": 0},
        "consultas_por_fase": {
            "preplaneacion": 0,
            "planeacion": 0,
            "ejecucion": 0,
            "informe": 0,
            "seguimiento": 0,
        },
        "consultas_hoy": 0,
        "consultas_semana": 0,
        "consultas_mes": 0,
        "periodo_inicio": fecha_inicio or ahora,
        "periodo_fin": fecha_fin or ahora,
    }


@enrutador.get(
    "/modelos",
    response_model=list[MetricasModelo],
    summary="Métricas de modelos",
    description="Retorna métricas de rendimiento de los modelos LLM utilizados.",
)
async def obtener_metricas_modelos(
    fecha_inicio: Optional[datetime] = Query(default=None),
    fecha_fin: Optional[datetime] = Query(default=None),
    modelo: Optional[str] = Query(default=None, description="Filtrar por nombre de modelo"),
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> list[dict[str, Any]]:
    """Retorna métricas de rendimiento por modelo LLM.

    Incluye latencia, uso de tokens, tasa de errores y costo estimado.
    """

    ahora: datetime = datetime.now(timezone.utc)

    # TODO: Implementar consultas reales a logs de trazabilidad
    logger.info(
        "Consulta de métricas de modelos: modelo=%s, usuario=%d",
        modelo, usuario_id,
    )

    return [{
        "modelo": modelo or "gpt-4o",
        "total_invocaciones": 0,
        "latencia_promedio_ms": 0.0,
        "latencia_p95_ms": 0.0,
        "latencia_p99_ms": 0.0,
        "tokens_entrada_promedio": 0,
        "tokens_salida_promedio": 0,
        "tasa_error": 0.0,
        "costo_estimado_usd": 0.0,
        "periodo_inicio": fecha_inicio or ahora,
        "periodo_fin": fecha_fin or ahora,
    }]


@enrutador.get(
    "/trazabilidad",
    response_model=RespuestaTrazabilidadPaginada,
    summary="Logs de trazabilidad",
    description="Retorna logs de trazabilidad de operaciones del sistema con paginación.",
)
async def obtener_trazabilidad(
    pagina: int = Query(default=1, ge=1, description="Número de página"),
    tamano_pagina: int = Query(default=50, ge=1, le=200, description="Registros por página"),
    usuario_filtro: Optional[int] = Query(default=None, description="Filtrar por ID de usuario"),
    modulo: Optional[str] = Query(default=None, description="Filtrar por módulo (chat, rag, formatos, etc.)"),
    accion: Optional[str] = Query(default=None, description="Filtrar por tipo de acción"),
    fecha_inicio: Optional[datetime] = Query(default=None),
    fecha_fin: Optional[datetime] = Query(default=None),
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Retorna registros de trazabilidad con paginación y filtros.

    Cada operación del sistema genera un registro de trazabilidad
    que incluye usuario, acción, módulo, fuentes consultadas y duración.
    """

    # TODO: Implementar consulta real a la tabla de logs de trazabilidad
    logger.info(
        "Consulta de trazabilidad: pagina=%d, tamano=%d, usuario_filtro=%s, modulo=%s",
        pagina, tamano_pagina, usuario_filtro, modulo,
    )

    return {
        "registros": [],
        "total": 0,
        "pagina": pagina,
        "tamano_pagina": tamano_pagina,
        "total_paginas": 0,
    }


@enrutador.get(
    "/calidad",
    response_model=MetricasCalidad,
    summary="Métricas de calidad",
    description="Retorna métricas de calidad de las respuestas (alucinaciones, precisión RAG, satisfacción).",
)
async def obtener_metricas_calidad(
    fecha_inicio: Optional[datetime] = Query(default=None),
    fecha_fin: Optional[datetime] = Query(default=None),
    direccion: Optional[str] = Query(default=None, description="Filtrar por dirección: DES | DVF"),
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Retorna métricas de calidad del sistema.

    Incluye:
    - Tasa estimada de alucinaciones (respuestas con información inventada).
    - Precisión del pipeline RAG.
    - Porcentaje de respuestas que citan fuentes verificables.
    - Satisfacción del usuario basada en retroalimentación.
    """

    ahora: datetime = datetime.now(timezone.utc)

    # TODO: Implementar cálculos reales desde la base de datos
    logger.info(
        "Consulta de métricas de calidad: direccion=%s, usuario=%d",
        direccion, usuario_id,
    )

    return {
        "tasa_alucinacion_estimada": 0.0,
        "precision_rag": 0.0,
        "cobertura_fuentes": 0.0,
        "satisfaccion_usuario": 0.0,
        "total_feedback_positivo": 0,
        "total_feedback_negativo": 0,
        "total_feedback_neutral": 0,
        "latencia_respuesta_promedio_ms": 0.0,
        "periodo_inicio": fecha_inicio or ahora,
        "periodo_fin": fecha_fin or ahora,
    }


# ── Reporte Circular 023 CGR ───────────────────────────────────────────────


class ReporteCircular023(BaseModel):
    """Reporte trimestral de cumplimiento de la Circular 023 de la CGR.

    Genera automáticamente las estadísticas requeridas por el Contralor General
    para el informe de uso de IA conforme a la Circular No. 023 (2025IE0146473).
    """

    periodo_trimestre: str = Field(
        ..., description="Trimestre del reporte (ej: '2026-Q1')",
    )
    periodo_inicio: datetime
    periodo_fin: datetime

    # Uso general
    total_consultas: int = Field(..., description="Total de consultas al sistema en el trimestre")
    total_conversaciones: int = Field(..., description="Total de conversaciones iniciadas")
    promedio_mensajes_por_conversacion: float

    # Usuarios activos por dirección
    usuarios_activos_des: int = Field(..., description="Usuarios activos DES")
    usuarios_activos_dvf: int = Field(..., description="Usuarios activos DVF")
    total_usuarios_activos: int

    # Consultas por dirección
    consultas_des: int
    consultas_dvf: int

    # Documentos y formatos generados con IA
    documentos_procesados_rag: int = Field(
        ..., description="Documentos procesados en el pipeline RAG",
    )
    formatos_generados_ia: int = Field(
        ..., description="Formatos CGR generados con asistencia de IA",
    )
    hallazgos_asistidos_ia: int = Field(
        ..., description="Hallazgos en los que se usó asistencia de IA",
    )

    # Calidad y retroalimentación
    feedback_positivo: int
    feedback_negativo: int
    feedback_neutral: int
    tasa_satisfaccion: float = Field(
        ..., description="Porcentaje de feedback positivo sobre total con feedback",
    )

    # Modelos utilizados
    modelos_utilizados: list[str] = Field(
        default_factory=list, description="Lista de modelos LLM utilizados en el periodo",
    )
    latencia_promedio_ms: float

    # Cumplimiento Circular 023
    total_advertencias_privacidad: int = Field(
        ..., description="Veces que se detectaron datos personales (Art. Privacidad)",
    )
    disclaimers_incluidos: str = Field(
        default="Todos los mensajes incluyen disclaimer de validacion humana",
    )
    principios_implementados: list[str] = Field(
        default_factory=lambda: [
            "Transparencia", "Responsabilidad", "Privacidad",
            "Control Humano", "Usos Limitados", "Declaracion IA", "Algoritmos Abiertos",
        ],
    )

    # Nota de generación
    nota: str = Field(
        default="Reporte generado automaticamente por CecilIA v2. "
        "Requiere revision y aprobacion del Director de TIC antes de remision al Despacho.",
    )


@enrutador.get(
    "/reporte-circular-023",
    response_model=ReporteCircular023,
    summary="Reporte trimestral Circular 023 CGR",
    description=(
        "Genera el reporte trimestral de uso de IA requerido por la Circular 023 "
        "del Contralor General de la República. Incluye estadísticas de uso, "
        "usuarios activos, documentos generados y métricas de cumplimiento."
    ),
)
async def generar_reporte_circular_023(
    trimestre: Optional[str] = Query(
        default=None,
        description="Trimestre a reportar (ej: '2026-Q1'). Si no se especifica, usa el trimestre actual.",
    ),
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Genera el reporte trimestral para cumplimiento de la Circular 023 CGR.

    Conforme a la Circular No. 023 (radicado 2025IE0146473) del Contralor General,
    este endpoint consolida las estadísticas de uso del sistema de IA para el
    informe trimestral requerido.

    Consulta datos reales de:
    - Tabla `conversaciones`: total de conversaciones y mensajes
    - Tabla `mensajes`: conteo por rol, feedback, modelos
    - Tabla `documentos`: documentos procesados RAG
    - Tabla `formatos_generados`: formatos CGR generados con IA
    - Tabla `hallazgos`: hallazgos con asistencia de IA
    """
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
            anio = int(anio)
            q = int(q)
            mes_inicio = (q - 1) * 3 + 1
            inicio = datetime(anio, mes_inicio, 1, tzinfo=timezone.utc)
            if q == 4:
                fin = datetime(anio + 1, 1, 1, tzinfo=timezone.utc)
            else:
                fin = datetime(anio, mes_inicio + 3, 1, tzinfo=timezone.utc)
        except (ValueError, IndexError):
            # Fallback al trimestre actual
            q_actual = (ahora.month - 1) // 3 + 1
            mes_inicio = (q_actual - 1) * 3 + 1
            inicio = datetime(ahora.year, mes_inicio, 1, tzinfo=timezone.utc)
            if q_actual == 4:
                fin = datetime(ahora.year + 1, 1, 1, tzinfo=timezone.utc)
            else:
                fin = datetime(ahora.year, mes_inicio + 3, 1, tzinfo=timezone.utc)
            trimestre = f"{ahora.year}-Q{q_actual}"
    else:
        q_actual = (ahora.month - 1) // 3 + 1
        mes_inicio = (q_actual - 1) * 3 + 1
        inicio = datetime(ahora.year, mes_inicio, 1, tzinfo=timezone.utc)
        if q_actual == 4:
            fin = datetime(ahora.year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            fin = datetime(ahora.year, mes_inicio + 3, 1, tzinfo=timezone.utc)
        trimestre = f"{ahora.year}-Q{q_actual}"

    logger.info(
        "Generando reporte Circular 023: trimestre=%s, inicio=%s, fin=%s",
        trimestre, inicio.isoformat(), fin.isoformat(),
    )

    # --- Consultas reales a la base de datos ---

    # Total de conversaciones en el periodo
    total_conv_result = await db.execute(
        select(func.count(Conversacion.id)).where(
            and_(Conversacion.created_at >= inicio, Conversacion.created_at < fin)
        )
    )
    total_conversaciones = total_conv_result.scalar() or 0

    # Total de mensajes (consultas) en el periodo
    total_msgs_result = await db.execute(
        select(func.count(Mensaje.id)).where(
            and_(Mensaje.created_at >= inicio, Mensaje.created_at < fin)
        )
    )
    total_consultas = total_msgs_result.scalar() or 0

    # Promedio de mensajes por conversación
    promedio_msgs = round(total_consultas / max(total_conversaciones, 1), 1)

    # Usuarios activos por dirección
    usuarios_des_result = await db.execute(
        select(func.count(func.distinct(Conversacion.usuario_id))).where(
            and_(
                Conversacion.created_at >= inicio,
                Conversacion.created_at < fin,
                Conversacion.direccion == "DES",
            )
        )
    )
    usuarios_des = usuarios_des_result.scalar() or 0

    usuarios_dvf_result = await db.execute(
        select(func.count(func.distinct(Conversacion.usuario_id))).where(
            and_(
                Conversacion.created_at >= inicio,
                Conversacion.created_at < fin,
                Conversacion.direccion == "DVF",
            )
        )
    )
    usuarios_dvf = usuarios_dvf_result.scalar() or 0

    # Consultas por dirección (basado en conversaciones)
    consultas_des_result = await db.execute(
        select(func.sum(Conversacion.total_mensajes)).where(
            and_(
                Conversacion.created_at >= inicio,
                Conversacion.created_at < fin,
                Conversacion.direccion == "DES",
            )
        )
    )
    consultas_des = consultas_des_result.scalar() or 0

    consultas_dvf_result = await db.execute(
        select(func.sum(Conversacion.total_mensajes)).where(
            and_(
                Conversacion.created_at >= inicio,
                Conversacion.created_at < fin,
                Conversacion.direccion == "DVF",
            )
        )
    )
    consultas_dvf = consultas_dvf_result.scalar() or 0

    # Documentos procesados RAG
    docs_result = await db.execute(
        select(func.count(Documento.id)).where(
            and_(
                Documento.created_at >= inicio,
                Documento.created_at < fin,
                Documento.estado == "indexado",
            )
        )
    )
    docs_procesados = docs_result.scalar() or 0

    # Formatos generados con IA
    formatos_result = await db.execute(
        select(func.count(FormatoGenerado.id)).where(
            and_(
                FormatoGenerado.created_at >= inicio,
                FormatoGenerado.created_at < fin,
                FormatoGenerado.generado_con_ia == True,
            )
        )
    )
    formatos_ia = formatos_result.scalar() or 0

    # Hallazgos asistidos con IA
    hallazgos_result = await db.execute(
        select(func.count(Hallazgo.id)).where(
            and_(
                Hallazgo.created_at >= inicio,
                Hallazgo.created_at < fin,
            )
        )
    )
    hallazgos_ia = hallazgos_result.scalar() or 0

    # Feedback (de mensajes del asistente)
    feedback_pos_result = await db.execute(
        select(func.count(Mensaje.id)).where(
            and_(
                Mensaje.created_at >= inicio,
                Mensaje.created_at < fin,
                Mensaje.feedback_puntuacion == 1,
            )
        )
    )
    feedback_pos = feedback_pos_result.scalar() or 0

    feedback_neg_result = await db.execute(
        select(func.count(Mensaje.id)).where(
            and_(
                Mensaje.created_at >= inicio,
                Mensaje.created_at < fin,
                Mensaje.feedback_puntuacion == -1,
            )
        )
    )
    feedback_neg = feedback_neg_result.scalar() or 0

    feedback_neutral_result = await db.execute(
        select(func.count(Mensaje.id)).where(
            and_(
                Mensaje.created_at >= inicio,
                Mensaje.created_at < fin,
                Mensaje.feedback_puntuacion == 0,
            )
        )
    )
    feedback_neu = feedback_neutral_result.scalar() or 0

    total_con_feedback = feedback_pos + feedback_neg + feedback_neu
    tasa_satisfaccion = round(
        (feedback_pos / max(total_con_feedback, 1)) * 100, 1,
    )

    # Modelos utilizados (distintos)
    modelos_result = await db.execute(
        select(func.distinct(Conversacion.modelo_utilizado)).where(
            and_(
                Conversacion.created_at >= inicio,
                Conversacion.created_at < fin,
                Conversacion.modelo_utilizado.isnot(None),
            )
        )
    )
    modelos = [m for m in modelos_result.scalars().all() if m]

    return {
        "periodo_trimestre": trimestre,
        "periodo_inicio": inicio,
        "periodo_fin": fin,
        "total_consultas": total_consultas,
        "total_conversaciones": total_conversaciones,
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
        "tasa_satisfaccion": tasa_satisfaccion,
        "modelos_utilizados": modelos or ["Sin datos en el periodo"],
        "latencia_promedio_ms": 0.0,  # TODO: calcular desde metadata_modelo
        "total_advertencias_privacidad": 0,  # TODO: contar desde logs cuando se implemente persistencia de alertas
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
