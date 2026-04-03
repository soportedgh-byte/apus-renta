"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/models/hallazgo.py
Proposito: Modelo de hallazgo de auditoria con sus atributos normativos
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Hallazgo(Base):
    """Modelo de hallazgo — alineado con migracion 001."""

    __tablename__ = "hallazgos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    auditoria_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("auditorias.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    usuario_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True,
    )
    titulo: Mapped[str] = mapped_column(String(500), nullable=False)
    tipo: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True,
        comment="administrativo | fiscal | disciplinario | penal | fiscal_y_disciplinario",
    )
    estado: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default="borrador", index=True,
    )
    cuantia: Mapped[Optional[float]] = mapped_column(Numeric(precision=20, scale=2), nullable=True)
    condicion: Mapped[str] = mapped_column(Text, nullable=False)
    criterio: Mapped[str] = mapped_column(Text, nullable=False)
    causa: Mapped[str] = mapped_column(Text, nullable=False)
    efecto: Mapped[str] = mapped_column(Text, nullable=False)
    recomendacion: Mapped[str] = mapped_column(Text, nullable=False)
    evidencias: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_extra: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False,
    )

    # ── Relaciones ────────────────────────────────────────────────────────
    usuario: Mapped[Optional["Usuario"]] = relationship(  # type: ignore[name-defined]
        "Usuario", back_populates="hallazgos",
    )

    def __repr__(self) -> str:
        return f"<Hallazgo(id={self.id}, titulo='{self.titulo[:30]}...', tipo='{self.tipo}')>"
