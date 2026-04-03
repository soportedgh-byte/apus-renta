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
from typing import Any, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Conversacion(Base):
    """Modelo de conversacion.

    Cada conversacion pertenece a un usuario y puede estar vinculada
    a un proyecto de auditoria especifico. Almacena la fase actual
    del proceso auditor y metadatos de contexto.
    """

    __tablename__ = "conversaciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True,
        comment="Referencia al usuario propietario de la conversacion",
    )
    titulo: Mapped[str] = mapped_column(
        String(500), nullable=False, default="Nueva conversacion",
        comment="Titulo descriptivo de la conversacion",
    )
    direccion: Mapped[Optional[str]] = mapped_column(
        String(10), nullable=True,
        comment="Direccion misional asociada (DES/DVF)",
    )
    fase_actual: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True,
        comment="Fase actual del proceso auditor en esta conversacion",
    )
    proyecto_auditoria_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("proyectos_auditoria.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Proyecto de auditoria vinculado (opcional)",
    )
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True, default=None,
        comment="Metadatos adicionales de la conversacion en formato JSON",
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
        "Mensaje", back_populates="conversacion", lazy="selectin",
        order_by="Mensaje.created_at",
    )
    proyecto_auditoria: Mapped[Optional["ProyectoAuditoria"]] = relationship(  # type: ignore[name-defined]
        "ProyectoAuditoria", back_populates="conversaciones",
    )

    def __repr__(self) -> str:
        return f"<Conversacion(id={self.id}, titulo='{self.titulo[:30]}...')>"
