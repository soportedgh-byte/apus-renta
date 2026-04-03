"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: memoria_service.py
Propósito: Servicio de memoria de sesión — almacena y recupera contexto de conversación
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

logger = logging.getLogger("cecilia.services.memoria")

# Configuración por defecto
MAX_MENSAJES_SESION: int = 50  # Máximo de mensajes por sesión
MAX_TOKENS_CONTEXTO: int = 8000  # Aproximación de tokens para contexto
TTL_SESION_HORAS: int = 24  # Tiempo de vida de la sesión


class MemoriaService:
    """Servicio de memoria de sesión para mantener contexto conversacional.

    Almacena mensajes de la conversación asociados a una sesión y
    al proyecto de auditoría activo. Permite recuperar historial
    para proporcionar contexto al grafo LangGraph.
    """

    def __init__(
        self,
        redis_client: Any = None,
        db_session: Any = None,
    ) -> None:
        """Inicializa el servicio de memoria.

        Soporta Redis como almacén principal (rápido, con TTL)
        y PostgreSQL como respaldo persistente.

        Args:
            redis_client: Cliente Redis para almacenamiento rápido.
            db_session: Sesión de BD para almacenamiento persistente.
        """
        self._redis = redis_client
        self._db = db_session
        # Fallback en memoria si no hay Redis ni BD
        self._memoria_local: dict[str, list[dict[str, Any]]] = {}

    def _clave_redis(self, session_id: str) -> str:
        """Genera la clave Redis para una sesión."""
        return f"cecilia:memoria:{session_id}"

    async def guardar_mensaje(
        self,
        session_id: str,
        rol: str,
        contenido: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Guarda un mensaje en la memoria de sesión.

        Args:
            session_id: Identificador de la sesión.
            rol: Rol del mensaje ('user', 'assistant', 'system').
            contenido: Contenido textual del mensaje.
            metadata: Metadatos opcionales (fase, fuentes, etc.).
        """
        mensaje: dict[str, Any] = {
            "rol": rol,
            "contenido": contenido,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }

        if self._redis:
            try:
                clave: str = self._clave_redis(session_id)
                await self._redis.rpush(clave, json.dumps(mensaje, ensure_ascii=False))
                await self._redis.expire(clave, TTL_SESION_HORAS * 3600)

                # Mantener máximo de mensajes
                longitud: int = await self._redis.llen(clave)
                if longitud > MAX_MENSAJES_SESION:
                    await self._redis.ltrim(clave, longitud - MAX_MENSAJES_SESION, -1)

                return
            except Exception:
                logger.exception("Error al guardar en Redis; usando fallback local.")

        # Fallback a memoria local
        if session_id not in self._memoria_local:
            self._memoria_local[session_id] = []

        self._memoria_local[session_id].append(mensaje)

        # Recortar si excede el máximo
        if len(self._memoria_local[session_id]) > MAX_MENSAJES_SESION:
            self._memoria_local[session_id] = self._memoria_local[session_id][-MAX_MENSAJES_SESION:]

    async def obtener_mensajes(
        self,
        session_id: str,
        limite: int = MAX_MENSAJES_SESION,
    ) -> list[Any]:
        """Recupera el historial de mensajes de una sesión como objetos LangChain.

        Args:
            session_id: Identificador de la sesión.
            limite: Número máximo de mensajes a recuperar.

        Returns:
            Lista de mensajes en formato LangChain.
        """
        mensajes_raw: list[dict[str, Any]] = []

        if self._redis:
            try:
                clave: str = self._clave_redis(session_id)
                datos: list[bytes] = await self._redis.lrange(clave, -limite, -1)
                mensajes_raw = [json.loads(d) for d in datos]
            except Exception:
                logger.exception("Error al leer de Redis.")

        if not mensajes_raw:
            mensajes_raw = self._memoria_local.get(session_id, [])[-limite:]

        # Convertir a objetos LangChain
        mensajes_langchain: list[Any] = []
        for msg in mensajes_raw:
            rol: str = msg["rol"]
            contenido: str = msg["contenido"]

            if rol == "user":
                mensajes_langchain.append(HumanMessage(content=contenido))
            elif rol == "assistant":
                mensajes_langchain.append(AIMessage(content=contenido))
            elif rol == "system":
                mensajes_langchain.append(SystemMessage(content=contenido))

        return mensajes_langchain

    async def obtener_mensajes_raw(
        self,
        session_id: str,
        limite: int = MAX_MENSAJES_SESION,
    ) -> list[dict[str, Any]]:
        """Recupera mensajes en formato diccionario (para API).

        Args:
            session_id: Identificador de la sesión.
            limite: Número máximo de mensajes.

        Returns:
            Lista de mensajes como diccionarios.
        """
        if self._redis:
            try:
                clave: str = self._clave_redis(session_id)
                datos: list[bytes] = await self._redis.lrange(clave, -limite, -1)
                return [json.loads(d) for d in datos]
            except Exception:
                logger.exception("Error al leer mensajes raw de Redis.")

        return self._memoria_local.get(session_id, [])[-limite:]

    async def limpiar_sesion(self, session_id: str) -> None:
        """Elimina todos los mensajes de una sesión.

        Args:
            session_id: Identificador de la sesión.
        """
        if self._redis:
            try:
                await self._redis.delete(self._clave_redis(session_id))
            except Exception:
                logger.exception("Error al limpiar sesión en Redis.")

        self._memoria_local.pop(session_id, None)
        logger.info("Sesión limpiada: %s", session_id[:8])

    async def obtener_contexto_proyecto(
        self,
        session_id: str,
        proyecto_auditoria_id: str,
    ) -> dict[str, Any]:
        """Obtiene el contexto completo del proyecto para la sesión.

        Combina el historial de mensajes con metadatos del proyecto.

        Args:
            session_id: Identificador de la sesión.
            proyecto_auditoria_id: ID del proyecto.

        Returns:
            Contexto completo para el grafo.
        """
        mensajes: list[Any] = await self.obtener_mensajes(session_id)

        return {
            "session_id": session_id,
            "proyecto_auditoria_id": proyecto_auditoria_id,
            "mensajes_count": len(mensajes),
            "mensajes": mensajes,
        }

    async def contar_sesiones_activas(self) -> int:
        """Cuenta las sesiones activas en memoria.

        Returns:
            Número de sesiones activas.
        """
        if self._redis:
            try:
                claves: list[bytes] = await self._redis.keys("cecilia:memoria:*")
                return len(claves)
            except Exception:
                pass

        return len(self._memoria_local)
