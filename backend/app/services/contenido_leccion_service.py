"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/services/contenido_leccion_service.py
Proposito: Generacion dinamica de contenido de lecciones desde el RAG,
           infografias Mermaid, flashcards, glosario y simulaciones.
Sprint: Capacitacion 2.0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("cecilia.services.contenido_leccion")

# ── Estilo de aprendizaje → adaptacion del prompt ──────────────────────────
ADAPTACIONES_ESTILO = {
    "lector": "Usa texto detallado, parrafos bien estructurados, citas textuales, notas al margen.",
    "auditivo": "Escribe como si fueras un profesor explicando en clase. Usa frases conversacionales, ejemplos hablados.",
    "visual": "Incluye tablas, listas, comparaciones lado a lado, y sugiere diagramas. Usa encabezados claros.",
    "kinestesico": "Incluye ejercicios practicos, pasos a seguir, y simulaciones. Pide al lector que haga algo en cada seccion.",
}

PROMPT_LECCION = """Eres un instructor experto en control fiscal colombiano de la CGR.
Genera el contenido de una leccion educativa sobre el siguiente tema:

LECCION: {titulo}
DESCRIPCION: {descripcion}
NIVEL: {nivel}
ESTILO DE APRENDIZAJE DEL USUARIO: {estilo}
ADAPTACION: {adaptacion}

CONTEXTO NORMATIVO DEL RAG:
{contexto_rag}

FORMATO DE SALIDA (Markdown):

## {titulo}

### Introduccion
(2-3 parrafos introductorios adaptados al estilo del usuario)

### Conceptos clave
(5-7 conceptos con definicion clara y cita normativa)

### Explicacion detallada
(Contenido principal con {adaptacion_corta})

### Ejemplos practicos
(3 ejemplos con datos ficticios — NUNCA datos reales)

### Analogias cotidianas
(2 analogias que conecten el tema con la vida diaria)

### Preguntas de reflexion
(3 preguntas para que el aprendiz reflexione)

### Resumen
(Resumen en 5 puntos clave)

### Referencias normativas
(Lista de normas citadas con articulos especificos)

---
*Contenido generado por CecilIA — Requiere validacion humana — Circular 023 CGR*
"""

PROMPT_FLASHCARDS = """Genera {num_tarjetas} tarjetas de memorizacion (flashcards) sobre el tema: "{tema}"

Cada tarjeta debe tener:
- frente: Una pregunta o concepto breve
- reverso: Respuesta concisa con referencia normativa cuando aplique
- nivel_bloom: recordar | comprender | aplicar | analizar | evaluar | crear
- dificultad: basica | intermedia | avanzada

CONTEXTO:
{contexto}

Responde en JSON:
[
  {{"frente": "...", "reverso": "...", "nivel_bloom": "recordar", "dificultad": "basica"}},
  ...
]
"""

PROMPT_INFOGRAFIA = """Genera un diagrama Mermaid para visualizar: "{tema}"
Tipo sugerido: {tipo_diagrama}

CONTEXTO:
{contexto}

Responde SOLO con el codigo Mermaid, sin texto adicional.
Ejemplo de formato:
```mermaid
flowchart TD
    A[Inicio] --> B[Paso 1]
    B --> C[Paso 2]
```
"""

PROMPT_SIMULACION_PASO = """Eres un instructor de la CGR guiando una simulacion de auditoria.

SIMULACION: {nombre_simulacion}
PASO ACTUAL: {paso_actual} de {total_pasos}
DESCRIPCION DEL PASO: {descripcion_paso}
CONTEXTO PREVIO: {contexto_previo}

Genera el contenido de este paso de la simulacion:
1. Presentacion del escenario (datos ficticios)
2. Informacion que el aprendiz necesita analizar
3. Pregunta o decision que debe tomar
4. Opciones de respuesta (4 opciones, solo 1 correcta)
5. Retroalimentacion para cada opcion (por que es correcta o incorrecta)

Responde en JSON:
{{
  "escenario": "...",
  "datos": ["dato1", "dato2"],
  "pregunta": "...",
  "opciones": [
    {{"texto": "...", "correcta": true, "retroalimentacion": "..."}},
    {{"texto": "...", "correcta": false, "retroalimentacion": "..."}},
    ...
  ],
  "tip": "Consejo del experto para este paso"
}}
"""


