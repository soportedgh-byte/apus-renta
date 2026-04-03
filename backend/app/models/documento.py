"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/models/documento.py
Proposito: Modelo de documento cargado al sistema para procesamiento RAG
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Documento(Base):
    """Modelo de documento — alineado con migracion 001."""

    __tablename__ = "documentos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    usuario_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True,
    )
    nombre_archivo: Mapped[str] = mapped_column(String(500), nullable=False)
    tipo_mime: Mapped[str] = mapped_column(String(100), nullable=False)
    tamano_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    coleccion: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="general", index=True,
    )
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="subido",
        comment="subido | procesando | indexado | error",
    )
    ruta_almacenamiento: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    hash_contenido: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    total_fragmentos: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    etiquetas: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    metadata_extra: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False,
    )

    # ── Relaciones ────────────────────────────────────────────────────────
    usuario: Mapped[Optional["Usuario"]] = relationship(  # type: ignore[name-defined]
        "Usuario", back_populates="documentos",
    )

    def __repr__(self) -> str:
        return f"<Documento(id={self.id}, nombre='{self.nombre_archivo}')>"
