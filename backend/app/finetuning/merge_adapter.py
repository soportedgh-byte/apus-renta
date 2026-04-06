"""
CecilIA v2 — Fusion de adaptadores LoRA con modelo base
Contraloria General de la Republica de Colombia

Archivo: app/finetuning/merge_adapter.py
Proposito: Merge del adaptador LoRA/QLoRA con el modelo base
           para generar un modelo completo listo para despliegue.
Sprint: 9
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import json
import logging
import shutil
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("cecilia.finetuning.merge")


@dataclass
class ResultadoMerge:
    """Resultado de una operacion de merge."""

    exitoso: bool = False
    modelo_base: str = ""
    directorio_adaptador: str = ""
    directorio_salida: str = ""
    tamano_modelo_gb: float = 0.0
    tiempo_segundos: float = 0.0
    fecha: str = ""
    errores: list[str] = field(default_factory=list)

    def a_dict(self) -> dict[str, Any]:
        return asdict(self)


def verificar_adaptador(directorio: str | Path) -> dict[str, Any]:
    """Verifica que un directorio contiene un adaptador LoRA valido.

    Args:
        directorio: Ruta al directorio del adaptador.

    Returns:
        Dict con informacion del adaptador y estado de validacion.
    """
    ruta = Path(directorio)
    info: dict[str, Any] = {
        "directorio": str(ruta),
        "existe": ruta.exists(),
        "valido": False,
        "errores": [],
    }

    if not ruta.exists():
        info["errores"].append("El directorio no existe")
        return info

    # Verificar archivos requeridos
    adapter_config = ruta / "adapter_config.json"
    if not adapter_config.exists():
        info["errores"].append("Falta adapter_config.json")
    else:
        with adapter_config.open() as f:
            config = json.load(f)
        info["modelo_base"] = config.get("base_model_name_or_path", "")
        info["lora_rank"] = config.get("r", 0)
        info["lora_alpha"] = config.get("lora_alpha", 0)
        info["target_modules"] = config.get("target_modules", [])
        info["task_type"] = config.get("task_type", "")

    # Verificar pesos del adaptador
    tiene_pesos = any(
        ruta.glob("adapter_model.*")
    ) or any(ruta.glob("*.safetensors"))
    if not tiene_pesos:
        info["errores"].append("No se encontraron pesos del adaptador (adapter_model.* o *.safetensors)")
    else:
        info["tiene_pesos"] = True

    # Verificar tokenizer
    tiene_tokenizer = (ruta / "tokenizer_config.json").exists()
    info["tiene_tokenizer"] = tiene_tokenizer

    info["valido"] = len(info["errores"]) == 0
    return info


def merge_lora(
    directorio_adaptador: str | Path,
    directorio_salida: str | Path,
    modelo_base: str | None = None,
    push_to_hub: bool = False,
    hub_repo: str | None = None,
) -> ResultadoMerge:
    """Fusiona un adaptador LoRA con su modelo base.

    Genera un modelo completo (sin adaptador separado) que puede
    desplegarse directamente con vLLM, Ollama o similar.

    Args:
        directorio_adaptador: Ruta al directorio del adaptador LoRA.
        directorio_salida: Ruta donde guardar el modelo fusionado.
        modelo_base: Nombre/ruta del modelo base. Si None, se lee de adapter_config.json.
        push_to_hub: Si subir a HuggingFace Hub.
        hub_repo: Nombre del repositorio en HF Hub.

    Returns:
        ResultadoMerge con estado y metricas.
    """
    resultado = ResultadoMerge(
        directorio_adaptador=str(directorio_adaptador),
        directorio_salida=str(directorio_salida),
        fecha=datetime.now(timezone.utc).isoformat(),
    )

    t_inicio = time.time()

    # 1. Verificar adaptador
    info = verificar_adaptador(directorio_adaptador)
    if not info["valido"]:
        resultado.errores = info["errores"]
        resultado.tiempo_segundos = time.time() - t_inicio
        return resultado

    # Determinar modelo base
    modelo = modelo_base or info.get("modelo_base", "")
    if not modelo:
        resultado.errores.append(
            "No se pudo determinar el modelo base. "
            "Especifiquelo con el parametro modelo_base."
        )
        resultado.tiempo_segundos = time.time() - t_inicio
        return resultado

    resultado.modelo_base = modelo

    try:
        # Verificar dependencias
        from app.finetuning.train_lora import verificar_dependencias
        deps = verificar_dependencias()
        if not deps.get("torch") or not deps.get("transformers") or not deps.get("peft"):
            resultado.errores.append(
                "Dependencias faltantes: torch, transformers y peft son requeridos para merge."
            )
            resultado.tiempo_segundos = time.time() - t_inicio
            return resultado

        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer

        # 2. Cargar modelo base
        logger.info("Cargando modelo base: %s", modelo)
        model = AutoModelForCausalLM.from_pretrained(
            modelo,
            torch_dtype=torch.float16,
            device_map="cpu",  # Merge en CPU para evitar OOM
            trust_remote_code=True,
        )

        # 3. Cargar adaptador LoRA
        logger.info("Cargando adaptador LoRA desde: %s", directorio_adaptador)
        model = PeftModel.from_pretrained(model, str(directorio_adaptador))

        # 4. Fusionar pesos
        logger.info("Fusionando pesos del adaptador con el modelo base...")
        model = model.merge_and_unload()

        # 5. Guardar modelo fusionado
        ruta_salida = Path(directorio_salida)
        ruta_salida.mkdir(parents=True, exist_ok=True)

        logger.info("Guardando modelo fusionado en: %s", ruta_salida)
        model.save_pretrained(str(ruta_salida), safe_serialization=True)

        # 6. Copiar/guardar tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            str(directorio_adaptador)
            if (Path(directorio_adaptador) / "tokenizer_config.json").exists()
            else modelo,
            trust_remote_code=True,
        )
        tokenizer.save_pretrained(str(ruta_salida))

        # 7. Guardar metadata
        metadata = {
            "modelo_base": modelo,
            "adaptador_origen": str(directorio_adaptador),
            "fecha_merge": resultado.fecha,
            "lora_rank": info.get("lora_rank"),
            "lora_alpha": info.get("lora_alpha"),
            "target_modules": info.get("target_modules"),
            "framework": "cecilia-v2",
        }
        with (ruta_salida / "cecilia_merge_info.json").open("w") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        # 8. Calcular tamano
        total_bytes = sum(f.stat().st_size for f in ruta_salida.rglob("*") if f.is_file())
        resultado.tamano_modelo_gb = round(total_bytes / (1024**3), 2)

        # 9. Push to Hub (opcional)
        if push_to_hub and hub_repo:
            logger.info("Subiendo a HuggingFace Hub: %s", hub_repo)
            model.push_to_hub(hub_repo)
            tokenizer.push_to_hub(hub_repo)

        resultado.exitoso = True
        logger.info(
            "Merge completado exitosamente: %s (%.2f GB)",
            ruta_salida, resultado.tamano_modelo_gb,
        )

    except Exception as exc:
        logger.error("Error durante merge: %s", exc, exc_info=True)
        resultado.errores.append(str(exc))

    resultado.tiempo_segundos = round(time.time() - t_inicio, 2)

    # Guardar resultado
    ruta_resultado = Path(directorio_salida) / "resultado_merge.json"
    ruta_resultado.parent.mkdir(parents=True, exist_ok=True)
    with ruta_resultado.open("w", encoding="utf-8") as f:
        json.dump(resultado.a_dict(), f, ensure_ascii=False, indent=2)

    return resultado


def crear_ollama_modelfile(
    directorio_modelo: str | Path,
    nombre_modelo: str = "cecilia-v2",
    system_prompt: str | None = None,
) -> Path:
    """Crea un Modelfile de Ollama para el modelo fusionado.

    Args:
        directorio_modelo: Directorio del modelo fusionado.
        nombre_modelo: Nombre para registrar en Ollama.
        system_prompt: Prompt de sistema personalizado.

    Returns:
        Ruta del Modelfile generado.
    """
    if system_prompt is None:
        system_prompt = (
            "Eres CecilIA, el asistente de inteligencia artificial de la "
            "Contraloria General de la Republica de Colombia. Tu funcion es "
            "asistir a los auditores en procesos de control fiscal, analisis "
            "de hallazgos, interpretacion normativa, calculos de materialidad "
            "y revision de contratacion publica. Responde de forma tecnica, "
            "precisa y fundamentada en la normatividad colombiana vigente."
        )

    ruta = Path(directorio_modelo)
    modelfile_content = f"""# CecilIA v2 — Modelo fine-tuned para control fiscal
# Contraloria General de la Republica de Colombia

FROM {ruta.resolve()}

PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_predict 4096
PARAMETER stop "### Instruccion:"
PARAMETER stop "### Entrada:"

SYSTEM \"\"\"{system_prompt}\"\"\"

TEMPLATE \"\"\"### Instruccion:
{{{{ .System }}}}

{{{{ .Prompt }}}}

### Respuesta:
{{{{ .Response }}}}\"\"\"
"""

    modelfile_path = ruta / "Modelfile"
    with modelfile_path.open("w", encoding="utf-8") as f:
        f.write(modelfile_content)

    logger.info("Modelfile de Ollama creado: %s", modelfile_path)
    logger.info("Para registrar en Ollama ejecute: ollama create %s -f %s", nombre_modelo, modelfile_path)

    return modelfile_path
