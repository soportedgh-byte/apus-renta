"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/models/auditoria.py
Proposito: Modelo de proceso de auditoria (nivel macro)
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

import enum
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TipoAuditoria(str, enum.Enum):
    """Tipos de auditoria segun la normativa de la CGR."""

    FINANCIERA = "financiera"
    CUMPLIMIENTO = "cumplimiento"
    DESEMPENO = "desempeno"
    ESPECIAL = "especial"


class EstadoAuditoria(str, enum.Enum):
    """Estados del ciclo de vida de una auditoria."""

    PLANEACION = "planeacion"
    EJECUCION = "ejecucion"
    INFORME = "informe"
    SEGUIMIENTO = "seguimiento"
    CERRADA = "cerrada"


class Auditoria(Base):
    """Modelo de auditoria.

    Representa un proceso de auditoria completo, desde su planeacion
    hasta su cierre, con la entidad auditada y vigencia fiscal.
    """

    __tablename__ = "auditorias"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(
        String(500), nullable=False,
        comment="Nombre descriptivo de la auditoria",
    )
    entidad_auditada: Mapped[str] = mapped_column(
        String(500), nullable=False,
        comment="Nombre de la entidad sujeta a auditoria",
    )
    vigencia: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="Vigencia fiscal auditada (ej: 2025, 2024-2025)",
    )
    tipo: Mapped[TipoAuditoria] = mapped_column(
        Enum(TipoAuditoria, name="tipo_auditoria_enum"),
        nullable=False,
        comment="Tipo de auditoria segun clasificacion CGR",
    )
    direccion: Mapped[str] = mapped_column(
        String(10), nullable=False,
        comment="Direccion misional responsable (DES/DVF)",
    )
    estado: Mapped[EstadoAuditoria] = mapped_column(
        Enum(EstadoAuditoria, name="estado_auditoria_enum"),
        nullable=False,
        default=EstadoAuditoria.PLANEACION,
        comment="Estado actual del proceso de auditoria",
    )
    fecha_inicio: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True,
        comment="Fecha de inicio de la auditoria",
    )
    fecha_fin: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True,
        comment="Fecha de finalizacion de la auditoria",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )

    # ── Relaciones ────────────────────────────────────────────────────────
    proyectos: Mapped[list["ProyectoAuditoria"]] = relationship(  # type: ignore[name-defined]
        "ProyectoAuditoria", back_populates="auditoria", lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<Auditoria(id={self.id}, nombre='{self.nombre[:30]}...', "
            f"tipo='{self.tipo}', estado='{self.estado}')>"
        )
