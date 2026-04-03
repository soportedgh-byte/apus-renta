"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/models/hallazgo.py
Proposito: Modelo de hallazgo de auditoria con sus atributos normativos
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ConnotacionHallazgo(str, enum.Enum):
    """Connotaciones posibles de un hallazgo de auditoria."""

    FISCAL = "fiscal"
    DISCIPLINARIA = "disciplinaria"
    PENAL = "penal"
    ADMINISTRATIVA = "administrativa"
    FISCAL_CON_PRESUNTO_ALCANCE = "fiscal_con_presunto_alcance"


class EstadoHallazgo(str, enum.Enum):
    """Estados del ciclo de vida de un hallazgo."""

    BORRADOR = "borrador"
    REVISION = "revision"
    APROBADO = "aprobado"
    TRASLADADO = "trasladado"


class Hallazgo(Base):
    """Modelo de hallazgo de auditoria.

    Estructura un hallazgo con los cinco elementos normativos exigidos
    por la CGR: criterio, condicion, causa, efecto y connotacion.
    """

    __tablename__ = "hallazgos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(
        String(500), nullable=False,
        comment="Titulo descriptivo del hallazgo",
    )
    descripcion: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Descripcion detallada del hallazgo",
    )
    connotacion: Mapped[ConnotacionHallazgo] = mapped_column(
        Enum(ConnotacionHallazgo, name="connotacion_hallazgo_enum"),
        nullable=False,
        comment="Tipo de connotacion del hallazgo",
    )
    criterio: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Norma, ley o reglamento que se incumple (el deber ser)",
    )
    condicion: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Situacion encontrada (lo que es)",
    )
    causa: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Razon por la que ocurrio la situacion",
    )
    efecto: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Consecuencia o impacto de la situacion encontrada",
    )
    estado: Mapped[EstadoHallazgo] = mapped_column(
        Enum(EstadoHallazgo, name="estado_hallazgo_enum"),
        nullable=False,
        default=EstadoHallazgo.BORRADOR,
        comment="Estado actual en el flujo de aprobacion",
    )
    proyecto_auditoria_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("proyectos_auditoria.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Proyecto de auditoria al que pertenece el hallazgo",
    )
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True,
        comment="Auditor que registro el hallazgo",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False,
    )

    # ── Relaciones ────────────────────────────────────────────────────────
    usuario: Mapped["Usuario"] = relationship(  # type: ignore[name-defined]
        "Usuario", back_populates="hallazgos",
    )
    proyecto_auditoria: Mapped[Optional["ProyectoAuditoria"]] = relationship(  # type: ignore[name-defined]
        "ProyectoAuditoria", back_populates="hallazgos",
    )

    def __repr__(self) -> str:
        return (
            f"<Hallazgo(id={self.id}, titulo='{self.titulo[:30]}...', "
            f"connotacion='{self.connotacion}', estado='{self.estado}')>"
        )
