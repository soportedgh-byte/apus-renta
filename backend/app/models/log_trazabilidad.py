"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/models/log_trazabilidad.py
Proposito: Modelo de log de trazabilidad para auditoria de uso del sistema IA
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class LogTrazabilidad(Base):
    """Modelo de log de trazabilidad.

    Registra cada interaccion con el sistema de IA para garantizar
    transparencia, auditabilidad y cumplimiento normativo. Cada registro
    incluye el contexto RAG recuperado, la respuesta generada, metricas
    de rendimiento y la fase del proceso auditor.
    """

    __tablename__ = "logs_trazabilidad"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Usuario que realizo la consulta",
    )
    rol: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="Rol del usuario al momento de la consulta",
    )
    direccion: Mapped[Optional[str]] = mapped_column(
        String(10), nullable=True,
        comment="Direccion misional del usuario (DES/DVF)",
    )
    session_id: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True,
        comment="Identificador unico de la sesion",
    )
    timestamp_inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        comment="Momento en que se inicio la consulta",
    )
    timestamp_fin: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        comment="Momento en que se completo la respuesta",
    )
    prompt_enviado: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Prompt completo enviado al LLM (incluye system prompt)",
    )
    contexto_rag_recuperado: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(
        JSONB, nullable=True, default=None,
        comment="Fragmentos de documentos recuperados por RAG",
    )
    respuesta_generada: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Respuesta completa generada por el LLM",
    )
    modelo_utilizado: Mapped[str] = mapped_column(
        String(100), nullable=False,
        comment="Identificador del modelo LLM utilizado",
    )
    tokens_input: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True,
        comment="Tokens de entrada consumidos",
    )
    tokens_output: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True,
        comment="Tokens de salida generados",
    )
    tiempo_total_ms: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True,
        comment="Tiempo total de procesamiento en milisegundos",
    )
    fase_proceso_auditor: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True,
        comment="Fase del proceso auditor en la que se realizo la consulta",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<LogTrazabilidad(id={self.id}, usuario_id={self.usuario_id}, "
            f"modelo='{self.modelo_utilizado}', tiempo_ms={self.tiempo_total_ms})>"
        )
