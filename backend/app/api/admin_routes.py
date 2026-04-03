"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: app/api/admin_routes.py
Propósito: Endpoints de administración — gestión de usuarios, configuración
           del sistema y consulta de logs operativos
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import obtener_sesion_db

logger = logging.getLogger("cecilia.api.admin")

enrutador = APIRouter()


# ── Roles y direcciones válidos ──────────────────────────────────────────────

ROLES_VALIDOS: set[str] = {
    "auditor_des", "auditor_dvf",
    "profesional_des", "profesional_dvf",
    "director_des", "director_dvf",
    "admin_tic", "observatorio",
}

DIRECCIONES_VALIDAS: set[str] = {"DES", "DVF"}


# ── Esquemas ─────────────────────────────────────────────────────────────────


class SolicitudCrearUsuario(BaseModel):
    """Esquema para crear un nuevo usuario en el sistema."""

    usuario: str = Field(..., min_length=3, max_length=100, description="Nombre de usuario único")
    nombre_completo: str = Field(..., min_length=3, max_length=255, description="Nombre completo del funcionario")
    email: EmailStr = Field(..., description="Correo electrónico institucional")
    rol: str = Field(..., description="Rol del usuario en el sistema")
    direccion: Optional[str] = Field(default=None, description="Dirección misional: DES | DVF (nulo para admin_tic)")
    password: str = Field(..., min_length=12, max_length=128, description="Contraseña (mínimo 12 caracteres)")


class SolicitudActualizarUsuario(BaseModel):
    """Esquema para actualizar datos de un usuario."""

    nombre_completo: Optional[str] = Field(default=None, min_length=3, max_length=255)
    email: Optional[EmailStr] = Field(default=None)
    rol: Optional[str] = Field(default=None)
    direccion: Optional[str] = Field(default=None)


class RespuestaUsuario(BaseModel):
    """Respuesta con datos de un usuario (sin contraseña)."""

    id: int
    usuario: str
    nombre_completo: str
    email: str
    rol: str
    direccion: Optional[str] = None
    activo: bool
    ultimo_acceso: Optional[datetime] = None
    creado_en: datetime
    actualizado_en: datetime


class ConfiguracionSistema(BaseModel):
    """Configuración editable del sistema."""

    llm_modelo: str
    llm_temperatura: float
    llm_max_tokens: int
    rag_chunk_size: int
    rag_chunk_overlap: int
    rag_top_k: int
    embeddings_modelo: str
    embeddings_dimensiones: int
    cors_origenes: list[str]
    debug: bool


class SolicitudActualizarConfig(BaseModel):
    """Esquema para actualizar la configuración del sistema."""

    llm_modelo: Optional[str] = Field(default=None)
    llm_temperatura: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    llm_max_tokens: Optional[int] = Field(default=None, ge=256, le=128000)
    rag_chunk_size: Optional[int] = Field(default=None, ge=100, le=10000)
    rag_chunk_overlap: Optional[int] = Field(default=None, ge=0, le=2000)
    rag_top_k: Optional[int] = Field(default=None, ge=1, le=50)


class RegistroLog(BaseModel):
    """Registro de log del sistema."""

    marca_temporal: datetime
    nivel: str  # DEBUG | INFO | WARNING | ERROR | CRITICAL
    modulo: str
    mensaje: str
    detalle: Optional[str] = None


class RespuestaLogsPaginada(BaseModel):
    """Respuesta paginada de logs del sistema."""

    registros: list[RegistroLog]
    total: int
    pagina: int
    tamano_pagina: int


# ── Dependencia de verificación de rol admin ─────────────────────────────────


async def _obtener_usuario_actual_id() -> int:
    """Dependencia temporal — será reemplazada por auth real."""
    return 1


async def _verificar_admin(usuario_id: int = Depends(_obtener_usuario_actual_id)) -> int:
    """Verifica que el usuario tenga rol admin_tic.

    TODO: Implementar verificación real contra la base de datos.
    Por ahora permite todas las solicitudes.
    """
    # En producción:
    # usuario = await db.get(Usuario, usuario_id)
    # if usuario.rol != RolUsuario.ADMIN_TIC:
    #     raise HTTPException(status_code=403, detail="Acceso restringido a administradores.")
    return usuario_id


# ── Endpoints de gestión de usuarios ─────────────────────────────────────────


