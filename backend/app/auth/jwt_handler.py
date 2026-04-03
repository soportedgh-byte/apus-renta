"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/auth/jwt_handler.py
Proposito: Creacion y verificacion de tokens JWT para autenticacion
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.config import configuracion


def crear_token_acceso(
    datos: dict[str, Any],
    expiracion_minutos: int | None = None,
) -> str:
    """Crea un token JWT de acceso con los datos proporcionados.

    Args:
        datos: Diccionario con los claims del token (sub, rol, direccion, etc.).
        expiracion_minutos: Minutos de validez del token. Si es None, usa la
            configuracion por defecto.

    Returns:
        Token JWT codificado como cadena.
    """
    datos_a_codificar: dict[str, Any] = datos.copy()
    minutos: int = expiracion_minutos or configuracion.JWT_EXPIRACION_MINUTOS
    fecha_expiracion: datetime = datetime.now(timezone.utc) + timedelta(minutes=minutos)

    datos_a_codificar.update({
        "exp": fecha_expiracion,
        "iat": datetime.now(timezone.utc),
        "tipo": "acceso",
    })

    token: str = jwt.encode(
        datos_a_codificar,
        configuracion.JWT_SECRET_KEY,
        algorithm=configuracion.JWT_ALGORITHM,
    )
    return token


def crear_token_refresco(datos: dict[str, Any]) -> str:
    """Crea un token JWT de refresco con mayor duracion.

    Args:
        datos: Diccionario con los claims minimos del token (sub).

    Returns:
        Token JWT de refresco codificado como cadena.
    """
    datos_a_codificar: dict[str, Any] = datos.copy()
    fecha_expiracion: datetime = datetime.now(timezone.utc) + timedelta(
        days=configuracion.JWT_REFRESH_EXPIRACION_DIAS
    )

    datos_a_codificar.update({
        "exp": fecha_expiracion,
        "iat": datetime.now(timezone.utc),
        "tipo": "refresco",
    })

    token: str = jwt.encode(
        datos_a_codificar,
        configuracion.JWT_SECRET_KEY,
        algorithm=configuracion.JWT_ALGORITHM,
    )
    return token


def verificar_token(token: str) -> dict[str, Any]:
    """Verifica y decodifica un token JWT.

    Args:
        token: Token JWT a verificar.

    Returns:
        Diccionario con los claims decodificados del token.

    Raises:
        JWTError: Si el token es invalido, esta expirado o la firma no coincide.
    """
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            configuracion.JWT_SECRET_KEY,
            algorithms=[configuracion.JWT_ALGORITHM],
        )
        return payload
    except JWTError as error:
        raise JWTError(f"Token invalido o expirado: {error}") from error
