"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/models/alerta.py
Proposito: Modelo de alerta/notificacion del sistema
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Alerta(Base):
    """Modelo de alerta — alineado con migracion 001."""

    __tablename__ = "alertas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    usuario_destino_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    tipo: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="info | advertencia | error | accion_requerida",
    )
    titulo: Mapped[str] = mapped_column(String(300), nullable=False)
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    leida: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false", index=True,
    )
    url_accion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    modulo_origen: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    metadata_extra: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Alerta(id={self.id}, titulo='{self.titulo[:30]}...')>"
