"""
CecilIA v2 — Evaluacion comparativa de modelos LLM
Contraloria General de la Republica de Colombia

Archivo: app/finetuning/eval_model.py
Proposito: Benchmark de modelos con 50 preguntas en 5 categorias,
           comparacion base vs fine-tuned vs Claude/Gemini,
           generacion de informe DOCX con resultados.
Sprint: 9
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import io
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("cecilia.finetuning.eval")

# ── Categorias de evaluacion ────────────────────────────────────────────────

CATEGORIAS_EVAL = [
    "normativo",
    "hallazgos",
    "materialidad",
    "financiero",
    "contratacion",
]


# ── Preguntas de benchmark ──────────────────────────────────────────────────

PREGUNTAS_BENCHMARK: list[dict[str, str]] = [
    # === NORMATIVO (10 preguntas) ===
    {"id": "N01", "categoria": "normativo", "pregunta": "Cual es el fundamento constitucional del control fiscal en Colombia y que articulos lo regulan?", "criterios": "Debe mencionar Art. 267-274 de la CP, control posterior y selectivo, CGR como supremo director."},
    {"id": "N02", "categoria": "normativo", "pregunta": "Explica las principales reformas introducidas por el Acto Legislativo 04 de 2019 al control fiscal.", "criterios": "Control concomitante y preventivo, fortalecimiento CGR, sin coadministracion."},
    {"id": "N03", "categoria": "normativo", "pregunta": "Que establece la Ley 610 de 2000 sobre el proceso de responsabilidad fiscal?", "criterios": "Etapas del proceso, prescripcion, auto de apertura, fallo, BREF."},
    {"id": "N04", "categoria": "normativo", "pregunta": "Cuales son los principios del control fiscal segun el Decreto 403 de 2020 (RGCF)?", "criterios": "Eficiencia, economia, eficacia, equidad, valoracion costos ambientales."},
    {"id": "N05", "categoria": "normativo", "pregunta": "Que diferencia hay entre control fiscal micro y control fiscal macro?", "criterios": "Micro: auditorias individuales. Macro: certificacion de cuentas nacionales, evaluacion politica fiscal."},
    {"id": "N06", "categoria": "normativo", "pregunta": "Explica el regimen de inhabilidades e incompatibilidades de los contralores segun la Ley 42 de 1993.", "criterios": "Prohibiciones, periodos de inhabilidad, parentesco, actividad politica."},
    {"id": "N07", "categoria": "normativo", "pregunta": "Que tipos de auditoria contempla la Guia de Auditoria Financiera (GAF) de la CGR?", "criterios": "Financiera, de cumplimiento, de desempeno, especial, integrada."},
    {"id": "N08", "categoria": "normativo", "pregunta": "Como funciona el sistema de alertas tempranas (control concomitante) despues del Acto Legislativo 04 de 2019?", "criterios": "Funcion preventiva, no vinculante, recomendaciones sin coadministrar."},
    {"id": "N09", "categoria": "normativo", "pregunta": "Que establece la Resolucion Organica 012 de 2023 de la CGR sobre rendicion de cuentas?", "criterios": "Plazos, formatos, SIRECI, sujetos obligados, sanciones."},
    {"id": "N10", "categoria": "normativo", "pregunta": "Cuales son las causales de caducidad y prescripcion en el proceso de responsabilidad fiscal?", "criterios": "5 anos para caducidad, 10 anos para prescripcion, interrupcion, suspension."},

    # === HALLAZGOS (10 preguntas) ===
    {"id": "H01", "categoria": "hallazgos", "pregunta": "Describe los 4 elementos obligatorios de un hallazgo de auditoria segun la GAF.", "criterios": "Condicion, criterio, causa, efecto. Cada uno con su definicion y ejemplo."},
    {"id": "H02", "categoria": "hallazgos", "pregunta": "Como se clasifica un hallazgo segun su connotacion juridica?", "criterios": "Administrativo, fiscal, disciplinario, penal. Puede tener multiples connotaciones."},
    {"id": "H03", "categoria": "hallazgos", "pregunta": "Redacta un hallazgo fiscal sobre sobrecostos en contratacion de TI por $800 millones.", "criterios": "Condicion cuantificada, criterio normativo especifico, causa estructural, efecto patrimonial."},
    {"id": "H04", "categoria": "hallazgos", "pregunta": "Que es la comunicacion de hallazgos y cual es el procedimiento?", "criterios": "Traslado al auditado, plazo de respuesta (5 dias), incorporacion al informe definitivo."},
    {"id": "H05", "categoria": "hallazgos", "pregunta": "Como se determina si un hallazgo tiene connotacion penal?", "criterios": "Tipificacion en Codigo Penal, peculado, prevaricato, contratos sin requisitos legales."},
    {"id": "H06", "categoria": "hallazgos", "pregunta": "Que diferencia hay entre un hallazgo y una observacion en auditoria fiscal?", "criterios": "Hallazgo: evidencia suficiente, 4 elementos. Observacion: situacion que requiere seguimiento."},
    {"id": "H07", "categoria": "hallazgos", "pregunta": "Explica el concepto de beneficio de auditoria y como se calcula.", "criterios": "Beneficios directos e indirectos, formula, reporte a la CGR, plan de mejoramiento."},
    {"id": "H08", "categoria": "hallazgos", "pregunta": "Como se documenta la evidencia de un hallazgo de auditoria?", "criterios": "Suficiente, competente, pertinente, relevante. Papeles de trabajo, cadena de custodia."},
    {"id": "H09", "categoria": "hallazgos", "pregunta": "Que es el plan de mejoramiento y como se formula despues de una auditoria?", "criterios": "Acciones correctivas, responsables, plazos, indicadores, seguimiento por CGR."},
    {"id": "H10", "categoria": "hallazgos", "pregunta": "Identifica las debilidades de este hallazgo: 'La entidad no cumplio la ley. Criterio: varias normas. Causa: desconocida. Efecto: perjuicio.'", "criterios": "Condicion vaga, criterio sin norma especifica, causa sin investigar, efecto sin cuantificar."},

    # === MATERIALIDAD (10 preguntas) ===
    {"id": "M01", "categoria": "materialidad", "pregunta": "Explica el concepto de materialidad en auditoria financiera segun NIA 320.", "criterios": "Importancia relativa, juicio profesional, bases de calculo, materialidad global vs ejecucion."},
    {"id": "M02", "categoria": "materialidad", "pregunta": "Calcula la materialidad global para una entidad con ingresos de $5 billones usando el 1% de ingresos.", "criterios": "Materialidad global = $50.000 millones. Materialidad ejecucion ~75% = $37.500 millones."},
    {"id": "M03", "categoria": "materialidad", "pregunta": "Que factores se consideran para seleccionar la base de calculo de materialidad?", "criterios": "Naturaleza de la entidad, volatilidad, usuarios, tipo de auditoria, benchmarks del sector."},
    {"id": "M04", "categoria": "materialidad", "pregunta": "Explica la NIA 450 sobre evaluacion de errores identificados durante la auditoria.", "criterios": "Acumulacion de errores, umbral de errores triviales, efecto sobre opinion, comunicacion."},
    {"id": "M05", "categoria": "materialidad", "pregunta": "Que es el muestreo estadistico y como se aplica en auditoria fiscal segun NIA 530?", "criterios": "Tipos de muestreo, tamano de muestra, estratificacion, extrapolacion de errores."},
    {"id": "M06", "categoria": "materialidad", "pregunta": "Como se determina la materialidad especifica cuando hay componentes de diferente naturaleza?", "criterios": "Materialidad por componente, ajuste por riesgo, rubros significativos."},
    {"id": "M07", "categoria": "materialidad", "pregunta": "Que porcentajes de materialidad son tipicos para entidades del sector publico colombiano?", "criterios": "0.5%-2% para ingresos/gastos, 0.5%-1% para activos, justificacion del porcentaje elegido."},
    {"id": "M08", "categoria": "materialidad", "pregunta": "Como se revisa la materialidad durante la ejecucion de la auditoria?", "criterios": "Revision obligatoria si cambian circunstancias, documentacion, efecto en pruebas ya realizadas."},
    {"id": "M09", "categoria": "materialidad", "pregunta": "Explica la relacion entre materialidad y riesgo de auditoria.", "criterios": "Relacion inversa, mayor riesgo = menor materialidad, NIA 315 evaluacion de riesgos."},
    {"id": "M10", "categoria": "materialidad", "pregunta": "Calcula el tamano de muestra para auditar 3.000 contratos con nivel de confianza del 95%.", "criterios": "Formula estadistica, parametros (confianza, error tolerable, tasa esperada), resultado numerico."},

    # === FINANCIERO (10 preguntas) ===
    {"id": "F01", "categoria": "financiero", "pregunta": "Que estados financieros debe presentar una entidad publica colombiana bajo NICSP?", "criterios": "Estado de situacion financiera, resultados, cambios patrimonio neto, flujos efectivo, notas."},
    {"id": "F02", "categoria": "financiero", "pregunta": "Explica las diferencias entre Marco Normativo para Entidades de Gobierno y Empresas bajo NICSP.", "criterios": "RCP 533/2015, catalogos contables diferentes, gobierno vs empresas, resoluciones CGN."},
    {"id": "F03", "categoria": "financiero", "pregunta": "Como se evalua la razonabilidad de los estados financieros en una auditoria de la CGR?", "criterios": "Opinion limpia, con salvedades, negativa, abstencion. Criterios para cada tipo."},
    {"id": "F04", "categoria": "financiero", "pregunta": "Que es el fenecimiento de la cuenta y cuando se decreta?", "criterios": "CGR fenece o no fenece, implicaciones, relacion con opinion de auditoria."},
    {"id": "F05", "categoria": "financiero", "pregunta": "Explica el concepto de empresa en marcha aplicado a entidades publicas colombianas.", "criterios": "NIA 570, indicadores de alerta, diferencias con sector privado, entidades en liquidacion."},
    {"id": "F06", "categoria": "financiero", "pregunta": "Como se auditan las operaciones reciprocas entre entidades publicas?", "criterios": "Conciliacion, eliminacion en consolidacion, diferencias, CGN como consolidador."},
    {"id": "F07", "categoria": "financiero", "pregunta": "Que procedimientos se aplican para auditar el rubro de propiedad, planta y equipo en una entidad publica?", "criterios": "Existencia, valuacion, depreciacion, deterioro, inventario fisico, titularidad."},
    {"id": "F08", "categoria": "financiero", "pregunta": "Explica el sistema presupuestal colombiano y su relacion con la contabilidad publica.", "criterios": "Ley organica de presupuesto, apropiaciones, CDP, RP, obligaciones, diferencia caja vs devengo."},
    {"id": "F09", "categoria": "financiero", "pregunta": "Que es el dictamen integral de la CGR y que componentes incluye?", "criterios": "Opinion financiera + gestion + resultados + cumplimiento + control interno."},
    {"id": "F10", "categoria": "financiero", "pregunta": "Como se evalua el sistema de control interno contable de una entidad publica?", "criterios": "Resolucion CGN, componentes COSO, evaluacion cualitativa/cuantitativa, calificacion."},

    # === CONTRATACION (10 preguntas) ===
    {"id": "C01", "categoria": "contratacion", "pregunta": "Cuales son las modalidades de seleccion en la contratacion publica colombiana?", "criterios": "Licitacion, seleccion abreviada, concurso de meritos, contratacion directa, minima cuantia."},
    {"id": "C02", "categoria": "contratacion", "pregunta": "Que requisitos tienen los estudios previos segun el Decreto 1082 de 2015?", "criterios": "Descripcion necesidad, objeto, obligaciones, analisis del sector, valor estimado, riesgos."},
    {"id": "C03", "categoria": "contratacion", "pregunta": "Explica que es el fraccionamiento de contratos y como se detecta en auditoria.", "criterios": "Division artificial para evadir modalidad, indicadores (mismo objeto, mismo contratista, fechas cercanas)."},
    {"id": "C04", "categoria": "contratacion", "pregunta": "Que es el SECOP y cual es su importancia para la transparencia en contratacion?", "criterios": "SECOP I y II, publicacion obligatoria, Colombia Compra Eficiente, tienda virtual."},
    {"id": "C05", "categoria": "contratacion", "pregunta": "Como se evalua la supervision e interventoria de contratos estatales?", "criterios": "Ley 1474/2011, funciones, responsabilidad, informes, herramientas de seguimiento."},
    {"id": "C06", "categoria": "contratacion", "pregunta": "Que es un contrato interadministrativo y cuando es legalmente procedente?", "criterios": "Entre entidades publicas, condiciones (objeto misional), restricciones post-Ley 1474."},
    {"id": "C07", "categoria": "contratacion", "pregunta": "Explica las adiciones y prorrogas contractuales y sus limites legales.", "criterios": "50% del valor inicial, justificacion, no nueva licitacion, excepciones."},
    {"id": "C08", "categoria": "contratacion", "pregunta": "Que mecanismos de garantia exigen los contratos estatales?", "criterios": "Poliza de cumplimiento, buen manejo de anticipo, pago de salarios, calidad, estabilidad obra."},
    {"id": "C09", "categoria": "contratacion", "pregunta": "Como se detectan irregularidades en la liquidacion de contratos?", "criterios": "Plazos (4 meses bilateral, 2 meses unilateral), acta de liquidacion, balance, saldos pendientes."},
    {"id": "C10", "categoria": "contratacion", "pregunta": "Analiza un caso donde una entidad adjudica 15 contratos de minima cuantia al mismo contratista en un mes para servicios similares.", "criterios": "Fraccionamiento probable, evasion de modalidad, indicadores de corrupcion, normas violadas."},
]


# ── Estructuras de datos ─────────────────────────────────────────────────────

@dataclass
class RespuestaEvaluacion:
    """Respuesta de un modelo a una pregunta de benchmark."""

    pregunta_id: str = ""
    categoria: str = ""
    pregunta: str = ""
    respuesta: str = ""
    tiempo_respuesta_s: float = 0.0
    tokens_entrada: int = 0
    tokens_salida: int = 0
    calificacion: float = 0.0  # 0-10
    notas_calificacion: str = ""
    error: str = ""


@dataclass
class ResultadoBenchmark:
    """Resultado completo de un benchmark para un modelo."""

    modelo_id: str = ""
    modelo_nombre: str = ""
    tipo: str = ""  # "base", "finetuned", "claude", "gemini"
    fecha: str = ""
    respuestas: list[RespuestaEvaluacion] = field(default_factory=list)
    metricas_globales: dict[str, float] = field(default_factory=dict)
    metricas_por_categoria: dict[str, dict[str, float]] = field(default_factory=dict)
    tiempo_total_s: float = 0.0
    errores: list[str] = field(default_factory=list)

    def a_dict(self) -> dict[str, Any]:
        return {
            "modelo_id": self.modelo_id,
            "modelo_nombre": self.modelo_nombre,
            "tipo": self.tipo,
            "fecha": self.fecha,
            "respuestas": [asdict(r) for r in self.respuestas],
            "metricas_globales": self.metricas_globales,
            "metricas_por_categoria": self.metricas_por_categoria,
            "tiempo_total_s": self.tiempo_total_s,
            "errores": self.errores,
        }


@dataclass
class ComparativaBenchmark:
    """Comparativa entre multiples modelos."""

    fecha: str = ""
    modelos: list[ResultadoBenchmark] = field(default_factory=list)
    ranking_global: list[dict[str, Any]] = field(default_factory=list)
    ranking_por_categoria: dict[str, list[dict[str, Any]]] = field(default_factory=dict)

    def a_dict(self) -> dict[str, Any]:
        return {
            "fecha": self.fecha,
            "modelos": [m.a_dict() for m in self.modelos],
            "ranking_global": self.ranking_global,
            "ranking_por_categoria": self.ranking_por_categoria,
        }


# ── Evaluacion con proveedor LLM ────────────────────────────────────────────

async def evaluar_con_llm(
    pregunta: str,
    respuesta: str,
    criterios: str,
) -> tuple[float, str]:
    """Evalua una respuesta usando un LLM como juez (GPT-4/Claude).

    Args:
        pregunta: Pregunta original.
        respuesta: Respuesta del modelo evaluado.
        criterios: Criterios de evaluacion.

    Returns:
        Tupla (calificacion 0-10, notas).
    """
    try:
        import httpx
        from app.config import configuracion

        prompt_evaluador = f"""Eres un evaluador experto en control fiscal colombiano.
