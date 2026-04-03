"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/auth/rbac.py
Proposito: Control de acceso basado en roles (RBAC) — verificacion de permisos
           y restricciones por direccion misional
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from typing import Any

from fastapi import Depends, HTTPException, status

from app.auth.middleware import obtener_usuario_actual
from app.auth.roles import ROLES
from app.models.usuario import Usuario


def verificar_permiso(usuario: Usuario, permiso: str) -> bool:
    """Verifica si un usuario tiene un permiso especifico segun su rol.

    Args:
        usuario: Instancia del modelo Usuario.
        permiso: Cadena con el nombre del permiso a verificar.

    Returns:
        True si el usuario tiene el permiso, False en caso contrario.
    """
    rol_config: dict[str, Any] | None = ROLES.get(usuario.rol.value)
    if rol_config is None:
        return False

    permisos: list[str] = rol_config.get("permisos", [])
    return permiso in permisos


def verificar_direccion(usuario: Usuario, direccion: str) -> bool:
    """Verifica si un usuario pertenece a una direccion misional especifica.

    Los administradores TIC tienen acceso a todas las direcciones.

    Args:
        usuario: Instancia del modelo Usuario.
        direccion: Codigo de la direccion (DES, DVF).

    Returns:
        True si el usuario pertenece a la direccion o es admin_tic.
    """
    # Los administradores TIC tienen acceso transversal
    if usuario.rol.value == "admin_tic":
        return True

    if usuario.direccion is None:
        return False

    return usuario.direccion.value == direccion


class RequierePermiso:
    """Dependencia FastAPI que exige un permiso especifico al usuario.

    Uso:
        @router.get("/ruta", dependencies=[Depends(RequierePermiso("hallazgos_crear"))])
        async def mi_endpoint():
            ...
    """

    def __init__(self, permiso: str) -> None:
        self.permiso: str = permiso

    async def __call__(
        self,
        usuario: Usuario = Depends(obtener_usuario_actual),
    ) -> Usuario:
        """Verifica el permiso y retorna el usuario autenticado.

        Args:
            usuario: Usuario extraido del token JWT.

        Returns:
            El usuario autenticado si tiene el permiso.

        Raises:
            HTTPException 403: Si el usuario no tiene el permiso requerido.
        """
        if not verificar_permiso(usuario, self.permiso):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Permiso insuficiente. Se requiere '{self.permiso}' "
                    f"para acceder a este recurso. Rol actual: '{usuario.rol.value}'."
                ),
            )
        return usuario


class RequiereDireccion:
    """Dependencia FastAPI que exige pertenencia a una direccion misional.

    Uso:
        @router.get("/ruta", dependencies=[Depends(RequiereDireccion("DES"))])
        async def mi_endpoint():
            ...
    """

    def __init__(self, direccion: str) -> None:
        self.direccion: str = direccion

    async def __call__(
        self,
        usuario: Usuario = Depends(obtener_usuario_actual),
    ) -> Usuario:
        """Verifica la direccion y retorna el usuario autenticado.

        Args:
            usuario: Usuario extraido del token JWT.

        Returns:
            El usuario autenticado si pertenece a la direccion.

        Raises:
            HTTPException 403: Si el usuario no pertenece a la direccion requerida.
        """
        if not verificar_direccion(usuario, self.direccion):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Acceso restringido a la direccion '{self.direccion}'. "
                    f"Direccion del usuario: '{usuario.direccion}'."
                ),
            )
        return usuario
