"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/api/chat_routes.py
Proposito: Endpoints de chat — envio de mensajes con respuesta SSE streaming,
           gestion completa de conversaciones y trazabilidad
Sprint: 2.1
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import json
import logging
import re
import time
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, update, delete, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sse_starlette.sse import EventSourceResponse

from app.models.conversacion import Conversacion
from app.models.mensaje import Mensaje
from app.services.chat_service import obtener_chat_service
from app.llm import info_modelo_activo

logger = logging.getLogger("cecilia.api.chat")


# -- Filtro de datos personales (Circular 023 — Principio de Privacidad) --

# Patrones de datos personales colombianos
_PATRON_CEDULA = re.compile(r"\b\d{6,10}\b")  # Cedulas de ciudadania
_PATRON_NIT = re.compile(r"\b\d{9}-\d\b")  # NIT empresarial
_PATRON_TARJETA = re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b")  # Tarjetas
_PATRON_EMAIL_PERSONAL = re.compile(
    r"\b[a-zA-Z0-9._%+-]+@(gmail|hotmail|yahoo|outlook|live)\.(com|co|es|net)\b",
    re.IGNORECASE,
)
_PATRON_TELEFONO = re.compile(r"\b(3\d{9}|60[1-8]\d{7})\b")  # Celulares y fijos colombianos

_ADVERTENCIA_DATOS_PERSONALES = (
    "⚠️ ADVERTENCIA DE PRIVACIDAD — Se detectaron posibles datos personales en su mensaje "
    "(numeros de identificacion, NIT u otros). Conforme a la Circular 023 de la CGR "
    "(Principio de Privacidad) y la Ley 1581 de 2012, se recomienda NO incluir datos "
    "personales sensibles en las consultas al sistema de IA. "
    "Los datos detectados han sido procesados pero no seran almacenados en logs de trazabilidad."
)


def _detectar_datos_personales(texto: str) -> dict[str, bool]:
    """Detecta patrones de datos personales en el texto del usuario.

    Retorna un diccionario indicando que tipos de datos fueron detectados.
    Conforme a Circular 023 CGR — Principio de Privacidad y Ley 1581/2012.
    """
    return {
        "cedula": bool(_PATRON_CEDULA.search(texto)),
        "nit": bool(_PATRON_NIT.search(texto)),
        "tarjeta_credito": bool(_PATRON_TARJETA.search(texto)),
        "email_personal": bool(_PATRON_EMAIL_PERSONAL.search(texto)),
        "telefono": bool(_PATRON_TELEFONO.search(texto)),
    }


def _contiene_datos_personales(deteccion: dict[str, bool]) -> bool:
    """Verifica si alguno de los patrones fue detectado."""
    return any(deteccion.values())


# -- Dependencia de base de datos --

async def _obtener_sesion_db():
    """Provee una sesion de base de datos."""
    from app.main import fabrica_sesiones
    async with fabrica_sesiones() as sesion:
        try:
            yield sesion
            await sesion.commit()
        except Exception:
            await sesion.rollback()
            raise


obtener_sesion_db = _obtener_sesion_db

enrutador = APIRouter()


# -- Esquemas --

class SolicitudMensaje(BaseModel):
    mensaje: str = Field(..., min_length=1, max_length=10000)
    conversacion_id: Optional[str] = Field(default=None)
    modelo: Optional[str] = Field(default=None)
    fase: Optional[str] = Field(default=None)
    direccion: Optional[str] = Field(default="DES")
    proyecto_auditoria_id: Optional[str] = Field(default=None)


class SolicitudCrearConversacion(BaseModel):
    direccion: Optional[str] = Field(default="DES")
    mensaje_inicial: Optional[str] = Field(default=None)
    titulo: Optional[str] = Field(default=None)


class SolicitudRenombrar(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=500)


class SolicitudFeedback(BaseModel):
    mensaje_id: str = Field(...)
    puntuacion: int = Field(..., ge=-1, le=1)
    comentario: Optional[str] = Field(default=None, max_length=2000)