# ── Datos del glosario base ────────────────────────────────────────────────
GLOSARIO_BASE = [
    {
        "termino": "Hallazgo de auditoria",
        "definicion_simple": "Situacion irregular encontrada durante una auditoria que se documenta formalmente.",
        "definicion_tecnica": "Resultado de la comparacion entre la condicion (lo que es) y el criterio (lo que deberia ser), con identificacion de causa y efecto, conforme a la metodologia del proceso auditor de la CGR.",
        "ejemplo": "Se encontro que la entidad no realizo los registros contables de 50 contratos por valor de 2.000 millones, incumpliendo las normas de contabilidad publica.",
        "norma_aplicable": "Ley 42/1993 Art. 10; Decreto 403/2020 Art. 124-130; GAF Seccion 3.4",
        "categoria": "auditoria",
        "terminos_relacionados": ["condicion", "criterio", "causa", "efecto", "connotacion"],
    },
    {
        "termino": "Materialidad",
        "definicion_simple": "Monto minimo a partir del cual un error o irregularidad se considera importante para la auditoria.",
        "definicion_tecnica": "Nivel de error o desviacion que, individual o acumuladamente, podria influir en las decisiones economicas de los usuarios de la informacion financiera. Se calcula como porcentaje de los activos totales, ingresos o presupuesto.",
        "ejemplo": "Para una entidad con activos de 500.000 millones, la materialidad al 1% seria 5.000 millones. Errores por debajo de este umbral no se consideran significativos.",
        "norma_aplicable": "GAF Instructivo 2; NIA 320; Resolucion 706/2016 CGR",
        "categoria": "financiero",
        "terminos_relacionados": ["importancia relativa", "error tolerable", "umbral de materialidad"],
    },
    {
        "termino": "Proceso de responsabilidad fiscal",
        "definicion_simple": "Proceso juridico para determinar si un funcionario debe devolver dinero publico que se perdio por su culpa.",
        "definicion_tecnica": "Conjunto de actuaciones administrativas adelantadas por la Contraloria para determinar la responsabilidad de servidores publicos y particulares por el manejo irregular de bienes o fondos publicos que ocasionen dano patrimonial al Estado.",
        "ejemplo": "Se inicio proceso fiscal contra el ordenador del gasto por aprobar pagos sin verificar la entrega de bienes por 800 millones de pesos.",
        "norma_aplicable": "Ley 610/2000; Constitucion Art. 268 numeral 5",
        "categoria": "normativa",
        "terminos_relacionados": ["detrimento patrimonial", "fallo con responsabilidad", "auto de apertura"],
    },
    {
        "termino": "Control fiscal",
        "definicion_simple": "Vigilancia que hace la Contraloria para verificar que el dinero publico se use correctamente.",
        "definicion_tecnica": "Funcion publica ejercida por la Contraloria General de la Republica para vigilar la gestion fiscal de la administracion y de los particulares o entidades que manejen fondos o bienes de la nacion.",
        "ejemplo": "La CGR audita anualmente a mas de 400 entidades del orden nacional verificando el buen uso de los recursos publicos.",
        "norma_aplicable": "Constitucion Art. 267-274; Ley 42/1993",
        "categoria": "institucional",
        "terminos_relacionados": ["auditoria", "vigilancia fiscal", "control de resultados"],
    },
    {
        "termino": "Detrimento patrimonial",
        "definicion_simple": "Perdida de dinero o bienes publicos causada por mala gestion.",
        "definicion_tecnica": "Lesion del patrimonio publico representada en el menoscabo, disminucion, perjuicio, detrimento, perdida o deterioro de los bienes o recursos publicos, o a los intereses patrimoniales del Estado, producida por una gestion fiscal antieconómica, ineficaz, ineficiente, inequitativa e inoportuna.",
        "ejemplo": "Una entidad pago 2.000 millones por obras que nunca se ejecutaron, constituyendo un detrimento patrimonial.",
        "norma_aplicable": "Ley 610/2000 Art. 6",
        "categoria": "auditoria",
        "terminos_relacionados": ["dano fiscal", "responsabilidad fiscal", "hallazgo fiscal"],
    },
    {
        "termino": "Connotacion del hallazgo",
        "definicion_simple": "Clasificacion de la gravedad de un hallazgo: administrativo, fiscal, disciplinario o penal.",
        "definicion_tecnica": "Calificacion juridica que se da a un hallazgo de auditoria segun la naturaleza de la irregularidad encontrada, determinando si genera responsabilidad administrativa, fiscal, disciplinaria o penal.",
        "ejemplo": "Un hallazgo por pago doble de 50 millones tiene connotacion fiscal (detrimento) y disciplinaria (incumplimiento de deberes).",
        "norma_aplicable": "GAF Seccion 3.4.3; Ley 610/2000; Ley 734/2002",
        "categoria": "auditoria",
        "terminos_relacionados": ["hallazgo administrativo", "hallazgo fiscal", "hallazgo disciplinario", "hallazgo penal"],
    },
    {
        "termino": "GAF",
        "definicion_simple": "Guia de Auditoria Financiera — manual que define como hacer auditorias en la CGR.",
        "definicion_tecnica": "Guia de Auditoria Financiera de la CGR que establece la metodologia, procedimientos, formatos y lineamientos tecnicos para la ejecucion de auditorias financieras en el marco del control fiscal colombiano.",
        "ejemplo": "Segun la GAF, toda auditoria financiera debe pasar por 5 fases: preplaneacion, planeacion, ejecucion, informe y seguimiento.",
        "norma_aplicable": "Resolucion Organica 7350/2013 CGR",
        "categoria": "institucional",
        "terminos_relacionados": ["auditoria financiera", "formatos CGR", "proceso auditor"],
    },
    {
        "termino": "Preplaneacion",
        "definicion_simple": "Primera fase de la auditoria donde se estudia la entidad antes de visitarla.",
        "definicion_tecnica": "Fase inicial del proceso auditor en la que se obtiene conocimiento general de la entidad auditada, se identifican riesgos preliminares, se define el alcance y se elabora el plan de trabajo.",
        "ejemplo": "En preplaneacion, el equipo auditor revisa los estados financieros de los ultimos 3 anios, identifica cambios normativos y solicita informacion preliminar.",
        "norma_aplicable": "GAF Seccion 2.1; Formato 1 y 3",
        "categoria": "auditoria",
        "terminos_relacionados": ["plan de trabajo", "conocimiento de la entidad", "riesgos preliminares"],
    },
    {
        "termino": "Circular 023 CGR",
        "definicion_simple": "Directriz de la CGR que regula como usar inteligencia artificial en el control fiscal.",
        "definicion_tecnica": "Circular 023 de 2025 (radicado 2025IE0146473) firmada por el Contralor General, que establece 10 principios para el uso responsable de IA en la CGR, incluyendo transparencia, supervision humana, trazabilidad y usos permitidos y limitados.",
        "ejemplo": "Segun la Circular 023, CecilIA solo puede generar borradores y sugerencias — nunca dictamenes o hallazgos definitivos sin revision humana.",
        "norma_aplicable": "Circular 023/2025 CGR; CONPES 4144/2025; CONPES 4145/2025",
        "categoria": "normativa",
        "terminos_relacionados": ["inteligencia artificial", "supervision humana", "trazabilidad"],
    },
    {
        "termino": "SECOP",
        "definicion_simple": "Sistema Electronico de Contratacion Publica — plataforma donde se publican todos los contratos del Estado.",
        "definicion_tecnica": "Sistema Electronico para la Contratacion Publica operado por Colombia Compra Eficiente, que permite la publicacion, gestion y seguimiento de procesos de contratacion estatal en todas sus modalidades.",
        "ejemplo": "Al auditar contratacion de MinTIC, se consulta SECOP para verificar que todos los contratos cumplan con los requisitos de publicidad.",
        "norma_aplicable": "Ley 1150/2007 Art. 3; Decreto 1082/2015",
        "categoria": "contratacion",
        "terminos_relacionados": ["contratacion publica", "Colombia Compra Eficiente", "proceso de seleccion"],
    },
]

