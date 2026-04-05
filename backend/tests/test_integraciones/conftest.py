"""
Conftest local para tests de integraciones.
Override del conftest global para evitar dependencias de BD/Redis.
"""

import pytest


@pytest.fixture(autouse=True)
def preparar_base_datos():
    """No-op: estos tests no necesitan base de datos."""
    yield
