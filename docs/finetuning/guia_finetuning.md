# Guía de Fine-Tuning del Modelo LLM — CecilIA v2

> Sistema de IA para Control Fiscal
> Contraloría General de la República de Colombia

## 1. Introducción

Esta guía describe el proceso de fine-tuning (ajuste fino) de modelos de lenguaje para CecilIA v2. El objetivo es adaptar un modelo base al dominio del control fiscal colombiano, mejorando la precisión en terminología jurídica, procedimientos de auditoría y normatividad vigente.

## 2. Cuándo Aplicar Fine-Tuning

### 2.1 Fine-tuning vs. RAG

| Criterio | RAG (sin fine-tuning) | Fine-tuning | RAG + Fine-tuning |
|----------|----------------------|-------------|-------------------|
| Conocimiento actualizable | Excelente | Limitado | Excelente |
| Tono y estilo específico | Limitado | Excelente | Excelente |
| Terminología especializada | Bueno | Excelente | Excelente |
| Costo de implementación | Bajo | Alto | Muy alto |
| Tiempo de preparación | Bajo | Alto | Muy alto |
| Citación de fuentes | Excelente | Limitado | Excelente |

### 2.2 Casos recomendados para fine-tuning

- El modelo base comete errores recurrentes en terminología fiscal colombiana.
- Se requiere un tono institucional específico de la CGR que no se logra con prompts.
- Los formatos de salida (hallazgos, informes) no se adhieren consistentemente a la estructura requerida.
- El rendimiento del modelo base es insuficiente en benchmarks específicos del dominio.

### 2.3 Casos donde NO se recomienda fine-tuning

- La información cambia frecuentemente (usar RAG en su lugar).
- El modelo base ya produce resultados aceptables con buenos prompts.
- No se dispone de suficientes datos de entrenamiento de alta calidad.

## 3. Preparación del Dataset

### 3.1 Fuentes de datos

| Fuente | Tipo | Volumen estimado |
|--------|------|-----------------|
| Pares pregunta-respuesta validados por auditores | Supervisado | 500-1000 ejemplos |
| Hallazgos fiscales previos (anonimizados) | Supervisado | 200-500 ejemplos |
| Conversaciones de prueba revisadas | Supervisado | 300-600 ejemplos |
| Informes de auditoría modelo | Supervisado | 100-200 ejemplos |

### 3.2 Formato del dataset

El formato recomendado es JSONL (JSON Lines) con la estructura de mensajes de chat:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Eres CecilIA, asistente de IA de la Contraloría General de la República de Colombia, especializada en control fiscal."
    },
    {
      "role": "user",
      "content": "Explica qué es la materialidad en una auditoría financiera según las NIA."
    },
    {
      "role": "assistant",
      "content": "La materialidad, según la NIA 320, es el importe o importes establecidos por el auditor..."
    }
  ]
}
```

### 3.3 Criterios de calidad del dataset

1. **Precisión jurídica:** Toda referencia normativa debe ser verificada y vigente.
2. **Terminología correcta:** Uso consistente de términos del control fiscal colombiano.
3. **Estructura CCCE:** Los hallazgos deben seguir la estructura Condición-Criterio-Causa-Efecto.
4. **Anonimización:** Ningún ejemplo debe contener datos personales o información clasificada.
5. **Diversidad:** Cubrir diferentes tipos de consultas, direcciones técnicas y complejidades.
6. **Validación experta:** Cada ejemplo debe ser revisado por al menos un auditor experimentado.

### 3.4 Proceso de curación

```
Datos crudos
     │
     ▼
┌─────────────────┐
│  Anonimización  │ ← Eliminar datos personales y sensibles
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Formateo JSONL │ ← Convertir a formato de entrenamiento
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Revisión par   │ ← Dos revisores por ejemplo
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Validación     │ ← Auditor experto aprueba el ejemplo
│  experta        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  División       │ ← 80% entrenamiento, 10% validación, 10% test
│  train/val/test │
└─────────────────┘
```

## 4. Proceso de Fine-Tuning

### 4.1 Con OpenAI

```python
"""
Ejemplo de fine-tuning con la API de OpenAI.
Requiere: pip install openai
"""
import openai

client = openai.OpenAI()

# 1. Subir el archivo de entrenamiento
archivo = client.files.create(
    file=open("dataset_cecilia_train.jsonl", "rb"),
    purpose="fine-tune",
)

# 2. Crear el trabajo de fine-tuning
trabajo = client.fine_tuning.jobs.create(
    training_file=archivo.id,
    model="gpt-4o-mini-2024-07-18",
    hyperparameters={
        "n_epochs": 3,
        "learning_rate_multiplier": 1.0,
        "batch_size": "auto",
    },
    suffix="cecilia-v2",
)

