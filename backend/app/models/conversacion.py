"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/models/conversacion.py
Proposito: Modelo de conversacion entre usuario y CecilIA
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Conversacion(Base):
    """Modelo de conversacion — alineado con migracion 001."""

    __tablename__ = "conversaciones"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    titulo: Mapped[str] = mapped_column(
        String(500), nullable=False, server_default="Nueva conversacion",
    )
    modelo_utilizado: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True,
    )
    fase: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True,
    )
    proyecto_auditoria_id: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True,
    )
    total_mensajes: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False,
    )

    # ── Relaciones ────────────────────────────────────────────────────────
    usuario: Mapped["Usuario"] = relationship(  # type: ignore[name-defined]
        "Usuario", back_populates="conversaciones",
    )
    mensajes: Mapped[list["Mensaje"]] = relationship(  # type: ignore[name-defined]
        "Mensaje", back_populates="conversacion", lazy="noload",
        order_by="Mensaje.created_at",
    )

    def __repr__(self) -> str:
        return f"<Conversacion(id={self.id}, titulo='{self.titulo[:30]}...')>"
