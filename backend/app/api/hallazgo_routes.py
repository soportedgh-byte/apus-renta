"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: app/api/hallazgo_routes.py
Propósito: Endpoints de gestión de hallazgos — CRUD, flujo de estados y
           traslados por los cinco elementos del hallazgo fiscal
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

logger = logging.getLogger("cecilia.api.hallazgos")

enrutador = APIRouter()


# ── Estados del flujo de trabajo de hallazgos ────────────────────────────────

ESTADOS_HALLAZGO: list[str] = [
    "borrador",
    "en_revision",
    "aprobado",
    "notificado",
    "con_respuesta",
    "confirmado",
    "trasladado",
    "archivado",
]

TRANSICIONES_VALIDAS: dict[str, list[str]] = {
    "borrador": ["en_revision"],
    "en_revision": ["aprobado", "borrador"],
    "aprobado": ["notificado", "borrador"],
    "notificado": ["con_respuesta", "confirmado"],
    "con_respuesta": ["confirmado", "borrador"],
    "confirmado": ["trasladado", "archivado"],
    "trasladado": ["archivado"],
    "archivado": [],
}


# ── Esquemas ─────────────────────────────────────────────────────────────────


class ElementoHallazgo(BaseModel):
    """Los cinco elementos del hallazgo fiscal según la normativa CGR."""

    condicion: str = Field(
        ..., min_length=10, max_length=5000,
        description="Condición: situación fáctica observada (lo que se encontró)",
    )
    criterio: str = Field(
        ..., min_length=10, max_length=5000,
        description="Criterio: norma o parámetro que se debía cumplir",
    )
    causa: str = Field(
        ..., min_length=10, max_length=5000,
        description="Causa: razón por la que se produjo la diferencia",
    )
    efecto: str = Field(
        ..., min_length=10, max_length=5000,
        description="Efecto: consecuencia o impacto de la situación",
    )
    recomendacion: str = Field(
        ..., min_length=10, max_length=5000,
        description="Recomendación: acción correctiva sugerida",
    )


class SolicitudCrearHallazgo(BaseModel):
    """Esquema para crear un nuevo hallazgo."""

    titulo: str = Field(..., min_length=10, max_length=500, description="Título descriptivo del hallazgo")
    auditoria_id: str = Field(..., description="ID de la auditoría asociada")
    tipo: str = Field(
        ..., description="Tipo: administrativo | fiscal | disciplinario | penal | fiscal_y_disciplinario",
    )
    cuantia: Optional[float] = Field(default=None, ge=0, description="Cuantía del hallazgo en pesos colombianos")
    elementos: ElementoHallazgo = Field(..., description="Los cinco elementos del hallazgo")
    evidencias: list[str] = Field(default_factory=list, description="IDs de documentos de evidencia")
    observaciones: Optional[str] = Field(default=None, max_length=3000)


class SolicitudActualizarHallazgo(BaseModel):
    """Esquema para actualizar un hallazgo existente."""

    titulo: Optional[str] = Field(default=None, min_length=10, max_length=500)
    tipo: Optional[str] = Field(default=None)
    cuantia: Optional[float] = Field(default=None, ge=0)
    elementos: Optional[ElementoHallazgo] = Field(default=None)
    evidencias: Optional[list[str]] = Field(default=None)
    observaciones: Optional[str] = Field(default=None, max_length=3000)


class SolicitudCambioEstado(BaseModel):
    """Esquema para cambiar el estado de un hallazgo."""

    nuevo_estado: str = Field(..., description="Nuevo estado del hallazgo")
    justificacion: str = Field(
        ..., min_length=10, max_length=2000,
        description="Justificación del cambio de estado",
    )


class SolicitudTraslado(BaseModel):
    """Esquema para iniciar traslado de un hallazgo (solo DVF)."""

    entidad_destino: str = Field(..., description="Entidad a la que se traslada el hallazgo")
    tipo_traslado: str = Field(
        ..., description="Tipo: fiscalia | procuraduria | contaduria | cgn | otro",
    )
    fundamento_legal: str = Field(
        ..., min_length=20, max_length=3000,
        description="Fundamento legal del traslado",
    )
    documentos_soporte: list[str] = Field(default_factory=list, description="IDs de documentos de soporte")


