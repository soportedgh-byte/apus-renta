"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/models/mensaje.py
Proposito: Modelo de mensaje individual dentro de una conversacion
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, ForeignKey, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Mensaje(Base):
    """Modelo de mensaje — alineado con migracion 001."""

    __tablename__ = "mensajes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    conversacion_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversaciones.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    rol: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="user | assistant | system",
    )
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    fuentes: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True,
    )
    metadata_modelo: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True,
    )
    feedback_puntuacion: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="-1, 0, 1",
    )
    feedback_comentario: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )

    # ── Relaciones ────────────────────────────────────────────────────────
    conversacion: Mapped["Conversacion"] = relationship(  # type: ignore[name-defined]
        "Conversacion", back_populates="mensajes",
    )

    def __repr__(self) -> str:
        return f"<Mensaje(id={self.id}, rol='{self.rol}', largo={len(self.contenido)})>"
