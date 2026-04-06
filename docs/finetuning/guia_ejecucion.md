# Guia de Ejecucion del Fine-tuning LoRA/QLoRA

**CecilIA v2 — Contraloria General de la Republica de Colombia**
**Sprint 9 | Abril 2026**

---

## 1. Requisitos Previos

### Software

```bash
pip install torch transformers peft bitsandbytes datasets trl
```

### Hardware minimo

- **LoRA (sin cuantizacion)**: GPU con 24GB VRAM (A5000, RTX 4090)
- **QLoRA (4-bit)**: GPU con 8GB VRAM (RTX 3070, T4)
- **CPU (solo desarrollo)**: 32GB RAM (sin cuantizacion)

## 2. Preparar el Dataset

```bash
# Generar dataset JSONL
cd backend
python -c "from app.finetuning.dataset_builder import construir_dataset; construir_dataset()"
```

O via API:

```bash
curl -X POST http://localhost:8000/api/modelos/dataset/construir \
  -H "Content-Type: application/json" \
  -d '{}'
```

## 3. Verificar Dependencias

```python
from app.finetuning.train_lora import verificar_dependencias
deps = verificar_dependencias()
print(deps)
# {'torch': True, 'cuda_disponible': True, 'gpu_nombre': 'NVIDIA A100', ...}
```

## 4. Configurar Hiperparametros

```python
from app.finetuning.train_lora import ConfiguracionLoRA

config = ConfiguracionLoRA(
    # Modelo base (compatible: Qwen3, Llama, Mistral)
    modelo_base="Qwen/Qwen2.5-7B-Instruct",

    # LoRA
    lora_rank=16,           # Rango: 8-16 recomendado
    lora_alpha=32,          # Alpha: 2x rank
    lora_dropout=0.05,
    target_modules=["q_proj", "v_proj"],

    # QLoRA
    usar_qlora=True,        # 4-bit cuantizacion

    # Entrenamiento
    epochs=3,               # 3-5 epochs
    batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,     # 1e-4 a 5e-4

    # Checkpoints
    save_steps=100,
    directorio_salida="modelos/lora_cecilia",
)
```

## 5. Ejecutar Entrenamiento

### Via Python

```python
from app.finetuning.train_lora import entrenar_lora

resultado = entrenar_lora(
    ruta_dataset="dataset_cecilia.jsonl",
    config=config,
)

if resultado.exitoso:
    print(f"Loss final: {resultado.loss_final:.4f}")
    print(f"Adaptador: {resultado.directorio_adaptador}")
else:
    print(f"Errores: {resultado.errores}")
```

### Via API

```bash
curl -X POST http://localhost:8000/api/modelos/train/iniciar \
  -H "Content-Type: application/json" \
  -d '{
    "ruta_dataset": "dataset_cecilia.jsonl",
    "modelo_base": "Qwen/Qwen2.5-7B-Instruct",
    "lora_rank": 16,
    "epochs": 3
  }'
```

## 6. Monitorear Progreso

```bash
# Ver checkpoints
curl http://localhost:8000/api/modelos/train/checkpoints

# Ver info del modelo
curl http://localhost:8000/api/modelos/train/info

# Ver tarea activa
curl http://localhost:8000/api/modelos/tareas/{tarea_id}
```

## 7. Merge del Adaptador

Despues del entrenamiento, fusionar el adaptador con el modelo base:

```python
from app.finetuning.merge_adapter import merge_lora

resultado = merge_lora(
    directorio_adaptador="modelos/lora_cecilia",
    directorio_salida="modelos/cecilia_v2_merged",
)
```

## 8. Despliegue con Ollama

```python
from app.finetuning.merge_adapter import crear_ollama_modelfile

crear_ollama_modelfile(
    directorio_modelo="modelos/cecilia_v2_merged",
    nombre_modelo="cecilia-v2",
)
```

```bash
ollama create cecilia-v2 -f modelos/cecilia_v2_merged/Modelfile
ollama run cecilia-v2 "Que es el control fiscal?"
```

## 9. Modelos Base Compatibles

| Modelo | Parametros | VRAM QLoRA | Notas |
|--------|-----------|------------|-------|
| Qwen/Qwen2.5-7B-Instruct | 7B | ~6GB | Recomendado para CecilIA |
| meta-llama/Llama-3.1-8B-Instruct | 8B | ~7GB | Buena alternativa |
| mistralai/Mistral-7B-Instruct-v0.3 | 7B | ~6GB | Rapido, buen espanol |
| Qwen/Qwen2.5-14B-Instruct | 14B | ~12GB | Mejor calidad, mas VRAM |

## 10. Problemas Comunes

| Problema | Solucion |
|----------|----------|
| CUDA out of memory | Reducir batch_size, activar QLoRA, reducir max_seq_length |
| Loss no converge | Aumentar epochs, ajustar learning_rate, verificar dataset |
| Import error PEFT | `pip install peft>=0.10.0` |
| Modelo no genera bien | Verificar template de prompt, aumentar datos de entrenamiento |

---

*Documento generado por el equipo tecnico CecilIA — CD-TIC-CGR*
