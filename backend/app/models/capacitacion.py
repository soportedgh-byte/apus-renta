"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/models/capacitacion.py
Proposito: Modelos para el modulo de capacitacion/tutor:
           rutas de aprendizaje, lecciones, progreso y quizzes.
Sprint: 6
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey, Integer,
    SmallInteger, String, Text, func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RutaAprendizaje(Base):
    """Ruta de aprendizaje tematica (ej: Conoce la CGR, Auditoria DVF)."""

    __tablename__ = "rutas_aprendizaje"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    icono: Mapped[str] = mapped_column(String(10), nullable=False, server_default="📚")
    color: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="#C9A84C",
        comment="Color hex para la UI",
    )
    direccion: Mapped[str] = mapped_column(
        String(10), nullable=False, server_default="TODOS",
        comment="DES|DVF|TODOS — a quienes aplica",
    )
    orden: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default="0",
    )
    activa: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true",
    )
    total_lecciones: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default="0",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )


class Leccion(Base):
    """Leccion individual dentro de una ruta de aprendizaje."""

    __tablename__ = "lecciones"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    ruta_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("rutas_aprendizaje.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    numero: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    titulo: Mapped[str] = mapped_column(String(300), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    contenido_md: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="",
        comment="Contenido de la leccion en Markdown",
    )
    duracion_minutos: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default="15",
    )
    orden: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )


class ProgresoUsuario(Base):
    """Progreso de un usuario en una leccion especifica."""

    __tablename__ = "progreso_usuarios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    ruta_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("rutas_aprendizaje.id", ondelete="CASCADE"),
        nullable=False,
    )
    leccion_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("lecciones.id", ondelete="CASCADE"),
        nullable=False,
    )
    completada: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false",
    )
    fecha_completada: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    puntaje_quiz: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True,
        comment="Puntaje del quiz (0-100) si aplica",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )


class QuizResultado(Base):
    """Resultado de un quiz de evaluacion."""

    __tablename__ = "quiz_resultados"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    leccion_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("lecciones.id", ondelete="SET NULL"),
        nullable=True,
    )
    ruta_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("rutas_aprendizaje.id", ondelete="CASCADE"),
        nullable=False,
    )
    puntaje: Mapped[float] = mapped_column(Float, nullable=False)
    total_preguntas: Mapped[int] = mapped_column(Integer, nullable=False)
    respuestas_json: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(
        JSONB, nullable=True, server_default="[]",
        comment='[{pregunta, respuesta_usuario, respuesta_correcta, correcta}]',
    )
    aprobado: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false",
        comment="True si puntaje >= 70%",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
