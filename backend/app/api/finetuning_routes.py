"""
CecilIA v2 — Rutas API para gestion de modelos y benchmark
Contraloria General de la Republica de Colombia

Archivo: app/api/finetuning_routes.py
Proposito: Endpoints REST para construir datasets, entrenar modelos,
           ejecutar benchmarks y gestionar adaptadores LoRA.
Sprint: 9
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

logger = logging.getLogger("cecilia.api.finetuning")

enrutador = APIRouter()


# ── Modelos Pydantic ────────────────────────────────────────────────────────

class SolicitudDataset(BaseModel):
    categorias: list[str] | None = None
    ruta_salida: str = "dataset_cecilia.jsonl"


class SolicitudEntrenamiento(BaseModel):
    ruta_dataset: str = "dataset_cecilia.jsonl"
    modelo_base: str = "Qwen/Qwen2.5-7B-Instruct"
    lora_rank: int = 16
    lora_alpha: int = 32
    epochs: int = 3
    learning_rate: float = 2e-4
    usar_qlora: bool = True


class SolicitudBenchmark(BaseModel):
    proveedores: list[str] = ["base"]
    categorias: list[str] | None = None
    usar_evaluador_llm: bool = False


class SolicitudMerge(BaseModel):
    directorio_adaptador: str
    directorio_salida: str
    modelo_base: str | None = None


# ── Estado global de tareas ─────────────────────────────────────────────────

_TAREAS: dict[str, dict[str, Any]] = {}


def _registrar_tarea(tipo: str, params: dict) -> str:
    """Registra una tarea en ejecucion y retorna su ID."""
    tarea_id = f"{tipo}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    _TAREAS[tarea_id] = {
        "id": tarea_id,
        "tipo": tipo,
        "estado": "en_ejecucion",
        "progreso": 0,
        "inicio": datetime.now(timezone.utc).isoformat(),
        "fin": None,
        "resultado": None,
        "error": None,
        "parametros": params,
    }
    return tarea_id


def _completar_tarea(tarea_id: str, resultado: Any = None, error: str | None = None) -> None:
    """Marca una tarea como completada."""
    if tarea_id in _TAREAS:
        _TAREAS[tarea_id]["estado"] = "error" if error else "completado"
        _TAREAS[tarea_id]["fin"] = datetime.now(timezone.utc).isoformat()
        _TAREAS[tarea_id]["resultado"] = resultado
        _TAREAS[tarea_id]["error"] = error
        _TAREAS[tarea_id]["progreso"] = 100 if not error else _TAREAS[tarea_id]["progreso"]


# ── Endpoints: Dataset ──────────────────────────────────────────────────────

@enrutador.post("/dataset/construir")
async def construir_dataset(solicitud: SolicitudDataset) -> dict:
    """Construye un dataset JSONL para fine-tuning."""
    from app.finetuning.dataset_builder import construir_dataset, CATEGORIAS

    cats = solicitud.categorias or CATEGORIAS
    try:
        stats = construir_dataset(
            ruta_salida=solicitud.ruta_salida,
            categorias=cats,
        )
        return {
            "exito": True,
            "mensaje": f"Dataset generado: {stats.total_ejemplos} ejemplos",
            "estadisticas": {
                "total_ejemplos": stats.total_ejemplos,
                "por_categoria": stats.por_categoria,
                "tokens_estimados": int(stats.tokens_estimados),
                "ruta": solicitud.ruta_salida,
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@enrutador.get("/dataset/categorias")
async def listar_categorias() -> dict:
    """Lista las categorias disponibles para el dataset."""
    from app.finetuning.dataset_builder import CATEGORIAS
    return {"categorias": CATEGORIAS}


# ── Endpoints: Entrenamiento ────────────────────────────────────────────────

@enrutador.get("/train/dependencias")
async def verificar_dependencias_train() -> dict:
    """Verifica que las dependencias de entrenamiento esten disponibles."""
    from app.finetuning.train_lora import verificar_dependencias
    deps = verificar_dependencias()
    return {"dependencias": deps, "listo": deps.get("todas_disponibles", False)}


@enrutador.post("/train/iniciar")
async def iniciar_entrenamiento(
    solicitud: SolicitudEntrenamiento,
    background_tasks: BackgroundTasks,
) -> dict:
    """Inicia un entrenamiento LoRA/QLoRA en background."""
    from app.finetuning.train_lora import ConfiguracionLoRA, entrenar_lora

    # Verificar que el dataset existe
    ruta_ds = Path(solicitud.ruta_dataset)
    if not ruta_ds.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Dataset no encontrado: {solicitud.ruta_dataset}",
        )

    config = ConfiguracionLoRA(
        modelo_base=solicitud.modelo_base,
        lora_rank=solicitud.lora_rank,
        lora_alpha=solicitud.lora_alpha,
        epochs=solicitud.epochs,
        learning_rate=solicitud.learning_rate,
        usar_qlora=solicitud.usar_qlora,
    )

    tarea_id = _registrar_tarea("entrenamiento", solicitud.model_dump())

    def _ejecutar():
        try:
            resultado = entrenar_lora(
                ruta_dataset=solicitud.ruta_dataset,
                config=config,
            )
            _completar_tarea(tarea_id, resultado.a_dict())
        except Exception as exc:
            _completar_tarea(tarea_id, error=str(exc))

    background_tasks.add_task(_ejecutar)

    return {
        "tarea_id": tarea_id,
        "mensaje": "Entrenamiento iniciado en background",
        "configuracion": config.a_dict(),
    }


@enrutador.get("/train/checkpoints")
async def listar_checkpoints_train(
    directorio: str = Query(default="modelos/lora_cecilia"),
) -> dict:
    """Lista los checkpoints disponibles."""
    from app.finetuning.train_lora import listar_checkpoints
    checkpoints = listar_checkpoints(directorio)
    return {"checkpoints": checkpoints, "total": len(checkpoints)}


@enrutador.get("/train/info")
async def info_modelo_entrenado(
    directorio: str = Query(default="modelos/lora_cecilia"),
) -> dict:
    """Obtiene informacion sobre un modelo LoRA entrenado."""
    from app.finetuning.train_lora import obtener_info_modelo
    info = obtener_info_modelo(directorio)
    return info


# ── Endpoints: Benchmark ────────────────────────────────────────────────────

@enrutador.get("/benchmark/preguntas")
async def listar_preguntas_benchmark(
    categoria: str | None = Query(default=None),
) -> dict:
    """Lista las preguntas del benchmark."""
    from app.finetuning.eval_model import PREGUNTAS_BENCHMARK, CATEGORIAS_EVAL

    preguntas = PREGUNTAS_BENCHMARK
    if categoria:
        preguntas = [p for p in preguntas if p["categoria"] == categoria]

    return {
        "total": len(preguntas),
        "categorias": CATEGORIAS_EVAL,
        "preguntas": preguntas,
    }


@enrutador.post("/benchmark/ejecutar")
async def ejecutar_benchmark(
    solicitud: SolicitudBenchmark,
    background_tasks: BackgroundTasks,
) -> dict:
    """Ejecuta un benchmark comparativo en background."""
    tarea_id = _registrar_tarea("benchmark", solicitud.model_dump())

    async def _ejecutar():
        try:
            from app.finetuning.eval_model import (
                ejecutar_benchmark_modelo,
                generar_comparativa,
                guardar_resultado,
                PREGUNTAS_BENCHMARK,
            )

            preguntas = PREGUNTAS_BENCHMARK
            if solicitud.categorias:
                preguntas = [p for p in preguntas if p["categoria"] in solicitud.categorias]

            resultados = []
            # Simulacion — en produccion se conectarian los proveedores reales
            for prov in solicitud.proveedores:
                async def _mock_inferencia(pregunta: str) -> str:
                    """Inferencia simulada para demo."""
                    return (
                        f"[Respuesta simulada del proveedor '{prov}'] "
                        f"Esta es una respuesta de ejemplo para la pregunta: {pregunta[:100]}... "
                        "En un entorno de produccion, esta respuesta vendria del modelo LLM real."
                    )

                resultado = await ejecutar_benchmark_modelo(
                    modelo_id=prov,
                    modelo_nombre=f"Modelo {prov}",
                    tipo=prov,
                    funcion_inferencia=_mock_inferencia,
                    preguntas=preguntas,
                    usar_evaluador_llm=solicitud.usar_evaluador_llm,
                )
                resultados.append(resultado)

            comparativa = generar_comparativa(resultados)
            _completar_tarea(tarea_id, comparativa.a_dict())

        except Exception as exc:
            _completar_tarea(tarea_id, error=str(exc))

    background_tasks.add_task(asyncio.create_task, _ejecutar())

    return {
        "tarea_id": tarea_id,
        "mensaje": f"Benchmark iniciado para {len(solicitud.proveedores)} proveedores",
    }


@enrutador.get("/benchmark/resultados")
async def listar_resultados_benchmark(
    directorio: str = Query(default="benchmark_resultados"),
) -> dict:
    """Lista los resultados de benchmarks anteriores."""
    ruta = Path(directorio)
    resultados = []

    if ruta.exists():
        for f in sorted(ruta.glob("benchmark_*.json"), reverse=True):
            try:
                with f.open() as fh:
                    data = json.load(fh)
                resultados.append({
                    "archivo": f.name,
                    "modelo": data.get("modelo_nombre", ""),
                    "tipo": data.get("tipo", ""),
                    "fecha": data.get("fecha", ""),
                    "promedio": data.get("metricas_globales", {}).get("promedio_calificacion", 0),
                })
            except Exception:
                continue

    return {"resultados": resultados, "total": len(resultados)}


@enrutador.get("/benchmark/informe")
async def descargar_informe_benchmark(
    directorio: str = Query(default="benchmark_resultados"),
) -> StreamingResponse:
    """Genera y descarga el informe DOCX del ultimo benchmark."""
    from app.finetuning.eval_model import (
        cargar_resultado,
        generar_comparativa,
        generar_informe_docx,
    )

    ruta = Path(directorio)
    archivos = sorted(ruta.glob("benchmark_*.json"), reverse=True)

    if not archivos:
        raise HTTPException(status_code=404, detail="No hay resultados de benchmark disponibles")

    # Cargar los ultimos resultados (uno por modelo)
    resultados = []
    modelos_vistos = set()
    for f in archivos:
        try:
            resultado = cargar_resultado(f)
            if resultado.modelo_id not in modelos_vistos:
                resultados.append(resultado)
                modelos_vistos.add(resultado.modelo_id)
        except Exception:
            continue

    if not resultados:
        raise HTTPException(status_code=404, detail="No se pudieron cargar resultados")

    comparativa = generar_comparativa(resultados)
    docx_bytes = generar_informe_docx(comparativa)

    import io
    return StreamingResponse(
        io.BytesIO(docx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f"attachment; filename=informe_benchmark_{datetime.now().strftime('%Y%m%d')}.docx"
        },
    )


# ── Endpoints: Merge ────────────────────────────────────────────────────────

@enrutador.post("/merge")
async def merge_adaptador(
    solicitud: SolicitudMerge,
    background_tasks: BackgroundTasks,
) -> dict:
    """Fusiona un adaptador LoRA con el modelo base."""
    from app.finetuning.merge_adapter import verificar_adaptador

    info = verificar_adaptador(solicitud.directorio_adaptador)
    if not info["valido"]:
        raise HTTPException(
            status_code=400,
            detail=f"Adaptador no valido: {'; '.join(info['errores'])}",
        )

    tarea_id = _registrar_tarea("merge", solicitud.model_dump())

    def _ejecutar():
        try:
            from app.finetuning.merge_adapter import merge_lora
            resultado = merge_lora(
                directorio_adaptador=solicitud.directorio_adaptador,
                directorio_salida=solicitud.directorio_salida,
                modelo_base=solicitud.modelo_base,
            )
            _completar_tarea(tarea_id, resultado.a_dict())
        except Exception as exc:
            _completar_tarea(tarea_id, error=str(exc))

    background_tasks.add_task(_ejecutar)

    return {
        "tarea_id": tarea_id,
        "mensaje": "Merge iniciado en background",
        "adaptador": info,
    }


@enrutador.get("/merge/verificar")
async def verificar_adaptador_endpoint(
    directorio: str = Query(..., description="Directorio del adaptador LoRA"),
) -> dict:
    """Verifica que un directorio contiene un adaptador LoRA valido."""
    from app.finetuning.merge_adapter import verificar_adaptador
    info = verificar_adaptador(directorio)
    return info


# ── Endpoints: Tareas ───────────────────────────────────────────────────────

@enrutador.get("/tareas")
async def listar_tareas() -> dict:
    """Lista todas las tareas de finetuning (entrenamiento, benchmark, merge)."""
    return {
        "tareas": list(_TAREAS.values()),
        "total": len(_TAREAS),
    }


@enrutador.get("/tareas/{tarea_id}")
async def obtener_tarea(tarea_id: str) -> dict:
    """Obtiene el estado de una tarea especifica."""
    tarea = _TAREAS.get(tarea_id)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea


# ── Endpoint: Resumen general ───────────────────────────────────────────────

@enrutador.get("/resumen")
async def resumen_finetuning() -> dict:
    """Resumen general del estado del pipeline de fine-tuning."""
    from app.finetuning.train_lora import verificar_dependencias

    deps = verificar_dependencias()

    # Contar tareas por tipo y estado
    tareas_resumen = {}
    for t in _TAREAS.values():
        key = f"{t['tipo']}_{t['estado']}"
        tareas_resumen[key] = tareas_resumen.get(key, 0) + 1

    # Verificar si hay modelo entrenado
    modelo_dir = Path("modelos/lora_cecilia")
    tiene_modelo = modelo_dir.exists() and (modelo_dir / "adapter_config.json").exists()

    # Verificar si hay resultados de benchmark
    benchmark_dir = Path("benchmark_resultados")
    n_benchmarks = len(list(benchmark_dir.glob("benchmark_*.json"))) if benchmark_dir.exists() else 0

    return {
        "dependencias_listas": deps.get("todas_disponibles", False),
        "cuda_disponible": deps.get("cuda_disponible", False),
        "gpu": deps.get("gpu_nombre", "N/A"),
        "tiene_modelo_entrenado": tiene_modelo,
        "benchmarks_ejecutados": n_benchmarks,
        "tareas_activas": sum(1 for t in _TAREAS.values() if t["estado"] == "en_ejecucion"),
        "tareas_resumen": tareas_resumen,
    }
