"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/models/alerta.py
Proposito: Modelo de alerta del Observatorio Fiscal
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class NivelUrgencia(str, enum.Enum):
    """Niveles de urgencia para alertas del observatorio."""

    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"


class Alerta(Base):
    """Modelo de alerta del Observatorio Fiscal.

    Representa una alerta generada por el modulo de observatorio,
    con informacion sobre el sector, fuente y nivel de urgencia.
    """

    __tablename__ = "alertas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(
        String(500), nullable=False,
        comment="Titulo descriptivo de la alerta",
    )
    descripcion: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Descripcion detallada de la alerta",
    )
    tipo_alerta: Mapped[str] = mapped_column(
        String(100), nullable=False,
        comment="Clasificacion del tipo de alerta (presupuestal, contractual, etc.)",
    )
    sector: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True,
        comment="Sector economico o institucional relacionado",
    )
    fuente: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True,
        comment="Fuente de datos que origino la alerta",
    )
    nivel_urgencia: Mapped[NivelUrgencia] = mapped_column(
        Enum(NivelUrgencia, name="nivel_urgencia_enum"),
        nullable=False,
        default=NivelUrgencia.MEDIO,
        comment="Nivel de urgencia de la alerta",
    )
    direccion: Mapped[Optional[str]] = mapped_column(
        String(10), nullable=True,
        comment="Direccion misional destinataria (DES/DVF)",
    )
    activa: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False,
        comment="Indica si la alerta esta activa",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<Alerta(id={self.id}, titulo='{self.titulo[:30]}...', "
            f"urgencia='{self.nivel_urgencia}')>"
        )
