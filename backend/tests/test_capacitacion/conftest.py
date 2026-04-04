"""
Conftest local para tests de capacitacion.
Override del conftest global para evitar la creacion de tablas con JSONB/SQLite.
"""

import pytest


@pytest.fixture(autouse=True)
def preparar_base_datos():
    """No-op: estos tests no necesitan base de datos."""
    yield
