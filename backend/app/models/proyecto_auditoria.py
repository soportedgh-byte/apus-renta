"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/models/proyecto_auditoria.py
Proposito: Modelo de proyecto de auditoria con memoria de sesion persistente —
           vincula usuario con auditoria, almacena estado, resumen de sesiones,
           documentos procesados y configuracion del workspace local.
Sprint: 11
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ProyectoAuditoria(Base):
    """Proyecto de auditoria con memoria de sesion persistente.

    Permite que CecilIA recuerde el contexto de trabajo de cada auditor:
    - Estado actual del proyecto (fase, documentos, hallazgos)
    - Resumen anonimizado de sesiones anteriores
    - Configuracion del workspace local (carpetas, archivos clave)

    Los resumenes se generan automaticamente al cerrar sesion o
    tras 30 minutos de inactividad, usando el LLM para condensar
    la conversacion en 200 palabras anonimizadas.
    """

    __tablename__ = "proyectos_auditoria"

    # ── Identificacion ──────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    auditoria_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("auditorias.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    usuario_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True,
    )
    nombre_sesion: Mapped[str] = mapped_column(String(300), nullable=False)

    # ── Contexto de la auditoria ────────────────────────────────────────────
    sujeto_control: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True,
        comment="Entidad auditada (ej: MinTIC, ANE, CRC)",
    )
    vigencia: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True,
        comment="Periodo auditado (ej: 2025-I)",
    )
    tipo_auditoria: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True,
        comment="financiera | cumplimiento | desempeno | especial",
    )
    fase: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="preplaneacion | planeacion | ejecucion | informe | seguimiento",
    )

    # ── Estado del proyecto (JSONB) ─────────────────────────────────────────
    estado_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True, server_default="{}",
        comment="Estado serializado: materias_examinadas, riesgos, prioridades, etc.",
    )

    # ── Memoria de sesion ───────────────────────────────────────────────────
    resumen_sesiones: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="Resumen acumulativo de sesiones anteriores (anonimizado, max 1000 palabras)",
    )
    ultima_sesion_resumen: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="Resumen de la ultima sesion (200 palabras, anonimizado)",
    )

    # ── Documentos y artefactos ─────────────────────────────────────────────
    documentos_procesados: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(
        JSONB, nullable=True, server_default="[]",
        comment='[{nombre, ruta, tipo, fecha_procesado, chunks}]',
    )
    hallazgos_vinculados: Mapped[Optional[list[str]]] = mapped_column(
        JSONB, nullable=True, server_default="[]",
        comment='[hallazgo_id, ...]',
    )
    formatos_generados: Mapped[Optional[list[str]]] = mapped_column(
        JSONB, nullable=True, server_default="[]",
        comment='[formato_id, ...]',
    )

    # ── Workspace local ─────────────────────────────────────────────────────
    configuracion_workspace: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True, server_default="{}",
        comment='{ carpetas: [], archivos_clave: [], ultimo_acceso: ... }',
    )

    # ── Estado y control ────────────────────────────────────────────────────
    activo: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true",
    )
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="activo",
    )
    objetivo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    contexto: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    # ── Timestamps ──────────────────────────────────────────────────────────
    ultima_actividad: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        comment="Timestamp de la ultima interaccion del usuario",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False,
    )

    # ── Relaciones ──────────────────────────────────────────────────────────
    auditoria: Mapped["Auditoria"] = relationship(  # type: ignore[name-defined]
        "Auditoria", back_populates="proyectos",
    )

    def __repr__(self) -> str:
        return (
            f"<ProyectoAuditoria(id={self.id}, sesion='{self.nombre_sesion}', "
            f"fase='{self.fase}', activo={self.activo})>"
        )
