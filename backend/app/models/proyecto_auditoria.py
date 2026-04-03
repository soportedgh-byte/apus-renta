"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/models/proyecto_auditoria.py
Proposito: Modelo de proyecto de auditoria — vincula usuario con auditoria
           y almacena el contexto de sesion para memoria de trabajo
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


class ProyectoAuditoria(Base):
    """Modelo de proyecto de auditoria (memoria de sesion).

    Vincula un usuario auditor con una auditoria especifica y mantiene
    el contexto de trabajo acumulado: fase actual, documentos asociados
    y contexto semantico de la sesion.
    """

    __tablename__ = "proyectos_auditoria"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    auditoria_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("auditorias.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Auditoria macro a la que pertenece el proyecto",
    )
    usuario_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Auditor asignado al proyecto",
    )
    fase_actual: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True,
        comment="Fase actual del proceso auditor (planeacion, ejecucion, informe, etc.)",
    )
    contexto_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True, default=None,
        comment="Contexto semantico acumulado de la sesion de trabajo",
    )
    documentos_asociados: Mapped[Optional[list[Any]]] = mapped_column(
        JSONB, nullable=True, default=None,
        comment="Lista de IDs de documentos vinculados al proyecto",
    )
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
    conversaciones: Mapped[list["Conversacion"]] = relationship(  # type: ignore[name-defined]
        "Conversacion", back_populates="proyecto_auditoria", lazy="selectin",
    )
    hallazgos: Mapped[list["Hallazgo"]] = relationship(  # type: ignore[name-defined]
        "Hallazgo", back_populates="proyecto_auditoria", lazy="selectin",
    )
    formatos_generados: Mapped[list["FormatoGenerado"]] = relationship(  # type: ignore[name-defined]
        "FormatoGenerado", back_populates="proyecto_auditoria", lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<ProyectoAuditoria(id={self.id}, auditoria_id={self.auditoria_id}, "
            f"usuario_id={self.usuario_id}, fase='{self.fase_actual}')>"
        )