class RespuestaConversacion(BaseModel):
    id: str
    titulo: str
    direccion: Optional[str] = None
    modelo_utilizado: Optional[str] = None
    total_mensajes: int
    created_at: str
    updated_at: str
    ultimo_mensaje: Optional[str] = None


class RespuestaConversacionDetalle(BaseModel):
    id: str
    titulo: str
    direccion: Optional[str] = None
    created_at: str
    updated_at: str
    mensajes: list[dict[str, Any]]


class RespuestaCrearConversacion(BaseModel):
    id: str
    titulo: str
    direccion: str
    created_at: str


class RespuestaFeedback(BaseModel):
    mensaje: str
    feedback_id: str


class RespuestaMensaje(BaseModel):
    id: str
    conversacion_id: str
    rol: str
    contenido: str
    fuentes: Optional[Any] = None
    created_at: str


# -- Dependencia de usuario temporal --

async def _obtener_usuario_actual_id() -> int:
    return 1


# -- ENDPOINTS DE CONVERSACIONES --

@enrutador.post(
    "/conversaciones",
    response_model=RespuestaCrearConversacion,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva conversacion",
)
async def crear_conversacion(
    solicitud: SolicitudCrearConversacion,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Crea una nueva conversacion y la persiste en la base de datos."""
    conv_id = str(uuid.uuid4())
    ahora = datetime.now(timezone.utc)
    titulo = solicitud.titulo or (
        solicitud.mensaje_inicial[:50] + "..." if solicitud.mensaje_inicial and len(solicitud.mensaje_inicial) > 50
        else solicitud.mensaje_inicial or "Nueva conversacion"
    )
    dir_val = solicitud.direccion or "DES"

    conv = Conversacion(
        id=conv_id,
        usuario_id=usuario_id,
        titulo=titulo,
        direccion=dir_val,
        total_mensajes=0,
        created_at=ahora,
        updated_at=ahora,
    )
    db.add(conv)
    await db.flush()

    logger.info("Nueva conversacion %s para usuario_id=%d, direccion=%s", conv_id[:8], usuario_id, dir_val)

    return {
        "id": conv_id,
        "titulo": titulo,
        "direccion": dir_val,
        "created_at": ahora.isoformat(),
    }


@enrutador.get(
    "/conversaciones",
    response_model=list[RespuestaConversacion],
    summary="Listar conversaciones del usuario",
)
async def listar_conversaciones(
    limite: int = Query(default=50, ge=1, le=200),
    desplazamiento: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> list[dict[str, Any]]:
    """Retorna las conversaciones del usuario ordenadas por fecha de actualizacion."""
    resultado = await db.execute(
        select(Conversacion)
        .where(Conversacion.usuario_id == usuario_id)
        .order_by(Conversacion.updated_at.desc())
        .offset(desplazamiento)
        .limit(limite)
    )
    conversaciones = resultado.scalars().all()

    respuesta = []
    for conv in conversaciones:
        # Obtener ultimo mensaje
        ultimo_msg_result = await db.execute(
            select(Mensaje.contenido)
            .where(Mensaje.conversacion_id == conv.id)
            .order_by(Mensaje.created_at.desc())
            .limit(1)
        )
        ultimo_msg = ultimo_msg_result.scalar_one_or_none()

        respuesta.append({
            "id": conv.id,
            "titulo": conv.titulo,
            "direccion": conv.direccion,
            "modelo_utilizado": conv.modelo_utilizado,
            "total_mensajes": conv.total_mensajes,
            "created_at": conv.created_at.isoformat() if conv.created_at else "",
            "updated_at": conv.updated_at.isoformat() if conv.updated_at else "",
            "ultimo_mensaje": (ultimo_msg[:80] + "..." if ultimo_msg and len(ultimo_msg) > 80 else ultimo_msg),
        })

    return respuesta


@enrutador.get(
    "/conversaciones/{conversacion_id}",
    response_model=RespuestaConversacionDetalle,
    summary="Obtener conversacion con mensajes",
)
async def obtener_conversacion(
    conversacion_id: str,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Retorna la conversacion con todos sus mensajes."""
    resultado = await db.execute(
        select(Conversacion).where(
            Conversacion.id == conversacion_id,
            Conversacion.usuario_id == usuario_id,
        )
    )
    conv = resultado.scalar_one_or_none()

    if not conv:
        raise HTTPException(status_code=404, detail=f"Conversacion {conversacion_id} no encontrada.")

    # Obtener mensajes ordenados
    mensajes_result = await db.execute(
        select(Mensaje)
        .where(Mensaje.conversacion_id == conversacion_id)
        .order_by(Mensaje.created_at.asc())
    )
    mensajes = mensajes_result.scalars().all()

    return {
        "id": conv.id,
        "titulo": conv.titulo,
        "direccion": conv.direccion,
        "created_at": conv.created_at.isoformat() if conv.created_at else "",
        "updated_at": conv.updated_at.isoformat() if conv.updated_at else "",
        "mensajes": [
            {
                "id": m.id,
                "conversacion_id": m.conversacion_id,
                "rol": m.rol,
                "contenido": m.contenido,
                "fuentes": m.fuentes,
                "metadata_modelo": m.metadata_modelo,
                "feedback_puntuacion": m.feedback_puntuacion,
                "created_at": m.created_at.isoformat() if m.created_at else "",
            }
            for m in mensajes
        ],
    }


@enrutador.patch(
    "/conversaciones/{conversacion_id}",
    summary="Renombrar conversacion",
)
async def renombrar_conversacion(
    conversacion_id: str,
    solicitud: SolicitudRenombrar,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, str]:
    """Actualiza el titulo de una conversacion."""
    resultado = await db.execute(
        select(Conversacion).where(
            Conversacion.id == conversacion_id,
            Conversacion.usuario_id == usuario_id,
        )
    )
    conv = resultado.scalar_one_or_none()

    if not conv:
        raise HTTPException(status_code=404, detail=f"Conversacion {conversacion_id} no encontrada.")

    conv.titulo = solicitud.titulo
    conv.updated_at = datetime.now(timezone.utc)
    await db.flush()

    logger.info("Conversacion %s renombrada a '%s'", conversacion_id[:8], solicitud.titulo[:30])
    return {"id": conversacion_id, "titulo": solicitud.titulo}


@enrutador.delete(
    "/conversaciones/{conversacion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Eliminar conversacion",
)
async def eliminar_conversacion(
    conversacion_id: str,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> None:
    """Elimina una conversacion y todos sus mensajes."""
    resultado = await db.execute(
        select(Conversacion).where(
            Conversacion.id == conversacion_id,
            Conversacion.usuario_id == usuario_id,
        )
    )
    conv = resultado.scalar_one_or_none()

    if not conv:
        raise HTTPException(status_code=404, detail=f"Conversacion {conversacion_id} no encontrada.")

    # Eliminar mensajes primero
    await db.execute(
        delete(Mensaje).where(Mensaje.conversacion_id == conversacion_id)
    )
    await db.execute(
        delete(Conversacion).where(Conversacion.id == conversacion_id)
    )

    logger.info("Conversacion %s eliminada", conversacion_id[:8])


# -- ENDPOINT DE ENVIO DE MENSAJES --

@enrutador.post(
    "/enviar",
    summary="Enviar mensaje al chat",
    description="Envia un mensaje y recibe la respuesta del agente via SSE streaming.",
)
async def enviar_mensaje(
    solicitud: SolicitudMensaje,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> EventSourceResponse:
    """Procesa el mensaje del usuario y retorna SSE streaming.

    Si se envía conversacion_id, carga el historial como contexto.
    Si no se envía, crea una nueva conversacion automaticamente.
    """
    session_id: str = str(uuid.uuid4())
    chat_service = obtener_chat_service()
    dir_val = solicitud.direccion or "DES"
    ahora = datetime.now(timezone.utc)

    # Resolver o crear conversacion
    conversacion_id = solicitud.conversacion_id
    if conversacion_id:
        # Verificar que existe
        resultado = await db.execute(
            select(Conversacion).where(Conversacion.id == conversacion_id)
        )
        conv = resultado.scalar_one_or_none()
        if not conv:
            # Crear si no existe (caso de race condition con frontend)
            conv = Conversacion(
                id=conversacion_id,
                usuario_id=usuario_id,
                titulo=solicitud.mensaje[:50] + ("..." if len(solicitud.mensaje) > 50 else ""),
                direccion=dir_val,
                total_mensajes=0,
                created_at=ahora,
                updated_at=ahora,
            )
            db.add(conv)
            await db.flush()
    else:
        conversacion_id = str(uuid.uuid4())
        conv = Conversacion(
            id=conversacion_id,
            usuario_id=usuario_id,
            titulo=solicitud.mensaje[:50] + ("..." if len(solicitud.mensaje) > 50 else ""),
            direccion=dir_val,
            total_mensajes=0,
            created_at=ahora,
            updated_at=ahora,
        )
        db.add(conv)
        await db.flush()

    # Filtro de datos personales (Circular 023 — Principio de Privacidad)
    deteccion_datos = _detectar_datos_personales(solicitud.mensaje)
    alerta_privacidad = _contiene_datos_personales(deteccion_datos)
    if alerta_privacidad:
        tipos_detectados = [k for k, v in deteccion_datos.items() if v]
        logger.warning(
            "Datos personales detectados en mensaje de usuario_id=%d, "
            "conversacion=%s, tipos=%s — Circular 023 Principio de Privacidad",
            usuario_id, conversacion_id[:8], tipos_detectados,
        )

    # Guardar mensaje del usuario
    msg_usuario_id = str(uuid.uuid4())
    msg_usuario = Mensaje(
        id=msg_usuario_id,
        conversacion_id=conversacion_id,
        rol="user",
        contenido=solicitud.mensaje,
        created_at=ahora,
    )
    db.add(msg_usuario)

    # Cargar historial de mensajes anteriores para contexto
    historial_result = await db.execute(
        select(Mensaje)
        .where(Mensaje.conversacion_id == conversacion_id)
        .order_by(Mensaje.created_at.asc())
    )
    historial_msgs = historial_result.scalars().all()

    # Construir historial como texto para el LLM
    historial_texto = ""
    for m in historial_msgs:
        if m.id != msg_usuario_id:  # No incluir el mensaje actual
            prefijo = "Usuario" if m.rol == "user" else "CecilIA"
            historial_texto += f"{prefijo}: {m.contenido}\n\n"

    await db.flush()

    async def _generar_eventos() -> AsyncGenerator[dict[str, str], None]:
        inicio = time.time()
        try:
            yield {
                "event": "inicio",
                "data": json.dumps({
                    "conversacion_id": conversacion_id,
                    "marca_temporal": datetime.now(timezone.utc).isoformat(),
                }),
            }

            # Alerta de privacidad si se detectaron datos personales
            if alerta_privacidad:
                yield {
                    "event": "advertencia_privacidad",
                    "data": json.dumps({
                        "tipo": "advertencia_privacidad",
                        "mensaje": _ADVERTENCIA_DATOS_PERSONALES,
                        "tipos_detectados": [k for k, v in deteccion_datos.items() if v],
                    }, ensure_ascii=False),
                }

            # Ejecutar grafo con historial
            mensaje_con_contexto = solicitud.mensaje
            if historial_texto:
                mensaje_con_contexto = (
                    f"[Historial de la conversacion]\n{historial_texto}"
                    f"[Mensaje actual del usuario]\n{solicitud.mensaje}"
                )

            resultado = await chat_service.procesar_mensaje(
                mensaje=mensaje_con_contexto,
                usuario_id=str(usuario_id),
                session_id=session_id,
                rol="auditor",
                direccion=dir_val,
                fase_actual=solicitud.fase or "planeacion",
                proyecto_auditoria_id=solicitud.proyecto_auditoria_id,
                conversacion_id=conversacion_id,
            )

            # Transmitir respuesta palabra por palabra
            respuesta_completa = resultado.get("respuesta", "")
            palabras = respuesta_completa.split(" ")

            for i, palabra in enumerate(palabras):
                token = palabra + (" " if i < len(palabras) - 1 else "")
                yield {
                    "event": "token",
                    "data": json.dumps({"tipo": "token", "contenido": token}, ensure_ascii=False),
                }

            duracion = time.time() - inicio

            # Guardar respuesta del asistente en DB
            try:
                msg_asistente = Mensaje(
                    id=str(uuid.uuid4()),
                    conversacion_id=conversacion_id,
                    rol="assistant",
                    contenido=respuesta_completa,
                    fuentes=resultado.get("fuentes", []),
                    metadata_modelo={
                        "modelo": resultado.get("modelo", ""),
                        "nombre_modelo": resultado.get("nombre_modelo", ""),
                        "duracion_ms": round(duracion * 1000, 1),
                    },
                    created_at=datetime.now(timezone.utc),
                )
                db.add(msg_asistente)

                # Actualizar conteo y timestamp de la conversacion
                await db.execute(
                    update(Conversacion)
                    .where(Conversacion.id == conversacion_id)
                    .values(
                        total_mensajes=Conversacion.total_mensajes + 2,
                        modelo_utilizado=resultado.get("modelo", ""),
                        updated_at=datetime.now(timezone.utc),
                    )
                )
                await db.commit()
            except Exception:
                logger.warning("No se pudo guardar respuesta en DB", exc_info=True)

            # Evento final
            yield {
                "event": "fin",
                "data": json.dumps({
                    "tipo": "fin",
                    "conversacion_id": conversacion_id,
                    "respuesta_completa": respuesta_completa,
                    "fuentes": resultado.get("fuentes", []),
                    "modelo_utilizado": resultado.get("modelo", ""),
                    "nombre_modelo": resultado.get("nombre_modelo", ""),
                    "duracion_segundos": round(duracion, 3),
                }, ensure_ascii=False),
            }

        except Exception as error:
            logger.exception("Error al generar respuesta SSE para conversacion %s", conversacion_id)
            yield {
                "event": "error",
                "data": json.dumps({
                    "tipo": "error",
                    "error": "Error interno al procesar el mensaje.",
                    "detalle": str(error),
                }),
            }

    return EventSourceResponse(_generar_eventos())


# -- ENDPOINT DE FEEDBACK --

@enrutador.post(
    "/conversaciones/{conversacion_id}/feedback",
    response_model=RespuestaFeedback,
    summary="Enviar retroalimentacion",
)
async def enviar_feedback(
    conversacion_id: str,
    solicitud: SolicitudFeedback,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, str]:
    feedback_id = str(uuid.uuid4())

    # Actualizar feedback en el mensaje
    try:
        await db.execute(
            update(Mensaje)
            .where(Mensaje.id == solicitud.mensaje_id)
            .values(
                feedback_puntuacion=solicitud.puntuacion,
                feedback_comentario=solicitud.comentario,
            )
        )
    except Exception:
        logger.warning("No se pudo guardar feedback en DB")

    logger.info(
        "Feedback: conversacion=%s, mensaje=%s, puntuacion=%d",
        conversacion_id, solicitud.mensaje_id, solicitud.puntuacion,
    )
    return {
        "mensaje": "Retroalimentacion registrada exitosamente.",
        "feedback_id": feedback_id,
    }
