"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/models/mensaje.py
Proposito: Modelo de mensaje individual dentro de una conversacion
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

import enum
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class RolMensaje(str, enum.Enum):
    """Roles posibles del emisor de un mensaje."""

    USUARIO = "usuario"
    ASISTENTE = "asistente"
    SISTEMA = "sistema"


class Mensaje(Base):
    """Modelo de mensaje en una conversacion.

    Almacena el contenido, las fuentes RAG utilizadas, el modelo
    que genero la respuesta y metricas de rendimiento.
    """

    __tablename__ = "mensajes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversacion_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("conversaciones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Referencia a la conversacion contenedora",
    )
    rol: Mapped[RolMensaje] = mapped_column(
        Enum(RolMensaje, name="rol_mensaje_enum"),
        nullable=False,
        comment="Rol del emisor: usuario, asistente o sistema",
    )
    contenido: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Contenido textual del mensaje",
    )
    fuentes_rag: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(
        JSONB, nullable=True, default=None,
        comment="Fuentes RAG utilizadas para generar la respuesta",
    )
    modelo_utilizado: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True,
        comment="Identificador del modelo LLM que genero la respuesta",
    )
    tokens_input: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True,
        comment="Cantidad de tokens de entrada consumidos",
    )
    tokens_output: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True,
        comment="Cantidad de tokens de salida generados",
    )
    tiempo_respuesta_ms: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True,
        comment="Tiempo de respuesta del LLM en milisegundos",
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
