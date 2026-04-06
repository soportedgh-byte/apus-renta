#!/usr/bin/env python3
"""
CecilIA v2 — Script de benchmark comparativo de modelos
Contraloria General de la Republica de Colombia

Archivo: scripts/benchmark_modelos.py
Proposito: Ejecuta las 50 preguntas del benchmark contra cada proveedor
           (base local, fine-tuned, Claude, Gemini) y genera tabla comparativa.

Uso:
    python scripts/benchmark_modelos.py
    python scripts/benchmark_modelos.py --proveedores base,claude
    python scripts/benchmark_modelos.py --categorias normativo,hallazgos
    python scripts/benchmark_modelos.py --salida resultados/

Sprint: 9
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Agregar el directorio backend al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.finetuning.eval_model import (
    CATEGORIAS_EVAL,
    PREGUNTAS_BENCHMARK,
    ComparativaBenchmark,
    ResultadoBenchmark,
    ejecutar_benchmark_modelo,
    generar_comparativa,
    generar_informe_docx,
    guardar_resultado,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("cecilia.benchmark")


# ── Funciones de inferencia por proveedor ────────────────────────────────────

async def inferencia_openai(pregunta: str) -> str:
    """Inferencia usando API compatible con OpenAI (base local, vLLM, Ollama)."""
    import httpx
    from app.config import configuracion

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            f"{configuracion.LLM_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {configuracion.LLM_API_KEY}"},
            json={
                "model": configuracion.LLM_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Eres CecilIA, asistente de IA de la Contraloria General "
                            "de la Republica de Colombia especializado en control fiscal."
                        ),
                    },
                    {"role": "user", "content": pregunta},
                ],
                "temperature": 0.3,
                "max_tokens": 2048,
            },
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


async def inferencia_claude(pregunta: str) -> str:
    """Inferencia usando la API de Anthropic (Claude)."""
    import httpx
    import os

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY no configurada")

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 2048,
                "system": (
                    "Eres un experto en control fiscal colombiano. "
                    "Responde de forma tecnica y fundamentada."
                ),
                "messages": [{"role": "user", "content": pregunta}],
            },
        )
        r.raise_for_status()
        return r.json()["content"][0]["text"]


async def inferencia_gemini(pregunta: str) -> str:
    """Inferencia usando la API de Google Gemini."""
    import httpx
    import os

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY no configurada")

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
            json={
                "contents": [{
                    "parts": [{
                        "text": (
                            "Eres un experto en control fiscal colombiano. "
                            "Responde de forma tecnica y fundamentada.\n\n"
                            f"Pregunta: {pregunta}"
                        ),
                    }],
                }],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 2048,
                },
            },
        )
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]


async def inferencia_finetuned(pregunta: str) -> str:
    """Inferencia usando modelo fine-tuned local (via Ollama o vLLM)."""
    import httpx

    # Intenta primero con Ollama
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "cecilia-v2",
                    "prompt": (
                        "### Instruccion:\nEres CecilIA, asistente de IA de la "
                        "Contraloria General de la Republica de Colombia.\n\n"
                        f"### Entrada:\n{pregunta}\n\n### Respuesta:\n"
                    ),
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 2048},
                },
            )
            r.raise_for_status()
            return r.json()["response"]
    except Exception:
        pass

    # Fallback: vLLM local
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            "http://localhost:8001/v1/chat/completions",
            json={
                "model": "cecilia-v2-finetuned",
                "messages": [
                    {"role": "system", "content": "Eres CecilIA, asistente de control fiscal."},
                    {"role": "user", "content": pregunta},
                ],
                "temperature": 0.3,
                "max_tokens": 2048,
            },
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


# ── Mapa de proveedores ─────────────────────────────────────────────────────

PROVEEDORES = {
    "base": {
        "id": "base",
        "nombre": "Modelo Base (LLM principal)",
        "tipo": "base",
        "funcion": inferencia_openai,
    },
    "finetuned": {
        "id": "finetuned",
        "nombre": "CecilIA v2 Fine-tuned (LoRA)",
        "tipo": "finetuned",
        "funcion": inferencia_finetuned,
    },
    "claude": {
        "id": "claude",
        "nombre": "Claude Sonnet 4 (Anthropic)",
        "tipo": "claude",
        "funcion": inferencia_claude,
    },
    "gemini": {
        "id": "gemini",
        "nombre": "Gemini 2.0 Flash (Google)",
        "tipo": "gemini",
        "funcion": inferencia_gemini,
    },
}


# ── Funciones principales ───────────────────────────────────────────────────

def filtrar_preguntas(
    categorias: list[str] | None = None,
) -> list[dict[str, str]]:
    """Filtra preguntas por categoria."""
    if not categorias:
        return PREGUNTAS_BENCHMARK
    return [p for p in PREGUNTAS_BENCHMARK if p["categoria"] in categorias]


def imprimir_tabla_resumen(comparativa: ComparativaBenchmark) -> None:
    """Imprime una tabla resumen en la consola."""
    print("\n" + "=" * 80)
    print("  BENCHMARK COMPARATIVO DE MODELOS — CecilIA v2")
    print("  Contraloria General de la Republica de Colombia")
    print("=" * 80)

    # Ranking global
    print(f"\n{'#':<4} {'Modelo':<35} {'Tipo':<12} {'Promedio':<10} {'Tiempo':<10} {'Exito':<8}")
    print("-" * 79)
    for i, r in enumerate(comparativa.ranking_global, 1):
        print(
            f"{i:<4} {r['modelo']:<35} {r['tipo']:<12} "
            f"{r['promedio']:.1f}/10   {r['tiempo_promedio_s']:.1f}s     "
            f"{r['tasa_exito']:.0f}%"
        )

    # Por categoria
    print("\n" + "-" * 79)
    print("DETALLE POR CATEGORIA:")
    for cat in CATEGORIAS_EVAL:
        rank = comparativa.ranking_por_categoria.get(cat, [])
        if rank:
            mejor = rank[0]
            print(f"  {cat:<25} Mejor: {mejor['modelo']} ({mejor['promedio']:.1f}/10)")

    print("=" * 80)


async def ejecutar_benchmark(
    proveedores_str: list[str],
    categorias: list[str] | None,
    directorio_salida: str,
    usar_evaluador_llm: bool,
) -> None:
    """Ejecuta el benchmark completo."""
    preguntas = filtrar_preguntas(categorias)
    logger.info(
        "Benchmark: %d preguntas, %d proveedores",
        len(preguntas), len(proveedores_str),
    )

    resultados: list[ResultadoBenchmark] = []
    dir_salida = Path(directorio_salida)
    dir_salida.mkdir(parents=True, exist_ok=True)

    for nombre_prov in proveedores_str:
        prov = PROVEEDORES.get(nombre_prov)
        if not prov:
            logger.warning("Proveedor desconocido: %s (disponibles: %s)",
                          nombre_prov, ", ".join(PROVEEDORES.keys()))
            continue

        logger.info("=" * 60)
        logger.info("Ejecutando benchmark para: %s", prov["nombre"])
        logger.info("=" * 60)

        try:
            resultado = await ejecutar_benchmark_modelo(
                modelo_id=prov["id"],
                modelo_nombre=prov["nombre"],
                tipo=prov["tipo"],
                funcion_inferencia=prov["funcion"],
                preguntas=preguntas,
                usar_evaluador_llm=usar_evaluador_llm,
            )
            resultados.append(resultado)
            guardar_resultado(resultado, dir_salida)
            logger.info(
                "Completado %s: promedio=%.1f, tiempo=%.1fs",
                prov["nombre"],
                resultado.metricas_globales.get("promedio_calificacion", 0),
                resultado.tiempo_total_s,
            )
        except Exception as exc:
            logger.error("Error con proveedor %s: %s", nombre_prov, exc)

    if not resultados:
        logger.error("No se obtuvieron resultados de ningun proveedor")
        return

    # Generar comparativa
    comparativa = generar_comparativa(resultados)

    # Guardar comparativa JSON
    comp_json = dir_salida / f"comparativa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with comp_json.open("w", encoding="utf-8") as f:
        json.dump(comparativa.a_dict(), f, ensure_ascii=False, indent=2)
    logger.info("Comparativa JSON: %s", comp_json)

    # Generar informe DOCX
    try:
        docx_bytes = generar_informe_docx(comparativa)
        docx_path = dir_salida / f"informe_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        with docx_path.open("wb") as f:
            f.write(docx_bytes)
        logger.info("Informe DOCX: %s", docx_path)
    except Exception as exc:
        logger.warning("No se pudo generar DOCX: %s", exc)

    # Imprimir resumen
    imprimir_tabla_resumen(comparativa)


# ── CLI ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="CecilIA v2 — Benchmark comparativo de modelos LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python benchmark_modelos.py
  python benchmark_modelos.py --proveedores base,claude
  python benchmark_modelos.py --categorias normativo,hallazgos --salida resultados/
  python benchmark_modelos.py --proveedores gemini --evaluador-llm
        """,
    )
    parser.add_argument(
        "--proveedores",
        default="base",
        help=f"Proveedores separados por coma (disponibles: {','.join(PROVEEDORES.keys())})",
    )
    parser.add_argument(
        "--categorias",
        default=None,
        help=f"Categorias separados por coma (disponibles: {','.join(CATEGORIAS_EVAL)})",
    )
    parser.add_argument(
        "--salida",
        default="benchmark_resultados",
        help="Directorio de salida para resultados",
    )
    parser.add_argument(
        "--evaluador-llm",
        action="store_true",
        help="Usar LLM como juez para calificar (requiere API key)",
    )

    args = parser.parse_args()

    proveedores = [p.strip() for p in args.proveedores.split(",")]
    categorias = (
        [c.strip() for c in args.categorias.split(",")]
        if args.categorias
        else None
    )

    asyncio.run(
        ejecutar_benchmark(
            proveedores_str=proveedores,
            categorias=categorias,
            directorio_salida=args.salida,
            usar_evaluador_llm=args.evaluador_llm,
        )
    )


if __name__ == "__main__":
    main()
