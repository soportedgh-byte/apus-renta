"""Ajusta la dimension del vector de embeddings segun el modelo configurado

La migracion 001 creo la columna embedding con vector(3072) para text-embedding-3-large.
Esta migracion la recrea con la dimension configurada en EMBEDDINGS_DIMENSIONES (default: 768
para nomic-embed-text via Ollama).

La tabla fragmentos_vectoriales debe estar vacia al ejecutar esta migracion.
Si contiene datos, se perderan los embeddings existentes.

Revision ID: 002_dimension_embeddings
Revises: 001_migracion_inicial
Create Date: 2026-04-03
"""

import os
from typing import Sequence, Union

from alembic import op

revision: str = "002_dimension_embeddings"
down_revision: str = "001_migracion_inicial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Leer dimension desde variable de entorno o usar 768 (nomic-embed-text)
DIMENSION: int = int(os.environ.get("EMBEDDINGS_DIMENSIONES", "768"))


def upgrade() -> None:
    """Recrea la columna embedding con la dimension configurada."""
    # Eliminar indice IVFFlat si existe
    op.execute(
        "DROP INDEX IF EXISTS ix_fv_embedding_ivfflat"
    )
    op.execute(
        "DROP INDEX IF EXISTS ix_fragmentos_vectoriales_embedding_ivfflat"
    )

    # Recrear columna con nueva dimension
    op.execute(
        "ALTER TABLE fragmentos_vectoriales DROP COLUMN IF EXISTS embedding"
    )
    op.execute(
        f"ALTER TABLE fragmentos_vectoriales ADD COLUMN embedding vector({DIMENSION})"
    )


def downgrade() -> None:
    """Restaura la columna a 3072 dimensiones (text-embedding-3-large)."""
    op.execute(
        "DROP INDEX IF EXISTS ix_fv_embedding_ivfflat"
    )
    op.execute(
        "ALTER TABLE fragmentos_vectoriales DROP COLUMN IF EXISTS embedding"
    )
    op.execute(
        "ALTER TABLE fragmentos_vectoriales ADD COLUMN embedding vector(3072)"
    )
