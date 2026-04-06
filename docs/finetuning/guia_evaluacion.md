# Guia de Evaluacion y Benchmark de Modelos

**CecilIA v2 — Contraloria General de la Republica de Colombia**
**Sprint 9 | Abril 2026**

---

## 1. Descripcion del Benchmark

El benchmark de CecilIA v2 evalua modelos LLM con **50 preguntas** distribuidas en **5 categorias** del dominio de control fiscal colombiano:

| Categoria | Preguntas | Descripcion |
|-----------|-----------|-------------|
| Normativo | 10 | Constitucion, leyes, decretos de control fiscal |
| Hallazgos | 10 | Redaccion, clasificacion y analisis de hallazgos |
| Materialidad | 10 | Calculos NIA 320/450/530, muestreo estadistico |
| Financiero | 10 | NICSP, estados financieros, dictamen integral |
| Contratacion | 10 | Ley 80/1993, modalidades, irregularidades |

## 2. Criterios de Calificacion

Cada respuesta se califica de 0 a 10:

| Criterio | Peso | Descripcion |
|----------|------|-------------|
| Precision tecnica | 40% | Datos correctos, normas reales, conceptos exactos |
| Completitud | 30% | Cubre todos los aspectos de la pregunta |
| Claridad | 20% | Estructura logica, lenguaje comprensible |
| Aplicabilidad | 10% | Utilidad practica para el auditor |

## 3. Metodos de Calificacion

### 3.1 Evaluador LLM (recomendado)

Usa un modelo LLM (GPT-4/Claude) como juez automatico:

```bash
python scripts/benchmark_modelos.py --proveedores base --evaluador-llm
```

### 3.2 Evaluacion Heuristica (sin API)

Evaluacion basica por longitud, criterios mencionados, estructura:

```bash
python scripts/benchmark_modelos.py --proveedores base
```

### 3.3 Evaluacion Manual

Exportar respuestas para revision por auditores expertos.

## 4. Ejecutar el Benchmark

### Via script CLI

```bash
# Solo modelo base
python scripts/benchmark_modelos.py --proveedores base

# Comparar base vs Claude
python scripts/benchmark_modelos.py --proveedores base,claude

# Todos los proveedores
python scripts/benchmark_modelos.py --proveedores base,finetuned,claude,gemini

# Solo categorias especificas
python scripts/benchmark_modelos.py --categorias normativo,hallazgos
```

### Via API

```bash
curl -X POST http://localhost:8000/api/modelos/benchmark/ejecutar \
  -H "Content-Type: application/json" \
  -d '{"proveedores": ["base"], "categorias": null}'
```

## 5. Interpretar Resultados

### Informe DOCX

```bash
curl -o informe.docx http://localhost:8000/api/modelos/benchmark/informe
```

El informe incluye:
1. Ranking global de modelos
2. Detalle por categoria
3. Metricas por modelo (promedio, min, max, tiempo)
4. Conclusiones y recomendaciones

### Resultados JSON

```bash
curl http://localhost:8000/api/modelos/benchmark/resultados
```

## 6. Metricas Clave

| Metrica | Descripcion | Objetivo |
|---------|-------------|----------|
| Promedio global | Media de todas las calificaciones | >= 7.0 |
| Tasa de exito | % de preguntas respondidas sin error | >= 95% |
| Tiempo promedio | Segundos por respuesta | < 10s |
| Peor categoria | Categoria con menor promedio | >= 5.0 |

## 7. Comparativa Base vs Fine-tuned

El objetivo del fine-tuning es superar al modelo base en:

- **Precision normativa**: Citar normas colombianas correctamente
- **Formato CGR**: Usar la estructura institucional de hallazgos
- **Terminologia**: Vocabulario tecnico de control fiscal
- **Calculos**: Formulas de materialidad y muestreo

Un fine-tuning exitoso deberia mostrar una mejora de al menos **1-2 puntos** sobre el modelo base en las categorias especializadas.

## 8. Proveedores Soportados

| Proveedor | ID | Requisito |
|-----------|-----|-----------|
| LLM principal (OpenAI/vLLM) | `base` | `LLM_BASE_URL` en .env |
| CecilIA fine-tuned | `finetuned` | Ollama o vLLM local |
| Claude (Anthropic) | `claude` | `ANTHROPIC_API_KEY` |
| Gemini (Google) | `gemini` | `GEMINI_API_KEY` |

---

*Documento generado por el equipo tecnico CecilIA — CD-TIC-CGR*
