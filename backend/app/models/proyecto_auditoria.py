"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/models/proyecto_auditoria.py
Proposito: Modelo de proyecto de auditoria — vincula usuario con auditoria
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ProyectoAuditoria(Base):
    """Modelo de proyecto de auditoria — alineado con migracion 001."""

    __tablename__ = "proyectos_auditoria"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    auditoria_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("auditorias.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    usuario_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True,
    )
    nombre_sesion: Mapped[str] = mapped_column(String(300), nullable=False)
    fase: Mapped[str] = mapped_column(String(50), nullable=False)
    objetivo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="activo",
    )
    contexto: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False,
    )

    # ── Relaciones ────────────────────────────────────────────────────────
    auditoria: Mapped["Auditoria"] = relationship(  # type: ignore[name-defined]
        "Auditoria", back_populates="proyectos",
    )

    def __repr__(self) -> str:
        return f"<ProyectoAuditoria(id={self.id}, fase='{self.fase}')>"
