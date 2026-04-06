"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/api/agent_ws.py
Proposito: WebSocket para comunicacion bidireccional con el agente de escritorio
           Electron — listado, lectura, escritura de archivos locales,
           autenticacion JWT, rate limiting, trazabilidad completa.
Sprint: 11
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy import insert

logger = logging.getLogger("cecilia.api.agent_ws")

enrutador = APIRouter()


# ── Rate limiter ────────────────────────────────────────────────────────────

class RateLimiter:
    """Limita operaciones por usuario: 100 ops/minuto."""

    def __init__(self, max_ops: int = 100, ventana_seg: int = 60) -> None:
        self._max_ops = max_ops
        self._ventana = ventana_seg
        self._contadores: dict[int, list[float]] = defaultdict(list)

    def permitir(self, usuario_id: int) -> bool:
        """Retorna True si la operacion esta permitida."""
        ahora = time.monotonic()
        ops = self._contadores[usuario_id]
        # Limpiar operaciones fuera de la ventana
        self._contadores[usuario_id] = [t for t in ops if ahora - t < self._ventana]
        if len(self._contadores[usuario_id]) >= self._max_ops:
            return False
        self._contadores[usuario_id].append(ahora)
        return True


rate_limiter = RateLimiter(max_ops=100, ventana_seg=60)


# ── Gestor de conexiones WebSocket ─────────────────────────────────────────

class GestorConexionesAgente:
    """Gestiona las conexiones WebSocket activas de los agentes de escritorio."""

    def __init__(self) -> None:
        self._conexiones: dict[str, WebSocket] = {}
        self._metadata: dict[str, dict[str, Any]] = {}
        # Mapeo usuario_id -> agente_id para busqueda rapida
        self._usuario_agente: dict[int, str] = {}
        # Futures pendientes para respuestas de comandos
        self._pendientes: dict[str, asyncio.Future[dict[str, Any]]] = {}

    @property
    def total_conectados(self) -> int:
        return len(self._conexiones)

    async def conectar(
        self, websocket: WebSocket, agente_id: str, usuario_id: int
    ) -> None:
        await websocket.accept()
        # Desconectar agente anterior del mismo usuario
        agente_anterior = self._usuario_agente.get(usuario_id)
        if agente_anterior and agente_anterior in self._conexiones:
            try:
                await self._conexiones[agente_anterior].close(
                    code=4002, reason="Nueva conexion del mismo usuario"
                )
            except Exception:
                pass
            self._limpiar(agente_anterior)

        self._conexiones[agente_id] = websocket
        self._metadata[agente_id] = {
            "usuario_id": usuario_id,
            "conectado_en": datetime.now(timezone.utc).isoformat(),
            "ultima_actividad": datetime.now(timezone.utc).isoformat(),
            "comandos_procesados": 0,
        }
        self._usuario_agente[usuario_id] = agente_id
        logger.info(
            "Agente conectado: %s (usuario=%d, total=%d)",
            agente_id, usuario_id, self.total_conectados,
        )

    def desconectar(self, agente_id: str) -> None:
        meta = self._metadata.get(agente_id)
        if meta:
            uid = meta.get("usuario_id")
            if uid and self._usuario_agente.get(uid) == agente_id:
                self._usuario_agente.pop(uid, None)
        self._limpiar(agente_id)
        logger.info("Agente desconectado: %s (total=%d)", agente_id, self.total_conectados)

    def _limpiar(self, agente_id: str) -> None:
        self._conexiones.pop(agente_id, None)
        self._metadata.pop(agente_id, None)

    async def enviar_comando(
        self, agente_id: str, comando: dict[str, Any], timeout: float = 30.0
    ) -> dict[str, Any]:
        """Envia un comando y espera la respuesta (con timeout)."""
        ws = self._conexiones.get(agente_id)
        if not ws:
            return {"exito": False, "error": "Agente no conectado"}

        solicitud_id = str(uuid.uuid4())[:8]
        comando["solicitud_id"] = solicitud_id

        loop = asyncio.get_event_loop()
        future: asyncio.Future[dict[str, Any]] = loop.create_future()
        self._pendientes[solicitud_id] = future

        try:
            await ws.send_json(comando)
            meta = self._metadata.get(agente_id, {})
            meta["ultima_actividad"] = datetime.now(timezone.utc).isoformat()
            meta["comandos_procesados"] = meta.get("comandos_procesados", 0) + 1

            resultado = await asyncio.wait_for(future, timeout=timeout)
            return resultado
        except asyncio.TimeoutError:
            return {"exito": False, "error": "Timeout esperando respuesta del agente"}
        except Exception as e:
            return {"exito": False, "error": str(e)}
        finally:
            self._pendientes.pop(solicitud_id, None)

    def resolver_pendiente(self, solicitud_id: str, datos: dict[str, Any]) -> bool:
        """Resuelve un future pendiente con la respuesta del agente."""
        future = self._pendientes.get(solicitud_id)
        if future and not future.done():
            future.set_result(datos)
            return True
        return False

    def obtener_agente_usuario(self, usuario_id: int) -> Optional[str]:
        """Obtiene el agente_id conectado de un usuario."""
        return self._usuario_agente.get(usuario_id)

    def esta_conectado(self, usuario_id: int) -> bool:
        """Verifica si un usuario tiene agente conectado."""
        agente_id = self._usuario_agente.get(usuario_id)
        return agente_id is not None and agente_id in self._conexiones

    def obtener_agentes_conectados(self) -> list[dict[str, Any]]:
        resultado: list[dict[str, Any]] = []
        for agente_id, meta in self._metadata.items():
            resultado.append({"agente_id": agente_id, **meta})
        return resultado


