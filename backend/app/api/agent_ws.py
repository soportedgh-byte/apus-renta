"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: app/api/agent_ws.py
Propósito: WebSocket para comunicación bidireccional con el agente de escritorio
           Electron — permite listado, lectura y observación de archivos locales
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

logger = logging.getLogger("cecilia.api.agent_ws")

enrutador = APIRouter()


# ── Gestor de conexiones WebSocket ───────────────────────────────────────────


class GestorConexionesAgente:
    """Gestiona las conexiones WebSocket activas de los agentes de escritorio.

    Mantiene un registro de agentes conectados indexados por
    su identificador de sesión, permitiendo enviar comandos y
    recibir respuestas de forma bidireccional.
    """

    def __init__(self) -> None:
        """Inicializa el gestor con un diccionario vacío de conexiones."""
        self._conexiones_activas: dict[str, WebSocket] = {}
        self._metadata_agentes: dict[str, dict[str, Any]] = {}

    @property
    def total_conectados(self) -> int:
        """Retorna el número de agentes conectados."""
        return len(self._conexiones_activas)

    async def conectar(self, websocket: WebSocket, agente_id: str) -> None:
        """Registra una nueva conexión de agente.

        Args:
            websocket: Conexión WebSocket del agente.
            agente_id: Identificador único del agente de escritorio.
        """
        await websocket.accept()
        self._conexiones_activas[agente_id] = websocket
        self._metadata_agentes[agente_id] = {
            "conectado_en": datetime.now(timezone.utc).isoformat(),
            "ultima_actividad": datetime.now(timezone.utc).isoformat(),
            "comandos_procesados": 0,
        }
        logger.info("Agente conectado: %s (total: %d)", agente_id, self.total_conectados)

    def desconectar(self, agente_id: str) -> None:
        """Desregistra una conexión de agente.

        Args:
            agente_id: Identificador del agente a desconectar.
        """
        self._conexiones_activas.pop(agente_id, None)
        self._metadata_agentes.pop(agente_id, None)
        logger.info("Agente desconectado: %s (total: %d)", agente_id, self.total_conectados)

    async def enviar_comando(self, agente_id: str, comando: dict[str, Any]) -> bool:
        """Envía un comando a un agente específico.

        Args:
            agente_id: Identificador del agente destino.
            comando: Diccionario con el comando a enviar.

        Returns:
            True si el comando se envió exitosamente, False en caso contrario.
        """
        websocket: Optional[WebSocket] = self._conexiones_activas.get(agente_id)
        if websocket is None:
            logger.warning("Agente %s no conectado — no se puede enviar comando.", agente_id)
            return False

        try:
            await websocket.send_json(comando)
            metadata: dict[str, Any] = self._metadata_agentes.get(agente_id, {})
            metadata["ultima_actividad"] = datetime.now(timezone.utc).isoformat()
            metadata["comandos_procesados"] = metadata.get("comandos_procesados", 0) + 1
            return True
        except Exception:
            logger.exception("Error al enviar comando a agente %s", agente_id)
            return False

    async def difundir(self, mensaje: dict[str, Any]) -> int:
        """Envía un mensaje a todos los agentes conectados.

        Args:
            mensaje: Diccionario con el mensaje a difundir.

        Returns:
            Número de agentes que recibieron el mensaje exitosamente.
        """
        exitosos: int = 0
        for agente_id in list(self._conexiones_activas.keys()):
            if await self.enviar_comando(agente_id, mensaje):
                exitosos += 1
        return exitosos

    def obtener_agentes_conectados(self) -> list[dict[str, Any]]:
        """Retorna la lista de agentes conectados con sus metadatos."""
        resultado: list[dict[str, Any]] = []
        for agente_id, metadata in self._metadata_agentes.items():
            resultado.append({
                "agente_id": agente_id,
                **metadata,
            })
        return resultado


# Instancia global del gestor de conexiones
gestor_conexiones = GestorConexionesAgente()


# ── Tipos de comandos soportados ─────────────────────────────────────────────

COMANDOS_VALIDOS: set[str] = {
    "listar_archivos",      # Listar archivos en un directorio local
    "leer_archivo",         # Leer el contenido de un archivo local
    "observar_archivo",     # Iniciar observación de cambios en un archivo
    "dejar_observar",       # Detener observación de un archivo
    "info_sistema",         # Información del sistema del agente
    "ping",                 # Verificación de conectividad
}


# ── Procesador de mensajes ───────────────────────────────────────────────────


