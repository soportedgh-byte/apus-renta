"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/models/documento.py
Proposito: Modelo de documento cargado al sistema para procesamiento RAG
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

import enum
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ColeccionDocumento(str, enum.Enum):
    """Colecciones disponibles para clasificacion de documentos RAG."""

    NORMATIVO = "normativo"
    INSTITUCIONAL = "institucional"
    ACADEMICO = "academico"
    TECNICO_TIC = "tecnico_tic"
    ESTADISTICO = "estadistico"
    JURISPRUDENCIAL = "jurisprudencial"
    AUDITORIA = "auditoria"


class Documento(Base):
    """Modelo de documento del sistema.

    Representa un documento cargado por un usuario, clasificado
    en una coleccion especifica para su procesamiento y consulta RAG.
    """

    __tablename__ = "documentos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(
        String(500), nullable=False,
        comment="Nombre original del archivo cargado",
    )
    tipo_archivo: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="Extension o tipo MIME del archivo (pdf, docx, xlsx, etc.)",
    )
    tamano_bytes: Mapped[int] = mapped_column(
        Integer, nullable=False,
        comment="Tamano del archivo en bytes",
    )
    coleccion: Mapped[ColeccionDocumento] = mapped_column(
        Enum(ColeccionDocumento, name="coleccion_documento_enum"),
        nullable=False,
        index=True,
        comment="Coleccion tematica del documento para RAG",
    )
    hash_sha256: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False,
        comment="Hash SHA-256 del contenido para deduplicacion",
    )
    chunks_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False,
        comment="Cantidad de fragmentos generados para RAG",
    )
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True,
        comment="Usuario que cargo el documento",
    )
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True, default=None,
        comment="Metadatos adicionales del documento (autor, fecha, etc.)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )

    # ── Relaciones ────────────────────────────────────────────────────────
    usuario: Mapped[Optional["Usuario"]] = relationship(  # type: ignore[name-defined]
        "Usuario", back_populates="documentos",
    )

    def __repr__(self) -> str:
        return f"<Documento(id={self.id}, nombre='{self.nombre}', coleccion='{self.coleccion}')>"
