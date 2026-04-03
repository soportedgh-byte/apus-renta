"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: alembic/env.py
Propósito: Configuración del entorno Alembic con soporte asíncrono —
           conecta a PostgreSQL usando asyncpg e importa todos los modelos
           para detección automática de cambios en el esquema
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path
from typing import Any

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Agregar el directorio backend al path para importar los módulos de la aplicación
directorio_backend: Path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(directorio_backend))

# Importar la configuración de la aplicación para obtener la URL de la base de datos
from app.config import configuracion  # noqa: E402

# Importar Base y TODOS los modelos para que Alembic detecte las tablas automáticamente
from app.models import Base  # noqa: E402
from app.models import (  # noqa: E402, F401
    Alerta,
    Auditoria,
    Conversacion,
    Documento,
    FormatoGenerado,
    Hallazgo,
    LogTrazabilidad,
    Mensaje,
    ProyectoAuditoria,
    Usuario,
)

# Objeto de configuración de Alembic (lee alembic.ini)
configuracion_alembic = context.config

# Configurar logging desde alembic.ini
if configuracion_alembic.config_file_name is not None:
    fileConfig(configuracion_alembic.config_file_name)

# Metadata de los modelos para autogeneración de migraciones
target_metadata = Base.metadata

# Establecer la URL de la base de datos desde la configuración de la aplicación
# Usa la URL síncrona para Alembic offline y la asíncrona para online
url_sincrona: str = configuracion.DATABASE_URL_SYNC
url_asincrona: str = configuracion.DATABASE_URL


def ejecutar_migraciones_offline() -> None:
    """Ejecuta migraciones en modo 'offline' (genera SQL sin conectar a la BD).

    En este modo, Alembic genera las sentencias SQL necesarias
    sin ejecutarlas. Útil para revisión y aplicación manual.
    """
    context.configure(
        url=url_sincrona,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def _ejecutar_migraciones_sync(conexion: Connection) -> None:
    """Callback síncrono para ejecutar migraciones dentro de una conexión.

    Args:
        conexion: Conexión activa a la base de datos.
    """
    context.configure(
        connection=conexion,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        # Incluir nombres de esquema en autogeneración
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def ejecutar_migraciones_online() -> None:
    """Ejecuta migraciones en modo 'online' con motor asíncrono (asyncpg).

    Crea un motor asíncrono, obtiene una conexión y ejecuta
    las migraciones dentro de esa conexión.
    """
    configuracion_engine: dict[str, Any] = {
        "sqlalchemy.url": url_asincrona,
        "sqlalchemy.pool_class": "sqlalchemy.pool.NullPool",
    }

    # Sobrescribir la configuración del motor desde alembic.ini con valores dinámicos
    configuracion_alembic.set_section_option(
        configuracion_alembic.config_ini_section,
        "sqlalchemy.url",
        url_asincrona,
    )

    motor_conectar = async_engine_from_config(
        configuracion_engine,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with motor_conectar.connect() as conexion:
        await conexion.run_sync(_ejecutar_migraciones_sync)

    await motor_conectar.dispose()


# Determinar el modo de ejecución (offline u online)
if context.is_offline_mode():
    ejecutar_migraciones_offline()
else:
    asyncio.run(ejecutar_migraciones_online())
