"""
CecilIA v2 — Construccion de datasets para fine-tuning
Contraloria General de la Republica de Colombia

Archivo: app/finetuning/dataset_builder.py
Proposito: Genera datasets JSONL para fine-tuning de modelos LLM
           con datos anonimizados del control fiscal colombiano.
           Cumple Ley 1581/2012 de proteccion de datos personales.
Sprint: 9
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from app.utils.anonimizacion import anonimizar_texto

logger = logging.getLogger("cecilia.finetuning.dataset")

# ── Categorias de entrenamiento ──────────────────────────────────────────────

CATEGORIAS = [
    "hallazgos",
    "preguntas_frecuentes",
    "interpretaciones_normativas",
    "calculos_materialidad",
    "contratacion",
]


@dataclass
class EjemploEntrenamiento:
    """Ejemplo individual para fine-tuning en formato instruccion."""

    instruction: str
    input: str
    output: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def a_jsonl(self) -> str:
        """Serializa a linea JSONL."""
        return json.dumps(
            {
                "instruction": self.instruction,
                "input": self.input,
                "output": self.output,
                "metadata": self.metadata,
            },
            ensure_ascii=False,
        )

    @classmethod
    def desde_dict(cls, d: dict[str, Any]) -> EjemploEntrenamiento:
        return cls(
            instruction=d["instruction"],
            input=d.get("input", ""),
            output=d["output"],
            metadata=d.get("metadata", {}),
        )


@dataclass
class DatasetStats:
    """Estadisticas del dataset generado."""

    total_ejemplos: int = 0
    por_categoria: dict[str, int] = field(default_factory=dict)
    tokens_estimados: int = 0
    pii_anonimizados: int = 0
    fecha_generacion: str = ""


# ── Anonimizacion conforme Ley 1581/2012 ────────────────────────────────────

def anonimizar(texto: str) -> str:
    """Anonimiza texto eliminando datos personales conforme Ley 1581/2012.

    Protege: cedulas, NIT, emails, telefonos, nombres propios,
    direcciones y cuentas bancarias.

    Args:
        texto: Texto con posibles datos personales.

    Returns:
        Texto anonimizado con pseudonimos deterministas.
    """
    resultado = anonimizar_texto(
        texto,
        anonimizar_cedulas=True,
        anonimizar_nit=True,
        anonimizar_emails=True,
        anonimizar_telefonos=True,
        anonimizar_nombres=True,
        anonimizar_direcciones=True,
        anonimizar_cuentas=True,
    )
    if resultado.total_reemplazos > 0:
        logger.debug(
            "Anonimizados %d items PII en texto de %d caracteres",
            resultado.total_reemplazos,
            len(texto),
        )
    return resultado.texto_anonimizado


# ── Generadores de ejemplos por categoria ────────────────────────────────────

def generar_ejemplos_hallazgos() -> list[EjemploEntrenamiento]:
    """Genera ejemplos de hallazgos de auditoria anonimizados."""
    ejemplos = [
        EjemploEntrenamiento(
            instruction="Redacta un hallazgo de auditoria con los 4 elementos obligatorios (condicion, criterio, causa, efecto) a partir de la siguiente situacion.",
            input="La Entidad ABC S.A. suscribio 12 contratos de conectividad por $2.345 millones con valores superiores al promedio del mercado en un 35%. Los estudios de mercado presentan deficiencias en la metodologia de comparacion de precios.",
            output="HALLAZGO: Sobrecosto en contratacion de servicios de conectividad\n\nCONDICION: Se evidencio que la entidad [ENTIDAD_ANONIMA] suscribio doce (12) contratos de servicios de conectividad por valor total de $2.345 millones, cuyos valores unitarios superan en un 35% el promedio de mercado para servicios equivalentes en el mismo periodo.\n\nCRITERIO: Articulo 25, numeral 12 de la Ley 80 de 1993 (Principio de Economia); Articulo 2.2.1.1.2.1.1 del Decreto 1082 de 2015, que establece la obligatoriedad de elaborar estudios de mercado que reflejen las condiciones reales del sector.\n\nCAUSA: Deficiencias en la metodologia de estudios de mercado de la entidad, que no considero un numero representativo de cotizaciones ni utilizo fuentes del SECOP para comparacion de precios historicos.\n\nEFECTO: Presunto detrimento patrimonial estimado en $820 millones, correspondiente al diferencial entre los valores contratados y el promedio de mercado.\n\nCONNOTACION: Fiscal y administrativa.\nCUANTIA ESTIMADA: $820.000.000",
            metadata={"categoria": "hallazgos", "connotacion": "fiscal", "dificultad": "media"},
        ),
        EjemploEntrenamiento(
            instruction="Identifica las debilidades en el siguiente hallazgo de auditoria y sugiere mejoras en su redaccion.",
            input="Hallazgo: La entidad no ejecuto el presupuesto. Criterio: La ley dice que hay que ejecutar. Causa: No se sabe. Efecto: Se perdio plata.",
            output="ANALISIS DE DEBILIDADES:\n\n1. CONDICION: Es demasiado vaga. Debe precisar: monto no ejecutado, porcentaje de inejecucion, rubros afectados, periodo especifico.\n   MEJORA: 'Se evidencio una inejecucion presupuestal del [X]% en el rubro de inversion del proyecto [nombre], equivalente a $[monto] millones, correspondiente a la vigencia [ano].'\n\n2. CRITERIO: No cita norma especifica. Debe referenciar articulo exacto.\n   MEJORA: 'Articulo 345 de la Constitucion Politica; Articulo 89 del Estatuto Organico de Presupuesto (Decreto 111 de 1996); Articulo 2 de la Ley 819 de 2003 sobre responsabilidad fiscal.'\n\n3. CAUSA: 'No se sabe' es inaceptable. Debe investigarse.\n   MEJORA: 'Deficiencias en la planeacion y programacion presupuestal, evidenciadas en la ausencia de cronogramas de ejecucion y la falta de seguimiento trimestral por parte de la oficina de planeacion.'\n\n4. EFECTO: 'Se perdio plata' es coloquial y no cuantifica.\n   MEJORA: 'Recursos publicos por $[monto] millones que no cumplieron su finalidad social, afectando la cobertura del programa [nombre] que beneficiaria a [X] personas.'",
            metadata={"categoria": "hallazgos", "tipo": "revision_redaccion", "dificultad": "alta"},
        ),
        EjemploEntrenamiento(
            instruction="Clasifica el siguiente hallazgo segun su connotacion: administrativa, fiscal, disciplinaria o penal.",
            input="La entidad adjudico un contrato de $5.000 millones sin publicar el pliego de condiciones en el SECOP, y el contratista adjudicatario es familiar en segundo grado del ordenador del gasto.",
            output="CLASIFICACION DEL HALLAZGO:\n\n1. CONNOTACION ADMINISTRATIVA: SI\n   Fundamento: Incumplimiento del Decreto 1082 de 2015, articulo 2.2.1.1.1.7.1, que obliga la publicacion de documentos del proceso en el SECOP.\n\n2. CONNOTACION FISCAL: SI (presunto detrimento patrimonial)\n   Fundamento: La ausencia de publicacion limito la competencia, lo que pudo generar un sobrecosto respecto a condiciones de mercado. Se estima un posible detrimento.\n\n3. CONNOTACION DISCIPLINARIA: SI\n   Fundamento: Articulo 35, numerales 1 y 13 del Codigo Disciplinario Unico (Ley 734 de 2002), por incumplimiento de deberes funcionales y violacion al regimen de inhabilidades e incompatibilidades.\n\n4. CONNOTACION PENAL: SI (presunto)\n   Fundamento: Articulo 408 del Codigo Penal (violacion del regimen legal o constitucional de inhabilidades e incompatibilidades) y articulo 410 (contrato sin cumplimiento de requisitos legales). El vinculo familiar con el contratista configura un posible conflicto de intereses que amerita traslado a la Fiscalia.\n\nRECOMENDACION: Traslado a la Procuraduria General de la Nacion (disciplinario), a la Contraloria para proceso de responsabilidad fiscal, y a la Fiscalia General de la Nacion (penal).",
            metadata={"categoria": "hallazgos", "tipo": "clasificacion", "dificultad": "alta"},
        ),
        EjemploEntrenamiento(
            instruction="Determina la connotacion y cuantia del siguiente hallazgo de auditoria.",
            input="En la revision del contrato de obra No. 045-2025, se evidencio que la entidad pago $1.200 millones por obras de pavimentacion que, segun la interventoria tecnica, presentan un 40% de inejecucion. Las actas de recibo parcial fueron firmadas por el supervisor sin verificar la ejecucion real en campo.",
            output="DETERMINACION DE CONNOTACION Y CUANTIA:\n\nCONNOTACION FISCAL: SI\nCuantia estimada del presunto detrimento: $480 millones (40% de inejecucion sobre $1.200 millones).\nFundamento: Articulo 6 de la Ley 610 de 2000 — constituye dano patrimonial al Estado el pago por obras no ejecutadas.\n\nCONNOTACION ADMINISTRATIVA: SI\nFundamento: Incumplimiento de las funciones de supervision (Ley 1474/2011, Art. 83-84). El supervisor firmo actas de recibo sin verificacion en campo.\n\nCONNOTACION DISCIPLINARIA: SI\nFundamento: Ley 734 de 2002, Art. 35 num. 1 — incumplimiento de deberes funcionales del supervisor del contrato.\n\nCONNOTACION PENAL: PROBABLE\nFundamento: Articulo 400 del Codigo Penal (peculado por apropiacion) si se demuestra que los recursos fueron desviados. Articulo 286 (falsedad ideologica en documento publico) por las actas de recibo parcial que no reflejan la realidad.\n\nRESUMEN:\n| Connotacion | Aplica | Cuantia |\n|-------------|--------|--------|\n| Fiscal | SI | $480 millones |\n| Administrativa | SI | N/A |\n| Disciplinaria | SI | N/A |\n| Penal | Probable | $480 millones |",
            metadata={"categoria": "hallazgos", "tipo": "determinacion_connotacion", "dificultad": "alta"},
        ),
    ]
    return [_anonimizar_ejemplo(e) for e in ejemplos]


def generar_ejemplos_preguntas_frecuentes() -> list[EjemploEntrenamiento]:
    """Genera ejemplos de preguntas frecuentes sobre control fiscal."""
    return [
        EjemploEntrenamiento(
            instruction="Responde la siguiente pregunta sobre control fiscal en Colombia de forma clara y precisa.",
            input="Que es el control fiscal y quien lo ejerce en Colombia?",
            output="El control fiscal es una funcion publica establecida en el Articulo 267 de la Constitucion Politica de Colombia. Consiste en la vigilancia de la gestion fiscal de la administracion y de los particulares o entidades que manejen fondos o bienes del Estado.\n\nLo ejerce la Contraloria General de la Republica (CGR) a nivel nacional, las contralorias departamentales a nivel territorial, y las contralorias municipales donde existan. El Contralor General es elegido por el Congreso de la Republica para un periodo de 4 anos, no reelegible.\n\nEl control fiscal es posterior y selectivo (Art. 267 C.P.), lo que significa que se ejerce despues de ejecutadas las operaciones financieras y sobre una muestra representativa, no sobre la totalidad de las transacciones.",
            metadata={"categoria": "preguntas_frecuentes", "tema": "conceptos_basicos"},
        ),
        EjemploEntrenamiento(
            instruction="Responde la siguiente pregunta sobre control fiscal en Colombia de forma clara y precisa.",
            input="Cuales son las fases del proceso auditor de la CGR?",
            output="El proceso auditor de la Contraloria General de la Republica comprende cinco (5) fases:\n\n1. PRE-PLANEACION: Conocimiento del sujeto de control, definicion del equipo auditor, declaraciones de independencia. Se elaboran los Formatos 1 al 10 de la GAF.\n\n2. PLANEACION: Evaluacion de riesgos, calculo de materialidad, determinacion del muestreo, elaboracion del memorando de planeacion. Formatos 11 al 20.\n\n3. EJECUCION: Aplicacion de pruebas sustantivas y de cumplimiento, recopilacion de evidencia, documentacion de hallazgos. Formatos 21 al 30.\n\n4. INFORME: Elaboracion del informe de auditoria con opinion, comunicacion de hallazgos, respuesta del auditado, informe definitivo.\n\n5. SEGUIMIENTO: Verificacion del cumplimiento de los planes de mejoramiento suscritos por el sujeto de control como resultado de la auditoria anterior.",
            metadata={"categoria": "preguntas_frecuentes", "tema": "proceso_auditor"},
        ),
        EjemploEntrenamiento(
            instruction="Responde la siguiente pregunta sobre control fiscal en Colombia de forma clara y precisa.",
            input="Que es un proceso de responsabilidad fiscal y cuando se inicia?",
            output="El proceso de responsabilidad fiscal esta regulado por la Ley 610 de 2000 y es el conjunto de actuaciones administrativas adelantadas por las contralorias para determinar la responsabilidad de los servidores publicos o particulares que, por accion u omision y en forma dolosa o gravemente culposa, causaron un dano patrimonial al Estado.\n\nSe inicia cuando:\n1. Se identifica un hallazgo fiscal con cuantia determinada o determinable\n2. Se establece un presunto detrimento patrimonial (perdida, dano o deterioro del patrimonio publico)\n3. Se individualiza a los presuntos responsables (servidores publicos, contratistas o particulares que manejen recursos publicos)\n\nEl proceso tiene dos etapas principales:\n- APERTURA E INVESTIGACION: Auto de apertura, vinculacion de presuntos responsables, periodo probatorio\n- JUICIO FISCAL: Auto de imputacion, audiencia, fallo con o sin responsabilidad fiscal\n\nSi se declara responsabilidad fiscal, se emite un fallo con obligacion de resarcir el dano patrimonial. Los responsables son incluidos en el Boletin de Responsables Fiscales (BREF) de la CGR.",
            metadata={"categoria": "preguntas_frecuentes", "tema": "responsabilidad_fiscal"},
        ),
        EjemploEntrenamiento(
            instruction="Responde la siguiente pregunta sobre control fiscal en Colombia de forma clara y precisa.",
            input="Que diferencia hay entre hallazgo administrativo, fiscal, disciplinario y penal?",
            output="Los hallazgos de auditoria se clasifican por su connotacion juridica:\n\n1. ADMINISTRATIVO: Incumplimiento de normas de gestion o procedimientos internos que no genera dano patrimonial directo. Se comunica a la entidad para que adopte correctivos en su plan de mejoramiento. Ejemplo: no llevar el inventario de bienes actualizado.\n\n2. FISCAL: Implica un presunto detrimento patrimonial al Estado (perdida de recursos publicos). Genera traslado para proceso de responsabilidad fiscal ante la propia Contraloria. Ejemplo: pago de obras no ejecutadas por $500 millones.\n\n3. DISCIPLINARIO: Constituye falta disciplinaria de un servidor publico por incumplimiento de deberes, extralimitacion de funciones o violacion de prohibiciones. Se traslada a la Procuraduria General de la Nacion. Ejemplo: no publicar los contratos en el SECOP.\n\n4. PENAL: Configura una conducta que puede constituir delito (peculado, prevaricato, celebracion indebida de contratos, etc.). Se traslada a la Fiscalia General de la Nacion. Ejemplo: apropiacion de dineros publicos para beneficio personal.\n\nIMPORTANTE: Un mismo hallazgo puede tener multiples connotaciones simultaneas.",
            metadata={"categoria": "preguntas_frecuentes", "tema": "tipos_hallazgos"},
        ),
        EjemploEntrenamiento(
            instruction="Responde la siguiente pregunta sobre control fiscal en Colombia de forma clara y precisa.",
            input="Que es el Boletin de Responsables Fiscales (BREF) y cuales son sus efectos juridicos?",
            output="El Boletin de Responsables Fiscales (BREF) es un registro publico administrado por la Contraloria General de la Republica, regulado por el Articulo 60 de la Ley 610 de 2000.\n\nCONTENIDO: Incluye a todas las personas naturales y juridicas que han sido declaradas responsables fiscalmente mediante fallo ejecutoriado.\n\nEFECTOS JURIDICOS:\n1. INHABILIDAD PARA CONTRATAR: Las personas incluidas en el BREF no pueden celebrar contratos con el Estado (Art. 8 Ley 80/1993, literal j).\n2. INHABILIDAD PARA CARGOS PUBLICOS: No pueden ser nombradas en cargos publicos ni tomar posesion de los mismos.\n3. PUBLICIDAD: El BREF es de consulta publica y se actualiza mensualmente.\n4. DURACION: La inclusion se mantiene hasta que se pague la totalidad de la obligacion fiscal.\n\nCONSULTA: Disponible en www.contraloria.gov.co/bref para entidades que verifican antecedentes antes de contratar.",
            metadata={"categoria": "preguntas_frecuentes", "tema": "bref"},
        ),
    ]


def generar_ejemplos_normativas() -> list[EjemploEntrenamiento]:
    """Genera ejemplos de interpretaciones normativas."""
    return [
        EjemploEntrenamiento(
            instruction="Interpreta la siguiente norma juridica en el contexto del control fiscal colombiano y explica su aplicacion practica.",
            input="Articulo 267 de la Constitucion Politica de Colombia sobre control fiscal.",
            output="INTERPRETACION DEL ARTICULO 267 C.P.:\n\nEl Articulo 267 establece los principios fundamentales del control fiscal en Colombia:\n\n1. NATURALEZA: El control fiscal es una funcion publica, no judicial. Es de caracter administrativo.\n\n2. ORGANO: Lo ejerce la Contraloria General de la Republica como supremo director del control fiscal.\n\n3. ALCANCE: Vigila la gestion fiscal de toda la administracion publica Y de los particulares o entidades que manejen fondos o bienes del Estado.\n\n4. MODALIDAD: Es posterior (despues de ejecutadas las operaciones) y selectivo (sobre muestras, no sobre la totalidad). Esto lo diferencia del control previo que existia antes de la Constitucion de 1991.\n\n5. PRINCIPIOS: Se ejerce con base en los principios de eficiencia, economia, equidad y valoracion de costos ambientales (adicionados por el Acto Legislativo 04 de 2019).\n\nAPLICACION PRACTICA:\n- Los auditores de la CGR NO aprueban gastos antes de ejecutarse (control previo fue eliminado en 1991)\n- El control se ejerce mediante auditorias financieras, de cumplimiento, de desempeno y especiales\n- Se aplica tanto a ministerios como a empresas privadas que administren recursos publicos (fiducias, concesiones, APP)\n- El Acto Legislativo 04 de 2019 fortalecio el control fiscal con el control concomitante y preventivo (sin coadministrar)",
            metadata={"categoria": "interpretaciones_normativas", "norma": "art_267_cp"},
        ),
        EjemploEntrenamiento(
            instruction="Interpreta la siguiente norma juridica en el contexto del control fiscal colombiano y explica su aplicacion practica.",
            input="Ley 80 de 1993 Articulo 25 - Principio de Economia en la contratacion estatal.",
            output="INTERPRETACION LEY 80/1993 ART. 25 - PRINCIPIO DE ECONOMIA:\n\nEl Principio de Economia en contratacion estatal establece que:\n\n1. ESTUDIOS PREVIOS: La entidad debe realizar estudios, disenos y proyectos requeridos antes de iniciar el proceso de seleccion. Esto incluye estudios de mercado, analisis del sector y justificacion de la necesidad.\n\n2. REGLAS DE SUBSANABILIDAD: Los requisitos de la propuesta que no afecten la asignacion de puntaje pueden subsanarse hasta la adjudicacion.\n\n3. PLAZOS: Los procedimientos se deben adelantar en el menor tiempo posible, sin dilaciones injustificadas.\n\n4. ECONOMIA PROCESAL: Se deben evitar tramites innecesarios, y la regla general es la seleccion objetiva mediante licitacion publica.\n\nAPLICACION EN CONTROL FISCAL:\n- Los auditores verifican que los estudios de mercado sean suficientes y reflejen precios reales del mercado\n- Se valida que los tiempos del proceso no excedan lo razonable\n- Se revisa que los costos administrativos del proceso sean proporcionales al valor del contrato\n- Cuando se evidencia ausencia de estudios previos, se configura un hallazgo administrativo; si hay sobrecostos demostrados, se agrega connotacion fiscal\n\nNORMAS COMPLEMENTARIAS: Decreto 1082 de 2015, que reglamenta los estudios del sector y los analisis de mercado.",
            metadata={"categoria": "interpretaciones_normativas", "norma": "ley_80_art25"},
        ),
        EjemploEntrenamiento(
            instruction="Interpreta la siguiente norma juridica en el contexto del control fiscal colombiano y explica su aplicacion practica.",
            input="Ley 1474 de 2011 (Estatuto Anticorrupcion) y su impacto en la contratacion publica.",
            output="INTERPRETACION LEY 1474/2011 - ESTATUTO ANTICORRUPCION:\n\nEsta ley fortalecio los mecanismos de lucha contra la corrupcion con impacto directo en contratacion publica:\n\n1. INHABILIDAD POR FINANCIACION DE CAMPANAS (Art. 2): Quienes hayan financiado campanas politicas no pueden contratar con la entidad territorial correspondiente durante el periodo del elegido.\n\n2. SUPERVISION E INTERVENTORIA OBLIGATORIA (Art. 83-84): Todo contrato estatal debe tener supervision; si supera cierto monto o complejidad, requiere interventoria externa con perfil tecnico.\n\n3. PUBLICACION EN SECOP (Art. 19): Obligatoriedad de publicar todos los documentos del proceso contractual en el Sistema Electronico de Contratacion Publica.\n\n4. MADURACION DE PROYECTOS (Art. 87): Los proyectos de infraestructura deben tener estudios de suelo, disenos y licencias antes de iniciar el proceso de seleccion.\n\n5. PROHIBICION DE ADENDAS EN ULTIMO DIA (Art. 89): Las adendas deben publicarse minimo 3 dias habiles antes del cierre (7 dias en licitacion publica).\n\nAPLICACION EN CONTROL FISCAL:\n- Los auditores verifican el cumplimiento de cada una de estas disposiciones\n- La violacion del Estatuto Anticorrupcion genera hallazgos con connotaciones multiples (fiscal, disciplinaria, y potencialmente penal)\n- Se cruzan datos de financiadores de campanas con contratistas del SECOP para detectar conflictos de interes",
            metadata={"categoria": "interpretaciones_normativas", "norma": "ley_1474_2011"},
        ),
        EjemploEntrenamiento(
            instruction="Interpreta la siguiente norma juridica en el contexto del control fiscal colombiano y explica su aplicacion practica.",
            input="Decreto 403 de 2020 — Regimen de Control Fiscal (RGCF) y sus implicaciones para las auditorias de la CGR.",
            output="INTERPRETACION DECRETO 403/2020 — REGIMEN GENERAL DE CONTROL FISCAL:\n\nEl Decreto 403 de 2020 compila y actualiza la normatividad del control fiscal colombiano. Principales aspectos:\n\n1. TIPOS DE VIGILANCIA FISCAL (Art. 36-42):\n   - Control macro: Certificacion de las finanzas del Estado, evaluacion de politica fiscal\n   - Control micro: Auditorias individuales a sujetos de control\n   - Control concomitante: Seguimiento en tiempo real (nuevo, Acto Legislativo 04/2019)\n   - Control preventivo: Alertas tempranas sin coadministrar\n\n2. PROCESO AUDITOR INTEGRAL (Art. 43-60):\n   - Planeacion basada en riesgos\n   - Ejecucion con enfoque de auditoria integrada\n   - Informe con opinion sobre gestion fiscal integral\n   - Seguimiento al plan de mejoramiento\n\n3. SUJETOS DE CONTROL (Art. 25-35):\n   - Todas las entidades publicas de todos los niveles\n   - Particulares que manejen recursos publicos\n   - Incluye: fiducias, concesiones, APP, fondos\n\n4. JURISDICCION COACTIVA (Art. 98-110):\n   - La CGR puede cobrar coactivamente los fallos de responsabilidad fiscal\n   - Embargos, secuestros, remate de bienes\n\nAPLICACION PRACTICA PARA AUDITORES:\n- El RGCF es la guia maestra para planificar las auditorias\n- Define los formatos y procedimientos estandar\n- Establece los plazos para comunicacion de hallazgos\n- Regula la interaccion con los sujetos de control durante la auditoria",
            metadata={"categoria": "interpretaciones_normativas", "norma": "decreto_403_2020"},
        ),
    ]


def generar_ejemplos_materialidad() -> list[EjemploEntrenamiento]:
    """Genera ejemplos de calculos de materialidad conforme NIA 320/450."""
    return [
        EjemploEntrenamiento(
            instruction="Calcula la materialidad global, materialidad de ejecucion y umbral de errores triviales para la siguiente auditoria financiera.",
            input="Entidad: MinTIC. Total activos: $8.500.000 millones. Ingresos totales: $12.000.000 millones. Total gastos: $11.200.000 millones. Utilidad neta: $800.000 millones.",
            output="CALCULO DE MATERIALIDAD — NIA 320 y 450\n\nBASE SELECCIONADA: Ingresos totales ($12.000.000 millones)\nJUSTIFICACION: Se seleccionan los ingresos como base porque es la cifra mas representativa para una entidad publica del sector TIC. Las entidades del gobierno central se evaluan tipicamente sobre ingresos o gastos totales.\n\n1. MATERIALIDAD GLOBAL (NIA 320.10)\n   Base: $12.000.000 millones\n   Porcentaje: 1% (rango tipico para entidades publicas: 0.5% - 2%)\n   MATERIALIDAD GLOBAL = $12.000.000 x 1% = $120.000 millones\n\n2. MATERIALIDAD DE EJECUCION (NIA 320.11)\n   Porcentaje sobre materialidad global: 75%\n   (Se usa 75% considerando que es primera auditoria y hay riesgo moderado de errores no detectados)\n   MATERIALIDAD DE EJECUCION = $120.000 x 75% = $90.000 millones\n\n3. UMBRAL DE ERRORES TRIVIALES (NIA 450.A2)\n   Porcentaje sobre materialidad global: 5%\n   UMBRAL = $120.000 x 5% = $6.000 millones\n\nRESUMEN:\n| Concepto | Valor (millones) |\n|----------|------------------|\n| Materialidad global | $120.000 |\n| Materialidad de ejecucion | $90.000 |\n| Umbral errores triviales | $6.000 |\n\nNOTA: Errores individuales por debajo de $6.000 millones se consideran claramente triviales. Errores entre $6.000 y $90.000 millones se acumulan y evaluan en conjunto. Errores superiores a $120.000 millones afectan la opinion de auditoria.",
            metadata={"categoria": "calculos_materialidad", "nia": "320_450"},
        ),
        EjemploEntrenamiento(
            instruction="Explica como aplicar el muestreo estadistico en una auditoria de la CGR segun la NIA 530.",
            input="Se requiere auditar 4.500 contratos de una entidad con valor total de $2.8 billones. El equipo auditor tiene 3 meses.",
            output="PLAN DE MUESTREO ESTADISTICO — NIA 530\n\nPOBLACION: 4.500 contratos por $2.8 billones\n\nPASO 1: ESTRATIFICACION\nDividir la poblacion en estratos por valor:\n- Estrato 1 (Alto): Contratos > $10.000 millones: revision del 100% (estimados ~45 contratos)\n- Estrato 2 (Medio): Contratos $1.000 - $10.000 millones: muestreo estadistico\n- Estrato 3 (Bajo): Contratos < $1.000 millones: muestreo por atributos\n\nPASO 2: CALCULO DEL TAMANO DE MUESTRA\nParametros:\n- Nivel de confianza: 95%\n- Error tolerable: Materialidad de ejecucion = $[calculada]\n- Tasa de error esperada: 2% (basada en auditorias anteriores)\n\nFormula (muestreo por atributos para estrato 3):\nn = (Z^2 * p * (1-p)) / e^2\nn = (1.96^2 * 0.02 * 0.98) / 0.05^2\nn = 30 contratos minimo del estrato 3\n\nPara estrato 2 (muestreo por unidades monetarias - MUS):\nn = Valor del estrato / Materialidad de ejecucion\n\nPASO 3: SELECCION\nMetodo: Muestreo sistematico con inicio aleatorio para estratos 2 y 3.\n\nPASO 4: EXTRAPOLACION\nLos errores encontrados en la muestra se extrapolan a la poblacion total del estrato para estimar el error total.\n\nTIEMPO ESTIMADO:\n- Estrato 1 (100% revision): 6 semanas\n- Estrato 2 (muestra): 4 semanas\n- Estrato 3 (muestra): 2 semanas\nTotal: 12 semanas = 3 meses (viable con el equipo)",
            metadata={"categoria": "calculos_materialidad", "nia": "530"},
        ),
        EjemploEntrenamiento(
            instruction="Explica como recalcular la materialidad cuando durante la ejecucion de la auditoria se descubren errores significativos.",
            input="Durante la auditoria de una entidad con materialidad global de $50.000 millones (1% de ingresos de $5 billones), se detectaron errores por $45.000 millones en el primer rubro examinado.",
            output="RECALCULO DE MATERIALIDAD — NIA 320.12-13\n\nSITUACION ACTUAL:\n- Materialidad global original: $50.000 millones (1% de $5 billones)\n- Materialidad de ejecucion original: $37.500 millones (75%)\n- Errores detectados: $45.000 millones (90% de la materialidad global)\n\nANALISIS:\nLos errores detectados ($45.000 millones) se acercan a la materialidad global ($50.000 millones), lo que indica que:\n1. El riesgo de auditoria es mayor al evaluado inicialmente\n2. La materialidad podria estar sobreestimada\n3. Pueden existir errores no detectados en otros rubros\n\nACCIONES REQUERIDAS (NIA 320.12):\n1. REVISAR la materialidad a la baja. Opciones:\n   - Reducir el porcentaje de 1% a 0.5% = $25.000 millones\n   - Cambiar la base de calculo (usar activos en vez de ingresos)\n\n2. AMPLIAR el alcance de pruebas ya realizadas\n3. EVALUAR si las pruebas completadas siguen siendo validas con la nueva materialidad\n4. DOCUMENTAR la justificacion del cambio en el memorando de planeacion\n\nNUEVA MATERIALIDAD PROPUESTA:\n| Concepto | Original | Revisada |\n|----------|----------|----------|\n| Global | $50.000 M | $25.000 M |\n| Ejecucion | $37.500 M | $18.750 M |\n| Trivialidad | $2.500 M | $1.250 M |\n\nIMPACTO: Los errores de $45.000 millones ahora superan ampliamente la materialidad global revisada, lo que afectara la opinion de auditoria.",
            metadata={"categoria": "calculos_materialidad", "nia": "320_revision"},
        ),
    ]


def generar_ejemplos_contratacion() -> list[EjemploEntrenamiento]:
    """Genera ejemplos sobre contratacion estatal."""
    return [
        EjemploEntrenamiento(
            instruction="Analiza el siguiente caso de contratacion publica e identifica posibles irregularidades.",
            input="Una entidad publica celebro un contrato de prestacion de servicios profesionales por $450 millones con una persona natural para 'asesoria juridica general' por 11 meses. El contrato fue suscrito el 2 de enero, un dia despues de la posesion del nuevo director.",
            output="ANALISIS DE POSIBLES IRREGULARIDADES:\n\n1. OBJETO CONTRACTUAL VAGO\n   Irregularidad: 'Asesoria juridica general' es un objeto excesivamente amplio e indeterminado.\n   Norma: Art. 3 Ley 80/1993 — El contrato debe tener objeto claro y delimitado.\n   Riesgo: Imposibilidad de verificar cumplimiento y calidad de entregables.\n\n2. POSIBLE DESNATURALIZACION DEL CONTRATO\n   Irregularidad: $450 millones por 11 meses para una sola persona sugiere un posible contrato de realidad laboral encubierto (subordinacion, horario, exclusividad).\n   Norma: Art. 32 Ley 80/1993; Concepto 7 de 2019 del Consejo de Estado.\n   Riesgo: Demandas laborales, pasivos contingentes.\n\n3. AUSENCIA DE PLURALIDAD DE OFERENTES\n   Irregularidad: La contratacion directa de servicios profesionales (Art. 2, num. 4, lit. h, Ley 1150/2006) requiere justificar la idoneidad Y experiencia especifica del contratista.\n   Riesgo: Si no hay soportes de idoneidad, se configura violacion al principio de seleccion objetiva.\n\n4. TIMING SOSPECHOSO\n   Irregularidad: Contrato celebrado 1 dia despues de la posesion del nuevo director sugiere un compromiso preexistente (posible pago de favores politicos).\n   Norma: Ley 1474/2011 (Estatuto Anticorrupcion).\n   Riesgo: Hallazgo con connotacion disciplinaria y posiblemente penal.\n\nRECOMENDACION PARA EL AUDITOR:\n- Solicitar los estudios previos y la justificacion de idoneidad\n- Verificar la hoja de vida del contratista en SIGEP\n- Cruzar con bases de financiadores de campanas\n- Revisar entregables especificos y su verificacion por el supervisor",
            metadata={"categoria": "contratacion", "tipo": "analisis_caso"},
        ),
        EjemploEntrenamiento(
            instruction="Explica las modalidades de seleccion en la contratacion publica colombiana y cuando aplica cada una.",
            input="Un auditor nuevo necesita entender las modalidades de contratacion para sus auditorias.",
            output="MODALIDADES DE SELECCION — Ley 1150 de 2007 y Decreto 1082 de 2015:\n\n1. LICITACION PUBLICA (regla general)\n   Aplica: Cuando el objeto no corresponde a ninguna otra modalidad.\n   Tipico: Obras civiles > umbral de menor cuantia, suministros complejos.\n   Plazo proceso: 4-6 meses tipicamente.\n\n2. SELECCION ABREVIADA\n   a) Menor cuantia: Segun presupuesto de la entidad (10% para grandes, hasta 100% para pequenas).\n   b) Subasta inversa: Para bienes de caracteristicas tecnicas uniformes (commodities).\n   c) Acuerdos marco: Compras a traves de Colombia Compra Eficiente.\n   d) Enajenacion de bienes del Estado.\n\n3. CONCURSO DE MERITOS\n   Aplica: Consultoria, estudios, interventoria.\n   Caracteristica: Se evalua primero la calidad tecnica; el precio se negocia despues con el primer elegible.\n\n4. CONTRATACION DIRECTA\n   Causales taxativas (Art. 2, num. 4, Ley 1150/2007):\n   a) Urgencia manifiesta\n   b) Contratacion de emprestitos\n   c) Contratos interadministrativos\n   d) Servicios profesionales y de apoyo a la gestion\n   e) Arrendamiento de inmuebles\n   f) Cuando no exista pluralidad de oferentes\n\n5. MINIMA CUANTIA (Ley 1474/2011, Art. 94)\n   Aplica: Valor <= 10% de la menor cuantia de la entidad.\n   Proceso: Simplificado, 1 dia habiles de publicacion.\n\nPUNTOS CLAVE PARA EL AUDITOR:\n- Verificar que la modalidad usada corresponda al objeto y la cuantia\n- La contratacion directa es la mas auditada por riesgo de discrecionalidad\n- Revisar fraccionamiento de contratos (dividir para evadir modalidad)",
            metadata={"categoria": "contratacion", "tema": "modalidades_seleccion"},
        ),
        EjemploEntrenamiento(
            instruction="Evalua si el siguiente contrato interadministrativo cumple los requisitos legales.",
            input="El Ministerio de Educacion celebro un contrato interadministrativo con la Universidad Nacional por $8.000 millones para 'asesoria en gestion publica'. La universidad subcontrato el 80% del objeto con una firma privada de consultoria.",
            output="EVALUACION DE CONTRATO INTERADMINISTRATIVO:\n\nREQUISITOS LEGALES (Art. 2, num. 4, lit. c, Ley 1150/2007; Art. 95 Ley 1474/2011):\n\n1. RELACION DIRECTA CON OBJETO MISIONAL: CUESTIONABLE\n   La 'asesoria en gestion publica' es un objeto generico que podria no estar directamente vinculado al objeto misional de la Universidad (docencia, investigacion, extension).\n   Riesgo: Si el objeto no es misional, la contratacion directa no procede.\n\n2. PROHIBICION DE SUBCONTRATACION (Ley 1474/2011, Art. 95):\n   IRREGULAR — La subcontratacion del 80% del objeto desnaturaliza el contrato interadministrativo. La razon de ser de esta modalidad es que la entidad contratada ejecute con sus propios recursos y capacidad.\n   La norma prohibe que los contratos interadministrativos sirvan como mecanismo para evadir la seleccion publica de contratistas.\n\n3. VALOR Y PROPORCION: $8.000 millones es un valor significativo para una asesoria. Se debe verificar la justificacion de precios.\n\nCONCLUSION:\nEl contrato presenta irregularidades por:\n- Posible desnaturalizacion del contrato interadministrativo (subcontratacion del 80%)\n- Objeto contractual posiblemente ajeno al misional de la universidad\n- Violacion del articulo 95 de la Ley 1474/2011\n\nCONNOTACION: Administrativa y potencialmente fiscal (si se demuestra sobrecosto vs. contratacion directa del consultor privado).",
            metadata={"categoria": "contratacion", "tipo": "evaluacion_interadministrativo"},
        ),
        EjemploEntrenamiento(
            instruction="Describe los indicadores de alerta de posible corrupcion en contratacion publica que un auditor debe verificar.",
            input="Un auditor junior necesita una lista de verificacion para detectar posibles irregularidades en los contratos de una entidad.",
            output="INDICADORES DE ALERTA (RED FLAGS) EN CONTRATACION PUBLICA:\n\n1. FRACCIONAMIENTO DE CONTRATOS\n   - Multiples contratos con el mismo objeto y contratista\n   - Valores justo por debajo del umbral de la modalidad\n   - Fechas de suscripcion consecutivas\n\n2. CONCENTRACION DE ADJUDICACIONES\n   - Un solo contratista recibe un porcentaje alto del presupuesto\n   - Empresas creadas recientemente con capital minimo ganan contratos grandes\n   - Los mismos subcontratistas aparecen en diferentes contratistas principales\n\n3. DEFICIENCIAS EN ESTUDIOS PREVIOS\n   - Estudios de mercado con una sola cotizacion\n   - Valores significativamente superiores al promedio del sector\n   - Especificaciones tecnicas direccionadas (requisitos que solo un oferente cumple)\n\n4. IRREGULARIDADES EN EL PROCESO\n   - Adendas que cambian criterios de evaluacion en ultimo momento\n   - Oferentes que se retiran para dejar un solo proponente\n   - Pliegos de condiciones copiados de contratos anteriores sin ajuste\n\n5. EJECUCION CONTRACTUAL\n   - Pagos sin soportes de entregables\n   - Adiciones superiores al 50% del valor inicial\n   - Supervisor que no reporta incumplimientos evidentes\n   - Liquidacion tardia o sin balance final\n\n6. CONFLICTOS DE INTERES\n   - Parentesco entre funcionarios y contratistas (verificar SIGEP)\n   - Financiadores de campanas que resultan contratistas\n   - Funcionarios que pasan al sector privado contratista (puerta giratoria)\n\nHERRAMIENTAS DE VERIFICACION:\n- SECOP I y II: historico de contratos\n- RUES: existencia legal del contratista\n- BREF: antecedentes fiscales\n- SIGEP: hojas de vida de funcionarios\n- Registro Mercantil: composicion accionaria",
            metadata={"categoria": "contratacion", "tipo": "lista_verificacion"},
        ),
    ]


# ── Funciones principales ────────────────────────────────────────────────────

def construir_dataset(
    ruta_salida: str | Path = "dataset_cecilia.jsonl",
    categorias: list[str] | None = None,
) -> DatasetStats:
    """Construye el dataset JSONL completo para fine-tuning.

    Args:
        ruta_salida: Ruta del archivo JSONL de salida.
        categorias: Lista de categorias a incluir. None = todas.

    Returns:
        Estadisticas del dataset generado.
    """
    cats = categorias or CATEGORIAS
    ruta = Path(ruta_salida)

    generadores = {
        "hallazgos": generar_ejemplos_hallazgos,
        "preguntas_frecuentes": generar_ejemplos_preguntas_frecuentes,
        "interpretaciones_normativas": generar_ejemplos_normativas,
        "calculos_materialidad": generar_ejemplos_materialidad,
        "contratacion": generar_ejemplos_contratacion,
    }

    stats = DatasetStats(fecha_generacion=datetime.now(timezone.utc).isoformat())
    todos: list[EjemploEntrenamiento] = []

    for cat in cats:
        gen = generadores.get(cat)
        if gen:
            ejemplos = gen()
            todos.extend(ejemplos)
            stats.por_categoria[cat] = len(ejemplos)
            logger.info("Categoria '%s': %d ejemplos", cat, len(ejemplos))

    # Escribir JSONL
    with ruta.open("w", encoding="utf-8") as f:
        for ej in todos:
            f.write(ej.a_jsonl() + "\n")

    stats.total_ejemplos = len(todos)
    stats.tokens_estimados = sum(
        len((e.instruction + e.input + e.output).split()) * 1.3
        for e in todos
    )

    logger.info(
        "Dataset generado: %d ejemplos, ~%d tokens estimados -> %s",
        stats.total_ejemplos,
        int(stats.tokens_estimados),
        ruta,
    )

    return stats


def cargar_dataset(ruta: str | Path) -> list[EjemploEntrenamiento]:
    """Carga un dataset JSONL."""
    ejemplos = []
    with Path(ruta).open("r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if linea:
                d = json.loads(linea)
                ejemplos.append(EjemploEntrenamiento.desde_dict(d))
    return ejemplos


def _anonimizar_ejemplo(ejemplo: EjemploEntrenamiento) -> EjemploEntrenamiento:
    """Anonimiza un ejemplo individual."""
    return EjemploEntrenamiento(
        instruction=ejemplo.instruction,
        input=anonimizar(ejemplo.input),
        output=anonimizar(ejemplo.output),
        metadata={**ejemplo.metadata, "anonimizado": True},
    )
