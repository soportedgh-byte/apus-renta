"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/api/hallazgo_routes.py
Proposito: CRUD de hallazgos + workflow de aprobacion + oficios de traslado.
           Incluye validacion Circular 023 y generacion DOCX.
Sprint: 5
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import io
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import obtener_sesion_db
from app.services.hallazgo_service import HallazgoService

logger = logging.getLogger("cecilia.api.hallazgos")

enrutador = APIRouter()


# ── Esquemas ─────────────────────────────────────────────────────────────────


class ConnotacionSchema(BaseModel):
    tipo: str = Field(..., description="administrativo|fiscal|disciplinario|penal")
    fundamentacion_legal: str = Field(default="", description="Fundamentacion legal")
    descripcion: str = Field(default="", description="Descripcion de la connotacion")


class ResponsableSchema(BaseModel):
    nombre: str = Field(default="")
    cargo: str = Field(default="")
    periodo: str = Field(default="")
    fundamentacion: str = Field(default="")


class EvidenciaSchema(BaseModel):
    documento_id: str = Field(default="")
    descripcion: str = Field(default="")
    folio: str = Field(default="")
    tipo: str = Field(default="documental")


class SolicitudCrearHallazgo(BaseModel):
    auditoria_id: str = Field(..., description="ID de la auditoria")
    titulo: str = Field(..., min_length=5, max_length=500)
    condicion: str = Field(..., min_length=10, description="Situacion factica")
    criterio: str = Field(..., min_length=10, description="Norma incumplida")
    causa: str = Field(..., min_length=10, description="Razon de la diferencia")
    efecto: str = Field(..., min_length=10, description="Consecuencia/impacto")
    recomendacion: Optional[str] = Field(default=None)
    connotaciones: list[ConnotacionSchema] = Field(default_factory=list)
    cuantia_presunto_dano: Optional[float] = Field(default=None, ge=0)
    presuntos_responsables: list[ResponsableSchema] = Field(default_factory=list)
    evidencias: list[EvidenciaSchema] = Field(default_factory=list)
    generado_por_ia: bool = Field(default=False)


class SolicitudActualizarHallazgo(BaseModel):
    titulo: Optional[str] = Field(default=None, min_length=5, max_length=500)
    condicion: Optional[str] = Field(default=None)
    criterio: Optional[str] = Field(default=None)
    causa: Optional[str] = Field(default=None)
    efecto: Optional[str] = Field(default=None)
    recomendacion: Optional[str] = Field(default=None)
    connotaciones: Optional[list[ConnotacionSchema]] = Field(default=None)
    cuantia_presunto_dano: Optional[float] = Field(default=None, ge=0)
    presuntos_responsables: Optional[list[ResponsableSchema]] = Field(default=None)
    evidencias: Optional[list[EvidenciaSchema]] = Field(default=None)


class SolicitudCambioEstado(BaseModel):
    nuevo_estado: str = Field(..., description="Nuevo estado del hallazgo")
    comentarios: str = Field(default="", max_length=2000)


class SolicitudOficioTraslado(BaseModel):
    destino: str = Field(..., description="fiscal|disciplinario|penal")


# ── Dependencia temporal ──────────────────────────────────────────────────


async def _obtener_usuario_actual_id() -> int:
    return 1


