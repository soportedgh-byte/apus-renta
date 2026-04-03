"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: app/api/audit_routes.py
Propósito: Endpoints de gestión de auditorías — CRUD de auditorías y
           creación/consulta de proyectos (sesiones) de auditoría
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import obtener_sesion_db

logger = logging.getLogger("cecilia.api.auditorias")

enrutador = APIRouter()


# ── Esquemas ─────────────────────────────────────────────────────────────────


class SolicitudCrearAuditoria(BaseModel):
    """Esquema para crear una nueva auditoría."""

    nombre: str = Field(..., min_length=5, max_length=500, description="Nombre de la auditoría")
    entidad_auditada: str = Field(..., min_length=2, max_length=500, description="Entidad sujeto de control")
    tipo_auditoria: str = Field(
        ..., description="Tipo: financiera | cumplimiento | desempeno | especial | integral",
    )
    vigencia: str = Field(..., description="Vigencia auditada (e.g., '2025', '2024-2025')")
    direccion: str = Field(..., description="Dirección responsable: DES | DVF")
    descripcion: Optional[str] = Field(default=None, max_length=2000, description="Descripción del alcance")
    fecha_inicio_planeada: Optional[datetime] = Field(default=None, description="Fecha de inicio planeada")
    fecha_fin_planeada: Optional[datetime] = Field(default=None, description="Fecha de fin planeada")


class SolicitudActualizarAuditoria(BaseModel):
    """Esquema para actualizar una auditoría existente."""

    nombre: Optional[str] = Field(default=None, min_length=5, max_length=500)
    entidad_auditada: Optional[str] = Field(default=None, min_length=2, max_length=500)
    tipo_auditoria: Optional[str] = Field(default=None)
    vigencia: Optional[str] = Field(default=None)
    descripcion: Optional[str] = Field(default=None, max_length=2000)
    fase_actual: Optional[str] = Field(
        default=None,
        description="Fase actual: preplaneacion | planeacion | ejecucion | informe | seguimiento",
    )
    fecha_inicio_planeada: Optional[datetime] = Field(default=None)
    fecha_fin_planeada: Optional[datetime] = Field(default=None)


class RespuestaAuditoria(BaseModel):
    """Respuesta con datos de una auditoría."""

    id: str
    nombre: str
    entidad_auditada: str
    tipo_auditoria: str
    vigencia: str
    direccion: str
    fase_actual: str
    descripcion: Optional[str] = None
    fecha_inicio_planeada: Optional[datetime] = None
    fecha_fin_planeada: Optional[datetime] = None
    creado_en: datetime
    actualizado_en: datetime
    usuario_creador_id: int


class SolicitudCrearProyecto(BaseModel):
    """Esquema para crear un proyecto (sesión) de auditoría."""

    nombre_sesion: str = Field(..., min_length=3, max_length=300, description="Nombre de la sesión de trabajo")
    fase: str = Field(
        ..., description="Fase: preplaneacion | planeacion | ejecucion | informe | seguimiento",
    )
    objetivo: Optional[str] = Field(default=None, max_length=2000, description="Objetivo de la sesión")


class RespuestaProyecto(BaseModel):
    """Respuesta con datos de un proyecto de auditoría."""

    id: str
    auditoria_id: str
    nombre_sesion: str
    fase: str
    objetivo: Optional[str] = None
    estado: str  # activo | finalizado | archivado
    creado_en: datetime
    usuario_id: int


# ── Tipos de auditoría válidos ───────────────────────────────────────────────

TIPOS_AUDITORIA_VALIDOS: set[str] = {
    "financiera", "cumplimiento", "desempeno", "especial", "integral",
}

FASES_VALIDAS: set[str] = {
    "preplaneacion", "planeacion", "ejecucion", "informe", "seguimiento",
}

DIRECCIONES_VALIDAS: set[str] = {"DES", "DVF"}


# ── Dependencia temporal de usuario autenticado ──────────────────────────────


async def _obtener_usuario_actual_id() -> int:
    """Dependencia temporal — será reemplazada por auth real."""
    return 1


# ── Endpoints ────────────────────────────────────────────────────────────────


