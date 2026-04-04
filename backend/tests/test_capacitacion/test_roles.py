"""
Tests para el rol APRENDIZ en el sistema de roles — Sprint 6.
Importa roles.py directamente para evitar la cadena de imports de app.auth.
"""

import pytest
import importlib.util
import sys
from pathlib import Path


def _cargar_roles():
    """Carga roles.py directamente sin pasar por app.auth.__init__."""
    ruta = Path(__file__).parent.parent.parent / "app" / "auth" / "roles.py"
    spec = importlib.util.spec_from_file_location("roles_mod", str(ruta))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.ROLES


class TestRolAprendiz:
    """Tests para la configuracion del rol APRENDIZ."""

    def test_aprendiz_existe(self):
        """El rol aprendiz esta definido."""
        ROLES = _cargar_roles()
        assert "aprendiz" in ROLES

    def test_aprendiz_tiene_descripcion(self):
        """El rol aprendiz tiene descripcion."""
        ROLES = _cargar_roles()
        assert "descripcion" in ROLES["aprendiz"]
        desc = ROLES["aprendiz"]["descripcion"].lower()
        assert "capacitacion" in desc or "induccion" in desc

    def test_aprendiz_permisos_restringidos(self):
        """El aprendiz tiene permisos limitados a capacitacion."""
        ROLES = _cargar_roles()
        permisos = ROLES["aprendiz"]["permisos"]
        assert "chat_tutor" in permisos
        assert "capacitacion" in permisos
        assert "biblioteca" in permisos
        assert "quizzes" in permisos

    def test_aprendiz_no_tiene_permisos_auditoria(self):
        """El aprendiz NO tiene permisos de auditoria real."""
        ROLES = _cargar_roles()
        permisos = ROLES["aprendiz"]["permisos"]
        assert "hallazgos_crear" not in permisos
        assert "hallazgos_editar" not in permisos
        assert "formatos_generar" not in permisos
        assert "auditoria_ver" not in permisos

    def test_aprendiz_modulos(self):
        """El aprendiz solo accede a modulos de capacitacion."""
        ROLES = _cargar_roles()
        modulos = ROLES["aprendiz"]["modulos"]
        assert "capacitacion" in modulos
        assert "chat" not in modulos
        assert "hallazgos" not in modulos

    def test_aprendiz_acciones_rapidas(self):
        """El aprendiz tiene acciones rapidas de aprendizaje."""
        ROLES = _cargar_roles()
        acciones = ROLES["aprendiz"]["acciones_rapidas"]
        assert len(acciones) >= 3

    def test_total_9_roles(self):
        """Ahora hay 9 roles en el sistema (8 originales + aprendiz)."""
        ROLES = _cargar_roles()
        assert len(ROLES) == 9

    def test_aprendiz_puede_ver_ambas_direcciones(self):
        """El aprendiz puede ver contenido DES y DVF."""
        ROLES = _cargar_roles()
        puede_ver = ROLES["aprendiz"]["puede_ver"]
        assert "DES" in puede_ver
        assert "DVF" in puede_ver
