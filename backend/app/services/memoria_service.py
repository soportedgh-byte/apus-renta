"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/services/memoria_service.py
Proposito: Servicio de memoria de sesion persistente — almacena y recupera
           contexto de conversacion, genera resumenes con LLM, inyecta
           contexto de proyecto al inicio de sesion.
Sprint: 11
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("cecilia.services.memoria")

# Configuracion
MAX_MENSAJES_SESION: int = 50
MAX_TOKENS_CONTEXTO: int = 8000
TTL_SESION_HORAS: int = 24
MAX_PALABRAS_RESUMEN: int = 200
MAX_PALABRAS_RESUMEN_ACUMULATIVO: int = 1000


class MemoriaService:
    """Servicio de memoria de sesion con persistencia Redis + PostgreSQL.

    Funcionalidades Sprint 11:
    - Almacenamiento rapido en Redis con fallback a memoria local
    - Generacion de resumen de sesion via LLM (200 palabras, anonimizado)
    - Carga de contexto de proyecto al iniciar sesion
    - Guardado de estado al cerrar sesion o tras 30min de inactividad
    """

    def __init__(
        self,
        redis_client: Any = None,
        db_session: Any = None,
    ) -> None:
        self._redis = redis_client
        self._db = db_session
        self._memoria_local: dict[str, list[dict[str, Any]]] = {}

    def _clave_redis(self, session_id: str) -> str:
        return f"cecilia:memoria:{session_id}"

    # ── Guardar / Recuperar mensajes ────────────────────────────────────────

    async def guardar_mensaje(
        self,
        session_id: str,
        rol: str,
        contenido: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Guarda un mensaje en la memoria de sesion."""
        mensaje: dict[str, Any] = {
            "rol": rol,
            "contenido": contenido,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }

        if self._redis:
            try:
                clave = self._clave_redis(session_id)
                await self._redis.rpush(clave, json.dumps(mensaje, ensure_ascii=False))
                await self._redis.expire(clave, TTL_SESION_HORAS * 3600)
                longitud = await self._redis.llen(clave)
                if longitud > MAX_MENSAJES_SESION:
                    await self._redis.ltrim(clave, longitud - MAX_MENSAJES_SESION, -1)
                return
            except Exception:
                logger.exception("Error al guardar en Redis; usando fallback local.")

        if session_id not in self._memoria_local:
            self._memoria_local[session_id] = []
        self._memoria_local[session_id].append(mensaje)
        if len(self._memoria_local[session_id]) > MAX_MENSAJES_SESION:
            self._memoria_local[session_id] = self._memoria_local[session_id][-MAX_MENSAJES_SESION:]

    async def obtener_mensajes(
        self,
        session_id: str,
        limite: int = MAX_MENSAJES_SESION,
    ) -> list[Any]:
        """Recupera mensajes como objetos LangChain."""
        mensajes_raw = await self.obtener_mensajes_raw(session_id, limite)

        mensajes_langchain: list[Any] = []
        for msg in mensajes_raw:
            rol = msg["rol"]
            contenido = msg["contenido"]
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
        """Recupera mensajes en formato diccionario."""
        if self._redis:
            try:
                clave = self._clave_redis(session_id)
                datos: list[bytes] = await self._redis.lrange(clave, -limite, -1)
                return [json.loads(d) for d in datos]
            except Exception:
                logger.exception("Error al leer de Redis.")

        return self._memoria_local.get(session_id, [])[-limite:]

    async def limpiar_sesion(self, session_id: str) -> None:
        """Elimina todos los mensajes de una sesion."""
        if self._redis:
            try:
                await self._redis.delete(self._clave_redis(session_id))
            except Exception:
                logger.exception("Error al limpiar sesion en Redis.")
        self._memoria_local.pop(session_id, None)
        logger.info("Sesion limpiada: %s", session_id[:8])

    # ── Contexto de proyecto ────────────────────────────────────────────────

    async def cargar_contexto_proyecto(
        self,
        db: AsyncSession,
        proyecto_id: str,
    ) -> dict[str, Any]:
        """Carga el contexto completo de un proyecto para inyectar al LLM.

        Retorna un diccionario con toda la informacion relevante del proyecto
        que se inyecta como system message al inicio de la conversacion.
        """
        from app.models.proyecto_auditoria import ProyectoAuditoria

        result = await db.execute(
            select(ProyectoAuditoria).where(ProyectoAuditoria.id == proyecto_id)
        )
        proyecto = result.scalar_one_or_none()

        if not proyecto:
            return {"existe": False, "proyecto_id": proyecto_id}

        contexto: dict[str, Any] = {
            "existe": True,
            "proyecto_id": proyecto.id,
            "nombre_sesion": proyecto.nombre_sesion,
            "fase": proyecto.fase,
            "sujeto_control": proyecto.sujeto_control,
            "vigencia": proyecto.vigencia,
            "tipo_auditoria": proyecto.tipo_auditoria,
            "objetivo": proyecto.objetivo,
            "estado": proyecto.estado_json or {},
            "documentos_procesados": len(proyecto.documentos_procesados or []),
            "hallazgos_vinculados": len(proyecto.hallazgos_vinculados or []),
            "formatos_generados": len(proyecto.formatos_generados or []),
            "workspace": proyecto.configuracion_workspace or {},
        }

        # Inyectar resumen de sesiones anteriores
        if proyecto.resumen_sesiones:
            contexto["resumen_sesiones_anteriores"] = proyecto.resumen_sesiones
        if proyecto.ultima_sesion_resumen:
            contexto["ultima_sesion"] = proyecto.ultima_sesion_resumen

        return contexto

    def construir_system_prompt_proyecto(
        self, contexto: dict[str, Any]
    ) -> str:
        """Construye el system prompt con el contexto del proyecto."""
        if not contexto.get("existe"):
            return ""

        partes = [
            f"CONTEXTO DEL PROYECTO DE AUDITORIA:",
            f"- Sesion: {contexto.get('nombre_sesion', 'Sin nombre')}",
            f"- Fase actual: {contexto.get('fase', 'No definida')}",
        ]

        if contexto.get("sujeto_control"):
            partes.append(f"- Sujeto de control: {contexto['sujeto_control']}")
        if contexto.get("vigencia"):
            partes.append(f"- Vigencia: {contexto['vigencia']}")
        if contexto.get("tipo_auditoria"):
            partes.append(f"- Tipo: {contexto['tipo_auditoria']}")
        if contexto.get("objetivo"):
            partes.append(f"- Objetivo: {contexto['objetivo']}")

        partes.append(f"- Documentos procesados: {contexto.get('documentos_procesados', 0)}")
        partes.append(f"- Hallazgos vinculados: {contexto.get('hallazgos_vinculados', 0)}")
        partes.append(f"- Formatos generados: {contexto.get('formatos_generados', 0)}")

        if contexto.get("ultima_sesion"):
            partes.append(f"\nRESUMEN DE LA ULTIMA SESION:\n{contexto['ultima_sesion']}")

        if contexto.get("resumen_sesiones_anteriores"):
            partes.append(
                f"\nCONTEXTO ACUMULADO DE SESIONES ANTERIORES:\n"
                f"{contexto['resumen_sesiones_anteriores']}"
            )

        return "\n".join(partes)

    # ── Guardar estado de sesion ────────────────────────────────────────────

    async def guardar_estado_sesion(
        self,
        db: AsyncSession,
        proyecto_id: str,
        estado: Optional[dict[str, Any]] = None,
        resumen: Optional[str] = None,
    ) -> None:
        """Guarda el estado del proyecto al cerrar sesion o por inactividad."""
        from app.models.proyecto_auditoria import ProyectoAuditoria

        updates: dict[str, Any] = {
            "ultima_actividad": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        if estado is not None:
            updates["estado_json"] = estado
        if resumen is not None:
            updates["ultima_sesion_resumen"] = resumen

        await db.execute(
            update(ProyectoAuditoria)
            .where(ProyectoAuditoria.id == proyecto_id)
            .values(**updates)
        )
        await db.commit()
        logger.info("Estado de sesion guardado: proyecto=%s", proyecto_id[:8])

    # ── Generar resumen de sesion via LLM ───────────────────────────────────

    async def generar_resumen_sesion(
        self,
        session_id: str,
        llm: Any = None,
    ) -> str:
        """Genera un resumen de la sesion usando el LLM.

        El resumen es anonimizado (sin nombres propios de personas) y
        condensado en maximo 200 palabras. Si el LLM no esta disponible,
        genera un resumen heuristico basico.
        """
        mensajes_raw = await self.obtener_mensajes_raw(session_id)

        if not mensajes_raw:
            return "Sesion sin mensajes."

        # Construir texto de la conversacion (ultimos 20 mensajes)
        conversacion = []
        for msg in mensajes_raw[-20:]:
            rol = "Usuario" if msg["rol"] == "user" else "CecilIA"
            conversacion.append(f"{rol}: {msg['contenido'][:300]}")
        texto_conversacion = "\n".join(conversacion)

        # Intentar resumen con LLM
        if llm:
            try:
                prompt_resumen = (
                    "Resume la siguiente conversacion de auditoria en MAXIMO 200 palabras. "
                    "El resumen debe:\n"
                    "1. Identificar los temas principales discutidos\n"
                    "2. Listar decisiones o conclusiones alcanzadas\n"
                    "3. Mencionar documentos o normas referenciados\n"
                    "4. ANONIMIZAR: reemplazar nombres propios de personas con sus cargos\n"
                    "5. Ser en espanol\n\n"
                    f"CONVERSACION:\n{texto_conversacion}\n\n"
                    "RESUMEN ANONIMIZADO:"
                )
                respuesta = await llm.ainvoke(prompt_resumen)
                resumen = respuesta.content if hasattr(respuesta, 'content') else str(respuesta)
                return resumen[:2000]
            except Exception:
                logger.warning("No se pudo generar resumen con LLM; usando heuristico.")

        # Resumen heuristico (fallback)
        temas_usuario = [
            msg["contenido"][:100]
            for msg in mensajes_raw
            if msg["rol"] == "user"
        ]
        total = len(mensajes_raw)
        resumen = (
            f"Sesion con {total} mensajes. "
            f"Consultas del usuario: {len(temas_usuario)}. "
        )
        if temas_usuario:
            resumen += "Temas principales: " + "; ".join(temas_usuario[:5])

        return resumen[:2000]

    async def acumular_resumen(
        self,
        db: AsyncSession,
        proyecto_id: str,
        nuevo_resumen: str,
    ) -> None:
        """Acumula el resumen de la sesion actual al resumen global del proyecto."""
        from app.models.proyecto_auditoria import ProyectoAuditoria

        result = await db.execute(
            select(ProyectoAuditoria.resumen_sesiones)
            .where(ProyectoAuditoria.id == proyecto_id)
        )
        resumen_actual = result.scalar_one_or_none() or ""

        # Acumular con separador de fecha
        ahora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        nuevo_acumulado = f"{resumen_actual}\n\n[{ahora}] {nuevo_resumen}".strip()

        # Truncar si excede el maximo
        palabras = nuevo_acumulado.split()
        if len(palabras) > MAX_PALABRAS_RESUMEN_ACUMULATIVO:
            # Mantener las sesiones mas recientes
            nuevo_acumulado = " ".join(palabras[-MAX_PALABRAS_RESUMEN_ACUMULATIVO:])

        await db.execute(
            update(ProyectoAuditoria)
            .where(ProyectoAuditoria.id == proyecto_id)
            .values(
                resumen_sesiones=nuevo_acumulado,
                ultima_sesion_resumen=nuevo_resumen,
                ultima_actividad=datetime.now(timezone.utc),
            )
        )
        await db.commit()
        logger.info("Resumen acumulado en proyecto=%s", proyecto_id[:8])

    # ── Obtener contexto completo (para inyeccion al grafo) ─────────────────

    async def obtener_contexto_proyecto(
        self,
        session_id: str,
        proyecto_auditoria_id: str,
    ) -> dict[str, Any]:
        """Obtiene contexto completo: historial + metadatos del proyecto."""
        mensajes = await self.obtener_mensajes(session_id)

        return {
            "session_id": session_id,
            "proyecto_auditoria_id": proyecto_auditoria_id,
            "mensajes_count": len(mensajes),
            "mensajes": mensajes,
        }

    async def contar_sesiones_activas(self) -> int:
        if self._redis:
            try:
                claves: list[bytes] = await self._redis.keys("cecilia:memoria:*")
                return len(claves)
            except Exception:
                pass
        return len(self._memoria_local)