Evalua la siguiente respuesta a una pregunta tecnica.

PREGUNTA: {pregunta}

CRITERIOS DE EVALUACION: {criterios}

RESPUESTA A EVALUAR:
{respuesta}

Califica de 0 a 10 considerando:
- Precision tecnica y normativa (40%)
- Completitud de la respuesta (30%)
- Claridad y estructura (20%)
- Aplicabilidad practica (10%)

Responde UNICAMENTE en formato JSON:
{{"calificacion": <numero 0-10>, "notas": "<explicacion breve>"}}"""

        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                f"{configuracion.LLM_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {configuracion.LLM_API_KEY}"},
                json={
                    "model": configuracion.LLM_MODEL,
                    "messages": [{"role": "user", "content": prompt_evaluador}],
                    "temperature": 0.1,
                    "max_tokens": 200,
                },
            )
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"]

            # Extraer JSON
            import re
            match = re.search(r'\{[^}]+\}', content)
            if match:
                data = json.loads(match.group())
                return float(data.get("calificacion", 5)), data.get("notas", "")

    except Exception as exc:
        logger.warning("Error evaluando con LLM: %s", exc)

    return 5.0, "Evaluacion automatica no disponible"


def evaluar_heuristico(
    respuesta: str,
    criterios: str,
) -> tuple[float, str]:
    """Evaluacion heuristica basica cuando el LLM no esta disponible.

    Args:
        respuesta: Respuesta a evaluar.
        criterios: Criterios esperados.

    Returns:
        Tupla (calificacion 0-10, notas).
    """
    if not respuesta or len(respuesta) < 50:
        return 1.0, "Respuesta vacia o demasiado corta"

    puntos = 5.0
    notas = []

    # Longitud razonable
    if len(respuesta) > 200:
        puntos += 1.0
        notas.append("Respuesta con extension adecuada")
    if len(respuesta) > 500:
        puntos += 0.5

    # Verificar mencion de criterios clave
    criterios_lower = criterios.lower()
    palabras_clave = [
        p.strip() for p in criterios_lower.replace(",", ".").split(".")
        if len(p.strip()) > 5
    ]
    mencionados = 0
    for pc in palabras_clave:
        if pc in respuesta.lower():
            mencionados += 1
    if palabras_clave:
        ratio = mencionados / len(palabras_clave)
        puntos += ratio * 2.0
        notas.append(f"Menciona {mencionados}/{len(palabras_clave)} criterios clave")

    # Estructura (parrafos, numeracion)
    if any(c in respuesta for c in ["1.", "1)", "a)", "-"]):
        puntos += 0.5
        notas.append("Respuesta estructurada")

    # Referencias normativas
    if any(kw in respuesta.lower() for kw in ["ley ", "decreto ", "articulo ", "resolucion ", "nia "]):
        puntos += 0.5
        notas.append("Incluye referencias normativas")

    puntos = min(10.0, max(0.0, puntos))
    return round(puntos, 1), "; ".join(notas) if notas else "Evaluacion heuristica"


# ── Ejecucion del benchmark ──────────────────────────────────────────────────

async def ejecutar_benchmark_modelo(
    modelo_id: str,
    modelo_nombre: str,
    tipo: str,
    funcion_inferencia: Any,
    preguntas: list[dict] | None = None,
    usar_evaluador_llm: bool = False,
) -> ResultadoBenchmark:
    """Ejecuta el benchmark completo para un modelo.

    Args:
        modelo_id: Identificador del modelo.
        modelo_nombre: Nombre descriptivo.
        tipo: Tipo ("base", "finetuned", "claude", "gemini").
        funcion_inferencia: Corrutina async(pregunta: str) -> str.
        preguntas: Lista de preguntas. None = todas las 50.
        usar_evaluador_llm: Si usar LLM como juez para calificar.

    Returns:
        ResultadoBenchmark con todas las metricas.
    """
    preguntas = preguntas or PREGUNTAS_BENCHMARK
    resultado = ResultadoBenchmark(
        modelo_id=modelo_id,
        modelo_nombre=modelo_nombre,
        tipo=tipo,
        fecha=datetime.now(timezone.utc).isoformat(),
    )

    t_total = time.time()

    for i, p in enumerate(preguntas):
        logger.info(
            "Evaluando [%d/%d] %s: %s...",
            i + 1, len(preguntas), p["id"], p["pregunta"][:50],
        )

        resp = RespuestaEvaluacion(
            pregunta_id=p["id"],
            categoria=p["categoria"],
            pregunta=p["pregunta"],
        )

        try:
            t_start = time.time()
            resp.respuesta = await funcion_inferencia(p["pregunta"])
            resp.tiempo_respuesta_s = round(time.time() - t_start, 2)

            # Calificar
            if usar_evaluador_llm:
                resp.calificacion, resp.notas_calificacion = await evaluar_con_llm(
                    p["pregunta"], resp.respuesta, p["criterios"]
                )
            else:
                resp.calificacion, resp.notas_calificacion = evaluar_heuristico(
                    resp.respuesta, p["criterios"]
                )

        except Exception as exc:
            resp.error = str(exc)
            resp.calificacion = 0.0
            resultado.errores.append(f"{p['id']}: {exc}")
            logger.error("Error evaluando %s: %s", p["id"], exc)

        resultado.respuestas.append(resp)

    resultado.tiempo_total_s = round(time.time() - t_total, 2)

    # Calcular metricas
    _calcular_metricas(resultado)

    return resultado


def _calcular_metricas(resultado: ResultadoBenchmark) -> None:
    """Calcula metricas agregadas del benchmark."""
    respuestas_ok = [r for r in resultado.respuestas if not r.error]

    if respuestas_ok:
        calificaciones = [r.calificacion for r in respuestas_ok]
        tiempos = [r.tiempo_respuesta_s for r in respuestas_ok]

        resultado.metricas_globales = {
            "promedio_calificacion": round(sum(calificaciones) / len(calificaciones), 2),
            "mediana_calificacion": round(sorted(calificaciones)[len(calificaciones) // 2], 2),
            "min_calificacion": min(calificaciones),
            "max_calificacion": max(calificaciones),
            "promedio_tiempo_s": round(sum(tiempos) / len(tiempos), 2),
            "total_respondidas": len(respuestas_ok),
            "total_errores": len(resultado.errores),
            "tasa_exito": round(len(respuestas_ok) / len(resultado.respuestas) * 100, 1),
        }

    # Por categoria
    for cat in CATEGORIAS_EVAL:
        resp_cat = [r for r in respuestas_ok if r.categoria == cat]
        if resp_cat:
            cals = [r.calificacion for r in resp_cat]
            resultado.metricas_por_categoria[cat] = {
                "promedio": round(sum(cals) / len(cals), 2),
                "min": min(cals),
                "max": max(cals),
                "total": len(resp_cat),
            }


# ── Comparativa entre modelos ────────────────────────────────────────────────

def generar_comparativa(
    resultados: list[ResultadoBenchmark],
) -> ComparativaBenchmark:
    """Genera la comparativa entre multiples modelos.

    Args:
        resultados: Lista de ResultadoBenchmark de cada modelo.

    Returns:
        ComparativaBenchmark con rankings.
    """
    comp = ComparativaBenchmark(
        fecha=datetime.now(timezone.utc).isoformat(),
        modelos=resultados,
    )

    # Ranking global
    ranking = []
    for r in resultados:
        prom = r.metricas_globales.get("promedio_calificacion", 0)
        ranking.append({
            "modelo": r.modelo_nombre,
            "tipo": r.tipo,
            "promedio": prom,
            "tiempo_promedio_s": r.metricas_globales.get("promedio_tiempo_s", 0),
            "tasa_exito": r.metricas_globales.get("tasa_exito", 0),
        })
    comp.ranking_global = sorted(ranking, key=lambda x: x["promedio"], reverse=True)

    # Ranking por categoria
    for cat in CATEGORIAS_EVAL:
        rank_cat = []
        for r in resultados:
            mc = r.metricas_por_categoria.get(cat, {})
            rank_cat.append({
                "modelo": r.modelo_nombre,
                "tipo": r.tipo,
                "promedio": mc.get("promedio", 0),
            })
        comp.ranking_por_categoria[cat] = sorted(
            rank_cat, key=lambda x: x["promedio"], reverse=True
        )

    return comp


# ── Generacion de informe DOCX ──────────────────────────────────────────────

def generar_informe_docx(comparativa: ComparativaBenchmark) -> bytes:
    """Genera un informe DOCX profesional con los resultados del benchmark.

    Args:
        comparativa: Datos de la comparativa entre modelos.

    Returns:
        Bytes del archivo DOCX.
    """
    from app.formatos.formato_base import FormatoBaseCGR

    class InformeBenchmark(FormatoBaseCGR):
        def __init__(self, comparativa: ComparativaBenchmark):
            super().__init__(
                numero_formato=99,
                nombre_formato="Benchmark de Modelos IA",
                datos={
                    "nombre_entidad": "Contraloria General de la Republica",
                    "vigencia": datetime.now().strftime("%Y"),
                    "tipo_auditoria": "Evaluacion de Modelos de IA",
                },
            )
            self.comparativa = comparativa

        def construir(self) -> None:
            c = self.comparativa

            # Seccion 1: Resumen ejecutivo
            self.agregar_titulo_seccion("1. Resumen Ejecutivo")
            self.agregar_parrafo_justificado(
                f"Se evaluaron {len(c.modelos)} modelos de lenguaje (LLM) "
                f"mediante un benchmark de {len(PREGUNTAS_BENCHMARK)} preguntas "
                f"distribuidas en {len(CATEGORIAS_EVAL)} categorias del dominio "
                f"de control fiscal colombiano. La evaluacion se realizo el "
                f"{c.fecha[:10]}."
            )

            # Tabla de ranking global
            self.agregar_titulo_seccion("2. Ranking Global")
            if c.ranking_global:
                encabezados = ["#", "Modelo", "Tipo", "Promedio", "Tiempo (s)", "Exito (%)"]
                filas = []
                for i, r in enumerate(c.ranking_global, 1):
                    filas.append([
                        str(i),
                        r["modelo"],
                        r["tipo"],
                        f"{r['promedio']:.1f}/10",
                        f"{r['tiempo_promedio_s']:.1f}",
                        f"{r['tasa_exito']:.0f}%",
                    ])
                self.crear_tabla(encabezados, filas, anchos=[1, 5, 2.5, 2.5, 2, 2])

            # Seccion 3: Detalle por categoria
            self.agregar_titulo_seccion("3. Resultados por Categoria")
            nombres_cat = {
                "normativo": "Normativo y Legal",
                "hallazgos": "Hallazgos de Auditoria",
                "materialidad": "Materialidad y Muestreo",
                "financiero": "Auditoria Financiera",
                "contratacion": "Contratacion Publica",
            }
            for cat in CATEGORIAS_EVAL:
                self.agregar_subtitulo(f"3.{CATEGORIAS_EVAL.index(cat)+1}. {nombres_cat.get(cat, cat)}")
                rank = c.ranking_por_categoria.get(cat, [])
                if rank:
                    enc = ["Modelo", "Promedio"]
                    filas_cat = [[r["modelo"], f"{r['promedio']:.1f}/10"] for r in rank]
                    self.crear_tabla(enc, filas_cat, anchos=[10, 4])

            # Seccion 4: Detalle por modelo
            self.agregar_titulo_seccion("4. Detalle por Modelo")
            for modelo in c.modelos:
                self.agregar_subtitulo(f"{modelo.modelo_nombre} ({modelo.tipo})")
                metricas = modelo.metricas_globales
                if metricas:
                    pares = [
                        ("Promedio general", f"{metricas.get('promedio_calificacion', 0):.1f}/10"),
                        ("Calificacion minima", f"{metricas.get('min_calificacion', 0):.1f}"),
                        ("Calificacion maxima", f"{metricas.get('max_calificacion', 0):.1f}"),
                        ("Tiempo promedio", f"{metricas.get('promedio_tiempo_s', 0):.1f} s"),
                        ("Preguntas respondidas", f"{metricas.get('total_respondidas', 0)}/{len(PREGUNTAS_BENCHMARK)}"),
                        ("Errores", str(metricas.get("total_errores", 0))),
                    ]
                    self.crear_tabla_clave_valor(pares)

            # Seccion 5: Conclusiones
            self.agregar_titulo_seccion("5. Conclusiones y Recomendaciones")
            if c.ranking_global:
                mejor = c.ranking_global[0]
                self.agregar_parrafo_justificado(
                    f"El modelo con mejor desempeno global fue '{mejor['modelo']}' "
                    f"({mejor['tipo']}) con un promedio de {mejor['promedio']:.1f}/10 "
                    f"y un tiempo de respuesta promedio de {mejor['tiempo_promedio_s']:.1f} segundos."
                )

            self.agregar_parrafo_justificado(
                "Se recomienda validar estos resultados con el equipo de auditores expertos "
                "de la CGR antes de tomar decisiones sobre la implementacion en produccion. "
                "La evaluacion automatica es indicativa y debe complementarse con revision humana "
                "de las respuestas, especialmente en las categorias de hallazgos y normativo."
            )

    informe = InformeBenchmark(comparativa)
    return informe.generar_bytes()


# ── Guardar y cargar resultados ──────────────────────────────────────────────

def guardar_resultado(resultado: ResultadoBenchmark, directorio: str | Path = "benchmark_resultados") -> Path:
    """Guarda el resultado de un benchmark como JSON."""
    ruta = Path(directorio)
    ruta.mkdir(parents=True, exist_ok=True)

    nombre = f"benchmark_{resultado.modelo_id}_{resultado.fecha[:10]}.json"
    archivo = ruta / nombre

    with archivo.open("w", encoding="utf-8") as f:
        json.dump(resultado.a_dict(), f, ensure_ascii=False, indent=2)

    logger.info("Resultado guardado: %s", archivo)
    return archivo


def cargar_resultado(ruta: str | Path) -> ResultadoBenchmark:
    """Carga un resultado de benchmark desde JSON."""
    with Path(ruta).open("r", encoding="utf-8") as f:
        data = json.load(f)

    resultado = ResultadoBenchmark(
        modelo_id=data["modelo_id"],
        modelo_nombre=data["modelo_nombre"],
        tipo=data["tipo"],
        fecha=data["fecha"],
        metricas_globales=data.get("metricas_globales", {}),
        metricas_por_categoria=data.get("metricas_por_categoria", {}),
        tiempo_total_s=data.get("tiempo_total_s", 0),
        errores=data.get("errores", []),
    )

    for r in data.get("respuestas", []):
        resultado.respuestas.append(RespuestaEvaluacion(**r))

    return resultado