@enrutador.post(
    "/",
    response_model=RespuestaAuditoria,
    status_code=status.HTTP_201_CREATED,
    summary="Crear auditoría",
    description="Crea una nueva auditoría en el sistema.",
)
async def crear_auditoria(
    solicitud: SolicitudCrearAuditoria,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Crea una nueva auditoría validando tipo, dirección y datos."""

    if solicitud.tipo_auditoria not in TIPOS_AUDITORIA_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de auditoría inválido. Válidos: {sorted(TIPOS_AUDITORIA_VALIDOS)}",
        )

    if solicitud.direccion not in DIRECCIONES_VALIDAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dirección inválida. Válidas: {sorted(DIRECCIONES_VALIDAS)}",
        )

    auditoria_id: str = str(uuid.uuid4())
    ahora: datetime = datetime.now(timezone.utc)

    # TODO: Persistir en base de datos cuando el modelo Auditoria esté disponible
    logger.info(
        "Auditoría creada: id=%s, nombre=%s, entidad=%s, tipo=%s, direccion=%s, usuario=%d",
        auditoria_id, solicitud.nombre, solicitud.entidad_auditada,
        solicitud.tipo_auditoria, solicitud.direccion, usuario_id,
    )

    return {
        "id": auditoria_id,
        "nombre": solicitud.nombre,
        "entidad_auditada": solicitud.entidad_auditada,
        "tipo_auditoria": solicitud.tipo_auditoria,
        "vigencia": solicitud.vigencia,
        "direccion": solicitud.direccion,
        "fase_actual": "preplaneacion",
        "descripcion": solicitud.descripcion,
        "fecha_inicio_planeada": solicitud.fecha_inicio_planeada,
        "fecha_fin_planeada": solicitud.fecha_fin_planeada,
        "creado_en": ahora,
        "actualizado_en": ahora,
        "usuario_creador_id": usuario_id,
    }


@enrutador.get(
    "/",
    response_model=list[RespuestaAuditoria],
    summary="Listar auditorías",
    description="Lista auditorías filtradas opcionalmente por dirección.",
)
async def listar_auditorias(
    direccion: Optional[str] = Query(default=None, description="Filtrar por dirección: DES | DVF"),
    fase: Optional[str] = Query(default=None, description="Filtrar por fase actual"),
    limite: int = Query(default=50, ge=1, le=200),
    desplazamiento: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> list[dict[str, Any]]:
    """Lista auditorías con filtros opcionales."""

    if direccion and direccion not in DIRECCIONES_VALIDAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dirección inválida. Válidas: {sorted(DIRECCIONES_VALIDAS)}",
        )

    if fase and fase not in FASES_VALIDAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fase inválida. Válidas: {sorted(FASES_VALIDAS)}",
        )

    logger.info(
        "Listando auditorías: direccion=%s, fase=%s, limite=%d, offset=%d",
        direccion, fase, limite, desplazamiento,
    )
    return []


@enrutador.get(
    "/{auditoria_id}",
    response_model=RespuestaAuditoria,
    summary="Obtener detalle de auditoría",
    description="Retorna los datos completos de una auditoría específica.",
)
async def obtener_auditoria(
    auditoria_id: str,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Obtiene una auditoría por su ID."""

    # TODO: Consultar base de datos real
    logger.info("Consultando auditoría %s para usuario %d", auditoria_id, usuario_id)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Auditoría {auditoria_id} no encontrada.",
    )


@enrutador.put(
    "/{auditoria_id}",
    response_model=RespuestaAuditoria,
    summary="Actualizar auditoría",
    description="Actualiza los datos de una auditoría existente.",
)
async def actualizar_auditoria(
    auditoria_id: str,
    solicitud: SolicitudActualizarAuditoria,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Actualiza una auditoría existente con los campos proporcionados."""

    if solicitud.tipo_auditoria and solicitud.tipo_auditoria not in TIPOS_AUDITORIA_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de auditoría inválido. Válidos: {sorted(TIPOS_AUDITORIA_VALIDOS)}",
        )

    if solicitud.fase_actual and solicitud.fase_actual not in FASES_VALIDAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fase inválida. Válidas: {sorted(FASES_VALIDAS)}",
        )

    # TODO: Implementar actualización real
    logger.info("Actualización de auditoría %s por usuario %d", auditoria_id, usuario_id)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Auditoría {auditoria_id} no encontrada.",
    )


@enrutador.post(
    "/{auditoria_id}/proyecto",
    response_model=RespuestaProyecto,
    status_code=status.HTTP_201_CREATED,
    summary="Crear proyecto de auditoría",
    description="Crea una sesión de trabajo (proyecto) para una auditoría específica.",
)
async def crear_proyecto_auditoria(
    auditoria_id: str,
    solicitud: SolicitudCrearProyecto,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Crea un proyecto (sesión de trabajo) vinculado a una auditoría."""

    if solicitud.fase not in FASES_VALIDAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fase inválida. Válidas: {sorted(FASES_VALIDAS)}",
        )

    proyecto_id: str = str(uuid.uuid4())

    # TODO: Verificar existencia de auditoría y persistir proyecto
    logger.info(
        "Proyecto creado: id=%s, auditoria=%s, fase=%s, usuario=%d",
        proyecto_id, auditoria_id, solicitud.fase, usuario_id,
    )

    return {
        "id": proyecto_id,
        "auditoria_id": auditoria_id,
        "nombre_sesion": solicitud.nombre_sesion,
        "fase": solicitud.fase,
        "objetivo": solicitud.objetivo,
        "estado": "activo",
        "creado_en": datetime.now(timezone.utc),
        "usuario_id": usuario_id,
    }


@enrutador.get(
    "/{auditoria_id}/proyecto",
    response_model=RespuestaProyecto,
    summary="Obtener proyecto activo",
    description="Retorna el contexto del proyecto (sesión) activo de una auditoría.",
)
async def obtener_proyecto_auditoria(
    auditoria_id: str,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Obtiene el proyecto activo más reciente de una auditoría."""

    # TODO: Consultar proyecto activo de la auditoría
    logger.info("Consultando proyecto activo de auditoría %s para usuario %d", auditoria_id, usuario_id)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No se encontró proyecto activo para auditoría {auditoria_id}.",
    )