async def _procesar_mensaje_agente(
    agente_id: str,
    websocket: WebSocket,
    mensaje_raw: str,
) -> None:
    """Procesa un mensaje recibido desde el agente de escritorio.

    Los mensajes pueden ser:
    - Respuestas a comandos enviados por el servidor.
    - Notificaciones de cambios en archivos observados.
    - Eventos del sistema del agente (errores, desconexión inminente).

    Args:
        agente_id: Identificador del agente que envía el mensaje.
        websocket: Conexión WebSocket del agente.
        mensaje_raw: Mensaje JSON sin procesar.
    """
    try:
        mensaje: dict[str, Any] = json.loads(mensaje_raw)
    except json.JSONDecodeError:
        logger.error("Agente %s envió mensaje no-JSON: %s", agente_id, mensaje_raw[:200])
        await websocket.send_json({
            "tipo": "error",
            "detalle": "Formato de mensaje inválido. Se espera JSON.",
        })
        return

    tipo_mensaje: str = mensaje.get("tipo", "desconocido")

    if tipo_mensaje == "respuesta_comando":
        # Respuesta a un comando previamente enviado
        comando_id: str = mensaje.get("comando_id", "")
        exito: bool = mensaje.get("exito", False)
        datos: Any = mensaje.get("datos")

        logger.info(
            "Agente %s respondió a comando %s: exito=%s",
            agente_id, comando_id, exito,
        )
        # TODO: Almacenar respuesta en caché o notificar al solicitante

    elif tipo_mensaje == "cambio_archivo":
        # Notificación de cambio en archivo observado
        ruta_archivo: str = mensaje.get("ruta", "")
        tipo_cambio: str = mensaje.get("tipo_cambio", "")  # creado | modificado | eliminado

        logger.info(
            "Agente %s notifica cambio en archivo: %s (%s)",
            agente_id, ruta_archivo, tipo_cambio,
        )
        # TODO: Procesar cambio de archivo (re-ingestión, actualización de índice)

    elif tipo_mensaje == "evento_sistema":
        # Evento del sistema del agente
        evento: str = mensaje.get("evento", "")
        detalle: str = mensaje.get("detalle", "")
        logger.info("Agente %s evento de sistema: %s — %s", agente_id, evento, detalle)

    elif tipo_mensaje == "pong":
        # Respuesta a ping de keep-alive
        logger.debug("Agente %s respondió pong.", agente_id)

    else:
        logger.warning("Agente %s envió tipo de mensaje desconocido: %s", agente_id, tipo_mensaje)
        await websocket.send_json({
            "tipo": "error",
            "detalle": f"Tipo de mensaje desconocido: {tipo_mensaje}",
        })


# ── Endpoint WebSocket ───────────────────────────────────────────────────────


@enrutador.websocket("/agente")
async def websocket_agente(websocket: WebSocket) -> None:
    """WebSocket para comunicación bidireccional con el agente de escritorio Electron.

    Protocolo de comunicación:
    1. El agente se conecta y envía un mensaje de autenticación.
    2. El servidor valida las credenciales y acepta la conexión.
    3. Comunicación bidireccional: el servidor envía comandos,
       el agente responde y notifica eventos.

    Formato de mensajes (JSON):
    - Del servidor al agente: {"tipo": "comando", "comando": "...", "comando_id": "...", "parametros": {...}}
    - Del agente al servidor: {"tipo": "respuesta_comando", "comando_id": "...", "exito": bool, "datos": ...}
    - Notificaciones: {"tipo": "cambio_archivo", "ruta": "...", "tipo_cambio": "..."}
    """

    agente_id: str = str(uuid.uuid4())

    # TODO: Validar token de autenticación del agente antes de aceptar
    # token = websocket.query_params.get("token")
    # if not _validar_token_agente(token):
    #     await websocket.close(code=4001, reason="Token inválido")
    #     return

    await gestor_conexiones.conectar(websocket, agente_id)

    # Enviar mensaje de bienvenida con ID asignado
    await websocket.send_json({
        "tipo": "bienvenida",
        "agente_id": agente_id,
        "version_servidor": "2.0.0",
        "comandos_soportados": sorted(COMANDOS_VALIDOS),
        "marca_temporal": datetime.now(timezone.utc).isoformat(),
    })

    try:
        while True:
            mensaje_raw: str = await websocket.receive_text()
            await _procesar_mensaje_agente(agente_id, websocket, mensaje_raw)

    except WebSocketDisconnect:
        logger.info("Agente %s se desconectó normalmente.", agente_id)
    except Exception:
        logger.exception("Error inesperado en WebSocket del agente %s.", agente_id)
    finally:
        gestor_conexiones.desconectar(agente_id)