@enrutador.get(
    "/usuarios",
    response_model=list[RespuestaUsuario],
    summary="Listar usuarios",
    description="Lista todos los usuarios del sistema con filtros opcionales.",
)
async def listar_usuarios(
    rol: Optional[str] = Query(default=None, description="Filtrar por rol"),
    direccion: Optional[str] = Query(default=None, description="Filtrar por dirección: DES | DVF"),
    activo: Optional[bool] = Query(default=None, description="Filtrar por estado activo"),
    limite: int = Query(default=50, ge=1, le=200),
    desplazamiento: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_verificar_admin),
) -> list[dict[str, Any]]:
    """Lista usuarios del sistema con filtrado y paginación.

    Solo accesible para usuarios con rol admin_tic.
    """

    if rol and rol not in ROLES_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rol inválido. Válidos: {sorted(ROLES_VALIDOS)}",
        )

    if direccion and direccion not in DIRECCIONES_VALIDAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dirección inválida. Válidas: {sorted(DIRECCIONES_VALIDAS)}",
        )

    # TODO: Implementar consulta real a la tabla de usuarios
    logger.info(
        "Admin: listando usuarios (rol=%s, direccion=%s, activo=%s) por usuario=%d",
        rol, direccion, activo, usuario_id,
    )
    return []


@enrutador.post(
    "/usuarios",
    response_model=RespuestaUsuario,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Crea un nuevo usuario en el sistema.",
)
async def crear_usuario(
    solicitud: SolicitudCrearUsuario,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_verificar_admin),
) -> dict[str, Any]:
    """Crea un nuevo usuario validando rol, dirección y unicidad."""

    if solicitud.rol not in ROLES_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rol inválido. Válidos: {sorted(ROLES_VALIDOS)}",
        )

    if solicitud.direccion and solicitud.direccion not in DIRECCIONES_VALIDAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dirección inválida. Válidas: {sorted(DIRECCIONES_VALIDAS)}",
        )

    # Validar que roles no-admin tengan dirección
    if solicitud.rol != "admin_tic" and not solicitud.direccion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Los usuarios con rol distinto a admin_tic deben tener dirección asignada.",
        )

    ahora: datetime = datetime.now(timezone.utc)

    # TODO: Verificar unicidad de usuario/email y hashear contraseña
    # from passlib.hash import bcrypt
    # password_hash = bcrypt.hash(solicitud.password)
    # nuevo_usuario = Usuario(...)
    # db.add(nuevo_usuario)

    logger.info(
        "Admin: usuario creado: usuario=%s, rol=%s, direccion=%s, por admin=%d",
        solicitud.usuario, solicitud.rol, solicitud.direccion, usuario_id,
    )

    return {
        "id": 0,  # Será asignado por la BD
        "usuario": solicitud.usuario,
        "nombre_completo": solicitud.nombre_completo,
        "email": solicitud.email,
        "rol": solicitud.rol,
        "direccion": solicitud.direccion,
        "activo": True,
        "ultimo_acceso": None,
        "creado_en": ahora,
        "actualizado_en": ahora,
    }


@enrutador.put(
    "/usuarios/{id_usuario}",
    response_model=RespuestaUsuario,
    summary="Actualizar usuario",
    description="Actualiza los datos de un usuario existente.",
)
async def actualizar_usuario(
    id_usuario: int,
    solicitud: SolicitudActualizarUsuario,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_verificar_admin),
) -> dict[str, Any]:
    """Actualiza un usuario existente con los campos proporcionados."""

    if solicitud.rol and solicitud.rol not in ROLES_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rol inválido. Válidos: {sorted(ROLES_VALIDOS)}",
        )

    if solicitud.direccion and solicitud.direccion not in DIRECCIONES_VALIDAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dirección inválida. Válidas: {sorted(DIRECCIONES_VALIDAS)}",
        )

    # TODO: Consultar usuario y actualizar
    logger.info("Admin: actualización de usuario %d por admin=%d", id_usuario, usuario_id)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Usuario {id_usuario} no encontrado.",
    )


@enrutador.put(
    "/usuarios/{id_usuario}/activar",
    response_model=RespuestaUsuario,
    summary="Activar/desactivar usuario",
    description="Cambia el estado activo/inactivo de un usuario.",
)
async def activar_desactivar_usuario(
    id_usuario: int,
    activo: bool = Query(..., description="True para activar, False para desactivar"),
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_verificar_admin),
) -> dict[str, Any]:
    """Activa o desactiva un usuario del sistema.

    No se puede desactivar al propio usuario admin que ejecuta la acción.
    """

    if id_usuario == usuario_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puede desactivar su propia cuenta de administrador.",
        )

    # TODO: Consultar usuario y cambiar estado
    logger.info("Admin: cambio de estado activo=%s para usuario %d por admin=%d", activo, id_usuario, usuario_id)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Usuario {id_usuario} no encontrado.",
    )


# ── Endpoints de configuración del sistema ───────────────────────────────────


