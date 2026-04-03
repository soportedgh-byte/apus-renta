"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: benchmark_modelos.py
Propósito: Evaluación comparativa de modelos LLM — mide tiempo de respuesta, calidad y uso de tokens
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

import json
import os
import sys
import time
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("benchmark_modelos")

OUTPUT_DIR: Path = Path(os.environ.get("BENCHMARK_OUTPUT", "benchmarks"))

# ---------------------------------------------------------------------------
# Proveedores y modelos a evaluar
# ---------------------------------------------------------------------------
PROVEEDORES: list[dict] = [
    {
        "nombre": "OpenAI",
        "modelos": ["gpt-4o", "gpt-4o-mini"],
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
    },
    {
        "nombre": "Anthropic",
        "modelos": ["claude-sonnet-4-20250514", "claude-haiku-35-20241022"],
        "base_url": "https://api.anthropic.com",
        "api_key_env": "ANTHROPIC_API_KEY",
    },
    {
        "nombre": "Azure OpenAI",
        "modelos": ["gpt-4o"],
        "base_url": os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
        "api_key_env": "AZURE_OPENAI_KEY",
    },
    {
        "nombre": "Ollama (local)",
        "modelos": ["llama3:8b", "mistral:7b"],
        "base_url": "http://localhost:11434/v1",
        "api_key_env": "",
    },
]

# ---------------------------------------------------------------------------
# Casos de prueba del dominio fiscal colombiano
# ---------------------------------------------------------------------------
CASOS_PRUEBA: list[dict] = [
    {
        "id": "CP-01",
        "categoria": "normativo",
        "prompt": (
            "Explica los principios constitucionales del control fiscal en Colombia "
            "según los artículos 267 y 268 de la Constitución Política."
        ),
        "criterios": ["mención art. 267", "mención art. 268", "precisión jurídica"],
    },
    {
        "id": "CP-02",
        "categoria": "calculo_materialidad",
        "prompt": (
            "Dado un presupuesto de inversión de $450.000 millones y un nivel de "
            "confianza del 95%, calcula la materialidad global y la materialidad de "
            "ejecución para una auditoría financiera según las NIA."
        ),
        "criterios": ["cálculo correcto", "referencia NIA 320", "justificación"],
    },
    {
        "id": "CP-03",
        "categoria": "analisis_benford",
        "prompt": (
            "Describe la Ley de Benford y cómo se aplica para detectar anomalías "
            "en los registros de pagos de un sujeto de control. Incluye un ejemplo "
            "con distribución esperada del primer dígito."
        ),
        "criterios": ["distribución correcta", "aplicación a auditoría", "ejemplo"],
    },
    {
        "id": "CP-04",
        "categoria": "hallazgo",
        "prompt": (
            "Redacta un hallazgo fiscal tipo de una auditoría a un programa de "
            "conectividad rural del MinTIC. Incluye condición, criterio, causa y "
            "efecto."
        ),
        "criterios": ["estructura CCCE", "lenguaje técnico", "coherencia"],
    },
    {
        "id": "CP-05",
        "categoria": "razonamiento",
        "prompt": (
            "Compara las ventajas y desventajas de usar RAG frente a fine-tuning "
            "para un asistente de auditoría gubernamental que debe citar normatividad "
            "vigente."
        ),
        "criterios": ["comparación equilibrada", "contexto auditoría", "recomendación"],
    },
]


# ---------------------------------------------------------------------------
# Estructura de resultados
# ---------------------------------------------------------------------------
@dataclass
class ResultadoModelo:
    """Almacena los resultados de un modelo en un caso de prueba."""

    proveedor: str
    modelo: str
    caso_id: str
    tiempo_respuesta_ms: float = 0.0
    tokens_prompt: int = 0
    tokens_respuesta: int = 0
    tokens_total: int = 0
    respuesta: str = ""
    error: str | None = None
    puntuacion_manual: float | None = None


@dataclass
class InformeBenchmark:
    """Consolidado de resultados de benchmark."""

    fecha: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    resultados: list[dict] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Ejecución de llamadas a modelos
# ---------------------------------------------------------------------------

def llamar_openai_compatible(
    base_url: str,
    api_key: str,
    modelo: str,
    prompt: str,
) -> ResultadoModelo:
    """Realiza una llamada a una API compatible con OpenAI y mide métricas."""
    try:
        import openai
    except ImportError:
        logger.error("openai no instalado. Ejecute: pip install openai")
        return ResultadoModelo(
            proveedor="", modelo=modelo, caso_id="",
            error="Paquete openai no instalado",
        )

    client = openai.OpenAI(base_url=base_url, api_key=api_key or "no-key")

    inicio = time.perf_counter()
    try:
        respuesta = client.chat.completions.create(
            model=modelo,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres CecilIA, asistente de IA de la Contraloría General "
                        "de la República de Colombia, especializada en control fiscal."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1024,
        )
        fin = time.perf_counter()

        uso = respuesta.usage
        return ResultadoModelo(
            proveedor="",
            modelo=modelo,
            caso_id="",
            tiempo_respuesta_ms=(fin - inicio) * 1000,
            tokens_prompt=uso.prompt_tokens if uso else 0,
            tokens_respuesta=uso.completion_tokens if uso else 0,
            tokens_total=uso.total_tokens if uso else 0,
            respuesta=respuesta.choices[0].message.content or "",
        )
    except Exception as exc:
        fin = time.perf_counter()
        return ResultadoModelo(
            proveedor="",
            modelo=modelo,
            caso_id="",
            tiempo_respuesta_ms=(fin - inicio) * 1000,
            error=str(exc),
        )