# 3. Monitorear el progreso
print(f"Trabajo creado: {trabajo.id}")
print(f"Estado: {trabajo.status}")
```

### 4.2 Hiperparámetros recomendados

| Parámetro | Valor recomendado | Notas |
|-----------|-------------------|-------|
| Épocas (n_epochs) | 3-5 | Más épocas con datasets pequeños |
| Tasa de aprendizaje | 1.0x (automático) | Reducir si hay sobreajuste |
| Tamaño de lote | Automático | El proveedor optimiza |
| Longitud máxima de contexto | 4096 tokens | Ajustar según necesidad |

### 4.3 Con modelos locales (Ollama + LoRA)

Para escenarios donde se requiere soberanía total de datos:

```bash
# 1. Preparar el dataset en formato Alpaca
python scripts/convertir_a_alpaca.py \
    --input dataset_cecilia_train.jsonl \
    --output dataset_alpaca.json

# 2. Fine-tuning con LoRA usando unsloth o axolotl
# (requiere GPU NVIDIA con al menos 16 GB VRAM)
python -m axolotl.train config_cecilia_lora.yaml

# 3. Exportar modelo a formato GGUF para Ollama
python -m axolotl.export --format gguf --output cecilia-v2.gguf

# 4. Crear modelo en Ollama
ollama create cecilia-v2 -f Modelfile
```

## 5. Evaluación del Modelo

### 5.1 Métricas cuantitativas

| Métrica | Descripción | Umbral aceptable |
|---------|-------------|------------------|
| Precisión terminológica | Uso correcto de términos fiscales | >= 95% |
| Adherencia a formato CCCE | Hallazgos con estructura completa | >= 90% |
| Citación correcta | Referencias normativas verificables | >= 90% |
| Coherencia | Respuestas lógicas y completas | >= 85% |
| Latencia | Tiempo de respuesta | < 5 segundos |

### 5.2 Evaluación con benchmark propio

Utilizar el script `scripts/benchmark_modelos.py` para comparar:

```bash
# Comparar modelo base vs. modelo fine-tuned
python scripts/benchmark_modelos.py
```

### 5.3 Evaluación humana

Protocolo de evaluación por auditores expertos:

1. Seleccionar 50 consultas representativas del dataset de test.
2. Generar respuestas con el modelo base y el modelo ajustado.
3. Presentar las respuestas de forma ciega (sin indicar cuál es cuál).
4. Cada auditor evalúa: precisión (1-5), utilidad (1-5), tono (1-5).
5. Compilar resultados y determinar si el fine-tuning aporta mejora significativa.

## 6. Despliegue del Modelo Ajustado

### 6.1 Configuración en CecilIA v2

Actualizar las variables de entorno del backend:

```env
# Modelo ajustado de OpenAI
LLM_MODEL=ft:gpt-4o-mini-2024-07-18:cecilia-v2:XXXXXXXX

# O modelo local
LLM_PROVIDER=ollama
LLM_MODEL=cecilia-v2
LLM_BASE_URL=http://localhost:11434/v1
```

### 6.2 Despliegue gradual

1. **Canario (5% del tráfico):** Dirigir un porcentaje menor al modelo ajustado.
2. **Monitoreo (1 semana):** Comparar métricas de calidad y rendimiento.
3. **Expansión (50%):** Si las métricas son favorables, ampliar el tráfico.
4. **Producción (100%):** Migración completa tras validación.

## 7. Mantenimiento Continuo

### 7.1 Ciclo de actualización

- **Trimestral:** Evaluar la necesidad de reentrenamiento con nuevos datos.
- **Semestral:** Actualizar el dataset con nuevos ejemplos validados.
- **Anual:** Evaluar cambio de modelo base por versiones más recientes.

### 7.2 Monitoreo de deriva

- Rastrear la calidad de respuestas en producción mediante evaluaciones periódicas.
- Detectar degradación en terminología o estructura de hallazgos.
- Reentrenar cuando las métricas caigan por debajo de los umbrales aceptables.

### 7.3 Versionado

- Cada modelo ajustado se versiona con la fecha y el dataset utilizado.
- Mantener al menos las 3 versiones anteriores para posibilidad de rollback.
- Documentar los cambios en el dataset entre versiones.

---

*Guía de Fine-Tuning — CecilIA v2 — Sprint 0 — Abril 2026*
*Equipo Técnico CecilIA — CD-TIC-CGR*
