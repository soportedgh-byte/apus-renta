# Guia de Preparacion de Dataset para Fine-tuning

**CecilIA v2 — Contraloria General de la Republica de Colombia**
**Sprint 9 | Abril 2026**

---

## 1. Introduccion

Esta guia describe el proceso de construccion de datasets JSONL para el fine-tuning de modelos LLM especializados en control fiscal colombiano.

## 2. Formato JSONL

Cada linea del archivo de entrenamiento es un objeto JSON con la siguiente estructura:

```json
{
  "instruction": "Instruccion clara sobre la tarea a realizar",
  "input": "Contexto o datos de entrada (puede estar vacio)",
  "output": "Respuesta esperada del modelo",
  "metadata": {
    "categoria": "hallazgos",
    "dificultad": "alta",
    "anonimizado": true
  }
}
```

### Campos obligatorios

| Campo | Descripcion | Ejemplo |
|-------|-------------|---------|
| `instruction` | Tarea que el modelo debe realizar | "Redacta un hallazgo de auditoria..." |
| `input` | Datos de contexto para la tarea | "La entidad ABC..." |
| `output` | Respuesta ideal esperada | "HALLAZGO: Sobrecosto en..." |

### Campos opcionales

| Campo | Descripcion |
|-------|-------------|
| `metadata.categoria` | Clasificacion del ejemplo |
| `metadata.dificultad` | baja, media, alta |
| `metadata.anonimizado` | Si ya fue procesado por anonimizacion |

## 3. Categorias de Entrenamiento

El dataset se organiza en 5 categorias:

1. **hallazgos** — Redaccion y analisis de hallazgos de auditoria con los 4 elementos (condicion, criterio, causa, efecto)
2. **preguntas_frecuentes** — Conceptos basicos de control fiscal colombiano
3. **interpretaciones_normativas** — Analisis de normas (Ley 80/1993, Ley 610/2000, etc.)
4. **calculos_materialidad** — Calculo de materialidad segun NIA 320/450/530
5. **contratacion** — Analisis de contratacion publica y deteccion de irregularidades

## 4. Criterios de Calidad

### Cada ejemplo debe cumplir:

- **Precision tecnica**: Citar normas reales y vigentes (verificar en Regimen Legal de Bogota)
- **Completitud**: Cubrir todos los aspectos relevantes de la pregunta
- **Formato estructurado**: Usar numeracion, subtitulos, tablas cuando aplique
- **Lenguaje institucional**: Formal, tecnico, alineado con la terminologia de la CGR
- **Anonimizacion**: Sin datos personales reales (cedulas, nombres, NIT)

### Longitud recomendada:

| Tipo | Instruccion | Input | Output |
|------|------------|-------|--------|
| Hallazgos | 20-50 palabras | 30-100 palabras | 200-500 palabras |
| Preguntas frecuentes | 15-30 palabras | 10-30 palabras | 150-400 palabras |
| Normativo | 20-40 palabras | 10-50 palabras | 200-500 palabras |
| Materialidad | 20-40 palabras | 30-80 palabras | 200-500 palabras |
| Contratacion | 20-50 palabras | 30-100 palabras | 200-500 palabras |

## 5. Generacion Automatica

Usar el modulo `dataset_builder.py`:

```python
from app.finetuning.dataset_builder import construir_dataset

# Generar dataset completo
stats = construir_dataset(ruta_salida="dataset_cecilia.jsonl")
print(f"Generados: {stats.total_ejemplos} ejemplos")
print(f"Tokens estimados: {stats.tokens_estimados}")

# Generar solo categorias especificas
stats = construir_dataset(
    ruta_salida="dataset_hallazgos.jsonl",
    categorias=["hallazgos", "contratacion"]
)
```

## 6. Generacion via API

```bash
curl -X POST http://localhost:8000/api/modelos/dataset/construir \
  -H "Content-Type: application/json" \
  -d '{"categorias": null, "ruta_salida": "dataset_cecilia.jsonl"}'
```

## 7. Agregar Ejemplos Personalizados

Para agregar ejemplos propios al dataset:

```python
import json

nuevo_ejemplo = {
    "instruction": "Analiza el siguiente contrato y determina si hay irregularidades.",
    "input": "Contrato de prestacion de servicios No. 001-2026...",
    "output": "ANALISIS DE IRREGULARIDADES:\n1. ...\n2. ...",
    "metadata": {"categoria": "contratacion", "fuente": "equipo_auditores"}
}

with open("dataset_cecilia.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(nuevo_ejemplo, ensure_ascii=False) + "\n")
```

## 8. Validacion del Dataset

Antes de entrenar, verificar:

- [ ] Todas las lineas son JSON valido
- [ ] Campos `instruction` y `output` no estan vacios
- [ ] No hay datos personales sin anonimizar
- [ ] Las normas citadas son reales y vigentes
- [ ] La distribucion por categorias es balanceada
- [ ] Minimo 20 ejemplos para fine-tuning basico, 100+ recomendado

---

*Documento generado por el equipo tecnico CecilIA — CD-TIC-CGR*
