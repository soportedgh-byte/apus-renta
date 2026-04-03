"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: app/api/chat_routes.py
Propósito: Endpoints de chat — envío de mensajes con respuesta SSE streaming,
           gestión de conversaciones y retroalimentación del usuario
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.main import obtener_sesion_db

logger = logging.getLogger("cecilia.api.chat")

enrutador = APIRouter()


# ── Esquemas de solicitud y respuesta ────────────────────────────────────────


class SolicitudMensaje(BaseModel):
    """Esquema para enviar un mensaje al chat."""

    mensaje: str = Field(..., min_length=1, max_length=10000, description="Texto del mensaje del usuario")
    conversacion_id: Optional[str] = Field(default=None, description="ID de conversación existente (None para nueva)")
    modelo: Optional[str] = Field(default=None, description="Modelo LLM a utilizar (override)")
    fase: Optional[str] = Field(default=None, description="Fase de auditoría actual")
    proyecto_auditoria_id: Optional[str] = Field(default=None, description="ID del proyecto de auditoría en contexto")


class RespuestaConversacion(BaseModel):
    """Esquema de resumen de una conversación."""

    id: str
    titulo: str
    creado_en: datetime
    actualizado_en: datetime
    total_mensajes: int


class RespuestaConversacionDetalle(BaseModel):
    """Esquema detallado de una conversación con sus mensajes."""

    id: str
    titulo: str
    creado_en: datetime
    actualizado_en: datetime
    mensajes: list[dict[str, Any]]


class SolicitudFeedback(BaseModel):
    """Esquema para retroalimentación del usuario sobre una respuesta."""

    mensaje_id: str = Field(..., description="ID del mensaje evaluado")
    puntuacion: int = Field(..., ge=-1, le=1, description="Puntuación: -1 (negativo), 0 (neutral), 1 (positivo)")
    comentario: Optional[str] = Field(default=None, max_length=2000, description="Comentario opcional del usuario")


class RespuestaFeedback(BaseModel):
    """Confirmación de retroalimentación registrada."""

    mensaje: str
    feedback_id: str


# ── Dependencia temporal de usuario autenticado ──────────────────────────────


async def _obtener_usuario_actual_id() -> int:
    """Dependencia temporal que retorna un ID de usuario simulado.

    Será reemplazada por la dependencia real de autenticación
    cuando auth_routes.py esté disponible.
    """
    return 1


# ── Endpoints ────────────────────────────────────────────────────────────────


