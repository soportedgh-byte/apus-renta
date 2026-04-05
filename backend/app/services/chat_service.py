"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: chat_service.py
Proposito: Servicio de orquestacion de chat — ejecuta el grafo y streaming SSE
Sprint: 2
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from collections.abc import AsyncGenerator
from typing import Any, Optional

from langchain_core.messages import AIMessage, HumanMessage

from app.agents.state import AuditState
from app.agents.graph import ejecutar_grafo
from app.llm import obtener_llm, invocar_con_fallback, info_modelo_activo

logger = logging.getLogger("cecilia.services.chat")


async def _recuperar_contexto_rag(consulta: str, colecciones: list[str] | None = None, top_k: int = 5) -> tuple[list[dict], list[dict]]:
    """Recupera contexto RAG y genera citas formateadas.

    Retorna (contexto_rag, fuentes) donde:
      - contexto_rag: fragmentos crudos para inyectar en el prompt
      - fuentes: citas formateadas para mostrar al usuario (CitaFuente)
    """
    try:
        from app.main import fabrica_sesiones
        from app.rag.retriever import buscar_similares

        async with fabrica_sesiones() as db:
            resultados = await buscar_similares(
                consulta=consulta,
                db=db,
                colecciones=colecciones,
                top_k=top_k,
                umbral_similitud=0.35,
            )

        contexto_rag = []
        fuentes = []
        for r in resultados:
            contexto_rag.append({
                "contenido": r.contenido,
                "coleccion": r.coleccion,
                "documento": r.fuente,
                "pagina": r.pagina,
                "score": r.score,
            })
            fuentes.append({
                "documento": r.fuente,
                "pagina": r.pagina,
                "seccion": r.metadata.get("seccion", None),
                "fragmento": r.contenido[:200] + ("..." if len(r.contenido) > 200 else ""),
                "confianza": round(r.score, 3),
                "coleccion": r.coleccion,
            })

        return contexto_rag, fuentes

    except Exception:
        logger.debug("RAG no disponible, continuando sin contexto", exc_info=True)
        return [], []


class ChatService:
    """Servicio principal de chat que orquesta el grafo LangGraph."""

    async def procesar_mensaje(
        self,
        mensaje: str,
        usuario_id: str,
        session_id: str,
        rol: str = "auditor",
        direccion: str = "DES",
        fase_actual: str = "planeacion",
        proyecto_auditoria_id: Optional[str] = None,
        conversacion_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Procesa un mensaje y retorna la respuesta completa."""
        inicio: float = time.time()
        interaccion_id: str = str(uuid.uuid4())

        logger.info(
            "Procesando mensaje [%s] usuario=%s sesion=%s fase=%s",
            interaccion_id[:8], usuario_id, session_id[:8], fase_actual,
        )

        # Recuperar contexto RAG
        contexto_rag, fuentes_rag = await _recuperar_contexto_rag(mensaje, top_k=5)

        # Construir estado
        state: AuditState = {
            "messages": [HumanMessage(content=mensaje)],
            "usuario_id": usuario_id,
            "rol": rol,
            "direccion": direccion,
            "fase_actual": fase_actual,
            "proyecto_auditoria_id": proyecto_auditoria_id,
            "contexto_rag": contexto_rag,
            "herramientas_disponibles": [],
            "respuesta_final": "",
            "fuentes": fuentes_rag,
            "modelo": "",
            "session_id": session_id,
        }

        # Ejecutar grafo
        resultado: AuditState = ejecutar_grafo(state)

        duracion: float = time.time() - inicio
        info_modelo = info_modelo_activo()

        # Combinar fuentes del RAG + fuentes generadas por el grafo
        fuentes_finales = fuentes_rag + [f for f in resultado.get("fuentes", []) if f not in fuentes_rag]

        respuesta: dict[str, Any] = {
            "interaccion_id": interaccion_id,
            "conversacion_id": conversacion_id or session_id,
            "respuesta": resultado.get("respuesta_final", ""),
            "fuentes": fuentes_finales,
            "fase_actual": fase_actual,
            "modelo": info_modelo.get("modelo", ""),
            "nombre_modelo": info_modelo.get("nombre_display", ""),
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
        conversacion_id: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Transmite la respuesta como SSE.

        Ejecuta el grafo completo y luego transmite la respuesta
        token por token para simular streaming real.
        """
        try:
            # Evento de inicio
            yield f"data: {json.dumps({'tipo': 'inicio', 'conversacion_id': conversacion_id or session_id})}\n\n"

            resultado: dict[str, Any] = await self.procesar_mensaje(
                mensaje=mensaje,
                usuario_id=usuario_id,
                session_id=session_id,
                conversacion_id=conversacion_id,
                **kwargs,
            )

            # Transmitir la respuesta en chunks
            respuesta_completa: str = resultado.get("respuesta", "")
            palabras = respuesta_completa.split(" ")

            for i, palabra in enumerate(palabras):
                token = palabra + (" " if i < len(palabras) - 1 else "")
                evento: dict[str, Any] = {
                    "tipo": "token",
                    "contenido": token,
                }
                yield f"data: {json.dumps(evento, ensure_ascii=False)}\n\n"

            # Evento de finalizacion
            evento_fin: dict[str, Any] = {
                "tipo": "fin",
                "interaccion_id": resultado.get("interaccion_id", ""),
                "conversacion_id": resultado.get("conversacion_id", ""),
                "fuentes": resultado.get("fuentes", []),
                "modelo": resultado.get("modelo", ""),
                "nombre_modelo": resultado.get("nombre_modelo", ""),
                "duracion_segundos": resultado.get("duracion_segundos", 0),
            }
            yield f"data: {json.dumps(evento_fin, ensure_ascii=False)}\n\n"

        except Exception as e:
            logger.exception("Error en streaming SSE.")
            evento_error: dict[str, str] = {
                "tipo": "error",
                "mensaje": f"Error interno al procesar la consulta: {str(e)}",
            }
            yield f"data: {json.dumps(evento_error)}\n\n"


# Singleton
_chat_service: ChatService | None = None


def obtener_chat_service() -> ChatService:
    """Retorna singleton del ChatService."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
