"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/models/usuario.py
Proposito: Modelo de usuario del sistema con roles y direcciones
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class RolUsuario(str, enum.Enum):
    """Roles disponibles en el sistema CecilIA v2."""

    AUDITOR_DES = "auditor_des"
    AUDITOR_DVF = "auditor_dvf"
    PROFESIONAL_DES = "profesional_des"
    PROFESIONAL_DVF = "profesional_dvf"
    DIRECTOR_DES = "director_des"
    DIRECTOR_DVF = "director_dvf"
    ADMIN_TIC = "admin_tic"
    OBSERVATORIO = "observatorio"
    APRENDIZ = "aprendiz"


class DireccionUsuario(str, enum.Enum):
    """Direcciones misionales de la CGR."""

    DES = "DES"  # Direccion de Estudios Sectoriales
    DVF = "DVF"  # Direccion de Vigilancia Fiscal


class Usuario(Base):
    """Modelo de usuario del sistema CecilIA v2.

    Representa a un funcionario de la CGR con su rol, direccion
    y credenciales de acceso.
    """

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True,
        comment="Nombre de usuario unico para inicio de sesion",
    )
    nombre_completo: Mapped[str] = mapped_column(
        String(255), nullable=False,
        comment="Nombre completo del funcionario",
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True,
        comment="Correo electronico institucional",
    )
    rol: Mapped[RolUsuario] = mapped_column(
        Enum(RolUsuario, name="rol_usuario_enum", values_callable=lambda e: [x.value for x in e]),
        nullable=False,
        comment="Rol del usuario en el sistema",
    )
    direccion: Mapped[Optional[DireccionUsuario]] = mapped_column(
        Enum(DireccionUsuario, name="direccion_usuario_enum", values_callable=lambda e: [x.value for x in e]),
        nullable=True,
        comment="Direccion misional (DES/DVF) — nulo para admin_tic",
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False,
        comment="Hash bcrypt de la contrasena",
    )
    activo: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False,
        comment="Indica si el usuario esta activo en el sistema",
    )
    ultimo_acceso: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        comment="Fecha y hora del ultimo inicio de sesion",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False,
    )

    # ── Relaciones ────────────────────────────────────────────────────────
    conversaciones: Mapped[list["Conversacion"]] = relationship(  # type: ignore[name-defined]
        "Conversacion", back_populates="usuario", lazy="noload",
    )
    documentos: Mapped[list["Documento"]] = relationship(  # type: ignore[name-defined]
        "Documento", back_populates="usuario", lazy="noload",
    )
    hallazgos: Mapped[list["Hallazgo"]] = relationship(  # type: ignore[name-defined]
        "Hallazgo",
        foreign_keys="[Hallazgo.created_by]",
        back_populates="creador",
        lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<Usuario(id={self.id}, usuario='{self.usuario}', rol='{self.rol}')>"
