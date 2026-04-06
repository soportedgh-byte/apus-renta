"""Capacitacion 2.0: perfiles aprendizaje, gamificacion, repasos, recursos, glosario

Revision ID: 004_capacitacion_2_0_tablas
Revises: 003_direccion_conversaciones
Create Date: 2026-04-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "004_capacitacion_2_0_tablas"
down_revision: Union[str, None] = "003_direccion_conversaciones"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Perfiles de aprendizaje VARK
    op.create_table(
        "perfiles_aprendizaje",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("usuario_id", sa.Integer, sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, unique=True, index=True),
        sa.Column("estilo_predominante", sa.String(20), nullable=False, comment="lector | auditivo | visual | kinestesico"),
        sa.Column("respuestas_cuestionario", JSONB, nullable=True),
        sa.Column("puntajes", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Gamificacion
    op.create_table(
        "gamificacion",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("usuario_id", sa.Integer, sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, unique=True, index=True),
        sa.Column("xp_total", sa.Integer, nullable=False, server_default="0"),
        sa.Column("nivel", sa.String(30), nullable=False, server_default="Practicante"),
        sa.Column("racha_dias", sa.Integer, nullable=False, server_default="0"),
        sa.Column("mejor_racha", sa.Integer, nullable=False, server_default="0"),
        sa.Column("insignias", JSONB, nullable=True, server_default="[]"),
        sa.Column("ultima_actividad", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Repasos programados (spaced repetition)
    op.create_table(
        "repasos_programados",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("usuario_id", sa.Integer, sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("leccion_id", sa.String(36), sa.ForeignKey("lecciones.id", ondelete="CASCADE"), nullable=False),
        sa.Column("fecha_proximo_repaso", sa.DateTime(timezone=True), nullable=False),
        sa.Column("intervalo_dias", sa.Integer, nullable=False, server_default="1"),
        sa.Column("intentos", sa.Integer, nullable=False, server_default="0"),
        sa.Column("aciertos", sa.Integer, nullable=False, server_default="0"),
        sa.Column("estado", sa.String(20), nullable=False, server_default="pendiente"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Recursos generados (podcasts, infografias, flashcards, etc.)
    op.create_table(
        "recursos_generados",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tipo", sa.String(30), nullable=False, comment="podcast | infografia | manual | flashcard | presentacion | glosario"),
        sa.Column("tema", sa.String(500), nullable=False),
        sa.Column("leccion_id", sa.String(36), sa.ForeignKey("lecciones.id", ondelete="SET NULL"), nullable=True),
        sa.Column("ruta_archivo", sa.String(500), nullable=True),
        sa.Column("formato", sa.String(20), nullable=False, server_default="html"),
        sa.Column("contenido_texto", sa.Text, nullable=True),
        sa.Column("duracion_segundos", sa.Integer, nullable=True),
        sa.Column("usuario_generador_id", sa.Integer, sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        sa.Column("metadata_extra", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Glosario interactivo
    op.create_table(
        "glosario_fiscal",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("termino", sa.String(200), nullable=False, unique=True, index=True),
        sa.Column("definicion_simple", sa.Text, nullable=False),
        sa.Column("definicion_tecnica", sa.Text, nullable=False),
        sa.Column("ejemplo", sa.Text, nullable=True),
        sa.Column("norma_aplicable", sa.String(500), nullable=True),
        sa.Column("categoria", sa.String(50), nullable=False, server_default="general"),
        sa.Column("terminos_relacionados", JSONB, nullable=True, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("glosario_fiscal")
    op.drop_table("recursos_generados")
    op.drop_table("repasos_programados")
    op.drop_table("gamificacion")
    op.drop_table("perfiles_aprendizaje")
