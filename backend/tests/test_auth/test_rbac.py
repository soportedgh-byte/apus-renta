"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: test_rbac.py
Propósito: Pruebas unitarias del sistema de control de acceso basado en roles (RBAC) y segregación por dirección técnica
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from dataclasses import dataclass

import pytest


# ---------------------------------------------------------------------------
# Modelos simulados para las pruebas
# ---------------------------------------------------------------------------
@dataclass
class Usuario:
    """Representación simplificada de un usuario para pruebas RBAC."""

    usuario: str
    nombre: str
    rol: str
    direccion: str | None


# ---------------------------------------------------------------------------
# Definición de roles y permisos
# ---------------------------------------------------------------------------
ROLES_VALIDOS = {
    "ADMIN",
    "DIRECTOR_DES",
    "DIRECTOR_DVF",
    "AUDITOR_DES",
    "AUDITOR_DVF",
    "LIDER_TECNICO",
    "COORDINADOR",
    "OBSERVADOR",
}

PERMISOS_POR_ROL: dict[str, set[str]] = {
    "ADMIN": {
        "usuarios:crear", "usuarios:leer", "usuarios:editar", "usuarios:eliminar",
        "chat:usar", "chat:ver_todos",
        "auditorias:crear", "auditorias:leer", "auditorias:editar",
        "hallazgos:crear", "hallazgos:aprobar",
        "herramientas:usar",
        "corpus:ingestar",
        "config:editar",
        "logs:ver",
    },
    "DIRECTOR_DES": {
        "chat:usar",
        "auditorias:leer", "auditorias:editar",
        "hallazgos:crear", "hallazgos:aprobar",
        "herramientas:usar",
    },
    "DIRECTOR_DVF": {
        "chat:usar",
        "auditorias:leer", "auditorias:editar",
        "hallazgos:crear", "hallazgos:aprobar",
        "herramientas:usar",
    },
    "AUDITOR_DES": {
        "chat:usar",
        "auditorias:leer",
        "hallazgos:crear",
        "herramientas:usar",
    },
    "AUDITOR_DVF": {
        "chat:usar",
        "auditorias:leer",
        "hallazgos:crear",
        "herramientas:usar",
    },
    "LIDER_TECNICO": {
        "chat:usar",
        "auditorias:leer",
        "herramientas:usar",
        "corpus:ingestar",
        "config:editar",
        "logs:ver",
    },
    "COORDINADOR": {
        "chat:usar",
        "auditorias:leer",
        "hallazgos:crear",
        "herramientas:usar",
    },
    "OBSERVADOR": {
        "auditorias:leer",
        "chat:usar",
    },
}

DIRECCIONES_VALIDAS = {"DES", "DVF"}


# ---------------------------------------------------------------------------
# Funciones RBAC a probar
# ---------------------------------------------------------------------------

def tiene_permiso(usuario: Usuario, permiso: str) -> bool:
    """Verifica si un usuario tiene un permiso específico."""
    permisos = PERMISOS_POR_ROL.get(usuario.rol, set())
    return permiso in permisos


def puede_acceder_direccion(usuario: Usuario, direccion_recurso: str) -> bool:
    """Verifica si un usuario puede acceder a recursos de una dirección técnica.

    Reglas:
    - ADMIN, LIDER_TECNICO y COORDINADOR acceden a todas las direcciones.
    - OBSERVADOR accede a todas las direcciones (solo lectura).
    - Directores y auditores solo acceden a su propia dirección.
    """
    roles_transversales = {"ADMIN", "LIDER_TECNICO", "COORDINADOR", "OBSERVADOR"}

    if usuario.rol in roles_transversales:
        return True

    return usuario.direccion == direccion_recurso


def validar_rol(rol: str) -> bool:
    """Verifica que un rol sea válido."""
    return rol in ROLES_VALIDOS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def admin():
    return Usuario("admin.cecilia", "Administrador CecilIA", "ADMIN", None)


@pytest.fixture
def director_des():
    return Usuario("juan.cobo", "Dr. Juan Carlos Cobo Gómez", "DIRECTOR_DES", "DES")