# ── Simulaciones disponibles ───────────────────────────────────────────────
SIMULACIONES = {
    "primera_auditoria": {
        "nombre": "Tu primera auditoria",
        "descripcion": "Guia paso a paso por las 5 fases del proceso auditor DVF con un caso ficticio de MinTIC.",
        "direccion": "DVF",
        "total_pasos": 5,
        "pasos": [
            {"titulo": "Preplaneacion", "descripcion": "Estudia la entidad y define el alcance de la auditoria"},
            {"titulo": "Planeacion", "descripcion": "Calcula materialidad, identifica riesgos y disena pruebas"},
            {"titulo": "Ejecucion", "descripcion": "Aplica pruebas de auditoria y documenta hallazgos"},
            {"titulo": "Informe", "descripcion": "Redacta el informe de auditoria con hallazgos y recomendaciones"},
            {"titulo": "Seguimiento", "descripcion": "Verifica que la entidad corrigio las observaciones"},
        ],
    },
    "estudio_sectorial": {
        "nombre": "Construye un estudio sectorial",
        "descripcion": "Caso del sector TIC con datos ficticios para aprender la metodologia DES.",
        "direccion": "DES",
        "total_pasos": 4,
        "pasos": [
            {"titulo": "Diagnostico sectorial", "descripcion": "Analiza el contexto del sector TIC en Colombia"},
            {"titulo": "Analisis de politica publica", "descripcion": "Evalua la politica TIC vigente y sus indicadores"},
            {"titulo": "Identificacion de hallazgos macro", "descripcion": "Detecta brechas y riesgos sectoriales"},
            {"titulo": "Conclusiones y recomendaciones", "descripcion": "Redacta conclusiones con impacto sectorial"},
        ],
    },
    "hallazgo_completo": {
        "nombre": "Configura un hallazgo completo",
        "descripcion": "Estructura un hallazgo fiscal con sus 4 elementos a partir de evidencia.",
        "direccion": "DVF",
        "total_pasos": 4,
        "pasos": [
            {"titulo": "Identifica la condicion", "descripcion": "Que encontraste — describe la situacion irregular"},
            {"titulo": "Establece el criterio", "descripcion": "Que norma se incumplio — cita la referencia legal"},
            {"titulo": "Determina la causa", "descripcion": "Por que ocurrio — falta de control, negligencia, etc."},
            {"titulo": "Cuantifica el efecto", "descripcion": "Cual es la consecuencia — cuantifica en pesos si aplica"},
        ],
    },
}