def _hallazgo_a_dict(h: Any) -> dict[str, Any]:
    """Convierte Hallazgo ORM a diccionario para respuesta."""
    return {
        "id": h.id,
        "auditoria_id": h.auditoria_id,
        "numero_hallazgo": h.numero_hallazgo,
        "titulo": h.titulo,
        "condicion": h.condicion,
        "criterio": h.criterio,
        "causa": h.causa,
        "efecto": h.efecto,
        "recomendacion": h.recomendacion or "",
        "connotaciones": h.connotaciones or [],
        "cuantia_presunto_dano": float(h.cuantia_presunto_dano) if h.cuantia_presunto_dano else None,
        "presuntos_responsables": h.presuntos_responsables or [],
        "evidencias": h.evidencias or [],
        "estado": h.estado,
        "fase_actual_workflow": h.fase_actual_workflow,
        "historial_workflow": h.historial_workflow or [],
        "redaccion_validada_humano": h.redaccion_validada_humano,
        "generado_por_ia": h.generado_por_ia,
        "validado_por": h.validado_por,
        "fecha_validacion": h.fecha_validacion.isoformat() if h.fecha_validacion else None,
        "created_by": h.created_by,
        "updated_by": h.updated_by,
        "created_at": h.created_at.isoformat() if h.created_at else None,
        "updated_at": h.updated_at.isoformat() if h.updated_at else None,
    }


# ── Endpoints ────────────────────────────────────────────────────────────────


