"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/api/auth_routes.py
Proposito: Endpoints de autenticacion — login, refresh, perfil y logout
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_handler import crear_token_acceso, crear_token_refresco, verificar_token
from app.auth.roles import ROLES
from app.models.usuario import Usuario

enrutador = APIRouter()

# ── Contexto de hashing de contrasenas ────────────────────────────────────────
contexto_cripto = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Esquema Bearer para endpoints protegidos ──────────────────────────────────
esquema_bearer = HTTPBearer(auto_error=True)


# ── Esquemas Pydantic de solicitud/respuesta ──────────────────────────────────
class SolicitudLogin(BaseModel):
    """Esquema de solicitud de inicio de sesion."""

    usuario: str = Field(..., min_length=3, max_length=100, description="Nombre de usuario")
    contrasena: str = Field(..., min_length=6, max_length=128, description="Contrasena")


class RespuestaLogin(BaseModel):
    """Esquema de respuesta de inicio de sesion exitoso."""

    token_acceso: str
    token_refresco: str
    tipo_token: str = "Bearer"
    expira_en_minutos: int
    usuario: dict[str, Any]


class SolicitudRefresh(BaseModel):
    """Esquema de solicitud de refresco de token."""

    token_refresco: str = Field(..., description="Token de refresco vigente")


class RespuestaRefresh(BaseModel):
    """Esquema de respuesta de refresco de token."""

    token_acceso: str
    tipo_token: str = "Bearer"
    expira_en_minutos: int


class RespuestaPerfil(BaseModel):
    """Esquema de respuesta del perfil de usuario."""

    id: int
    usuario: str
    nombre_completo: str
    email: str
    rol: str
    direccion: str | None
    activo: bool
    modulos: list[str]
    permisos: list[str]
    acciones_rapidas: list[str]


class RespuestaLogout(BaseModel):
    """Esquema de respuesta de cierre de sesion."""

    mensaje: str


# ── Dependencia de sesion de base de datos ────────────────────────────────────
# Se importa aqui para evitar importaciones circulares con main.py
def _obtener_sesion_db_dep() -> Any:
    """Retorna la dependencia de sesion de base de datos de main.py.

    Se resuelve en tiempo de ejecucion para evitar importaciones circulares.
    """
    from app.main import obtener_sesion_db
    return obtener_sesion_db


# ── POST /api/auth/login ─────────────────────────────────────────────────────
@enrutador.post(
    "/login",
    response_model=RespuestaLogin,
    summary="Iniciar sesion",
    description="Autentica al usuario y retorna tokens JWT junto con informacion del rol.",
)
async def login(
    solicitud: SolicitudLogin,
    sesion: AsyncSession = Depends(lambda: _obtener_sesion_db_dep()),
) -> RespuestaLogin:
    """Autentica un usuario con sus credenciales.

    Flujo:
        1. Busca al usuario por nombre de usuario
        2. Verifica la contrasena con bcrypt
        3. Genera token de acceso y de refresco
        4. Actualiza la fecha de ultimo acceso
        5. Retorna tokens y datos del perfil con permisos del rol
    """
    # Resolver la dependencia de sesion correctamente
    from app.main import obtener_sesion_db
    async for sesion_real in obtener_sesion_db():
        sesion = sesion_real
        break

    # Buscar usuario
    resultado = await sesion.execute(
        select(Usuario).where(Usuario.usuario == solicitud.usuario)
    )
    usuario_db: Usuario | None = resultado.scalar_one_or_none()

    if usuario_db is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas. Verifique su usuario y contrasena.",
        )

    # Verificar contrasena
    if not contexto_cripto.verify(solicitud.contrasena, usuario_db.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas. Verifique su usuario y contrasena.",
        )

    # Verificar que el usuario este activo
    if not usuario_db.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta esta desactivada. Contacte al administrador.",
        )

    # Generar tokens
    datos_token: dict[str, Any] = {
        "sub": str(usuario_db.id),
        "usuario": usuario_db.usuario,
        "rol": usuario_db.rol.value,
        "direccion": usuario_db.direccion.value if usuario_db.direccion else None,
    }

    from app.config import configuracion

    token_acceso: str = crear_token_acceso(datos_token)
    token_refresco: str = crear_token_refresco({"sub": str(usuario_db.id)})

    # Actualizar ultimo acceso
    await sesion.execute(
        update(Usuario)
        .where(Usuario.id == usuario_db.id)
        .values(ultimo_acceso=datetime.now(timezone.utc))
    )
    await sesion.commit()

    # Obtener configuracion del rol
    rol_config: dict[str, Any] = ROLES.get(usuario_db.rol.value, {})

    return RespuestaLogin(
        token_acceso=token_acceso,
        token_refresco=token_refresco,
        tipo_token="Bearer",
        expira_en_minutos=configuracion.JWT_EXPIRACION_MINUTOS,
        usuario={
            "id": usuario_db.id,
            "usuario": usuario_db.usuario,
            "nombre_completo": usuario_db.nombre_completo,
            "email": usuario_db.email,
            "rol": usuario_db.rol.value,
            "direccion": usuario_db.direccion.value if usuario_db.direccion else None,
            "modulos": rol_config.get("modulos", []),
            "permisos": rol_config.get("permisos", []),
            "acciones_rapidas": rol_config.get("acciones_rapidas", []),
        },
    )


