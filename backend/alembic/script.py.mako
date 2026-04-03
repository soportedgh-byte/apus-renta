"""${message}

CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia
Sprint: 0

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# Identificadores de revisión utilizados por Alembic
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """Aplica la migración (avanzar esquema)."""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Revierte la migración (retroceder esquema)."""
    ${downgrades if downgrades else "pass"}
