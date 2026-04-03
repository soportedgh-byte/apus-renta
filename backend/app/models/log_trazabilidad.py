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

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class LogTrazabilidad(Base):
    """Modelo de log de trazabilidad — alineado con migracion 001."""

    __tablename__ = "logs_trazabilidad"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    usuario_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True,
    )
    accion: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    modulo: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    detalle: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    modelo_utilizado: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    fuentes_consultadas: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    tokens_entrada: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    tokens_salida: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duracion_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ip_origen: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    codigo_respuesta: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    metadata_extra: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True,
    )

    def __repr__(self) -> str:
        return f"<LogTrazabilidad(id={self.id}, accion='{self.accion}', modulo='{self.modulo}')>"
