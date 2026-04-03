"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: generar_formato.py
Propósito: Herramienta LangChain para generación de formatos CGR del proceso auditor (1-30)
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional

from langchain_core.tools import tool

logger = logging.getLogger("cecilia.tools.generar_formato")

# Catálogo de formatos y sus campos requeridos
CATALOGO_FORMATOS: dict[int, dict[str, Any]] = {
    1: {
        "nombre": "Carta de Presentación del Informe de Auditoría",
        "fase": "informe",
        "campos": [
            "destinatario", "nombre_entidad", "tipo_auditoria",
            "vigencia", "fecha_informe", "director_tecnico",
        ],
    },
    6: {
        "nombre": "Cálculo de Materialidad",
        "fase": "planeacion",
        "campos": [
            "nombre_entidad", "vigencia", "tipo_auditoria",
            "base_calculo", "valor_base", "porcentaje",
            "materialidad_global", "materialidad_ejecucion",
            "umbral_errores_insignificantes", "justificacion",
        ],
    },
    7: {
        "nombre": "Diseño de Muestreo",
        "fase": "planeacion",
        "campos": [
            "nombre_entidad", "vigencia", "componente",
            "objetivo_prueba", "metodo_muestreo", "poblacion",
            "tamano_muestra", "nivel_confianza", "criterio_seleccion",
        ],
    },
    11: {
        "nombre": "Hoja de Hallazgo",
        "fase": "ejecucion",
        "campos": [
            "nombre_entidad", "vigencia", "numero_hallazgo",
            "titulo_hallazgo", "condicion", "criterio",
            "causa", "efecto", "cuantia", "tipo_incidencia",
            "recomendacion", "evidencia_soporte",
        ],
    },
    23: {
        "nombre": "Plan de Mejoramiento",
        "fase": "seguimiento",
        "campos": [
            "nombre_entidad", "vigencia_auditoria",
            "hallazgos", "acciones_correctivas",
            "responsable", "fecha_inicio", "fecha_fin",
            "indicador_cumplimiento", "meta",
        ],
    },
}


def _generar_plantilla(
    numero_formato: int,
    datos: dict[str, Any],
) -> str:
    """Genera la plantilla del formato con los datos proporcionados.

    Args:
        numero_formato: Número del formato CGR.
        datos: Datos para pre-llenar el formato.

    Returns:
        Texto del formato generado.
    """
    fecha_actual: str = datetime.now().strftime("%d de %B de %Y")
    nombre_entidad: str = datos.get("nombre_entidad", "[PENDIENTE]")
    vigencia: str = datos.get("vigencia", "[PENDIENTE]")

    encabezado: str = (
        "=" * 70 + "\n"
        "CONTRALORÍA GENERAL DE LA REPÚBLICA\n"
        "=" * 70 + "\n"
    )

    if numero_formato == 11:
        return _generar_hoja_hallazgo(encabezado, datos, nombre_entidad, vigencia, fecha_actual)
    elif numero_formato == 6:
        return _generar_formato_materialidad(encabezado, datos, nombre_entidad, vigencia, fecha_actual)
    elif numero_formato == 7:
        return _generar_formato_muestreo(encabezado, datos, nombre_entidad, vigencia, fecha_actual)
    elif numero_formato == 23:
        return _generar_plan_mejoramiento(encabezado, datos, nombre_entidad, vigencia, fecha_actual)
    else:
        return _generar_formato_generico(encabezado, numero_formato, datos, nombre_entidad, vigencia, fecha_actual)


