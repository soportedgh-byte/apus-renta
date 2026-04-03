"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: chat_service.py
Propósito: Servicio de orquestación de chat — recibe mensajes, ejecuta el grafo, streaming SSE
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from collections.abc import AsyncGenerator
from typing import Any, Optional

from langchain_core.messages import HumanMessage

from backend.app.agents.state import AuditState
from backend.app.agents.graph import ejecutar_grafo

logger = logging.getLogger("cecilia.services.chat")


class ChatService:
    """Servicio principal de chat que orquesta la interacción con el grafo LangGraph.

    Responsabilidades:
    - Recibir mensajes del usuario vía API.
    - Construir el estado inicial del grafo con contexto RAG.
    - Ejecutar el grafo de agentes.
    - Transmitir la respuesta vía SSE (Server-Sent Events).
    - Registrar trazabilidad de cada interacción.
    """

    def __init__(
        self,
        memoria_service: Any = None,
        trazabilidad_service: Any = None,
        rag_retriever: Any = None,
    ) -> None:
        """Inicializa el servicio de chat.

        Args:
            memoria_service: Servicio de memoria de sesión.
            trazabilidad_service: Servicio de trazabilidad.
            rag_retriever: Retriever RAG para contexto.
        """
        self._memoria = memoria_service
        self._trazabilidad = trazabilidad_service
        self._retriever = rag_retriever

    async def procesar_mensaje(
        self,
        mensaje: str,
        usuario_id: str,
        session_id: str,
        rol: str = "auditor",
        direccion: str = "DES",
        fase_actual: str = "planeacion",
        proyecto_auditoria_id: Optional[str] = None,
        modelo: str = "gpt-4o",
    ) -> dict[str, Any]:
        """Procesa un mensaje del usuario y retorna la respuesta completa.

        Args:
            mensaje: Texto del mensaje del usuario.
            usuario_id: Identificador del usuario.
            session_id: Identificador de la sesión.
            rol: Rol del usuario (auditor, supervisor, gerente, admin).
            direccion: Dirección (DES o DVF).
            fase_actual: Fase actual del proceso auditor.
            proyecto_auditoria_id: ID del proyecto de auditoría.
            modelo: Modelo LLM a utilizar.

        Returns:
            Diccionario con la respuesta, fuentes y metadatos.
        """
        inicio: float = time.time()
        interaccion_id: str = str(uuid.uuid4())

        logger.info(
            "Procesando mensaje [%s] usuario=%s sesion=%s fase=%s",
            interaccion_id[:8], usuario_id, session_id[:8], fase_actual,
        )

        # Recuperar historial de la sesión
        mensajes_previos: list = []
        if self._memoria:
            mensajes_previos = await self._memoria.obtener_mensajes(session_id)

        # Recuperar contexto RAG
        contexto_rag: list[str] = []
        if self._retriever:
            try:
                from backend.app.rag.retriever import buscar_similares
                resultados = await buscar_similares(
                    mensaje, coleccion=f"proyecto_{proyecto_auditoria_id}" if proyecto_auditoria_id else "general",
                    top_k=5,
                )
                contexto_rag = [r.contenido for r in resultados]
            except Exception:
                logger.exception("Error al recuperar contexto RAG.")

        # Construir estado
        mensajes_completos: list = mensajes_previos + [HumanMessage(content=mensaje)]

        state: AuditState = {
            "messages": mensajes_completos,
            "usuario_id": usuario_id,
            "rol": rol,
            "direccion": direccion,
            "fase_actual": fase_actual,
            "proyecto_auditoria_id": proyecto_auditoria_id,
            "contexto_rag": contexto_rag,
            "herramientas_disponibles": [],
            "respuesta_final": "",
            "fuentes": [],
            "modelo": modelo,
            "session_id": session_id,
        }

        # Ejecutar grafo
        resultado: AuditState = ejecutar_grafo(state)

        duracion: float = time.time() - inicio

        # Guardar en memoria
        if self._memoria:
            await self._memoria.guardar_mensaje(
                session_id=session_id,
                rol="user",
                contenido=mensaje,
            )
            await self._memoria.guardar_mensaje(
                session_id=session_id,
                rol="assistant",
                contenido=resultado.get("respuesta_final", ""),
            )

        # Registrar trazabilidad
        if self._trazabilidad:
            await self._trazabilidad.registrar_interaccion(
                interaccion_id=interaccion_id,
                usuario_id=usuario_id,
                session_id=session_id,
                mensaje_usuario=mensaje,
                respuesta=resultado.get("respuesta_final", ""),
                fuentes=resultado.get("fuentes", []),
                modelo=modelo,
                fase=fase_actual,
                duracion_segundos=duracion,
                tokens_entrada=0,  # TODO: obtener del callback
                tokens_salida=0,
            )

        respuesta: dict[str, Any] = {
            "interaccion_id": interaccion_id,
            "respuesta": resultado.get("respuesta_final", ""),
            "fuentes": resultado.get("fuentes", []),
            "fase_actual": fase_actual,
            "modelo": modelo,
            "duracion_segundos": round(duracion, 3),
        }

        logger.info(
            "Mensaje procesado [%s] en %.2fs — fuentes: %d",
            interaccion_id[:8], duracion, len(respuesta["fuentes"]),
        )

        return respuesta

    async def stream_respuesta(
        self,
        mensaje: str,
        usuario_id: str,
        session_id: str,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Transmite la respuesta como Server-Sent Events (SSE).

        Args:
            mensaje: Texto del mensaje del usuario.
            usuario_id: Identificador del usuario.
            session_id: Identificador de la sesión.
            **kwargs: Parámetros adicionales para procesar_mensaje.

        Yields:
            Líneas formateadas como SSE (data: ...).
        """
        try:
            # Evento de inicio
            yield f"data: {json.dumps({'tipo': 'inicio', 'session_id': session_id})}\n\n"

            resultado: dict[str, Any] = await self.procesar_mensaje(
                mensaje=mensaje,
                usuario_id=usuario_id,
                session_id=session_id,
                **kwargs,
            )

            # Simular streaming dividiendo la respuesta en chunks
            respuesta_completa: str = resultado.get("respuesta", "")
            chunk_size: int = 50  # caracteres por chunk

            for i in range(0, len(respuesta_completa), chunk_size):
                chunk: str = respuesta_completa[i:i + chunk_size]
                evento: dict[str, Any] = {
                    "tipo": "chunk",
                    "contenido": chunk,
                }
                yield f"data: {json.dumps(evento, ensure_ascii=False)}\n\n"

            # Evento de finalización
            evento_fin: dict[str, Any] = {
                "tipo": "fin",
                "interaccion_id": resultado.get("interaccion_id", ""),
                "fuentes": resultado.get("fuentes", []),
                "duracion_segundos": resultado.get("duracion_segundos", 0),
            }
            yield f"data: {json.dumps(evento_fin, ensure_ascii=False)}\n\n"

        except Exception as e:
            logger.exception("Error en streaming SSE.")
            evento_error: dict[str, str] = {
                "tipo": "error",
                "mensaje": "Error interno al procesar la consulta.",
            }
            yield f"data: {json.dumps(evento_error)}\n\n"
