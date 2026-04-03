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

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class FormatoGenerado(Base):
    """Modelo de formato oficial generado.

    Representa uno de los 30 formatos oficiales del proceso auditor
    de la CGR, generado con asistencia de CecilIA v2 y almacenado
    en formato JSON estructurado.
    """

    __tablename__ = "formatos_generados"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre_formato: Mapped[str] = mapped_column(
        String(300), nullable=False,
        comment="Nombre oficial del formato CGR",
    )
    numero_formato: Mapped[int] = mapped_column(
        Integer, nullable=False,
        comment="Numero del formato (1 a 30) segun la guia de auditoria CGR",
    )
    contenido_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False,
        comment="Contenido estructurado del formato en JSON",
    )
    proyecto_auditoria_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("proyectos_auditoria.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Proyecto de auditoria asociado",
    )
    usuario_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Usuario que genero el formato",
    )
    estado: Mapped[str] = mapped_column(
        String(50), nullable=False, default="borrador",
        comment="Estado del formato: borrador, revision, aprobado, exportado",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )

    # ── Relaciones ────────────────────────────────────────────────────────
    proyecto_auditoria: Mapped[Optional["ProyectoAuditoria"]] = relationship(  # type: ignore[name-defined]
        "ProyectoAuditoria", back_populates="formatos_generados",
    )

    def __repr__(self) -> str:
        return (
            f"<FormatoGenerado(id={self.id}, numero={self.numero_formato}, "
            f"nombre='{self.nombre_formato[:30]}...', estado='{self.estado}')>"
        )
