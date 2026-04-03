"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/models/formato_generado.py
Proposito: Modelo de formato oficial generado por CecilIA (formatos 1-30 CGR)
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class FormatoGenerado(Base):
    """Modelo de formato generado — alineado con migracion 001."""

    __tablename__ = "formatos_generados"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    numero_formato: Mapped[int] = mapped_column(SmallInteger, nullable=False, index=True)
    nombre_formato: Mapped[str] = mapped_column(String(300), nullable=False)
    auditoria_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("auditorias.id", ondelete="SET NULL"), nullable=True, index=True,
    )
    usuario_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True,
    )
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="generando",
    )
    generado_con_ia: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true",
    )
    ruta_archivo: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    parametros: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    contenido_generado: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False,
    )

    def __repr__(self) -> str:
        return f"<FormatoGenerado(id={self.id}, numero={self.numero_formato})>"