# ── POST /api/auth/refresh ───────────────────────────────────────────────────
@enrutador.post(
    "/refresh",
    response_model=RespuestaRefresh,
    summary="Refrescar token de acceso",
    description="Genera un nuevo token de acceso a partir de un token de refresco vigente.",
)
async def refresh(solicitud: SolicitudRefresh) -> RespuestaRefresh:
    """Refresca el token de acceso usando un token de refresco valido.

    Args:
        solicitud: Contiene el token de refresco a validar.

    Returns:
        Nuevo token de acceso con su tiempo de expiracion.
    """
    try:
        payload: dict[str, Any] = verificar_token(solicitud.token_refresco)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresco invalido o expirado.",
        )

    # Verificar que sea un token de refresco
    if payload.get("tipo") != "refresco":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token proporcionado no es un token de refresco.",
        )

    usuario_id: str | None = payload.get("sub")
    if usuario_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresco no contiene identificador de usuario.",
        )

    # Buscar usuario para obtener datos actualizados del rol
    from app.main import obtener_sesion_db
    async for sesion in obtener_sesion_db():
        resultado = await sesion.execute(
            select(Usuario).where(Usuario.id == int(usuario_id))
        )
        usuario_db: Usuario | None = resultado.scalar_one_or_none()
        break

    if usuario_db is None or not usuario_db.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o desactivado.",
        )

    datos_token: dict[str, Any] = {
        "sub": str(usuario_db.id),
        "usuario": usuario_db.usuario,
        "rol": usuario_db.rol.value,
        "direccion": usuario_db.direccion.value if usuario_db.direccion else None,
    }

    from app.config import configuracion

    nuevo_token: str = crear_token_acceso(datos_token)

    return RespuestaRefresh(
        token_acceso=nuevo_token,
        tipo_token="Bearer",
        expira_en_minutos=configuracion.JWT_EXPIRACION_MINUTOS,
    )


# ── GET /api/auth/me ─────────────────────────────────────────────────────────
@enrutador.get(
    "/me",
    response_model=RespuestaPerfil,
    summary="Perfil del usuario actual",
    description="Retorna la informacion del usuario autenticado con sus permisos y modulos.",
)
async def perfil_usuario(
    credenciales: HTTPAuthorizationCredentials = Depends(esquema_bearer),
) -> RespuestaPerfil:
    """Obtiene el perfil completo del usuario autenticado.

    Args:
        credenciales: Token JWT del encabezado Authorization.

    Returns:
        Perfil del usuario con sus permisos, modulos y acciones rapidas.
    """
    try:
        payload: dict[str, Any] = verificar_token(credenciales.credentials)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso invalido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    usuario_id: str | None = payload.get("sub")
    if usuario_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no contiene identificador de usuario.",
        )

    from app.main import obtener_sesion_db
    async for sesion in obtener_sesion_db():
        resultado = await sesion.execute(
            select(Usuario).where(Usuario.id == int(usuario_id))
        )
        usuario_db: Usuario | None = resultado.scalar_one_or_none()
        break

    if usuario_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )

    rol_config: dict[str, Any] = ROLES.get(usuario_db.rol.value, {})

    return RespuestaPerfil(
        id=usuario_db.id,
        usuario=usuario_db.usuario,
        nombre_completo=usuario_db.nombre_completo,
        email=usuario_db.email,
        rol=usuario_db.rol.value,
        direccion=usuario_db.direccion.value if usuario_db.direccion else None,
        activo=usuario_db.activo,
        modulos=rol_config.get("modulos", []),
        permisos=rol_config.get("permisos", []),
        acciones_rapidas=rol_config.get("acciones_rapidas", []),
    )


# ── POST /api/auth/logout ────────────────────────────────────────────────────
@enrutador.post(
    "/logout",
    response_model=RespuestaLogout,
    summary="Cerrar sesion",
    description="Invalida la sesion del usuario en Redis.",
)
async def logout(
    credenciales: HTTPAuthorizationCredentials = Depends(esquema_bearer),
) -> RespuestaLogout:
    """Cierra la sesion del usuario invalidando el token en Redis.

    Args:
        credenciales: Token JWT a invalidar.

    Returns:
        Mensaje de confirmacion del cierre de sesion.
    """
    try:
        payload: dict[str, Any] = verificar_token(credenciales.credentials)
    except JWTError:
        # Si el token ya es invalido, el logout igualmente es exitoso
        return RespuestaLogout(mensaje="Sesion cerrada correctamente.")

    # Invalidar el token en Redis (blacklist)
    try:
        import redis.asyncio as aioredis
        from app.config import configuracion

        cliente_redis = aioredis.from_url(configuracion.REDIS_URL)
        token_id: str = credenciales.credentials[-16:]  # Ultimos 16 chars como ID
        expiracion: int = payload.get("exp", 0)
        tiempo_restante: int = max(expiracion - int(__import__("time").time()), 0)

        if tiempo_restante > 0:
            await cliente_redis.setex(
                f"token_invalido:{token_id}",
                tiempo_restante,
                "invalidado",
            )
        await cliente_redis.aclose()
    except Exception:
        # Si Redis no esta disponible, el logout aun se considera exitoso
        # El token expirara naturalmente
        pass

    return RespuestaLogout(mensaje="Sesion cerrada correctamente.")