@pytest.fixture
def director_dvf():
    return Usuario("jose.ramirez", "Dr. José Fernando Ramírez Muñoz", "DIRECTOR_DVF", "DVF")


@pytest.fixture
def auditor_des():
    return Usuario("auditor.des.01", "Auditor DES Pruebas 01", "AUDITOR_DES", "DES")


@pytest.fixture
def auditor_dvf():
    return Usuario("auditor.dvf.01", "Auditor DVF Pruebas 01", "AUDITOR_DVF", "DVF")


@pytest.fixture
def lider_tecnico():
    return Usuario("gustavo.castillo", "Ing. Gustavo Adolfo Castillo Romero", "LIDER_TECNICO", None)


@pytest.fixture
def coordinador():
    return Usuario("karen.suevis", "Abog. Karen Tatiana Suevis Gómez", "COORDINADOR", None)


@pytest.fixture
def observador():
    return Usuario("observador.cgr", "Observador CGR", "OBSERVADOR", None)


# ---------------------------------------------------------------------------
# Tests de validación de roles
# ---------------------------------------------------------------------------
class TestValidacionRoles:
    """Pruebas de validación de roles del sistema."""

    @pytest.mark.parametrize("rol", list(ROLES_VALIDOS))
    def test_roles_validos_son_aceptados(self, rol):
        """Cada rol definido en el catálogo debe ser reconocido como válido."""
        assert validar_rol(rol) is True

    @pytest.mark.parametrize("rol", ["SUPERADMIN", "ROOT", "AUDITOR", "", "admin"])
    def test_roles_invalidos_son_rechazados(self, rol):
        """Roles que no están en el catálogo deben ser rechazados."""
        assert validar_rol(rol) is False

    def test_total_roles_definidos(self):
        """Deben existir exactamente 8 roles en el sistema."""
        assert len(ROLES_VALIDOS) == 8


# ---------------------------------------------------------------------------
# Tests de permisos por rol
# ---------------------------------------------------------------------------
class TestPermisosAdmin:
    """Pruebas de permisos del rol ADMIN."""

    def test_admin_puede_crear_usuarios(self, admin):
        assert tiene_permiso(admin, "usuarios:crear") is True

    def test_admin_puede_eliminar_usuarios(self, admin):
        assert tiene_permiso(admin, "usuarios:eliminar") is True

    def test_admin_puede_ver_logs(self, admin):
        assert tiene_permiso(admin, "logs:ver") is True

    def test_admin_puede_editar_config(self, admin):
        assert tiene_permiso(admin, "config:editar") is True

    def test_admin_puede_ingestar_corpus(self, admin):
        assert tiene_permiso(admin, "corpus:ingestar") is True

    def test_admin_puede_aprobar_hallazgos(self, admin):
        assert tiene_permiso(admin, "hallazgos:aprobar") is True


class TestPermisosDirector:
    """Pruebas de permisos de los roles DIRECTOR."""

    def test_director_des_puede_aprobar_hallazgos(self, director_des):
        assert tiene_permiso(director_des, "hallazgos:aprobar") is True

    def test_director_dvf_puede_aprobar_hallazgos(self, director_dvf):
        assert tiene_permiso(director_dvf, "hallazgos:aprobar") is True

    def test_director_no_puede_crear_usuarios(self, director_des):
        assert tiene_permiso(director_des, "usuarios:crear") is False

    def test_director_no_puede_ver_logs(self, director_des):
        assert tiene_permiso(director_des, "logs:ver") is False

    def test_director_puede_usar_chat(self, director_des):
        assert tiene_permiso(director_des, "chat:usar") is True

    def test_director_puede_usar_herramientas(self, director_dvf):
        assert tiene_permiso(director_dvf, "herramientas:usar") is True


