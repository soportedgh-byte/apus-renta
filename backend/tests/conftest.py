"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: tests/conftest.py
Proposito: Fixtures basicos de pytest para pruebas del backend —
           base de datos en memoria, cliente HTTP y usuario de prueba
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.base import Base
from app.models.usuario import DireccionUsuario, RolUsuario, Usuario

# ── Configuracion de base de datos de prueba (SQLite asincrono) ───────────────
URL_BD_PRUEBA: str = "sqlite+aiosqlite:///./test_cecilia.db"

motor_prueba = create_async_engine(
    URL_BD_PRUEBA,
    echo=False,
    connect_args={"check_same_thread": False},
)

fabrica_sesiones_prueba: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=motor_prueba,
    class_=AsyncSession,
    expire_on_commit=False,
)

contexto_cripto = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Fixture: crear y destruir tablas ──────────────────────────────────────────
@pytest_asyncio.fixture(autouse=True)
async def preparar_base_datos() -> AsyncGenerator[None, None]:
    """Crea todas las tablas antes de cada prueba y las destruye al finalizar."""
    async with motor_prueba.begin() as conexion:
        await conexion.run_sync(Base.metadata.create_all)
    yield
    async with motor_prueba.begin() as conexion:
        await conexion.run_sync(Base.metadata.drop_all)


# ── Fixture: sesion de base de datos ──────────────────────────────────────────
@pytest_asyncio.fixture
async def sesion_db() -> AsyncGenerator[AsyncSession, None]:
    """Provee una sesion de base de datos asincrona para pruebas."""
    async with fabrica_sesiones_prueba() as sesion:
        yield sesion


# ── Fixture: usuario de prueba ────────────────────────────────────────────────
@pytest_asyncio.fixture
async def usuario_prueba(sesion_db: AsyncSession) -> Usuario:
    """Crea un usuario auditor DES de prueba en la base de datos."""
    usuario = Usuario(
        usuario="auditor_prueba",
        nombre_completo="Auditor de Prueba DES",
        email="auditor.prueba@contraloria.gov.co",
        rol=RolUsuario.AUDITOR_DES,
        direccion=DireccionUsuario.DES,
        password_hash=contexto_cripto.hash("contrasena_segura_123"),
        activo=True,
    )
    sesion_db.add(usuario)
    await sesion_db.commit()
    await sesion_db.refresh(usuario)
    return usuario


# ── Fixture: usuario administrador TIC ────────────────────────────────────────
@pytest_asyncio.fixture
async def usuario_admin(sesion_db: AsyncSession) -> Usuario:
    """Crea un usuario administrador TIC de prueba en la base de datos."""
    usuario = Usuario(
        usuario="admin_tic_prueba",
        nombre_completo="Administrador TIC de Prueba",
        email="admin.tic.prueba@contraloria.gov.co",
        rol=RolUsuario.ADMIN_TIC,
        direccion=None,
        password_hash=contexto_cripto.hash("admin_seguro_456"),
        activo=True,
    )
    sesion_db.add(usuario)
    await sesion_db.commit()
    await sesion_db.refresh(usuario)
    return usuario


# ── Fixture: token JWT de prueba ──────────────────────────────────────────────
@pytest.fixture
def token_prueba(usuario_prueba: Usuario) -> str:
    """Genera un token JWT de acceso para el usuario de prueba."""
    from app.auth.jwt_handler import crear_token_acceso

    datos: dict[str, Any] = {
        "sub": str(usuario_prueba.id),
        "usuario": usuario_prueba.usuario,
        "rol": usuario_prueba.rol.value,
        "direccion": usuario_prueba.direccion.value if usuario_prueba.direccion else None,
    }
    return crear_token_acceso(datos)


# ── Fixture: cliente HTTP asincrono ───────────────────────────────────────────
@pytest_asyncio.fixture
async def cliente_http() -> AsyncGenerator[AsyncClient, None]:
    """Provee un cliente HTTP asincrono configurado contra la app FastAPI.

    Sobreescribe la dependencia de base de datos para usar la BD de prueba.
    """
    from app.main import app, obtener_sesion_db

    async def _obtener_sesion_prueba() -> AsyncGenerator[AsyncSession, None]:
        async with fabrica_sesiones_prueba() as sesion:
            try:
                yield sesion
                await sesion.commit()
            except Exception:
                await sesion.rollback()
                raise

    app.dependency_overrides[obtener_sesion_db] = _obtener_sesion_prueba

    transporte = ASGITransport(app=app)
    async with AsyncClient(transport=transporte, base_url="http://test") as cliente:
        yield cliente

    app.dependency_overrides.clear()


# ── Fixture: encabezados autenticados ─────────────────────────────────────────
@pytest.fixture
def encabezados_auth(token_prueba: str) -> dict[str, str]:
    """Retorna encabezados HTTP con el token JWT de autenticacion."""
    return {
        "Authorization": f"Bearer {token_prueba}",
        "Content-Type": "application/json",
    }
