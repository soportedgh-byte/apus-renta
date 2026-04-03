"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: logging.py
Propósito: Configuración de logging estructurado con OpenTelemetry
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Any, Optional

# Formato estructurado JSON para producción
FORMATO_JSON: str = (
    '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
    '"logger": "%(name)s", "message": "%(message)s", '
    '"module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}'
)

# Formato legible para desarrollo
FORMATO_DESARROLLO: str = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
)


def configurar_logging(
    nivel: str = "INFO",
    formato: str = "desarrollo",
    log_file: Optional[str] = None,
) -> None:
    """Configura el sistema de logging estructurado.

    Args:
        nivel: Nivel mínimo de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        formato: Formato de salida: 'desarrollo' (legible) o 'json' (estructurado).
        log_file: Ruta opcional para archivo de log.
    """
    nivel_log: int = getattr(logging, nivel.upper(), logging.INFO)

    formato_str: str = FORMATO_JSON if formato == "json" else FORMATO_DESARROLLO

    # Configurar root logger
    root_logger: logging.Logger = logging.getLogger()
    root_logger.setLevel(nivel_log)

    # Limpiar handlers existentes
    root_logger.handlers.clear()

    # Handler para consola
    handler_consola: logging.Handler = logging.StreamHandler(sys.stdout)
    handler_consola.setLevel(nivel_log)
    handler_consola.setFormatter(logging.Formatter(formato_str, datefmt="%Y-%m-%d %H:%M:%S"))
    root_logger.addHandler(handler_consola)

    # Handler para archivo (si se especifica)
    if log_file:
        handler_archivo: logging.Handler = logging.FileHandler(log_file, encoding="utf-8")
        handler_archivo.setLevel(nivel_log)
        handler_archivo.setFormatter(logging.Formatter(FORMATO_JSON, datefmt="%Y-%m-%d %H:%M:%S"))
        root_logger.addHandler(handler_archivo)

    # Reducir ruido de librerías de terceros
    for nombre_lib in ["httpx", "httpcore", "urllib3", "asyncio", "openai", "langchain"]:
        logging.getLogger(nombre_lib).setLevel(logging.WARNING)

    logging.getLogger("cecilia").info(
        "Logging configurado: nivel=%s, formato=%s, archivo=%s",
        nivel, formato, log_file or "ninguno",
    )


def configurar_opentelemetry(
    service_name: str = "cecilia-v2-backend",
    otlp_endpoint: Optional[str] = None,
) -> None:
    """Configura OpenTelemetry para trazas distribuidas y métricas.

    Args:
        service_name: Nombre del servicio para identificación en trazas.
        otlp_endpoint: Endpoint del colector OTLP (ej: http://localhost:4317).
    """
    otlp_endpoint = otlp_endpoint or os.environ.get(
        "OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"
    )

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.logging import LoggingInstrumentor

        # Configurar recurso
        resource: Resource = Resource.create({
            "service.name": service_name,
            "service.version": "2.0.0",
            "deployment.environment": os.environ.get("ENVIRONMENT", "development"),
        })

        # Configurar proveedor de trazas
        provider: TracerProvider = TracerProvider(resource=resource)

        # Exportador OTLP
        exportador: OTLPSpanExporter = OTLPSpanExporter(endpoint=otlp_endpoint)
        provider.add_span_processor(BatchSpanProcessor(exportador))

        trace.set_tracer_provider(provider)

        # Instrumentar logging para incluir trace_id y span_id
        LoggingInstrumentor().instrument(set_logging_format=True)

        logging.getLogger("cecilia").info(
            "OpenTelemetry configurado: servicio=%s, endpoint=%s",
            service_name, otlp_endpoint,
        )

    except ImportError:
        logging.getLogger("cecilia").warning(
            "OpenTelemetry no disponible. Instale: pip install opentelemetry-sdk "
            "opentelemetry-exporter-otlp opentelemetry-instrumentation-logging"
        )

    except Exception:
        logging.getLogger("cecilia").exception(
            "Error al configurar OpenTelemetry."
        )


def configurar_metricas(
    service_name: str = "cecilia-v2-backend",
    otlp_endpoint: Optional[str] = None,
) -> None:
    """Configura métricas de OpenTelemetry.

    Args:
        service_name: Nombre del servicio.
        otlp_endpoint: Endpoint del colector OTLP.
    """
    otlp_endpoint = otlp_endpoint or os.environ.get(
        "OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"
    )

    try:
        from opentelemetry import metrics
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
        from opentelemetry.sdk.resources import Resource

        resource: Resource = Resource.create({
            "service.name": service_name,
        })

        exportador = OTLPMetricExporter(endpoint=otlp_endpoint)
        reader = PeriodicExportingMetricReader(exportador, export_interval_millis=30000)

        provider = MeterProvider(resource=resource, metric_readers=[reader])
        metrics.set_meter_provider(provider)

        # Crear métricas personalizadas de CecilIA
        meter = metrics.get_meter("cecilia.metricas", "2.0.0")

        # Contadores
        meter.create_counter(
            name="cecilia.interacciones.total",
            description="Total de interacciones con el LLM",
            unit="1",
        )
        meter.create_counter(
            name="cecilia.tokens.consumidos",
            description="Total de tokens consumidos",
            unit="tokens",
        )

        # Histogramas
        meter.create_histogram(
            name="cecilia.respuesta.duracion",
            description="Duración de respuesta del sistema",
            unit="s",
        )

        logging.getLogger("cecilia").info("Métricas OpenTelemetry configuradas.")

    except ImportError:
        logging.getLogger("cecilia").warning(
            "OpenTelemetry Metrics no disponible."
        )
    except Exception:
        logging.getLogger("cecilia").exception("Error al configurar métricas.")