@enrutador.post(
    "/enviar",
    summary="Enviar mensaje al chat",
    description="Envía un mensaje y recibe la respuesta del agente vía Server-Sent Events (SSE).",
    status_code=status.HTTP_200_OK,
)
async def enviar_mensaje(
    solicitud: SolicitudMensaje,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> EventSourceResponse:
    """Procesa el mensaje del usuario y retorna una respuesta SSE streaming.

    El flujo es:
    1. Crear o recuperar la conversación.
    2. Almacenar el mensaje del usuario en la base de datos.
    3. Invocar el grafo LangGraph del agente supervisor.
    4. Transmitir la respuesta token por token vía SSE.
    5. Al finalizar, almacenar la respuesta completa.
    """

    conversacion_id: str = solicitud.conversacion_id or str(uuid.uuid4())

    async def _generar_eventos() -> AsyncGenerator[dict[str, str], None]:
        """Generador asíncrono de eventos SSE para la respuesta del agente."""
        try:
            # Evento inicial con metadatos de la conversación
            yield {
                "event": "inicio",
                "data": json.dumps({
                    "conversacion_id": conversacion_id,
                    "marca_temporal": datetime.now(timezone.utc).isoformat(),
                }),
            }

            # TODO: Integrar con el grafo LangGraph del supervisor
            # Por ahora, respuesta de marcador de posición
            respuesta_parcial: str = (
                "Soy CecilIA v2, su asistente de control fiscal. "
                "El servicio de chat se encuentra en implementación. "
                "Por favor, intente de nuevo cuando el módulo esté completamente configurado."
            )

            # Simular streaming token por token
            tokens: list[str] = respuesta_parcial.split(" ")
            acumulado: str = ""
            for token in tokens:
                acumulado += (" " if acumulado else "") + token
                yield {
                    "event": "token",
                    "data": json.dumps({"contenido": token + " "}),
                }

            # Evento final con la respuesta completa y fuentes
            yield {
                "event": "fin",
                "data": json.dumps({
                    "conversacion_id": conversacion_id,
                    "respuesta_completa": acumulado,
                    "fuentes": [],
                    "modelo_utilizado": solicitud.modelo or "pendiente",
                }),
            }

        except Exception as error:
            logger.exception("Error al generar respuesta SSE para conversación %s", conversacion_id)
            yield {
                "event": "error",
                "data": json.dumps({
                    "error": "Error interno al procesar el mensaje.",
                    "detalle": str(error),
                }),
            }

    return EventSourceResponse(_generar_eventos())


@enrutador.get(
    "/conversaciones",
    response_model=list[RespuestaConversacion],
    summary="Listar conversaciones del usuario",
    description="Retorna todas las conversaciones del usuario autenticado, ordenadas por fecha.",
)
async def listar_conversaciones(
    limite: int = Query(default=50, ge=1, le=200, description="Número máximo de resultados"),
    desplazamiento: int = Query(default=0, ge=0, description="Desplazamiento para paginación"),
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> list[dict[str, Any]]:
    """Lista las conversaciones del usuario con paginación."""

    # TODO: Implementar consulta real cuando el modelo Conversacion esté disponible
    # resultado = await db.execute(
    #     select(Conversacion)
    #     .where(Conversacion.usuario_id == usuario_id)
    #     .order_by(desc(Conversacion.updated_at))
    #     .limit(limite)
    #     .offset(desplazamiento)
    # )
    # conversaciones = resultado.scalars().all()

    logger.info(
        "Listando conversaciones para usuario_id=%d (limite=%d, offset=%d)",
        usuario_id, limite, desplazamiento,
    )
    return []


@enrutador.get(
    "/conversaciones/{conversacion_id}",
    response_model=RespuestaConversacionDetalle,
    summary="Obtener conversación con mensajes",
    description="Retorna una conversación específica con todos sus mensajes.",
)
async def obtener_conversacion(
    conversacion_id: str,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Obtiene una conversación por su ID, incluyendo todos los mensajes."""

    # TODO: Implementar consulta real cuando los modelos estén disponibles
    # resultado = await db.execute(
    #     select(Conversacion)
    #     .where(Conversacion.id == conversacion_id, Conversacion.usuario_id == usuario_id)
    # )
    # conversacion = resultado.scalar_one_or_none()
    # if not conversacion:
    #     raise HTTPException(status_code=404, detail="Conversación no encontrada")

    logger.info("Consultando conversación %s para usuario_id=%d", conversacion_id, usuario_id)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Conversación {conversacion_id} no encontrada.",
    )


@enrutador.delete(
    "/conversaciones/{conversacion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar conversación",
    description="Elimina una conversación y todos sus mensajes asociados.",
)
async def eliminar_conversacion(
    conversacion_id: str,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> None:
    """Elimina una conversación verificando que pertenezca al usuario."""

    # TODO: Implementar eliminación real cuando los modelos estén disponibles
    # resultado = await db.execute(
    #     select(Conversacion)
    #     .where(Conversacion.id == conversacion_id, Conversacion.usuario_id == usuario_id)
    # )
    # conversacion = resultado.scalar_one_or_none()
    # if not conversacion:
    #     raise HTTPException(status_code=404, detail="Conversación no encontrada")
    # await db.delete(conversacion)

    logger.info("Solicitud de eliminación de conversación %s por usuario_id=%d", conversacion_id, usuario_id)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Conversación {conversacion_id} no encontrada.",
    )


@enrutador.post(
    "/conversaciones/{conversacion_id}/feedback",
    response_model=RespuestaFeedback,
    summary="Enviar retroalimentación",
    description="Registra retroalimentación (pulgar arriba/abajo) sobre una respuesta del agente.",
)
async def enviar_feedback(
    conversacion_id: str,
    solicitud: SolicitudFeedback,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, str]:
    """Registra la retroalimentación del usuario para métricas de calidad."""

    feedback_id: str = str(uuid.uuid4())

    # TODO: Almacenar en la base de datos cuando el modelo de feedback esté disponible
    logger.info(
        "Feedback recibido: conversacion=%s, mensaje=%s, puntuacion=%d, usuario=%d",
        conversacion_id, solicitud.mensaje_id, solicitud.puntuacion, usuario_id,
    )

    return {
        "mensaje": "Retroalimentación registrada exitosamente.",
        "feedback_id": feedback_id,
    }
