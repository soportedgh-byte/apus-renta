"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/auth/__init__.py
Proposito: Inicializacion del paquete de autenticacion y autorizacion
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from app.auth.jwt_handler import crear_token_acceso, verificar_token
from app.auth.rbac import RequiereDireccion, RequierePermiso, verificar_direccion, verificar_permiso
from app.auth.roles import ROLES

__all__: list[str] = [
    "ROLES",
    "crear_token_acceso",
    "verificar_token",
    "verificar_permiso",
    "verificar_direccion",
    "RequierePermiso",
    "RequiereDireccion",
]