class RespuestaHallazgo(BaseModel):
    """Respuesta con datos completos de un hallazgo."""

    id: str
    titulo: str
    auditoria_id: str
    tipo: str
    estado: str
    cuantia: Optional[float] = None
    elementos: dict[str, str]
    evidencias: list[str]
    observaciones: Optional[str] = None
    creado_en: datetime
    actualizado_en: datetime
    usuario_creador_id: int


class RespuestaTraslado(BaseModel):
    """Respuesta de un traslado iniciado."""

    traslado_id: str
    hallazgo_id: str
    entidad_destino: str
    tipo_traslado: str
    estado: str
    creado_en: datetime


# ── Tipos de hallazgo válidos ────────────────────────────────────────────────

TIPOS_HALLAZGO_VALIDOS: set[str] = {
    "administrativo", "fiscal", "disciplinario", "penal", "fiscal_y_disciplinario",
}

TIPOS_TRASLADO_VALIDOS: set[str] = {
    "fiscalia", "procuraduria", "contaduria", "cgn", "otro",
}


# ── Dependencia temporal de usuario autenticado ──────────────────────────────


async def _obtener_usuario_actual_id() -> int:
    """Dependencia temporal — será reemplazada por auth real."""
    return 1


# ── Endpoints ────────────────────────────────────────────────────────────────


@enrutador.post(
    "/",
    response_model=RespuestaHallazgo,
    status_code=status.HTTP_201_CREATED,
    summary="Crear hallazgo",
    description="Crea un nuevo hallazgo con los cinco elementos requeridos.",
)
async def crear_hallazgo(
    solicitud: SolicitudCrearHallazgo,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Crea un hallazgo validando tipo y elementos obligatorios."""

    if solicitud.tipo not in TIPOS_HALLAZGO_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de hallazgo inválido. Válidos: {sorted(TIPOS_HALLAZGO_VALIDOS)}",
        )

    hallazgo_id: str = str(uuid.uuid4())
    ahora: datetime = datetime.now(timezone.utc)

    elementos_dict: dict[str, str] = {
        "condicion": solicitud.elementos.condicion,
        "criterio": solicitud.elementos.criterio,
        "causa": solicitud.elementos.causa,
        "efecto": solicitud.elementos.efecto,
        "recomendacion": solicitud.elementos.recomendacion,
    }

    # TODO: Persistir en base de datos cuando el modelo Hallazgo esté disponible
    logger.info(
        "Hallazgo creado: id=%s, titulo=%s, tipo=%s, auditoria=%s, usuario=%d",
        hallazgo_id, solicitud.titulo, solicitud.tipo, solicitud.auditoria_id, usuario_id,
    )

    return {
        "id": hallazgo_id,
        "titulo": solicitud.titulo,
        "auditoria_id": solicitud.auditoria_id,
        "tipo": solicitud.tipo,
        "estado": "borrador",
        "cuantia": solicitud.cuantia,
        "elementos": elementos_dict,
        "evidencias": solicitud.evidencias,
        "observaciones": solicitud.observaciones,
        "creado_en": ahora,
        "actualizado_en": ahora,
        "usuario_creador_id": usuario_id,
    }


@enrutador.get(
    "/",
    response_model=list[RespuestaHallazgo],
    summary="Listar hallazgos",
    description="Lista hallazgos con filtros opcionales.",
)
async def listar_hallazgos(
    auditoria_id: Optional[str] = Query(default=None, description="Filtrar por auditoría"),
    tipo: Optional[str] = Query(default=None, description="Filtrar por tipo de hallazgo"),
    estado: Optional[str] = Query(default=None, description="Filtrar por estado"),
    limite: int = Query(default=50, ge=1, le=200),
    desplazamiento: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> list[dict[str, Any]]:
    """Lista hallazgos con filtrado y paginación."""

    if tipo and tipo not in TIPOS_HALLAZGO_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo inválido. Válidos: {sorted(TIPOS_HALLAZGO_VALIDOS)}",
        )

    if estado and estado not in ESTADOS_HALLAZGO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido. Válidos: {ESTADOS_HALLAZGO}",
        )

    logger.info(
        "Listando hallazgos: auditoria=%s, tipo=%s, estado=%s, usuario=%d",
        auditoria_id, tipo, estado, usuario_id,
    )
    return []


@enrutador.get(
    "/{hallazgo_id}",
    response_model=RespuestaHallazgo,
    summary="Obtener detalle de hallazgo",
    description="Retorna los datos completos de un hallazgo.",
)
async def obtener_hallazgo(
    hallazgo_id: str,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Obtiene un hallazgo por su ID."""

    logger.info("Consultando hallazgo %s para usuario %d", hallazgo_id, usuario_id)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Hallazgo {hallazgo_id} no encontrado.",
    )