def _generar_hoja_hallazgo(
    encabezado: str,
    datos: dict[str, Any],
    entidad: str,
    vigencia: str,
    fecha: str,
) -> str:
    """Genera Formato 11 — Hoja de Hallazgo con 5 elementos."""
    return f"""{encabezado}
FORMATO F11 — HOJA DE HALLAZGO

Entidad auditada: {entidad}
Vigencia auditada: {vigencia}
Fecha de elaboración: {fecha}
Hallazgo No.: {datos.get('numero_hallazgo', '[PENDIENTE]')}

--- TÍTULO DEL HALLAZGO ---
{datos.get('titulo_hallazgo', '[PENDIENTE — Describa brevemente el hallazgo]')}

--- 1. CONDICIÓN (Lo que se encontró) ---
{datos.get('condicion', '[PENDIENTE — Describa la situación actual observada con base en la evidencia recopilada]')}

--- 2. CRITERIO (Norma o estándar aplicable) ---
{datos.get('criterio', '[PENDIENTE — Cite la ley, decreto, resolución o estándar contra el cual se compara. Incluya artículo específico]')}

--- 3. CAUSA (Por qué ocurrió) ---
{datos.get('causa', '[PENDIENTE — Identifique las razones que generaron la diferencia entre la condición y el criterio]')}

--- 4. EFECTO (Impacto o consecuencia) ---
{datos.get('efecto', '[PENDIENTE — Describa el impacto real o potencial. Cuantifique en COP cuando sea posible]')}
Cuantía estimada: {datos.get('cuantia', '[PENDIENTE]')}

--- 5. TIPO DE INCIDENCIA ---
[ ] Administrativo
[ ] Administrativo con presunta incidencia fiscal
[ ] Administrativo con presunta incidencia disciplinaria
[ ] Administrativo con presunta incidencia penal
Tipo seleccionado: {datos.get('tipo_incidencia', '[PENDIENTE]')}

--- RECOMENDACIÓN ---
{datos.get('recomendacion', '[PENDIENTE — Proponga la acción correctiva o preventiva]')}

--- EVIDENCIA SOPORTE ---
{datos.get('evidencia_soporte', '[PENDIENTE — Liste los papeles de trabajo y documentos soporte]')}

--- FIRMAS ---
Elaboró: _________________________ Fecha: _________
Revisó:  _________________________ Fecha: _________
Aprobó:  _________________________ Fecha: _________
"""


def _generar_formato_materialidad(
    encabezado: str,
    datos: dict[str, Any],
    entidad: str,
    vigencia: str,
    fecha: str,
) -> str:
    """Genera Formato 6 — Cálculo de Materialidad."""
    return f"""{encabezado}
FORMATO F06 — CÁLCULO DE MATERIALIDAD

Entidad auditada: {entidad}
Vigencia: {vigencia}
Tipo de auditoría: {datos.get('tipo_auditoria', '[PENDIENTE]')}
Fecha: {fecha}

--- BASE DE CÁLCULO ---
Base seleccionada: {datos.get('base_calculo', '[PENDIENTE]')}
Valor de la base: {datos.get('valor_base', '[PENDIENTE]')}
Justificación de la base: {datos.get('justificacion', '[PENDIENTE]')}

--- CÁLCULO ---
Porcentaje aplicado: {datos.get('porcentaje', '[PENDIENTE]')}
Materialidad global: {datos.get('materialidad_global', '[PENDIENTE]')}
Materialidad de ejecución: {datos.get('materialidad_ejecucion', '[PENDIENTE]')}
Umbral de errores insignificantes: {datos.get('umbral_errores_insignificantes', '[PENDIENTE]')}

--- FUNDAMENTACIÓN ---
NIA 320 — Materialidad en planificación y ejecución.
NIA 450 — Evaluación de incorrecciones.

--- FIRMAS ---
Elaboró: _________________________ Fecha: _________
Revisó:  _________________________ Fecha: _________
"""


def _generar_formato_muestreo(
    encabezado: str,
    datos: dict[str, Any],
    entidad: str,
    vigencia: str,
    fecha: str,
) -> str:
    """Genera Formato 7 — Diseño de Muestreo."""
    return f"""{encabezado}
FORMATO F07 — DISEÑO DE MUESTREO

Entidad auditada: {entidad}
Vigencia: {vigencia}
Componente: {datos.get('componente', '[PENDIENTE]')}
Fecha: {fecha}

--- DISEÑO ---
Objetivo de la prueba: {datos.get('objetivo_prueba', '[PENDIENTE]')}
Método de muestreo: {datos.get('metodo_muestreo', '[PENDIENTE]')}
Población (N): {datos.get('poblacion', '[PENDIENTE]')}
Tamaño de muestra (n): {datos.get('tamano_muestra', '[PENDIENTE]')}
Nivel de confianza: {datos.get('nivel_confianza', '[PENDIENTE]')}
Criterio de selección: {datos.get('criterio_seleccion', '[PENDIENTE]')}

--- FIRMAS ---
Elaboró: _________________________ Fecha: _________
Revisó:  _________________________ Fecha: _________
"""