class ContenidoLeccionService:
    """Generacion dinamica de contenido desde el RAG."""

    def __init__(self, llm=None, rag_retriever=None):
        self.llm = llm
        self.rag_retriever = rag_retriever

    async def generar_contenido_leccion(
        self, db: AsyncSession, leccion_id: str, estilo_usuario: str = "lector"
    ) -> dict[str, Any]:
        """Genera contenido adaptado al estilo de aprendizaje del usuario."""
        from app.models.capacitacion import Leccion

        result = await db.execute(
            select(Leccion).where(Leccion.id == leccion_id)
        )
        leccion = result.scalar_one_or_none()
        if not leccion:
            return {"error": "Leccion no encontrada"}

        # Si ya tiene contenido estatico, usarlo como base
        if leccion.contenido_md and len(leccion.contenido_md) > 200:
            return {
                "leccion_id": leccion_id,
                "titulo": leccion.titulo,
                "contenido_md": leccion.contenido_md,
                "generado_dinamicamente": False,
            }

        # Generar desde RAG + LLM
        contexto_rag = await self._buscar_contexto_rag(leccion.titulo)
        adaptacion = ADAPTACIONES_ESTILO.get(estilo_usuario, ADAPTACIONES_ESTILO["lector"])

        if self.llm:
            try:
                prompt = PROMPT_LECCION.format(
                    titulo=leccion.titulo,
                    descripcion=leccion.descripcion,
                    nivel="intermedio",
                    estilo=estilo_usuario,
                    adaptacion=adaptacion,
                    adaptacion_corta=adaptacion[:50],
                    contexto_rag=contexto_rag,
                )
                resp = await asyncio.to_thread(self.llm.invoke, prompt)
                contenido = resp.content if hasattr(resp, "content") else str(resp)
                return {
                    "leccion_id": leccion_id,
                    "titulo": leccion.titulo,
                    "contenido_md": contenido,
                    "generado_dinamicamente": True,
                    "estilo_adaptado": estilo_usuario,
                }
            except Exception as e:
                logger.error("Error generando contenido: %s", e)

        return {
            "leccion_id": leccion_id,
            "titulo": leccion.titulo,
            "contenido_md": leccion.contenido_md or f"# {leccion.titulo}\n\n{leccion.descripcion}",
            "generado_dinamicamente": False,
        }

    async def generar_flashcards(
        self, tema: str, num_tarjetas: int = 10, contexto_extra: str = ""
    ) -> list[dict[str, str]]:
        """Genera set de flashcards sobre un tema."""
        contexto = await self._buscar_contexto_rag(tema)
        if contexto_extra:
            contexto += "\n" + contexto_extra

        if self.llm:
            try:
                prompt = PROMPT_FLASHCARDS.format(
                    num_tarjetas=num_tarjetas, tema=tema, contexto=contexto
                )
                resp = await asyncio.to_thread(self.llm.invoke, prompt)
                texto = resp.content if hasattr(resp, "content") else str(resp)
                import json
                # Intentar parsear JSON del response
                inicio = texto.find("[")
                fin = texto.rfind("]") + 1
                if inicio >= 0 and fin > inicio:
                    return json.loads(texto[inicio:fin])
            except Exception as e:
                logger.error("Error generando flashcards: %s", e)

        # Fallback: flashcards basicas
        return self._flashcards_fallback(tema)

    async def generar_infografia_mermaid(
        self, tema: str, tipo_diagrama: str = "flowchart"
    ) -> str:
        """Genera diagrama Mermaid para visualizacion."""
        contexto = await self._buscar_contexto_rag(tema)

        if self.llm:
            try:
                prompt = PROMPT_INFOGRAFIA.format(
                    tema=tema, tipo_diagrama=tipo_diagrama, contexto=contexto
                )
                resp = await asyncio.to_thread(self.llm.invoke, prompt)
                texto = resp.content if hasattr(resp, "content") else str(resp)
                # Extraer solo el codigo mermaid
                if "```mermaid" in texto:
                    inicio = texto.find("```mermaid") + len("```mermaid")
                    fin = texto.find("```", inicio)
                    return texto[inicio:fin].strip()
                return texto.strip()
            except Exception as e:
                logger.error("Error generando infografia: %s", e)

        return self._infografia_fallback(tema)

    async def obtener_glosario(
        self, db: AsyncSession, categoria: Optional[str] = None, busqueda: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Obtiene entradas del glosario con filtros opcionales."""
        from app.models.capacitacion import EntradaGlosario

        query = select(EntradaGlosario).order_by(EntradaGlosario.termino)
        if categoria:
            query = query.where(EntradaGlosario.categoria == categoria)
        if busqueda:
            query = query.where(EntradaGlosario.termino.ilike(f"%{busqueda}%"))

        result = await db.execute(query)
        entradas = result.scalars().all()

        return [
            {
                "id": e.id,
                "termino": e.termino,
                "definicion_simple": e.definicion_simple,
                "definicion_tecnica": e.definicion_tecnica,
                "ejemplo": e.ejemplo,
                "norma_aplicable": e.norma_aplicable,
                "categoria": e.categoria,
                "terminos_relacionados": e.terminos_relacionados or [],
            }
            for e in entradas
        ]

    async def seed_glosario(self, db: AsyncSession) -> int:
        """Puebla el glosario con terminos base."""
        from app.models.capacitacion import EntradaGlosario

        count = 0
        for entrada in GLOSARIO_BASE:
            # Verificar si ya existe
            result = await db.execute(
                select(EntradaGlosario).where(
                    EntradaGlosario.termino == entrada["termino"]
                )
            )
            if result.scalar_one_or_none():
                continue

            db.add(EntradaGlosario(
                id=str(uuid.uuid4()),
                **entrada,
            ))
            count += 1

        await db.flush()
        return count

    def obtener_simulaciones_disponibles(self) -> list[dict[str, Any]]:
        """Retorna lista de simulaciones disponibles."""
        return [
            {
                "id": sid,
                "nombre": s["nombre"],
                "descripcion": s["descripcion"],
                "direccion": s["direccion"],
                "total_pasos": s["total_pasos"],
            }
            for sid, s in SIMULACIONES.items()
        ]

    async def obtener_paso_simulacion(
        self, simulacion_id: str, paso: int, contexto_previo: str = ""
    ) -> dict[str, Any]:
        """Genera contenido para un paso de simulacion."""
        sim = SIMULACIONES.get(simulacion_id)
        if not sim:
            return {"error": "Simulacion no encontrada"}
        if paso < 1 or paso > sim["total_pasos"]:
            return {"error": f"Paso {paso} fuera de rango (1-{sim['total_pasos']})"}

        paso_info = sim["pasos"][paso - 1]

        if self.llm:
            try:
                prompt = PROMPT_SIMULACION_PASO.format(
                    nombre_simulacion=sim["nombre"],
                    paso_actual=paso,
                    total_pasos=sim["total_pasos"],
                    descripcion_paso=paso_info["descripcion"],
                    contexto_previo=contexto_previo or "Inicio de la simulacion",
                )
                resp = await asyncio.to_thread(self.llm.invoke, prompt)
                texto = resp.content if hasattr(resp, "content") else str(resp)
                import json
                inicio = texto.find("{")
                fin = texto.rfind("}") + 1
                if inicio >= 0 and fin > inicio:
                    data = json.loads(texto[inicio:fin])
                    data["paso"] = paso
                    data["titulo"] = paso_info["titulo"]
                    data["total_pasos"] = sim["total_pasos"]
                    return data
            except Exception as e:
                logger.error("Error generando paso de simulacion: %s", e)

        # Fallback
        return {
            "paso": paso,
            "titulo": paso_info["titulo"],
            "total_pasos": sim["total_pasos"],
            "escenario": f"Estas en la fase de {paso_info['titulo']} de una auditoria a MinTIC.",
            "datos": [
                "Presupuesto asignado: $50.000 millones",
                "Contratos vigentes: 45",
                "Periodo auditado: 2025",
            ],
            "pregunta": f"En la fase de {paso_info['titulo']}, cual es la accion prioritaria?",
            "opciones": [
                {"texto": paso_info["descripcion"], "correcta": True, "retroalimentacion": "Correcto. Esta es la accion principal de esta fase."},
                {"texto": "Saltar directamente al informe final", "correcta": False, "retroalimentacion": "Incorrecto. Cada fase es secuencial y obligatoria."},
                {"texto": "Delegar al equipo sin supervision", "correcta": False, "retroalimentacion": "Incorrecto. El auditor responsable debe supervisar cada fase."},
                {"texto": "Esperar instrucciones del director", "correcta": False, "retroalimentacion": "Incorrecto. El auditor tiene autonomia tecnica en la ejecucion."},
            ],
            "tip": f"Recuerda que la GAF establece procedimientos especificos para la fase de {paso_info['titulo']}.",
        }

    # ── Metodos internos ───────────────────────────────────────────────────

    async def _buscar_contexto_rag(self, tema: str) -> str:
        if self.rag_retriever:
            try:
                docs = await asyncio.to_thread(self.rag_retriever.invoke, tema)
                return "\n".join([d.page_content[:500] for d in docs[:5]])
            except Exception:
                pass
        return ""

    def _flashcards_fallback(self, tema: str) -> list[dict[str, str]]:
        return [
            {"frente": "Que es un hallazgo de auditoria?", "reverso": "Resultado de comparar condicion vs criterio. 4 elementos: condicion, criterio, causa, efecto. (GAF 3.4)", "nivel_bloom": "recordar", "dificultad": "basica"},
            {"frente": "Cuales son las 5 fases del proceso auditor?", "reverso": "1. Preplaneacion, 2. Planeacion, 3. Ejecucion, 4. Informe, 5. Seguimiento (GAF)", "nivel_bloom": "recordar", "dificultad": "basica"},
            {"frente": "Que norma regula la responsabilidad fiscal?", "reverso": "Ley 610 del 2000 — establece el proceso de responsabilidad fiscal", "nivel_bloom": "recordar", "dificultad": "basica"},
            {"frente": "Como se calcula la materialidad?", "reverso": "Porcentaje sobre activos totales, ingresos o presupuesto. Tipicamente 0.5%-3% segun GAF Instructivo 2", "nivel_bloom": "comprender", "dificultad": "intermedia"},
            {"frente": "Diferencia entre hallazgo administrativo y fiscal?", "reverso": "Administrativo: incumplimiento sin perdida economica. Fiscal: hay detrimento patrimonial (perdida de dinero publico)", "nivel_bloom": "analizar", "dificultad": "intermedia"},
        ]

    def _infografia_fallback(self, tema: str) -> str:
        return """flowchart TD
    A["1. Preplaneacion"] --> B["2. Planeacion"]
    B --> C["3. Ejecucion"]
    C --> D["4. Informe"]
    D --> E["5. Seguimiento"]
    A --> |"Conocer la entidad"| A1["Analisis preliminar"]
    B --> |"Materialidad y riesgos"| B1["Plan de auditoria"]
    C --> |"Pruebas y evidencia"| C1["Hallazgos"]
    D --> |"Comunicar resultados"| D1["Informe final"]
    E --> |"Verificar correcciones"| E1["Plan de mejoramiento"]
    style A fill:#C9A84C,color:#000
    style B fill:#1A5276,color:#fff
    style C fill:#1E8449,color:#fff
    style D fill:#C9A84C,color:#000
    style E fill:#1A5276,color:#fff"""
