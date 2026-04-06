"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/main.py
Proposito: Punto de entrada principal de la API FastAPI — configuracion de rutas,
           middleware, instrumentacion y ciclo de vida de la aplicacion
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import __version__
from app.config import configuracion


# ── Motor de base de datos asincrono ──────────────────────────────────────────
# Convertir URL postgresql:// a postgresql+asyncpg:// para driver asíncrono
_url_bd = configuracion.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

motor_asincrono = create_async_engine(
    _url_bd,
    echo=configuracion.DEBUG,
    pool_size=configuracion.DB_POOL_SIZE,
    max_overflow=configuracion.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
)

fabrica_sesiones: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=motor_asincrono,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def obtener_sesion_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependencia FastAPI que provee una sesion de base de datos asincrona."""
    async with fabrica_sesiones() as sesion:
        try:
            yield sesion
            await sesion.commit()
        except Exception:
            await sesion.rollback()
            raise


# ── Ciclo de vida de la aplicacion ────────────────────────────────────────────
@asynccontextmanager
async def ciclo_de_vida(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gestiona la conexion a la base de datos y recursos al iniciar/detener."""
    # Inicio: verificar conexion a la base de datos
    async with motor_asincrono.begin() as conexion:
        await conexion.execute(
            __import__("sqlalchemy").text("SELECT 1")
        )

    yield

    # Cierre: liberar conexiones del pool
    await motor_asincrono.dispose()


# ── Creacion de la aplicacion FastAPI ─────────────────────────────────────────
app = FastAPI(
    title="CecilIA v2 — API de Control Fiscal",
    description=(
        "Sistema de Inteligencia Artificial para asistencia en procesos de "
        "control fiscal de la Contraloria General de la Republica de Colombia."
    ),
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=ciclo_de_vida,
)


# ── Middleware CORS ───────────────────────────────────────────────────────────
origenes_permitidos: list[str] = configuracion.CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes_permitidos,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Instrumentacion OpenTelemetry ─────────────────────────────────────────────
def configurar_telemetria() -> None:
    """Configura el proveedor de trazas de OpenTelemetry."""
    recurso = Resource.create(
        attributes={
            "service.name": "cecilia-v2-api",
            "service.version": __version__,
        }
    )
    proveedor_trazas = TracerProvider(resource=recurso)
    procesador = BatchSpanProcessor(ConsoleSpanExporter())
    proveedor_trazas.add_span_processor(procesador)
    trace.set_tracer_provider(proveedor_trazas)


configurar_telemetria()
FastAPIInstrumentor.instrument_app(app)


# ── Registro de routers (carga segura) ───────────────────────────────────────
import importlib
import logging

_logger = logging.getLogger("cecilia.startup")

_RUTAS: list[tuple[str, str, str]] = [
    ("app.api.auth_routes", "/api/auth", "Autenticacion"),
    ("app.api.chat_routes", "/api/chat", "Chat"),
    ("app.api.document_routes", "/api/documentos", "Documentos"),
    ("app.api.audit_routes", "/api/auditorias", "Auditorias"),
    ("app.api.hallazgo_routes", "/api/hallazgos", "Hallazgos"),
    ("app.api.format_routes", "/api/formatos", "Formatos CGR"),
    ("app.api.rag_routes", "/api/rag", "RAG"),
    ("app.api.config_routes", "/api/config", "Configuracion"),
    ("app.api.integracion_routes", "/api/integraciones", "Integraciones"),
    ("app.api.analytics_routes", "/api/analytics", "Analitica"),
    ("app.api.admin_routes", "/api/admin", "Administracion"),
    ("app.api.agent_ws", "/api/ws", "WebSocket Agente"),
    ("app.api.capacitacion_routes", "/api/capacitacion", "Capacitacion"),
    ("app.api.observatorio_routes", "/api/observatorio", "Observatorio TIC"),
    ("app.api.finetuning_routes", "/api/modelos", "Modelos y Fine-tuning"),
    ("app.api.sesion_routes", "/api/sesion", "Memoria de Sesion"),
]

for _modulo, _prefijo, _tag in _RUTAS:
    try:
        _mod = importlib.import_module(_modulo)
        app.include_router(_mod.enrutador, prefix=_prefijo, tags=[_tag])
        _logger.info("Router registrado: %s -> %s", _tag, _prefijo)
    except Exception as _exc:
        _logger.warning("No se pudo cargar %s: %s", _modulo, _exc)


# ── Endpoints de salud ────────────────────────────────────────────────────────
@app.get("/salud", tags=["Sistema"])
@app.get("/api/health", tags=["Sistema"])
async def verificar_salud() -> dict[str, str]:
    """Endpoint de verificacion de salud del servicio."""
    return {
        "estado": "saludable",
        "version": __version__,
        "servicio": "CecilIA v2 — API de Control Fiscal",
    }


@app.get("/", tags=["Sistema"])
async def raiz() -> dict[str, str]:
    """Redirige a la documentacion o informa del estado del API."""
    return {
        "mensaje": "CecilIA v2 — API de Control Fiscal activa",
        "documentacion": "/docs",
        "salud": "/salud",
    }
