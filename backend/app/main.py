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
motor_asincrono = create_async_engine(
    configuracion.DATABASE_URL,
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
    docs_url="/docs" if configuracion.DEBUG else None,
    redoc_url="/redoc" if configuracion.DEBUG else None,
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


# ── Registro de routers ──────────────────────────────────────────────────────
from app.api.auth_routes import enrutador as enrutador_auth  # noqa: E402

app.include_router(enrutador_auth, prefix="/api/auth", tags=["Autenticacion"])

from app.api.chat_routes import enrutador as enrutador_chat  # noqa: E402
from app.api.document_routes import enrutador as enrutador_documentos  # noqa: E402
from app.api.audit_routes import enrutador as enrutador_auditorias  # noqa: E402
from app.api.hallazgo_routes import enrutador as enrutador_hallazgos  # noqa: E402
from app.api.format_routes import enrutador as enrutador_formatos  # noqa: E402
from app.api.rag_routes import enrutador as enrutador_rag  # noqa: E402
from app.api.integracion_routes import enrutador as enrutador_integraciones  # noqa: E402
from app.api.analytics_routes import enrutador as enrutador_analitica  # noqa: E402
from app.api.admin_routes import enrutador as enrutador_admin  # noqa: E402
from app.api.agent_ws import enrutador as enrutador_ws  # noqa: E402

app.include_router(enrutador_chat, prefix="/api/chat", tags=["Chat"])
app.include_router(enrutador_documentos, prefix="/api/documentos", tags=["Documentos"])
app.include_router(enrutador_auditorias, prefix="/api/auditorias", tags=["Auditorias"])
app.include_router(enrutador_hallazgos, prefix="/api/hallazgos", tags=["Hallazgos"])
app.include_router(enrutador_formatos, prefix="/api/formatos", tags=["Formatos CGR"])
app.include_router(enrutador_rag, prefix="/api/rag", tags=["RAG"])
app.include_router(enrutador_integraciones, prefix="/api/integraciones", tags=["Integraciones"])
app.include_router(enrutador_analitica, prefix="/api/analytics", tags=["Analitica"])
app.include_router(enrutador_admin, prefix="/api/admin", tags=["Administracion"])
app.include_router(enrutador_ws, prefix="/api/ws", tags=["WebSocket Agente"])


# ── Endpoints de salud ────────────────────────────────────────────────────────
@app.get("/salud", tags=["Sistema"])
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
