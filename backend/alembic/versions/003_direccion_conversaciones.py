"""Agrega campo direccion a la tabla conversaciones

Revision ID: 003_direccion_conversaciones
Revises: 002_dimension_embeddings_configurable
Create Date: 2026-04-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003_direccion_conversaciones"
down_revision: Union[str, None] = "002_dimension_embeddings_configurable"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "conversaciones",
        sa.Column("direccion", sa.String(10), nullable=True, server_default="DES"),
    )


def downgrade() -> None:
    op.drop_column("conversaciones", "direccion")