def llamar_anthropic(
    api_key: str,
    modelo: str,
    prompt: str,
) -> ResultadoModelo:
    """Realiza una llamada a la API de Anthropic y mide métricas."""
    try:
        import anthropic
    except ImportError:
        logger.error("anthropic no instalado. Ejecute: pip install anthropic")
        return ResultadoModelo(
            proveedor="Anthropic", modelo=modelo, caso_id="",
            error="Paquete anthropic no instalado",
        )

    client = anthropic.Anthropic(api_key=api_key)

    inicio = time.perf_counter()
    try:
        respuesta = client.messages.create(
            model=modelo,
            max_tokens=1024,
            system=(
                "Eres CecilIA, asistente de IA de la Contraloría General "
                "de la República de Colombia, especializada en control fiscal."
            ),
            messages=[{"role": "user", "content": prompt}],
        )
        fin = time.perf_counter()

        texto = respuesta.content[0].text if respuesta.content else ""
        return ResultadoModelo(
            proveedor="Anthropic",
            modelo=modelo,
            caso_id="",
            tiempo_respuesta_ms=(fin - inicio) * 1000,
            tokens_prompt=respuesta.usage.input_tokens,
            tokens_respuesta=respuesta.usage.output_tokens,
            tokens_total=respuesta.usage.input_tokens + respuesta.usage.output_tokens,
            respuesta=texto,
        )
    except Exception as exc:
        fin = time.perf_counter()
        return ResultadoModelo(
            proveedor="Anthropic",
            modelo=modelo,
            caso_id="",
            tiempo_respuesta_ms=(fin - inicio) * 1000,
            error=str(exc),
        )


# ---------------------------------------------------------------------------
# Orquestación del benchmark
# ---------------------------------------------------------------------------

def ejecutar_benchmark() -> InformeBenchmark:
    """Ejecuta todos los casos de prueba contra todos los proveedores."""
    informe = InformeBenchmark()

    for proveedor in PROVEEDORES:
        api_key = os.environ.get(proveedor["api_key_env"], "") if proveedor["api_key_env"] else ""
        nombre_prov = proveedor["nombre"]

        if not api_key and proveedor["api_key_env"]:
            logger.warning(
                "Clave API no encontrada para %s (%s). Se omite.",
                nombre_prov,
                proveedor["api_key_env"],
            )
            continue

        for modelo in proveedor["modelos"]:
            logger.info("Evaluando %s / %s …", nombre_prov, modelo)

            for caso in CASOS_PRUEBA:
                logger.info("  Caso %s (%s)", caso["id"], caso["categoria"])

                if nombre_prov == "Anthropic":
                    resultado = llamar_anthropic(api_key, modelo, caso["prompt"])
                else:
                    resultado = llamar_openai_compatible(
                        proveedor["base_url"], api_key, modelo, caso["prompt"]
                    )

                resultado.proveedor = nombre_prov
                resultado.caso_id = caso["id"]

                logger.info(
                    "    → %.0f ms | %d tokens | error=%s",
                    resultado.tiempo_respuesta_ms,
                    resultado.tokens_total,
                    resultado.error or "ninguno",
                )

                informe.resultados.append(asdict(resultado))

    return informe


# ---------------------------------------------------------------------------
# Generación de reporte
# ---------------------------------------------------------------------------

def generar_reporte(informe: InformeBenchmark) -> Path:
    """Genera un reporte JSON con los resultados del benchmark."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    ruta = OUTPUT_DIR / f"benchmark_{timestamp}.json"

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(asdict(informe), f, ensure_ascii=False, indent=2)

    logger.info("Reporte guardado en: %s", ruta)

    # Resumen por modelo
    resumen: dict[str, dict] = {}
    for r in informe.resultados:
        clave = f"{r['proveedor']}/{r['modelo']}"
        if clave not in resumen:
            resumen[clave] = {
                "casos": 0,
                "errores": 0,
                "tiempo_total_ms": 0.0,
                "tokens_total": 0,
            }
        resumen[clave]["casos"] += 1
        if r.get("error"):
            resumen[clave]["errores"] += 1
        resumen[clave]["tiempo_total_ms"] += r["tiempo_respuesta_ms"]
        resumen[clave]["tokens_total"] += r["tokens_total"]

    logger.info("\n" + "=" * 70)
    logger.info("RESUMEN COMPARATIVO DE MODELOS")
    logger.info("%-30s %8s %8s %10s %8s", "Modelo", "Casos", "Errores", "Tiempo(ms)", "Tokens")
    logger.info("-" * 70)
    for clave, datos in resumen.items():
        promedio_ms = datos["tiempo_total_ms"] / max(datos["casos"], 1)
        logger.info(
            "%-30s %8d %8d %10.0f %8d",
            clave,
            datos["casos"],
            datos["errores"],
            promedio_ms,
            datos["tokens_total"],
        )
    logger.info("=" * 70)

    return ruta


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("Iniciando benchmark de modelos LLM para CecilIA v2 …")
    informe = ejecutar_benchmark()
    ruta_reporte = generar_reporte(informe)
    logger.info("Benchmark finalizado. Reporte: %s", ruta_reporte)