@enrutador.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Crear hallazgo",
    description="Crea un nuevo hallazgo en estado BORRADOR con numero secuencial.",
)
async def crear_hallazgo(
    solicitud: SolicitudCrearHallazgo,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    try:
        servicio = HallazgoService(db)
        hallazgo = await servicio.crear_hallazgo(
            auditoria_id=solicitud.auditoria_id,
            datos={
                "titulo": solicitud.titulo,
                "condicion": solicitud.condicion,
                "criterio": solicitud.criterio,
                "causa": solicitud.causa,
                "efecto": solicitud.efecto,
                "recomendacion": solicitud.recomendacion,
                "connotaciones": [c.model_dump() for c in solicitud.connotaciones],
                "cuantia_presunto_dano": solicitud.cuantia_presunto_dano,
                "presuntos_responsables": [r.model_dump() for r in solicitud.presuntos_responsables],
                "evidencias": [e.model_dump() for e in solicitud.evidencias],
                "generado_por_ia": solicitud.generado_por_ia,
            },
            usuario_id=usuario_id,
        )
        return _hallazgo_a_dict(hallazgo)
    except Exception as exc:
        logger.error("Error creando hallazgo: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))


@enrutador.get(
    "/",
    summary="Listar hallazgos",
    description="Lista hallazgos con filtros por auditoria, estado y connotacion.",
)
async def listar_hallazgos(
    auditoria_id: Optional[str] = Query(default=None),
    estado: Optional[str] = Query(default=None),
    connotacion: Optional[str] = Query(default=None),
    cuantia_minima: Optional[float] = Query(default=None, ge=0),
    limite: int = Query(default=50, ge=1, le=200),
    desplazamiento: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> list[dict[str, Any]]:
    try:
        servicio = HallazgoService(db)
        hallazgos = await servicio.listar_hallazgos(
            auditoria_id=auditoria_id,
            estado=estado,
            connotacion=connotacion,
            cuantia_minima=cuantia_minima,
            limite=limite,
            desplazamiento=desplazamiento,
        )
        return [_hallazgo_a_dict(h) for h in hallazgos]
    except Exception as exc:
        logger.warning("Error listando hallazgos: %s", exc)
        return []


@enrutador.get(
    "/estadisticas",
    summary="Estadisticas de hallazgos",
    description="KPIs: total, por estado, por connotacion, cuantia total.",
)
async def obtener_estadisticas(
    auditoria_id: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    try:
        servicio = HallazgoService(db)
        return await servicio.obtener_estadisticas(auditoria_id)
    except Exception as exc:
        logger.warning("Error obteniendo estadisticas: %s", exc)
        return {
            "total_hallazgos": 0, "por_estado": {}, "por_connotacion": {},
            "cuantia_total_presunto_dano": 0, "borradores": 0,
            "en_revision": 0, "aprobados": 0, "trasladados": 0,
        }


@enrutador.get(
    "/{hallazgo_id}",
    summary="Obtener detalle de hallazgo",
    description="Retorna datos completos con historial de workflow.",
)
async def obtener_hallazgo(
    hallazgo_id: str,
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    servicio = HallazgoService(db)
    hallazgo = await servicio.obtener_hallazgo(hallazgo_id)
    if not hallazgo:
        raise HTTPException(status_code=404, detail="Hallazgo no encontrado.")
    return _hallazgo_a_dict(hallazgo)


@enrutador.put(
    "/{hallazgo_id}",
    summary="Actualizar hallazgo",
    description="Actualiza campos. Solo en estado BORRADOR o EN_REVISION.",
)
async def actualizar_hallazgo(
    hallazgo_id: str,
    solicitud: SolicitudActualizarHallazgo,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    try:
        servicio = HallazgoService(db)
        datos = solicitud.model_dump(exclude_none=True)
        if "connotaciones" in datos:
            datos["connotaciones"] = [c.model_dump() if hasattr(c, "model_dump") else c for c in datos["connotaciones"]]
        if "presuntos_responsables" in datos:
            datos["presuntos_responsables"] = [r.model_dump() if hasattr(r, "model_dump") else r for r in datos["presuntos_responsables"]]
        if "evidencias" in datos:
            datos["evidencias"] = [e.model_dump() if hasattr(e, "model_dump") else e for e in datos["evidencias"]]

        hallazgo = await servicio.actualizar_hallazgo(hallazgo_id, datos, usuario_id)
        return _hallazgo_a_dict(hallazgo)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@enrutador.post(
    "/{hallazgo_id}/cambiar-estado",
    summary="Transicionar estado",
    description="Cambia estado del hallazgo siguiendo el workflow.",
)
async def cambiar_estado(
    hallazgo_id: str,
    solicitud: SolicitudCambioEstado,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    try:
        servicio = HallazgoService(db)
        hallazgo = await servicio.cambiar_estado(
            hallazgo_id, solicitud.nuevo_estado, usuario_id,
            comentarios=solicitud.comentarios,
        )
        return _hallazgo_a_dict(hallazgo)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@enrutador.post(
    "/{hallazgo_id}/aprobar",
    summary="Aprobar hallazgo",
    description="Solo DIRECTOR_DVF. Requiere validacion humana (Circular 023).",
)
async def aprobar_hallazgo(
    hallazgo_id: str,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    try:
        servicio = HallazgoService(db)
        hallazgo = await servicio.aprobar_hallazgo(
            hallazgo_id, usuario_id, rol_usuario="director_dvf",
        )
        return _hallazgo_a_dict(hallazgo)
    except (ValueError, PermissionError) as exc:
        code = 403 if isinstance(exc, PermissionError) else 400
        raise HTTPException(status_code=code, detail=str(exc))


@enrutador.post(
    "/{hallazgo_id}/validar-redaccion",
    summary="Validar redaccion humana",
    description="Marca el hallazgo como validado por humano (Circular 023).",
)
async def validar_redaccion(
    hallazgo_id: str,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    try:
        servicio = HallazgoService(db)
        hallazgo = await servicio.validar_redaccion(hallazgo_id, usuario_id)
        return _hallazgo_a_dict(hallazgo)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@enrutador.post(
    "/{hallazgo_id}/oficio-traslado",
    summary="Generar oficio de traslado DOCX",
    description="Genera DOCX de oficio de traslado segun connotacion. Solo hallazgos APROBADOS.",
)
async def generar_oficio_traslado(
    hallazgo_id: str,
    solicitud: SolicitudOficioTraslado,
    db: AsyncSession = Depends(obtener_sesion_db),
) -> StreamingResponse:
    try:
        servicio = HallazgoService(db)
        docx_bytes = await servicio.generar_oficio_traslado(
            hallazgo_id, solicitud.destino,
        )

        nombre = f"Oficio_Traslado_{solicitud.destino}_{hallazgo_id[:8]}.docx"
        return StreamingResponse(
            io.BytesIO(docx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