def _generar_plan_mejoramiento(
    encabezado: str,
    datos: dict[str, Any],
    entidad: str,
    vigencia: str,
    fecha: str,
) -> str:
    """Genera Formato 23 — Plan de Mejoramiento."""
    return f"""{encabezado}
FORMATO F23 — PLAN DE MEJORAMIENTO

Entidad: {entidad}
Vigencia de la auditoría: {datos.get('vigencia_auditoria', vigencia)}
Fecha de suscripción: {fecha}

--- ACCIONES CORRECTIVAS ---
No. | Hallazgo | Acción Correctiva | Responsable | Fecha Inicio | Fecha Fin | Indicador | Meta
----|----------|-------------------|-------------|-------------|-----------|-----------|-----
{datos.get('tabla_acciones', '[PENDIENTE — Diligencie la tabla con las acciones correctivas por hallazgo]')}

--- FIRMAS ---
Representante Legal Entidad: _________________________ Fecha: _________
Director Técnico CGR:        _________________________ Fecha: _________
"""


def _generar_formato_generico(
    encabezado: str,
    numero: int,
    datos: dict[str, Any],
    entidad: str,
    vigencia: str,
    fecha: str,
) -> str:
    """Genera un formato genérico para números no implementados específicamente."""
    info_formato: dict[str, Any] | None = CATALOGO_FORMATOS.get(numero)
    nombre: str = info_formato["nombre"] if info_formato else f"Formato {numero}"

    campos_str: str = ""
    if info_formato and "campos" in info_formato:
        for campo in info_formato["campos"]:
            valor: str = datos.get(campo, "[PENDIENTE]")
            campo_legible: str = campo.replace("_", " ").title()
            campos_str += f"{campo_legible}: {valor}\n"

    return f"""{encabezado}
FORMATO F{numero:02d} — {nombre.upper()}

Entidad: {entidad}
Vigencia: {vigencia}
Fecha: {fecha}

--- CONTENIDO ---
{campos_str if campos_str else '[PENDIENTE — Complete los campos requeridos del formato]'}

--- FIRMAS ---
Elaboró: _________________________ Fecha: _________
Revisó:  _________________________ Fecha: _________
"""


@tool
def generar_formato(
    numero_formato: int,
    datos: Optional[dict[str, Any]] = None,
) -> str:
    """Genera un formato CGR oficial del proceso auditor (formatos 1 a 30).

    Genera borradores de los formatos oficiales utilizados en el proceso
    auditor de la Contraloría General de la República de Colombia.
    Los campos con información disponible se pre-llenan; los faltantes
    se marcan como [PENDIENTE].

    Args:
        numero_formato: Número del formato CGR (1-30).
        datos: Diccionario con los datos para pre-llenar el formato.
               Las claves dependen del formato solicitado.

    Returns:
        Texto del formato generado con campos pre-llenados.
    """
    logger.info("Generando formato CGR F%02d", numero_formato)

    if numero_formato < 1 or numero_formato > 30:
        return (
            f"Formato {numero_formato} no válido. "
            f"Los formatos CGR van del 1 al 30."
        )

    if datos is None:
        datos = {}

    formato_generado: str = _generar_plantilla(numero_formato, datos)

    nota_final: str = (
        "\n\n⚠️ Este formato es un BORRADOR generado por IA. "
        "Debe ser revisado, completado y aprobado por el equipo auditor "
        "antes de su uso oficial. Verifique que cumple con las guías "
        "de auditoría vigentes de la CGR."
    )

    return formato_generado + nota_final
