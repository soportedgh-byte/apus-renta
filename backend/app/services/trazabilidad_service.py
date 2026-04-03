"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: trazabilidad_service.py
Propósito: Servicio de trazabilidad — registra cada llamada al LLM con detalle completo
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

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("cecilia.services.trazabilidad")


class TrazabilidadService:
    """Servicio de trazabilidad para auditoría de uso del sistema.

    Registra cada interacción con el LLM para cumplir con los requisitos
    de transparencia y rendición de cuentas de la CGR. Cada registro incluye:
    - Quién preguntó (usuario, rol, dirección).
    - Qué preguntó (mensaje completo).
    - Qué respondió el sistema (respuesta completa).
    - Qué fuentes se citaron.
    - Qué modelo se usó.
    - Cuánto tiempo tomó.
    - Cuántos tokens se consumieron.
    """

    def __init__(self, db_session: Optional[AsyncSession] = None) -> None:
        """Inicializa el servicio de trazabilidad.

        Args:
            db_session: Sesión de base de datos asíncrona.
        """
        self._db = db_session
        # Buffer para registros cuando no hay BD disponible
        self._buffer: list[dict[str, Any]] = []

    async def registrar_interaccion(
        self,
        interaccion_id: str,
        usuario_id: str,
        session_id: str,
        mensaje_usuario: str,
        respuesta: str,
        fuentes: list[str],
        modelo: str,
        fase: str,
        duracion_segundos: float,
        tokens_entrada: int = 0,
        tokens_salida: int = 0,
        agente_utilizado: Optional[str] = None,
        herramientas_invocadas: Optional[list[str]] = None,
        metadata_extra: Optional[dict[str, Any]] = None,
    ) -> str:
        """Registra una interacción completa con el LLM.

        Args:
            interaccion_id: ID único de la interacción.
            usuario_id: ID del usuario.
            session_id: ID de la sesión.
            mensaje_usuario: Mensaje original del usuario.
            respuesta: Respuesta generada por el sistema.
            fuentes: Fuentes normativas citadas.
            modelo: Modelo LLM utilizado.
            fase: Fase del proceso auditor.
            duracion_segundos: Tiempo de procesamiento.
            tokens_entrada: Tokens de entrada consumidos.
            tokens_salida: Tokens de salida generados.
            agente_utilizado: Nombre del agente que procesó la consulta.
            herramientas_invocadas: Lista de herramientas usadas.
            metadata_extra: Metadatos adicionales.

        Returns:
            ID del registro de trazabilidad.
        """
        registro_id: str = str(uuid.uuid4())
        ahora: datetime = datetime.now(timezone.utc)

        registro: dict[str, Any] = {
            "id": registro_id,
            "interaccion_id": interaccion_id,
            "usuario_id": usuario_id,
            "session_id": session_id,
            "mensaje_usuario": mensaje_usuario,
            "respuesta": respuesta,
            "fuentes": fuentes,
            "modelo": modelo,
            "fase": fase,
            "agente_utilizado": agente_utilizado or "no_identificado",
            "herramientas_invocadas": herramientas_invocadas or [],
            "duracion_segundos": duracion_segundos,
            "tokens_entrada": tokens_entrada,
            "tokens_salida": tokens_salida,
            "tokens_total": tokens_entrada + tokens_salida,
            "timestamp": ahora.isoformat(),
            "metadata": metadata_extra or {},
        }

        if self._db:
            try:
                await self._db.execute(
                    text("""
                        INSERT INTO trazabilidad_llm
                            (id, interaccion_id, usuario_id, session_id,
                             mensaje_usuario, respuesta, fuentes, modelo,
                             fase, agente_utilizado, herramientas_invocadas,
                             duracion_segundos, tokens_entrada, tokens_salida,
                             tokens_total, timestamp, metadata)
                        VALUES
                            (:id, :interaccion_id, :usuario_id, :session_id,
                             :mensaje_usuario, :respuesta, :fuentes, :modelo,
                             :fase, :agente_utilizado, :herramientas_invocadas,
                             :duracion_segundos, :tokens_entrada, :tokens_salida,
                             :tokens_total, :timestamp, :metadata)
                    """),
                    {
                        "id": registro_id,
                        "interaccion_id": interaccion_id,
                        "usuario_id": usuario_id,
                        "session_id": session_id,
                        "mensaje_usuario": mensaje_usuario,
                        "respuesta": respuesta,
                        "fuentes": json.dumps(fuentes),
                        "modelo": modelo,
                        "fase": fase,
                        "agente_utilizado": registro["agente_utilizado"],
                        "herramientas_invocadas": json.dumps(registro["herramientas_invocadas"]),
                        "duracion_segundos": duracion_segundos,
                        "tokens_entrada": tokens_entrada,
                        "tokens_salida": tokens_salida,
                        "tokens_total": registro["tokens_total"],
                        "timestamp": ahora.isoformat(),
                        "metadata": json.dumps(registro["metadata"]),
                    },
                )
                await self._db.commit()

            except Exception:
                logger.exception("Error al registrar trazabilidad en BD.")
                self._buffer.append(registro)
        else:
            self._buffer.append(registro)

        logger.info(
            "Trazabilidad [%s]: usuario=%s modelo=%s fase=%s duracion=%.2fs tokens=%d",
            registro_id[:8], usuario_id, modelo, fase,
            duracion_segundos, registro["tokens_total"],
        )

        return registro_id

    async def consultar_interacciones(
        self,
        usuario_id: Optional[str] = None,
        session_id: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        modelo: Optional[str] = None,
        limite: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Consulta registros de trazabilidad con filtros.

        Args:
            usuario_id: Filtrar por usuario.
            session_id: Filtrar por sesión.
            fecha_desde: Fecha de inicio (ISO format).
            fecha_hasta: Fecha de fin (ISO format).
            modelo: Filtrar por modelo LLM.
            limite: Número máximo de resultados.
            offset: Desplazamiento para paginación.

        Returns:
            Lista de registros de trazabilidad.
        """
        if not self._db:
            # Devolver del buffer local
            return self._buffer[-limite:]

        condiciones: list[str] = []
        params: dict[str, Any] = {"limite": limite, "offset": offset}

        if usuario_id:
            condiciones.append("usuario_id = :usuario_id")
            params["usuario_id"] = usuario_id
        if session_id:
            condiciones.append("session_id = :session_id")
            params["session_id"] = session_id
        if fecha_desde:
            condiciones.append("timestamp >= :fecha_desde")
            params["fecha_desde"] = fecha_desde
        if fecha_hasta:
            condiciones.append("timestamp <= :fecha_hasta")
            params["fecha_hasta"] = fecha_hasta
        if modelo:
            condiciones.append("modelo = :modelo")
            params["modelo"] = modelo

        where: str = "WHERE " + " AND ".join(condiciones) if condiciones else ""

        result = await self._db.execute(
            text(f"""
                SELECT * FROM trazabilidad_llm
                {where}
                ORDER BY timestamp DESC
                LIMIT :limite OFFSET :offset
            """),
            params,
        )

        return [dict(row._mapping) for row in result.fetchall()]

    async def estadisticas_uso(
        self,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
    ) -> dict[str, Any]:
        """Genera estadísticas de uso del sistema.

        Args:
            fecha_desde: Fecha de inicio.
            fecha_hasta: Fecha de fin.

        Returns:
            Estadísticas agregadas de uso.
        """
        if not self._db:
            total: int = len(self._buffer)
            tokens_total: int = sum(r.get("tokens_total", 0) for r in self._buffer)
            return {
                "total_interacciones": total,
                "tokens_total": tokens_total,
                "fuente": "buffer_local",
            }

        condiciones: list[str] = []
        params: dict[str, Any] = {}

        if fecha_desde:
            condiciones.append("timestamp >= :fecha_desde")
            params["fecha_desde"] = fecha_desde
        if fecha_hasta:
            condiciones.append("timestamp <= :fecha_hasta")
            params["fecha_hasta"] = fecha_hasta

        where: str = "WHERE " + " AND ".join(condiciones) if condiciones else ""

        result = await self._db.execute(
            text(f"""
                SELECT
                    COUNT(*) as total_interacciones,
                    COUNT(DISTINCT usuario_id) as usuarios_unicos,
                    COUNT(DISTINCT session_id) as sesiones_unicas,
                    COALESCE(SUM(tokens_entrada), 0) as tokens_entrada_total,
                    COALESCE(SUM(tokens_salida), 0) as tokens_salida_total,
                    COALESCE(SUM(tokens_total), 0) as tokens_total,
                    COALESCE(AVG(duracion_segundos), 0) as duracion_promedio,
                    modelo,
                    fase
                FROM trazabilidad_llm
                {where}
                GROUP BY modelo, fase
            """),
            params,
        )

        filas = result.fetchall()
        estadisticas: dict[str, Any] = {
            "total_interacciones": 0,
            "usuarios_unicos": 0,
            "tokens_total": 0,
            "duracion_promedio": 0.0,
            "por_modelo": {},
            "por_fase": {},
        }

        for fila in filas:
            row = fila._mapping
            estadisticas["total_interacciones"] += row["total_interacciones"]
            estadisticas["tokens_total"] += row["tokens_total"]

            modelo_key: str = row["modelo"]
            if modelo_key not in estadisticas["por_modelo"]:
                estadisticas["por_modelo"][modelo_key] = {"interacciones": 0, "tokens": 0}
            estadisticas["por_modelo"][modelo_key]["interacciones"] += row["total_interacciones"]
            estadisticas["por_modelo"][modelo_key]["tokens"] += row["tokens_total"]

            fase_key: str = row["fase"]
            if fase_key not in estadisticas["por_fase"]:
                estadisticas["por_fase"][fase_key] = 0
            estadisticas["por_fase"][fase_key] += row["total_interacciones"]

        return estadisticas

    async def flush_buffer(self) -> int:
        """Persiste los registros del buffer local en la base de datos.

        Returns:
            Número de registros persistidos.
        """
        if not self._db or not self._buffer:
            return 0

        count: int = 0
        for registro in self._buffer:
            try:
                await self._db.execute(
                    text("""
                        INSERT INTO trazabilidad_llm
                            (id, interaccion_id, usuario_id, session_id,
                             mensaje_usuario, respuesta, fuentes, modelo,
                             fase, agente_utilizado, herramientas_invocadas,
                             duracion_segundos, tokens_entrada, tokens_salida,
                             tokens_total, timestamp, metadata)
                        VALUES
                            (:id, :interaccion_id, :usuario_id, :session_id,
                             :mensaje_usuario, :respuesta, :fuentes, :modelo,
                             :fase, :agente_utilizado, :herramientas_invocadas,
                             :duracion_segundos, :tokens_entrada, :tokens_salida,
                             :tokens_total, :timestamp, :metadata)
                    """),
                    {
                        **registro,
                        "fuentes": json.dumps(registro["fuentes"]),
                        "herramientas_invocadas": json.dumps(registro["herramientas_invocadas"]),
                        "metadata": json.dumps(registro["metadata"]),
                    },
                )
                count += 1
            except Exception:
                logger.exception("Error al persistir registro del buffer.")

        await self._db.commit()
        self._buffer.clear()

        logger.info("Buffer de trazabilidad persistido: %d registros", count)
        return count