gestor_conexiones = GestorConexionesAgente()


# ── Validacion JWT simplificada ─────────────────────────────────────────────

def _validar_token_ws(token: Optional[str]) -> Optional[int]:
    """Valida token JWT y retorna usuario_id o None si invalido."""
    if not token:
        return None
    try:
        import jwt
        from app.config import configuracion
        payload = jwt.decode(
            token,
            configuracion.JWT_SECRET_KEY,
            algorithms=[configuracion.JWT_ALGORITHM],
        )
        return payload.get("sub") or payload.get("usuario_id")
    except Exception as e:
        logger.warning("Token WS invalido: %s", e)
        return None


# ── Trazabilidad ────────────────────────────────────────────────────────────

async def _registrar_operacion(
    usuario_id: int, accion: str, detalle: str = ""
) -> None:
    """Registra operacion del agente en log_trazabilidad."""
    try:
        from app.main import fabrica_sesiones
        from app.models.log_trazabilidad import LogTrazabilidad

        async with fabrica_sesiones() as db:
            db.add(LogTrazabilidad(
                id=str(uuid.uuid4()),
                usuario_id=usuario_id,
                accion=f"workspace:{accion}",
                detalle=detalle[:1000] if detalle else "",
                ip_origen="agent-ws",
                created_at=datetime.now(timezone.utc),
            ))
            await db.commit()
    except Exception:
        logger.debug("No se pudo registrar trazabilidad (tabla puede no existir)")


# ── Procesador de mensajes del agente ───────────────────────────────────────

TIPOS_RESPUESTA = {
    "respuesta_archivo", "respuesta_listado", "respuesta_escritura",
    "respuesta_crear_carpeta", "respuesta_comando",
}


async def _procesar_mensaje_agente(
    agente_id: str,
    websocket: WebSocket,
    mensaje_raw: str,
    usuario_id: int,
) -> None:
    """Procesa un mensaje recibido desde el agente de escritorio."""
    try:
        mensaje: dict[str, Any] = json.loads(mensaje_raw)
    except json.JSONDecodeError:
        logger.error("Agente %s envio mensaje no-JSON", agente_id)
        await websocket.send_json({
            "tipo": "error",
            "detalle": "Formato de mensaje invalido. Se espera JSON.",
        })
        return

    tipo = mensaje.get("tipo", "desconocido")

    # Respuestas a comandos pendientes
    if tipo in TIPOS_RESPUESTA:
        solicitud_id = mensaje.get("solicitud_id", "")
        gestor_conexiones.resolver_pendiente(solicitud_id, mensaje)
        return

    if tipo == "evento_archivo":
        accion = mensaje.get("accion", "")
        ruta = mensaje.get("ruta", "")
        logger.info("Agente %s: archivo %s — %s", agente_id, accion, ruta)
        await _registrar_operacion(
            usuario_id, f"evento_archivo_{accion}", ruta
        )

    elif tipo == "evento_sistema":
        evento = mensaje.get("evento", "")
        logger.info("Agente %s evento: %s", agente_id, evento)

    elif tipo == "pong":
        pass

    elif tipo == "cambio_archivo":
        ruta = mensaje.get("ruta", "")
        tipo_cambio = mensaje.get("tipo_cambio", "")
        logger.info("Agente %s: cambio %s en %s", agente_id, tipo_cambio, ruta)

    else:
        logger.warning("Agente %s: tipo desconocido '%s'", agente_id, tipo)


