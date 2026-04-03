"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/config.py
Proposito: Configuracion centralizada de la aplicacion mediante variables de entorno.
           Incluye parametros eticos y criterios de calidad de IA.
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracion(BaseSettings):
    """Configuracion principal del sistema CecilIA v2.

    Todas las variables se leen desde el entorno o un archivo .env.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── Metadata de la aplicacion ─────────────────────────────────────────
    NOMBRE_APP: str = "CecilIA v2"
    VERSION: str = "2.0.0"
    DESCRIPCION: str = "Sistema de IA para Control Fiscal — CGR Colombia"
    AMBIENTE: str = Field(default="desarrollo", description="desarrollo | staging | produccion")
    DEBUG: bool = Field(default=False, description="Modo depuracion")

    # ── Base de datos PostgreSQL ──────────────────────────────────────────
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://cecilia:cecilia_dev@localhost:5432/cecilia_v2",
        description="URL de conexion asincrona a PostgreSQL",
    )
    DATABASE_URL_SYNC: str = Field(
        default="postgresql+psycopg2://cecilia:cecilia_dev@localhost:5432/cecilia_v2",
        description="URL de conexion sincrona (para Alembic)",
    )
    DB_POOL_SIZE: int = Field(default=20, description="Tamano del pool de conexiones")
    DB_MAX_OVERFLOW: int = Field(default=10, description="Conexiones extra sobre el pool")

    # ── Redis ─────────────────────────────────────────────────────────────
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="URL de conexion a Redis",
    )

    # ── Proveedor LLM (multi-proveedor) ──────────────────────────────────
    LLM_BASE_URL: str = Field(
        default="https://api.openai.com/v1",
        description="URL base del proveedor LLM (OpenAI, Azure, vLLM, Ollama, etc.)",
    )
    LLM_MODEL: str = Field(
        default="gpt-4o",
        description="Modelo LLM principal para generacion de respuestas",
    )
    LLM_API_KEY: str = Field(
        default="",
        description="Clave API del proveedor LLM",
    )
    LLM_TEMPERATURA: float = Field(
        default=0.3,
        description="Temperatura del modelo LLM (0.0 = determinista, 1.0 = creativo)",
    )
    LLM_MAX_TOKENS: int = Field(
        default=4096,
        description="Maximo de tokens en la respuesta del LLM",
    )
    LLM_TIMEOUT_SEGUNDOS: int = Field(
        default=120,
        description="Timeout en segundos para llamadas al LLM",
    )
    LLM_BACKUP_BASE_URL: str = ""
    LLM_BACKUP_MODEL: str = ""
    LLM_BACKUP_API_KEY: str = ""
    LLM_REINTENTOS: int = 2

    # ── Embeddings ────────────────────────────────────────────────────────
    EMBEDDINGS_BASE_URL: str = Field(
        default="https://api.openai.com/v1",
        description="URL base del proveedor de embeddings",
    )
    EMBEDDINGS_MODEL: str = Field(
        default="nomic-embed-text",
        description="Modelo de embeddings para RAG (nomic-embed-text, text-embedding-3-small, etc.)",
    )
    EMBEDDINGS_API_KEY: str = Field(
        default="ollama",
        description="Clave API del proveedor de embeddings",
    )
    EMBEDDINGS_DIMENSIONES: int = Field(
        default=768,
        description="Dimensiones del vector de embeddings (768 para nomic-embed-text, 1536 para text-embedding-3-small, 3072 para text-embedding-3-large)",
    )

    # ── JWT y Autenticacion ───────────────────────────────────────────────
    JWT_SECRET_KEY: str = Field(
        default="CAMBIAR_EN_PRODUCCION_clave_secreta_jwt_cecilia_v2",
        description="Clave secreta para firmar tokens JWT",
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="Algoritmo de firma JWT")
    JWT_EXPIRACION_MINUTOS: int = Field(
        default=480,
        description="Minutos de validez del token de acceso (8 horas)",
    )
    JWT_REFRESH_EXPIRACION_DIAS: int = Field(
        default=7,
        description="Dias de validez del token de refresco",
    )

    # ── CORS ──────────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Origenes permitidos para CORS",
    )

    # ── RAG y Documentos ──────────────────────────────────────────────────
    RAG_CHUNK_SIZE: int = Field(default=1000, description="Tamano de fragmento para RAG")
    RAG_CHUNK_OVERLAP: int = Field(default=200, description="Solapamiento entre fragmentos")
    RAG_TOP_K: int = Field(default=5, description="Numero de documentos recuperados por consulta")
    RUTA_ALMACENAMIENTO_DOCS: str = Field(
        default="/datos/documentos",
        description="Ruta para almacenamiento de documentos cargados",
    )

    # ── OpenTelemetry ─────────────────────────────────────────────────────
    OTEL_SERVICE_NAME: str = Field(default="cecilia-v2-api", description="Nombre del servicio")
    OTEL_EXPORTER_ENDPOINT: str = Field(
        default="http://localhost:4317",
        description="Endpoint del exportador OTLP",
    )

    # ── Parametros eticos del sistema ─────────────────────────────────────
    PARAMETROS_ETICOS: ClassVar[dict[str, str | bool]] = {
        "transparencia": True,
        "trazabilidad_completa": True,
        "no_reemplaza_juicio_humano": True,
        "sesgo_controlado": True,
        "privacidad_datos": True,
        "explicabilidad": (
            "Toda respuesta del sistema debe incluir las fuentes consultadas "
            "y el razonamiento aplicado, de forma que el auditor pueda "
            "verificar y validar la informacion."
        ),
        "alcance_asistencial": (
            "CecilIA v2 es un asistente tecnico. No toma decisiones "
            "autonomas sobre hallazgos, responsabilidades fiscales "
            "ni traslados de competencia."
        ),
        "cumplimiento_normativo": (
            "El sistema se alinea con la Constitucion Politica de Colombia, "
            "la Ley 42 de 1993, el Decreto 403 de 2020 (RGCF), y las "
            "resoluciones internas de la CGR."
        ),
    }

    # ── Criterios de calidad de IA ────────────────────────────────────────
    CRITERIOS_CALIDAD_IA: ClassVar[dict[str, str | float]] = {
        "precision_minima_rag": 0.85,
        "cobertura_fuentes": (
            "Toda respuesta RAG debe citar al menos una fuente normativa "
            "o documental verificable."
        ),
        "latencia_maxima_ms": 5000,
        "formato_respuesta": (
            "Las respuestas deben seguir la estructura: contexto normativo, "
            "analisis tecnico, conclusion y fuentes."
        ),
        "idioma": "es-CO",
        "tono": (
            "Formal, tecnico y respetuoso. Alineado con el lenguaje "
            "institucional de la CGR."
        ),
        "prohibiciones": (
            "No inventar normas, no citar articulos inexistentes, "
            "no emitir juicios de responsabilidad fiscal."
        ),
        "validacion_humana": (
            "Toda respuesta critica (hallazgos, traslados, conceptos juridicos) "
            "requiere validacion del auditor antes de ser oficializada."
        ),
    }


# ── Instancia global de configuracion ────────────────────────────────────────
configuracion: Configuracion = Configuracion()
