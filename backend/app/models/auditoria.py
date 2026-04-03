"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/models/auditoria.py
Proposito: Modelo de proceso de auditoria (nivel macro)
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


class Auditoria(Base):
    """Modelo de auditoria — alineado con migracion 001."""

    __tablename__ = "auditorias"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(500), nullable=False)
    entidad_auditada: Mapped[str] = mapped_column(String(500), nullable=False)
    tipo_auditoria: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="financiera | cumplimiento | desempeno | especial | integral",
    )
    vigencia: Mapped[str] = mapped_column(String(20), nullable=False)
    direccion: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    fase_actual: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="preplaneacion", index=True,
    )
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fecha_inicio_planeada: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    fecha_fin_planeada: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    fecha_inicio_real: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    fecha_fin_real: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    usuario_creador_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True,
    )
    metadata_extra: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False,
    )

    # ── Relaciones ────────────────────────────────────────────────────────
    proyectos: Mapped[list["ProyectoAuditoria"]] = relationship(  # type: ignore[name-defined]
        "ProyectoAuditoria", back_populates="auditoria", lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<Auditoria(id={self.id}, nombre='{self.nombre[:30]}...')>"