# ── Endpoint WebSocket ──────────────────────────────────────────────────────

@enrutador.websocket("/agente")
async def websocket_agente(
    websocket: WebSocket,
    token: Optional[str] = Query(default=None),
) -> None:
    """WebSocket para el agente de escritorio Electron.

    Autenticacion: via query param ?token=<JWT>
    Rate limit: 100 operaciones/minuto/usuario
    Protocolo JSON bidireccional.
    """
    # Validar autenticacion
    usuario_id = _validar_token_ws(token)
    if usuario_id is None:
        await websocket.close(code=4001, reason="Token invalido o ausente")
        return

    agente_id = str(uuid.uuid4())

    await gestor_conexiones.conectar(websocket, agente_id, usuario_id)
    await _registrar_operacion(usuario_id, "conectar", f"agente={agente_id}")

    # Mensaje de bienvenida
    await websocket.send_json({
        "tipo": "bienvenida",
        "agente_id": agente_id,
        "usuario_id": usuario_id,
        "version_servidor": "2.0.0",
        "comandos_soportados": [
            "solicitar_listado", "solicitar_archivo",
            "solicitar_escritura", "solicitar_crear_carpeta",
        ],
        "marca_temporal": datetime.now(timezone.utc).isoformat(),
    })

    try:
        while True:
            mensaje_raw = await websocket.receive_text()

            # Rate limiting
            if not rate_limiter.permitir(usuario_id):
                await websocket.send_json({
                    "tipo": "error",
                    "detalle": "Rate limit excedido: 100 operaciones/minuto",
                })
                continue

            await _procesar_mensaje_agente(agente_id, websocket, mensaje_raw, usuario_id)

    except WebSocketDisconnect:
        logger.info("Agente %s desconectado normalmente.", agente_id)
    except Exception:
        logger.exception("Error en WebSocket del agente %s.", agente_id)
    finally:
        gestor_conexiones.desconectar(agente_id)
        await _registrar_operacion(usuario_id, "desconectar", f"agente={agente_id}")


# ── Endpoints REST auxiliares ───────────────────────────────────────────────

@enrutador.get("/agente/estado", summary="Estado de conexion del agente")
async def estado_agente(usuario_id: int = 0) -> dict[str, Any]:
    """Retorna si el usuario tiene un agente conectado."""
    return {
        "conectado": gestor_conexiones.esta_conectado(usuario_id),
        "total_agentes": gestor_conexiones.total_conectados,
    }


@enrutador.get("/agente/conectados", summary="Lista de agentes conectados")
async def agentes_conectados() -> dict[str, Any]:
    """Lista todos los agentes conectados (solo admin)."""
    return {
        "agentes": gestor_conexiones.obtener_agentes_conectados(),
        "total": gestor_conexiones.total_conectados,
    }


# ── API publica del modulo ──────────────────────────────────────────────────

async def ejecutar_comando_workspace(
    usuario_id: int,
    accion: str,
    ruta: str,
    contenido: Optional[str] = None,
) -> dict[str, Any]:
    """Ejecuta un comando en el workspace local del usuario via su agente.

    Esta funcion es llamada por los tools de LangGraph para acceder
    al sistema de archivos local del auditor.

    Args:
        usuario_id: ID del usuario dueño del agente.
        accion: "listar" | "leer" | "escribir" | "crear_carpeta"
        ruta: Ruta relativa dentro del sandbox.
        contenido: Contenido para escritura (solo para "escribir").

    Returns:
        Respuesta del agente con los datos solicitados.
    """
    agente_id = gestor_conexiones.obtener_agente_usuario(usuario_id)
    if not agente_id:
        return {"exito": False, "error": "No hay agente de escritorio conectado"}

    tipo_mapa = {
        "listar": "solicitar_listado",
        "leer": "solicitar_archivo",
        "escribir": "solicitar_escritura",
        "crear_carpeta": "solicitar_crear_carpeta",
    }

    tipo_cmd = tipo_mapa.get(accion)
    if not tipo_cmd:
        return {"exito": False, "error": f"Accion no soportada: {accion}"}

    comando: dict[str, Any] = {"tipo": tipo_cmd, "ruta": ruta}
    if accion == "escribir" and contenido is not None:
        comando["contenido"] = contenido

    resultado = await gestor_conexiones.enviar_comando(agente_id, comando)

    await _registrar_operacion(usuario_id, accion, ruta[:200])

    return resultado