@enrutador.get(
    "/configuracion",
    response_model=ConfiguracionSistema,
    summary="Obtener configuración del sistema",
    description="Retorna la configuración actual del sistema (sin secretos).",
)
async def obtener_configuracion(
    usuario_id: int = Depends(_verificar_admin),
) -> dict[str, Any]:
    """Retorna los parámetros de configuración editables del sistema.

    No expone secretos (claves API, contraseñas, tokens JWT).
    """

    from app.config import configuracion

    logger.info("Admin: consulta de configuración por usuario=%d", usuario_id)

    return {
        "llm_modelo": configuracion.LLM_MODEL,
        "llm_temperatura": configuracion.LLM_TEMPERATURA,
        "llm_max_tokens": configuracion.LLM_MAX_TOKENS,
        "rag_chunk_size": configuracion.RAG_CHUNK_SIZE,
        "rag_chunk_overlap": configuracion.RAG_CHUNK_OVERLAP,
        "rag_top_k": configuracion.RAG_TOP_K,
        "embeddings_modelo": configuracion.EMBEDDINGS_MODEL,
        "embeddings_dimensiones": configuracion.EMBEDDINGS_DIMENSIONES,
        "cors_origenes": configuracion.CORS_ORIGINS,
        "debug": configuracion.DEBUG,
    }


@enrutador.put(
    "/configuracion",
    response_model=ConfiguracionSistema,
    summary="Actualizar configuración del sistema",
    description="Actualiza parámetros de configuración del sistema en tiempo de ejecución.",
)
async def actualizar_configuracion(
    solicitud: SolicitudActualizarConfig,
    usuario_id: int = Depends(_verificar_admin),
) -> dict[str, Any]:
    """Actualiza la configuración del sistema en tiempo de ejecución.

    Los cambios se aplican en memoria y persisten hasta el reinicio.
    Para cambios permanentes, actualizar variables de entorno o .env.
    """

    from app.config import configuracion

    # Aplicar cambios en memoria
    campos_actualizados: list[str] = []

    if solicitud.llm_modelo is not None:
        configuracion.LLM_MODEL = solicitud.llm_modelo
        campos_actualizados.append("llm_modelo")

    if solicitud.llm_temperatura is not None:
        configuracion.LLM_TEMPERATURA = solicitud.llm_temperatura
        campos_actualizados.append("llm_temperatura")

    if solicitud.llm_max_tokens is not None:
        configuracion.LLM_MAX_TOKENS = solicitud.llm_max_tokens
        campos_actualizados.append("llm_max_tokens")

    if solicitud.rag_chunk_size is not None:
        configuracion.RAG_CHUNK_SIZE = solicitud.rag_chunk_size
        campos_actualizados.append("rag_chunk_size")

    if solicitud.rag_chunk_overlap is not None:
        configuracion.RAG_CHUNK_OVERLAP = solicitud.rag_chunk_overlap
        campos_actualizados.append("rag_chunk_overlap")

    if solicitud.rag_top_k is not None:
        configuracion.RAG_TOP_K = solicitud.rag_top_k
        campos_actualizados.append("rag_top_k")

    logger.info(
        "Admin: configuración actualizada (campos=%s) por usuario=%d",
        campos_actualizados, usuario_id,
    )

    return {
        "llm_modelo": configuracion.LLM_MODEL,
        "llm_temperatura": configuracion.LLM_TEMPERATURA,
        "llm_max_tokens": configuracion.LLM_MAX_TOKENS,
        "rag_chunk_size": configuracion.RAG_CHUNK_SIZE,
        "rag_chunk_overlap": configuracion.RAG_CHUNK_OVERLAP,
        "rag_top_k": configuracion.RAG_TOP_K,
        "embeddings_modelo": configuracion.EMBEDDINGS_MODEL,
        "embeddings_dimensiones": configuracion.EMBEDDINGS_DIMENSIONES,
        "cors_origenes": configuracion.CORS_ORIGINS,
        "debug": configuracion.DEBUG,
    }


# ── Endpoints de logs ────────────────────────────────────────────────────────


@enrutador.get(
    "/logs",
    response_model=RespuestaLogsPaginada,
    summary="Logs del sistema",
    description="Retorna logs operativos del sistema con filtros y paginación.",
)
async def obtener_logs(
    nivel: Optional[str] = Query(
        default=None,
        description="Filtrar por nivel: DEBUG | INFO | WARNING | ERROR | CRITICAL",
    ),
    modulo: Optional[str] = Query(default=None, description="Filtrar por módulo"),
    fecha_inicio: Optional[datetime] = Query(default=None),
    fecha_fin: Optional[datetime] = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    tamano_pagina: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_verificar_admin),
) -> dict[str, Any]:
    """Retorna logs del sistema con filtrado y paginación.

    Incluye logs de operaciones, errores, advertencias y eventos
    del sistema para monitoreo y depuración.
    """

    niveles_validos: set[str] = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if nivel and nivel.upper() not in niveles_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Nivel inválido. Válidos: {sorted(niveles_validos)}",
        )

    # TODO: Implementar consulta real a logs almacenados
    logger.info(
        "Admin: consulta de logs (nivel=%s, modulo=%s, pagina=%d) por usuario=%d",
        nivel, modulo, pagina, usuario_id,
    )

    return {
        "registros": [],
        "total": 0,
        "pagina": pagina,
        "tamano_pagina": tamano_pagina,
    }
