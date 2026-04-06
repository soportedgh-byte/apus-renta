"""
CecilIA v2 — Entrenamiento LoRA/QLoRA para modelos LLM
Contraloria General de la Republica de Colombia

Archivo: app/finetuning/train_lora.py
Proposito: Fine-tuning con LoRA/QLoRA usando PEFT + bitsandbytes.
           Compatible con Qwen3, Llama y Mistral.
Sprint: 9
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("cecilia.finetuning.train")

# ── Configuracion de entrenamiento ────────────────────────────────────────────

@dataclass
class ConfiguracionLoRA:
    """Parametros de entrenamiento LoRA/QLoRA."""

    # Modelo base
    modelo_base: str = "Qwen/Qwen2.5-7B-Instruct"
    revision: str = "main"

    # LoRA hiperparametros
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    target_modules: list[str] = field(
        default_factory=lambda: ["q_proj", "v_proj"]
    )
    bias: str = "none"
    task_type: str = "CAUSAL_LM"

    # QLoRA (cuantizacion 4-bit)
    usar_qlora: bool = True
    bnb_4bit_compute_dtype: str = "float16"
    bnb_4bit_quant_type: str = "nf4"
    bnb_4bit_use_double_quant: bool = True

    # Entrenamiento
    epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    weight_decay: float = 0.01
    warmup_ratio: float = 0.03
    lr_scheduler_type: str = "cosine"
    max_seq_length: int = 2048

    # Guardado y checkpoints
    save_steps: int = 100
    logging_steps: int = 10
    eval_steps: int = 50
    save_total_limit: int = 3

    # Directorios
    directorio_salida: str = "modelos/lora_cecilia"
    directorio_logs: str = "modelos/logs"
    directorio_cache: str = "modelos/cache"

    # Semilla para reproducibilidad
    seed: int = 42

    def a_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ResultadoEntrenamiento:
    """Resultado de un entrenamiento LoRA/QLoRA."""

    exitoso: bool = False
    modelo_base: str = ""
    directorio_adaptador: str = ""
    epoca_final: int = 0
    loss_final: float = 0.0
    loss_evaluacion: float = 0.0
    tiempo_total_segundos: float = 0.0
    pasos_totales: int = 0
    ejemplos_entrenamiento: int = 0
    ejemplos_evaluacion: int = 0
    hiperparametros: dict[str, Any] = field(default_factory=dict)
    metricas_por_paso: list[dict[str, Any]] = field(default_factory=list)
    errores: list[str] = field(default_factory=list)
    fecha_inicio: str = ""
    fecha_fin: str = ""
    gpu_utilizada: str = ""

    def a_dict(self) -> dict[str, Any]:
        return asdict(self)


# ── Formato de prompt ────────────────────────────────────────────────────────

TEMPLATE_PROMPT = """### Instruccion:
{instruction}

### Entrada:
{input}

### Respuesta:
{output}"""

TEMPLATE_PROMPT_SIN_INPUT = """### Instruccion:
{instruction}