@enrutador.put(
    "/{hallazgo_id}",
    response_model=RespuestaHallazgo,
    summary="Actualizar hallazgo",
    description="Actualiza los datos de un hallazgo existente (solo en estado borrador).",
)
async def actualizar_hallazgo(
    hallazgo_id: str,
    solicitud: SolicitudActualizarHallazgo,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Actualiza un hallazgo. Solo permitido en estado 'borrador'."""

    if solicitud.tipo and solicitud.tipo not in TIPOS_HALLAZGO_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo inválido. Válidos: {sorted(TIPOS_HALLAZGO_VALIDOS)}",
        )

    # TODO: Verificar que el hallazgo esté en estado 'borrador' antes de actualizar
    logger.info("Actualización de hallazgo %s por usuario %d", hallazgo_id, usuario_id)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Hallazgo {hallazgo_id} no encontrado.",
    )


@enrutador.put(
    "/{hallazgo_id}/estado",
    response_model=RespuestaHallazgo,
    summary="Cambiar estado de hallazgo",
    description="Cambia el estado de un hallazgo siguiendo el flujo de trabajo definido.",
)
async def cambiar_estado_hallazgo(
    hallazgo_id: str,
    solicitud: SolicitudCambioEstado,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Cambia el estado de un hallazgo validando las transiciones permitidas.

    El flujo de estados es:
    borrador → en_revision → aprobado → notificado → con_respuesta → confirmado → trasladado/archivado
    """

    if solicitud.nuevo_estado not in ESTADOS_HALLAZGO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido '{solicitud.nuevo_estado}'. Válidos: {ESTADOS_HALLAZGO}",
        )

    # TODO: Verificar estado actual y validar transición
    # estado_actual = hallazgo.estado
    # if solicitud.nuevo_estado not in TRANSICIONES_VALIDAS.get(estado_actual, []):
    #     raise HTTPException(
    #         status_code=400,
    #         detail=f"Transición de '{estado_actual}' a '{solicitud.nuevo_estado}' no permitida.",
    #     )

    logger.info(
        "Cambio de estado de hallazgo %s a '%s' por usuario %d: %s",
        hallazgo_id, solicitud.nuevo_estado, usuario_id, solicitud.justificacion,
    )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Hallazgo {hallazgo_id} no encontrado.",
    )


@enrutador.post(
    "/{hallazgo_id}/traslado",
    response_model=RespuestaTraslado,
    status_code=status.HTTP_201_CREATED,
    summary="Iniciar traslado de hallazgo",
    description="Inicia el proceso de traslado de un hallazgo (solo DVF, hallazgo confirmado).",
)
async def iniciar_traslado(
    hallazgo_id: str,
    solicitud: SolicitudTraslado,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Inicia el traslado de un hallazgo a una entidad competente.

    Solo disponible para usuarios de la Dirección de Vigilancia Fiscal (DVF)
    y cuando el hallazgo está en estado 'confirmado'.
    """

    if solicitud.tipo_traslado not in TIPOS_TRASLADO_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de traslado inválido. Válidos: {sorted(TIPOS_TRASLADO_VALIDOS)}",
        )

    # TODO: Verificar que el usuario sea DVF y que el hallazgo esté 'confirmado'
    traslado_id: str = str(uuid.uuid4())

    logger.info(
        "Traslado iniciado: traslado=%s, hallazgo=%s, destino=%s, tipo=%s, usuario=%d",
        traslado_id, hallazgo_id, solicitud.entidad_destino, solicitud.tipo_traslado, usuario_id,
    )

    return {
        "traslado_id": traslado_id,
        "hallazgo_id": hallazgo_id,
        "entidad_destino": solicitud.entidad_destino,
        "tipo_traslado": solicitud.tipo_traslado,
        "estado": "iniciado",
        "creado_en": datetime.now(timezone.utc),
    }