class TestPermisosAuditor:
    """Pruebas de permisos de los roles AUDITOR."""

    def test_auditor_puede_usar_chat(self, auditor_des):
        assert tiene_permiso(auditor_des, "chat:usar") is True

    def test_auditor_puede_crear_hallazgos(self, auditor_des):
        assert tiene_permiso(auditor_des, "hallazgos:crear") is True

    def test_auditor_no_puede_aprobar_hallazgos(self, auditor_des):
        assert tiene_permiso(auditor_des, "hallazgos:aprobar") is False

    def test_auditor_no_puede_crear_usuarios(self, auditor_dvf):
        assert tiene_permiso(auditor_dvf, "usuarios:crear") is False

    def test_auditor_no_puede_editar_config(self, auditor_dvf):
        assert tiene_permiso(auditor_dvf, "config:editar") is False

    def test_auditor_puede_usar_herramientas(self, auditor_des):
        assert tiene_permiso(auditor_des, "herramientas:usar") is True


class TestPermisosObservador:
    """Pruebas de permisos del rol OBSERVADOR."""

    def test_observador_puede_leer_auditorias(self, observador):
        assert tiene_permiso(observador, "auditorias:leer") is True

    def test_observador_puede_usar_chat(self, observador):
        assert tiene_permiso(observador, "chat:usar") is True

    def test_observador_no_puede_crear_hallazgos(self, observador):
        assert tiene_permiso(observador, "hallazgos:crear") is False

    def test_observador_no_puede_usar_herramientas(self, observador):
        assert tiene_permiso(observador, "herramientas:usar") is False

    def test_observador_no_puede_editar_auditorias(self, observador):
        assert tiene_permiso(observador, "auditorias:editar") is False


class TestPermisosLiderTecnico:
    """Pruebas de permisos del rol LIDER_TECNICO."""

    def test_lider_puede_ver_logs(self, lider_tecnico):
        assert tiene_permiso(lider_tecnico, "logs:ver") is True

    def test_lider_puede_ingestar_corpus(self, lider_tecnico):
        assert tiene_permiso(lider_tecnico, "corpus:ingestar") is True

    def test_lider_no_puede_crear_usuarios(self, lider_tecnico):
        assert tiene_permiso(lider_tecnico, "usuarios:crear") is False

    def test_lider_no_puede_aprobar_hallazgos(self, lider_tecnico):
        assert tiene_permiso(lider_tecnico, "hallazgos:aprobar") is False


# ---------------------------------------------------------------------------
# Tests de segregación por dirección técnica
# ---------------------------------------------------------------------------
class TestSegregacionDireccion:
    """Pruebas de segregación de acceso por dirección técnica (DES / DVF)."""

    def test_auditor_des_accede_a_des(self, auditor_des):
        assert puede_acceder_direccion(auditor_des, "DES") is True

    def test_auditor_des_no_accede_a_dvf(self, auditor_des):
        assert puede_acceder_direccion(auditor_des, "DVF") is False

    def test_auditor_dvf_accede_a_dvf(self, auditor_dvf):
        assert puede_acceder_direccion(auditor_dvf, "DVF") is True

    def test_auditor_dvf_no_accede_a_des(self, auditor_dvf):
        assert puede_acceder_direccion(auditor_dvf, "DES") is False

    def test_director_des_accede_a_des(self, director_des):
        assert puede_acceder_direccion(director_des, "DES") is True

    def test_director_des_no_accede_a_dvf(self, director_des):
        assert puede_acceder_direccion(director_des, "DVF") is False

    def test_admin_accede_a_cualquier_direccion(self, admin):
        assert puede_acceder_direccion(admin, "DES") is True
        assert puede_acceder_direccion(admin, "DVF") is True

    def test_lider_tecnico_accede_a_cualquier_direccion(self, lider_tecnico):
        assert puede_acceder_direccion(lider_tecnico, "DES") is True
        assert puede_acceder_direccion(lider_tecnico, "DVF") is True

    def test_coordinador_accede_a_cualquier_direccion(self, coordinador):
        assert puede_acceder_direccion(coordinador, "DES") is True
        assert puede_acceder_direccion(coordinador, "DVF") is True

    def test_observador_accede_a_cualquier_direccion(self, observador):
        assert puede_acceder_direccion(observador, "DES") is True
        assert puede_acceder_direccion(observador, "DVF") is True
