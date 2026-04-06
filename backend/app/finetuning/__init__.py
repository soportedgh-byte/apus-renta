"""
CecilIA v2 — Pipeline de fine-tuning LoRA y benchmark de modelos
Contraloria General de la Republica de Colombia

Paquete: app/finetuning
Proposito: Construccion de datasets, entrenamiento LoRA/QLoRA,
           evaluacion comparativa y fusion de adaptadores.
Sprint: 9
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026

Modulos:
    dataset_builder  — Construccion de datasets JSONL con anonimizacion
    train_lora       — Entrenamiento LoRA/QLoRA con PEFT + bitsandbytes
    eval_model       — Benchmark de 50 preguntas en 5 categorias + informe DOCX
    merge_adapter    — Fusion de adaptadores LoRA con modelo base
"""
