"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/models/hallazgo.py
Proposito: Modelo de hallazgo con workflow de aprobacion, connotaciones,
           cuantificacion de dano patrimonial y cumplimiento Circular 023
Sprint: 5
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Hallazgo(Base):
    """Modelo de hallazgo de auditoria con workflow completo.

    Implementa los 4 elementos obligatorios, connotaciones multiples,
    cuantificacion del dano patrimonial, workflow de aprobacion
    (auditor -> supervisor -> coordinador -> director) y cumplimiento
    de la Circular 023 (validacion humana obligatoria).

    Estados del workflow:
        BORRADOR -> EN_REVISION -> OBSERVACION_TRASLADADA -> RESPUESTA_RECIBIDA ->
        HALLAZGO_CONFIGURADO -> APROBADO -> TRASLADADO
    """

    __tablename__ = "hallazgos"

    # ── Identificacion ──────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    auditoria_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("auditorias.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    numero_hallazgo: Mapped[int] = mapped_column(
        Integer, nullable=False,
        comment="Secuencial por auditoria: H-001, H-002...",
    )
    titulo: Mapped[str] = mapped_column(String(500), nullable=False)

    # ── 4 elementos obligatorios ────────────────────────────────────────────
    condicion: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Que se encontro (situacion factica)",
    )
    criterio: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Norma incumplida (cita EXACTA: ley, articulo, numeral)",
    )
    causa: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Por que ocurrio",
    )
    efecto: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Consecuencia (cuantificada cuando sea posible)",
    )
    recomendacion: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="Accion correctiva sugerida (5to elemento opcional)",
    )

    # ── Connotaciones y clasificacion ───────────────────────────────────────
    connotaciones: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(
        JSONB, nullable=True, server_default="[]",
        comment='[{tipo, fundamentacion_legal, descripcion}]',
    )
    # tipos: administrativo, fiscal, disciplinario, penal

    cuantia_presunto_dano: Mapped[Optional[float]] = mapped_column(
        Numeric(precision=20, scale=2), nullable=True,
        comment="Cuantia en pesos colombianos del presunto dano patrimonial",
    )
    presuntos_responsables: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(
        JSONB, nullable=True, server_default="[]",
        comment='[{nombre, cargo, periodo, fundamentacion}]',
    )

    evidencias: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(
        JSONB, nullable=True, server_default="[]",
        comment='[{documento_id, descripcion, folio, tipo}]',
    )

    # ── Workflow de aprobacion ──────────────────────────────────────────────
    estado: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="BORRADOR", index=True,
        comment="BORRADOR|EN_REVISION|OBSERVACION_TRASLADADA|RESPUESTA_RECIBIDA|HALLAZGO_CONFIGURADO|APROBADO|TRASLADADO",
    )
    fase_actual_workflow: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="auditor",
        comment="auditor|supervisor|coordinador|director",
    )
    historial_workflow: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(
        JSONB, nullable=True, server_default="[]",
        comment='[{usuario_id, usuario_nombre, accion, estado_anterior, estado_nuevo, fecha, comentarios}]',
    )

    # ── Circular 023 — Validacion humana ────────────────────────────────────
    redaccion_validada_humano: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false",
        comment="True si un auditor valido la redaccion (Circular 023)",
    )
    validado_por: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True,
    )
    fecha_validacion: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    generado_por_ia: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false",
        comment="True si fue generado con asistencia de CecilIA",
    )

    # ── Trazabilidad ────────────────────────────────────────────────────────
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True,
    )
    updated_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False,
    )

    # ── Metadata ────────────────────────────────────────────────────────────
    metadata_extra: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True,
    )

    def __repr__(self) -> str:
        return (
            f"<Hallazgo(id={self.id}, H-{self.numero_hallazgo:03d}, "
            f"estado='{self.estado}')>"
        )
