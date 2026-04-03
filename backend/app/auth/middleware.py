"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/auth/middleware.py
Proposito: Middleware de autenticacion — extraccion y validacion de JWT
           desde el encabezado Authorization
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_handler import verificar_token
from app.models.usuario import Usuario

# Esquema de seguridad Bearer para extraer el token del encabezado Authorization
esquema_bearer = HTTPBearer(
    scheme_name="Token JWT",
    description="Token de acceso JWT obtenido en /api/auth/login",
    auto_error=True,
)


async def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(esquema_bearer),
    sesion: AsyncSession = Depends(_obtener_sesion_placeholder),
) -> Usuario:
    """Dependencia FastAPI que extrae y valida el usuario desde el token JWT.

    Flujo:
        1. Extrae el token del encabezado Authorization: Bearer <token>
        2. Decodifica y verifica el token JWT
        3. Busca al usuario en la base de datos
        4. Verifica que el usuario este activo

    Args:
        credenciales: Credenciales HTTP Bearer con el token JWT.
        sesion: Sesion asincrona de base de datos.

    Returns:
        Instancia del modelo Usuario autenticado.

    Raises:
        HTTPException 401: Si el token es invalido, el usuario no existe o esta inactivo.
    """
    token: str = credenciales.credentials

    # Paso 1: Verificar el token JWT
    try:
        payload: dict[str, Any] = verificar_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso invalido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Paso 2: Extraer el identificador del usuario
    usuario_id_str: str | None = payload.get("sub")
    if usuario_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no contiene identificador de usuario.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Paso 3: Buscar al usuario en la base de datos
    try:
        usuario_id: int = int(usuario_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identificador de usuario invalido en el token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    resultado = await sesion.execute(
        select(Usuario).where(Usuario.id == usuario_id)
    )
    usuario: Usuario | None = resultado.scalar_one_or_none()

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado en el sistema.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Paso 4: Verificar que el usuario este activo
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La cuenta de usuario esta desactivada. Contacte al administrador.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return usuario


async def _obtener_sesion_placeholder() -> None:  # type: ignore[return]
    """Placeholder para la dependencia de sesion de base de datos.

    En produccion, este placeholder se reemplaza con la dependencia real
    `obtener_sesion_db` de app.main al registrar las rutas. Esto evita
    importaciones circulares entre main.py y middleware.py.

    La inyeccion real se hace en app/api/auth_routes.py mediante:
        Depends(obtener_sesion_db)
    """
    raise NotImplementedError(
        "Esta dependencia debe ser sobreescrita con obtener_sesion_db de app.main"
    )
