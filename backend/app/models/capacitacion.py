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


# ── Sprint Capacitacion 2.0 — Aprendizaje adaptativo ──────────────────────


class PerfilAprendizaje(Base):
    """Perfil de estilo de aprendizaje del usuario (visual/auditivo/lector/kinestesico)."""

    __tablename__ = "perfiles_aprendizaje"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True,
    )
    estilo_predominante: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="lector | auditivo | visual | kinestesico",
    )
    respuestas_cuestionario: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True,
        comment='{"pregunta_1": "a", "pregunta_2": "b", ...}',
    )
    puntajes: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True,
        comment='{"lector": 3, "auditivo": 1, "visual": 0, "kinestesico": 1}',
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False,
    )


class Gamificacion(Base):
    """Estado de gamificacion del usuario: XP, nivel, racha, insignias."""

    __tablename__ = "gamificacion"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True,
    )
    xp_total: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    nivel: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default="Practicante",
        comment="Practicante | Auxiliar | Auditor Junior | Auditor Senior | Experto",
    )
    racha_dias: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    mejor_racha: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    insignias: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(
        JSONB, nullable=True, server_default="[]",
        comment='[{"id": "primera_leccion", "nombre": "...", "fecha": "..."}]',
    )
    ultima_actividad: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )


class RepasoProgramado(Base):
    """Repaso espaciado (spaced repetition) para lecciones completadas."""

    __tablename__ = "repasos_programados"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    leccion_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("lecciones.id", ondelete="CASCADE"),
        nullable=False,
    )
    fecha_proximo_repaso: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    intervalo_dias: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="1",
        comment="Intervalo actual: 1, 3, 7, 14, 30, 60",
    )
    intentos: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    aciertos: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="pendiente",
        comment="pendiente | completado | vencido",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )


class RecursoGenerado(Base):
    """Recurso multimedia generado: podcast, infografia, manual, flashcards."""

    __tablename__ = "recursos_generados"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tipo: Mapped[str] = mapped_column(
        String(30), nullable=False,
        comment="podcast | infografia | manual | flashcard | presentacion | glosario",
    )
    tema: Mapped[str] = mapped_column(String(500), nullable=False)
    leccion_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("lecciones.id", ondelete="SET NULL"),
        nullable=True,
    )
    ruta_archivo: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True,
        comment="Ruta al archivo generado (MP3, SVG, DOCX, HTML)",
    )
    formato: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="html",
        comment="mp3 | svg | html | docx | json",
    )
    contenido_texto: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="Script del podcast, SVG inline, HTML, etc.",
    )
    duracion_segundos: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True,
    )
    usuario_generador_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
    )
    metadata_extra: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )


class EntradaGlosario(Base):
    """Entrada del glosario interactivo de control fiscal."""

    __tablename__ = "glosario_fiscal"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    termino: Mapped[str] = mapped_column(
        String(200), nullable=False, unique=True, index=True,
    )
    definicion_simple: Mapped[str] = mapped_column(Text, nullable=False)
    definicion_tecnica: Mapped[str] = mapped_column(Text, nullable=False)
    ejemplo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    norma_aplicable: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True,
        comment="Referencia normativa (ej: Ley 610/2000, Art. 5)",
    )
    categoria: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="general",
        comment="auditoria | normativa | financiero | presupuestal | contratacion | institucional",
    )
    terminos_relacionados: Mapped[Optional[list[str]]] = mapped_column(
        JSONB, nullable=True, server_default="[]",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