### Respuesta:
{output}"""


def formatear_ejemplo(ejemplo: dict[str, str]) -> str:
    """Formatea un ejemplo de entrenamiento al template de instruccion.

    Args:
        ejemplo: Dict con 'instruction', 'input' (opcional), 'output'.

    Returns:
        Texto formateado listo para tokenizacion.
    """
    if ejemplo.get("input", "").strip():
        return TEMPLATE_PROMPT.format(**ejemplo)
    return TEMPLATE_PROMPT_SIN_INPUT.format(
        instruction=ejemplo["instruction"],
        output=ejemplo["output"],
    )


# ── Verificacion de dependencias ────────────────────────────────────────────

def verificar_dependencias() -> dict[str, bool]:
    """Verifica que las dependencias de entrenamiento esten disponibles.

    Returns:
        Dict con el estado de cada dependencia.
    """
    deps = {}

    # torch
    try:
        import torch
        deps["torch"] = True
        deps["torch_version"] = torch.__version__
        deps["cuda_disponible"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            deps["gpu_nombre"] = torch.cuda.get_device_name(0)
            deps["gpu_memoria_gb"] = round(
                torch.cuda.get_device_properties(0).total_mem / 1e9, 1
            )
    except ImportError:
        deps["torch"] = False
        deps["cuda_disponible"] = False

    # transformers
    try:
        import transformers
        deps["transformers"] = True
        deps["transformers_version"] = transformers.__version__
    except ImportError:
        deps["transformers"] = False

    # peft
    try:
        import peft
        deps["peft"] = True
        deps["peft_version"] = peft.__version__
    except ImportError:
        deps["peft"] = False

    # bitsandbytes
    try:
        import bitsandbytes
        deps["bitsandbytes"] = True
        deps["bitsandbytes_version"] = bitsandbytes.__version__
    except ImportError:
        deps["bitsandbytes"] = False

    # datasets
    try:
        import datasets
        deps["datasets"] = True
        deps["datasets_version"] = datasets.__version__
    except ImportError:
        deps["datasets"] = False

    # trl
    try:
        import trl
        deps["trl"] = True
        deps["trl_version"] = trl.__version__
    except ImportError:
        deps["trl"] = False

    deps["todas_disponibles"] = all([
        deps.get("torch", False),
        deps.get("transformers", False),
        deps.get("peft", False),
        deps.get("datasets", False),
    ])

    return deps


# ── Carga de datos ──────────────────────────────────────────────────────────

def cargar_dataset_jsonl(ruta: str | Path) -> list[dict[str, str]]:
    """Carga un dataset JSONL y lo formatea para entrenamiento.

    Args:
        ruta: Ruta al archivo JSONL.

    Returns:
        Lista de ejemplos formateados.
    """
    ejemplos = []
    with Path(ruta).open("r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if linea:
                d = json.loads(linea)
                ejemplos.append({
                    "instruction": d["instruction"],
                    "input": d.get("input", ""),
                    "output": d["output"],
                    "text": formatear_ejemplo(d),
                })
    logger.info("Dataset cargado: %d ejemplos desde %s", len(ejemplos), ruta)
    return ejemplos


def dividir_train_eval(
    ejemplos: list[dict],
    porcentaje_eval: float = 0.15,
    seed: int = 42,
) -> tuple[list[dict], list[dict]]:
    """Divide el dataset en entrenamiento y evaluacion.

    Args:
        ejemplos: Lista de ejemplos.
        porcentaje_eval: Porcentaje para evaluacion (0.0-1.0).
        seed: Semilla aleatoria.

    Returns:
        Tupla (train, eval).
    """
    import random
    rng = random.Random(seed)
    shuffled = list(ejemplos)
    rng.shuffle(shuffled)

    n_eval = max(1, int(len(shuffled) * porcentaje_eval))
    return shuffled[n_eval:], shuffled[:n_eval]


# ── Entrenamiento principal ────────────────────────────────────────────────

def entrenar_lora(
    ruta_dataset: str | Path,
    config: ConfiguracionLoRA | None = None,
    callback_progreso: Any = None,
) -> ResultadoEntrenamiento:
    """Ejecuta el entrenamiento LoRA/QLoRA completo.

    Args:
        ruta_dataset: Ruta al archivo JSONL con los datos de entrenamiento.
        config: Configuracion de hiperparametros. None = valores por defecto.
        callback_progreso: Callback opcional (paso, total, loss) para reportar progreso.

    Returns:
        ResultadoEntrenamiento con metricas y estado.
    """
    config = config or ConfiguracionLoRA()
    resultado = ResultadoEntrenamiento(
        modelo_base=config.modelo_base,
        hiperparametros=config.a_dict(),
        fecha_inicio=datetime.now(timezone.utc).isoformat(),
    )

    t_inicio = time.time()

    # 1. Verificar dependencias
    deps = verificar_dependencias()
    if not deps.get("todas_disponibles"):
        faltantes = [
            k for k in ("torch", "transformers", "peft", "datasets")
            if not deps.get(k, False)
        ]
        resultado.errores.append(
            f"Dependencias faltantes: {', '.join(faltantes)}. "
            "Instale con: pip install torch transformers peft bitsandbytes datasets trl"
        )
        resultado.fecha_fin = datetime.now(timezone.utc).isoformat()
        resultado.tiempo_total_segundos = time.time() - t_inicio
        return resultado

    if not deps.get("cuda_disponible") and config.usar_qlora:
        logger.warning("CUDA no disponible — QLoRA requiere GPU. Desactivando cuantizacion.")
        config.usar_qlora = False

    resultado.gpu_utilizada = deps.get("gpu_nombre", "CPU")

    try:
        import torch
        from datasets import Dataset
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, TaskType
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            BitsAndBytesConfig,
            TrainingArguments,
            Trainer,
            DataCollatorForLanguageModeling,
        )

        # 2. Cargar y dividir dataset
        logger.info("Cargando dataset desde %s", ruta_dataset)
        ejemplos = cargar_dataset_jsonl(ruta_dataset)
        train_data, eval_data = dividir_train_eval(
            ejemplos, porcentaje_eval=0.15, seed=config.seed
        )
        resultado.ejemplos_entrenamiento = len(train_data)
        resultado.ejemplos_evaluacion = len(eval_data)
        logger.info(
            "Dataset dividido: %d train, %d eval",
            len(train_data), len(eval_data),
        )

        # 3. Cargar tokenizer
        logger.info("Cargando tokenizer: %s", config.modelo_base)
        tokenizer = AutoTokenizer.from_pretrained(
            config.modelo_base,
            revision=config.revision,
            cache_dir=config.directorio_cache,
            trust_remote_code=True,
        )
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            tokenizer.pad_token_id = tokenizer.eos_token_id

        # 4. Tokenizar datos
        def tokenizar(ejemplo: dict) -> dict:
            tokens = tokenizer(
                ejemplo["text"],
                truncation=True,
                max_length=config.max_seq_length,
                padding="max_length",
            )
            tokens["labels"] = tokens["input_ids"].copy()
            return tokens

        ds_train = Dataset.from_list(train_data).map(
            tokenizar, remove_columns=["instruction", "input", "output", "text"]
        )
        ds_eval = Dataset.from_list(eval_data).map(
            tokenizar, remove_columns=["instruction", "input", "output", "text"]
        )

        # 5. Configurar cuantizacion (QLoRA)
        bnb_config = None
        if config.usar_qlora:
            logger.info("Configurando QLoRA con cuantizacion 4-bit NF4")
            compute_dtype = getattr(torch, config.bnb_4bit_compute_dtype, torch.float16)
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=compute_dtype,
                bnb_4bit_quant_type=config.bnb_4bit_quant_type,
                bnb_4bit_use_double_quant=config.bnb_4bit_use_double_quant,
            )

        # 6. Cargar modelo base
        logger.info("Cargando modelo base: %s", config.modelo_base)
        modelo = AutoModelForCausalLM.from_pretrained(
            config.modelo_base,
            revision=config.revision,
            quantization_config=bnb_config,
            device_map="auto",
            cache_dir=config.directorio_cache,
            trust_remote_code=True,
            torch_dtype=torch.float16 if not config.usar_qlora else None,
        )

        if config.usar_qlora:
            modelo = prepare_model_for_kbit_training(modelo)

        # 7. Configurar LoRA
        logger.info(
            "Configurando LoRA: rank=%d, alpha=%d, target=%s",
            config.lora_rank, config.lora_alpha, config.target_modules,
        )
        lora_config = LoraConfig(
            r=config.lora_rank,
            lora_alpha=config.lora_alpha,
            lora_dropout=config.lora_dropout,
            target_modules=config.target_modules,
            bias=config.bias,
            task_type=TaskType.CAUSAL_LM,
        )
        modelo = get_peft_model(modelo, lora_config)

        # Reportar parametros entrenables
        trainable, total = modelo.get_nb_trainable_parameters()
        logger.info(
            "Parametros: %d entrenables / %d totales (%.2f%%)",
            trainable, total, 100 * trainable / total,
        )

        # 8. Configurar entrenamiento
        Path(config.directorio_salida).mkdir(parents=True, exist_ok=True)
        Path(config.directorio_logs).mkdir(parents=True, exist_ok=True)

        training_args = TrainingArguments(
            output_dir=config.directorio_salida,
            num_train_epochs=config.epochs,
            per_device_train_batch_size=config.batch_size,
            per_device_eval_batch_size=config.batch_size,
            gradient_accumulation_steps=config.gradient_accumulation_steps,
            learning_rate=config.learning_rate,
            weight_decay=config.weight_decay,
            warmup_ratio=config.warmup_ratio,
            lr_scheduler_type=config.lr_scheduler_type,
            logging_dir=config.directorio_logs,
            logging_steps=config.logging_steps,
            eval_strategy="steps",
            eval_steps=config.eval_steps,
            save_strategy="steps",
            save_steps=config.save_steps,
            save_total_limit=config.save_total_limit,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            fp16=torch.cuda.is_available(),
            bf16=False,
            seed=config.seed,
            report_to="none",
            remove_unused_columns=False,
        )

        collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer, mlm=False
        )

        # 9. Entrenar
        logger.info("=" * 60)
        logger.info("INICIANDO ENTRENAMIENTO LoRA")
        logger.info("Modelo: %s", config.modelo_base)
        logger.info("Epochs: %d | LR: %s | Batch: %d",
                     config.epochs, config.learning_rate, config.batch_size)
        logger.info("=" * 60)

        trainer = Trainer(
            model=modelo,
            args=training_args,
            train_dataset=ds_train,
            eval_dataset=ds_eval,
            data_collator=collator,
        )

        train_result = trainer.train()

        # 10. Guardar adaptador LoRA
        logger.info("Guardando adaptador LoRA en %s", config.directorio_salida)
        modelo.save_pretrained(config.directorio_salida)
        tokenizer.save_pretrained(config.directorio_salida)

        # Guardar metricas
        metricas = train_result.metrics
        trainer.log_metrics("train", metricas)
        trainer.save_metrics("train", metricas)

        # Evaluacion final
        eval_metrics = trainer.evaluate()
        trainer.log_metrics("eval", eval_metrics)
        trainer.save_metrics("eval", eval_metrics)

        # 11. Completar resultado
        resultado.exitoso = True
        resultado.directorio_adaptador = str(Path(config.directorio_salida).resolve())
        resultado.epoca_final = config.epochs
        resultado.loss_final = metricas.get("train_loss", 0.0)
        resultado.loss_evaluacion = eval_metrics.get("eval_loss", 0.0)
        resultado.pasos_totales = metricas.get("train_steps", 0)

        logger.info("=" * 60)
        logger.info("ENTRENAMIENTO COMPLETADO")
        logger.info("Loss final: %.4f | Eval loss: %.4f",
                     resultado.loss_final, resultado.loss_evaluacion)
        logger.info("Adaptador guardado en: %s", resultado.directorio_adaptador)
        logger.info("=" * 60)

    except Exception as exc:
        logger.error("Error durante entrenamiento: %s", exc, exc_info=True)
        resultado.errores.append(str(exc))

    resultado.fecha_fin = datetime.now(timezone.utc).isoformat()
    resultado.tiempo_total_segundos = time.time() - t_inicio

    # Guardar resultado como JSON
    ruta_resultado = Path(config.directorio_salida) / "resultado_entrenamiento.json"
    ruta_resultado.parent.mkdir(parents=True, exist_ok=True)
    with ruta_resultado.open("w", encoding="utf-8") as f:
        json.dump(resultado.a_dict(), f, ensure_ascii=False, indent=2)

    return resultado


# ── Utilidades ──────────────────────────────────────────────────────────────

def listar_checkpoints(directorio: str | Path) -> list[dict[str, Any]]:
    """Lista los checkpoints disponibles en un directorio de entrenamiento.

    Args:
        directorio: Directorio raiz del entrenamiento.

    Returns:
        Lista de checkpoints con su informacion.
    """
    checkpoints = []
    ruta = Path(directorio)
    if not ruta.exists():
        return checkpoints

    for d in sorted(ruta.iterdir()):
        if d.is_dir() and d.name.startswith("checkpoint-"):
            paso = int(d.name.split("-")[1])
            trainer_state = d / "trainer_state.json"
            info: dict[str, Any] = {"paso": paso, "directorio": str(d)}

            if trainer_state.exists():
                with trainer_state.open() as f:
                    state = json.load(f)
                info["loss"] = state.get("log_history", [{}])[-1].get("loss", None)
                info["epoch"] = state.get("epoch", None)

            checkpoints.append(info)

    return checkpoints


def limpiar_checkpoints(directorio: str | Path, mantener: int = 1) -> int:
    """Elimina checkpoints antiguos manteniendo solo los N mas recientes.

    Args:
        directorio: Directorio raiz del entrenamiento.
        mantener: Numero de checkpoints a conservar.

    Returns:
        Numero de checkpoints eliminados.
    """
    checkpoints = listar_checkpoints(directorio)
    if len(checkpoints) <= mantener:
        return 0

    eliminados = 0
    for cp in checkpoints[:-mantener]:
        ruta = Path(cp["directorio"])
        if ruta.exists():
            shutil.rmtree(ruta)
            eliminados += 1
            logger.info("Checkpoint eliminado: %s", ruta)

    return eliminados


def obtener_info_modelo(directorio: str | Path) -> dict[str, Any]:
    """Obtiene informacion sobre un modelo LoRA entrenado.

    Args:
        directorio: Directorio del adaptador LoRA.

    Returns:
        Dict con informacion del modelo.
    """
    ruta = Path(directorio)
    info: dict[str, Any] = {
        "directorio": str(ruta),
        "existe": ruta.exists(),
    }

    if not ruta.exists():
        return info

    # Leer config del adaptador
    adapter_config = ruta / "adapter_config.json"
    if adapter_config.exists():
        with adapter_config.open() as f:
            config = json.load(f)
        info["modelo_base"] = config.get("base_model_name_or_path", "")
        info["lora_rank"] = config.get("r", 0)
        info["lora_alpha"] = config.get("lora_alpha", 0)
        info["target_modules"] = config.get("target_modules", [])

    # Leer resultado de entrenamiento
    resultado_json = ruta / "resultado_entrenamiento.json"
    if resultado_json.exists():
        with resultado_json.open() as f:
            resultado = json.load(f)
        info["loss_final"] = resultado.get("loss_final", None)
        info["loss_evaluacion"] = resultado.get("loss_evaluacion", None)
        info["fecha_entrenamiento"] = resultado.get("fecha_fin", "")
        info["tiempo_entrenamiento_s"] = resultado.get("tiempo_total_segundos", 0)

    # Tamano del adaptador
    total_bytes = sum(f.stat().st_size for f in ruta.rglob("*") if f.is_file())
    info["tamano_mb"] = round(total_bytes / (1024 * 1024), 1)

    return info
