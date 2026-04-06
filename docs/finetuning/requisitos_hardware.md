# Requisitos de Hardware para Fine-tuning

**CecilIA v2 — Contraloria General de la Republica de Colombia**
**Sprint 9 | Abril 2026**

---

## 1. Resumen de Requisitos

| Escenario | GPU | VRAM | RAM | Disco | Tiempo estimado |
|-----------|-----|------|-----|-------|----------------|
| QLoRA 7B (recomendado) | RTX 3070+ / T4 | 8GB | 16GB | 50GB | 1-2 horas |
| QLoRA 14B | RTX 4090 / A5000 | 16GB | 32GB | 100GB | 2-4 horas |
| LoRA 7B (sin cuantizacion) | A5000 / A100 | 24GB | 32GB | 80GB | 1-3 horas |
| LoRA 14B (sin cuantizacion) | A100 40GB | 40GB | 64GB | 150GB | 3-6 horas |
| Solo inferencia 7B (QLoRA) | RTX 3060+ | 6GB | 16GB | 30GB | N/A |
| Solo benchmark (API) | Cualquiera | N/A | 4GB | 1GB | 30 min |

## 2. Configuraciones Recomendadas

### 2.1 Desarrollo y pruebas (minimo)

```
GPU: NVIDIA RTX 3070 (8GB VRAM)
CPU: 8 cores
RAM: 16GB
Disco: 50GB SSD libre
SO: Ubuntu 22.04 / Windows 11 + WSL2
```

**Notas:**
- Solo QLoRA (4-bit) con modelos de 7B parametros
- Batch size: 1-2
- Gradient accumulation: 8-16

### 2.2 Produccion CGR (recomendado)

```
GPU: NVIDIA A100 40GB o RTX 4090 24GB
CPU: 16 cores
RAM: 64GB
Disco: 500GB NVMe SSD
SO: Ubuntu 22.04 LTS
```

**Notas:**
- Soporta LoRA y QLoRA con modelos hasta 14B
- Batch size: 4-8
- Puede ejecutar entrenamiento y servir inferencia simultaneamente

### 2.3 Nube (alternativa)

| Proveedor | Instancia | GPU | Costo estimado |
|-----------|-----------|-----|---------------|
| AWS | g5.xlarge | A10G 24GB | ~$1.00/hora |
| AWS | p4d.24xlarge | 8x A100 40GB | ~$32.00/hora |
| GCP | a2-highgpu-1g | A100 40GB | ~$3.67/hora |
| Azure | NC24ads_A100_v4 | A100 80GB | ~$3.67/hora |

## 3. Software Requerido

### 3.1 Driver NVIDIA

```bash
# Verificar version
nvidia-smi

# Minimo: Driver 525+ para CUDA 12.0
# Recomendado: Driver 545+ para CUDA 12.3
```

### 3.2 CUDA Toolkit

```bash
# Verificar CUDA
nvcc --version

# Minimo: CUDA 11.8
# Recomendado: CUDA 12.1+
```

### 3.3 Paquetes Python

```bash
pip install torch>=2.1.0 --index-url https://download.pytorch.org/whl/cu121
pip install transformers>=4.40.0
pip install peft>=0.10.0
pip install bitsandbytes>=0.43.0
pip install datasets>=2.18.0
pip install trl>=0.8.0
pip install accelerate>=0.29.0
```

## 4. Optimizacion de Memoria

### 4.1 QLoRA (4-bit)

Reduce el uso de VRAM en ~75%:

```python
config = ConfiguracionLoRA(
    usar_qlora=True,
    bnb_4bit_compute_dtype="float16",
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)
```

### 4.2 Gradient Checkpointing

Intercambia velocidad por memoria:

```python
config = ConfiguracionLoRA(
    gradient_accumulation_steps=8,  # Simula batch grande
    batch_size=1,                   # Batch real pequeno
)
```

### 4.3 Reducir Secuencia

```python
config = ConfiguracionLoRA(
    max_seq_length=1024,  # Reducir de 2048
)
```

## 5. Estimacion de VRAM

Formula aproximada para QLoRA:

```
VRAM ≈ (Parametros_modelo * 0.5 GB/B) + (LoRA_params * 2 bytes) + (Batch * Seq * Hidden * 2 bytes)
```

Ejemplos:
- Qwen2.5-7B QLoRA: ~4GB modelo + 0.1GB LoRA + 2GB activaciones ≈ **6GB**
- Llama-3.1-8B QLoRA: ~4.5GB modelo + 0.1GB LoRA + 2GB activaciones ≈ **7GB**
- Qwen2.5-14B QLoRA: ~8GB modelo + 0.2GB LoRA + 3GB activaciones ≈ **11GB**

## 6. Benchmark sin GPU

El benchmark de evaluacion (50 preguntas) **no requiere GPU** ya que usa APIs externas:

```bash
# Solo necesita conexion a internet y API keys
python scripts/benchmark_modelos.py --proveedores claude,gemini
```

---

*Documento generado por el equipo tecnico CecilIA — CD-TIC-CGR*
