"""
CecilIA v2 — Registro de Formatos CGR Implementados
Sprint: 4

Mapea numeros de formato a sus clases generadoras.
Los formatos no implementados usan un generador generico.
"""

from __future__ import annotations

from typing import Any, Type

from app.formatos.formato_base import FormatoBaseCGR

# ── Catalogo completo de formatos CGR (1-30) ────────────────────────────────

CATALOGO_FORMATOS: dict[int, dict[str, str]] = {
    1:  {"nombre": "Declaracion de Independencia", "fase": "pre-planeacion"},
    2:  {"nombre": "Comunicacion de Inicio de Auditoria", "fase": "pre-planeacion"},
    3:  {"nombre": "Datos Generales de la Entidad", "fase": "pre-planeacion"},
    4:  {"nombre": "Carta de Representacion", "fase": "pre-planeacion"},
    5:  {"nombre": "Analisis Financiero", "fase": "pre-planeacion"},
    6:  {"nombre": "Solicitud de Informacion", "fase": "pre-planeacion"},
    7:  {"nombre": "Analisis Presupuestal", "fase": "pre-planeacion"},
    8:  {"nombre": "Conocimiento de la Entidad", "fase": "pre-planeacion"},
    9:  {"nombre": "Identificacion de Procesos", "fase": "pre-planeacion"},
    10: {"nombre": "Memorando de Pre-planeacion", "fase": "pre-planeacion"},
    11: {"nombre": "Memorando de Planeacion", "fase": "planeacion"},
    12: {"nombre": "Evaluacion de Control Interno (COSO)", "fase": "planeacion"},
    13: {"nombre": "Evaluacion del Riesgo de Fraude", "fase": "planeacion"},
    14: {"nombre": "Matriz de Riesgos de Auditoria", "fase": "planeacion"},
    15: {"nombre": "Determinacion de la Muestra", "fase": "planeacion"},
    16: {"nombre": "Procedimientos Analiticos", "fase": "planeacion"},
    17: {"nombre": "Calculo de Materialidad", "fase": "planeacion"},
    18: {"nombre": "Plan de Trabajo de Auditoria", "fase": "planeacion"},
    19: {"nombre": "Comunicaciones con la Direccion", "fase": "planeacion"},
    20: {"nombre": "Programa de Auditoria", "fase": "planeacion"},
    21: {"nombre": "Cedula de Hallazgo", "fase": "ejecucion"},
    22: {"nombre": "Pruebas de Detalle", "fase": "ejecucion"},
    23: {"nombre": "Pruebas de Cumplimiento", "fase": "ejecucion"},
    24: {"nombre": "Cedula Sumaria", "fase": "ejecucion"},
    25: {"nombre": "Resumen de Diferencias de Auditoria", "fase": "ejecucion"},
    26: {"nombre": "Evaluacion de Estimaciones", "fase": "ejecucion"},
    27: {"nombre": "Hechos Posteriores", "fase": "ejecucion"},
    28: {"nombre": "Empresa en Funcionamiento", "fase": "ejecucion"},
    29: {"nombre": "Informe Preliminar", "fase": "ejecucion"},
    30: {"nombre": "Informe Final de Auditoria", "fase": "ejecucion"},
}


def _importar_formatos() -> dict[int, Type[FormatoBaseCGR]]:
    """Importa las clases de formatos implementados."""
    from app.formatos.formato_01_independencia import FormatoF01Independencia
    from app.formatos.formato_03_datos_generales import FormatoF03DatosGenerales
    from app.formatos.formato_05_analisis_financiero import FormatoF05AnalisisFinanciero
    from app.formatos.formato_07_presupuestal import FormatoF07Presupuestal
    from app.formatos.formato_12_control_interno import FormatoF12ControlInterno
    from app.formatos.formato_14_matriz_riesgos import FormatoF14MatrizRiesgos
    from app.formatos.formato_17_materialidad import FormatoF17Materialidad
    from app.formatos.formato_18_plan_trabajo import FormatoF18PlanTrabajo
    from app.formatos.formato_20_programa_auditoria import FormatoF20ProgramaAuditoria
    from app.formatos.formato_22_pruebas_detalle import FormatoF22PruebasDetalle
    from app.formatos.formato_25_resumen_diferencias import FormatoF25ResumenDiferencias

    return {
        1: FormatoF01Independencia,
        3: FormatoF03DatosGenerales,
        5: FormatoF05AnalisisFinanciero,
        7: FormatoF07Presupuestal,
        12: FormatoF12ControlInterno,
        14: FormatoF14MatrizRiesgos,
        17: FormatoF17Materialidad,
        18: FormatoF18PlanTrabajo,
        20: FormatoF20ProgramaAuditoria,
        22: FormatoF22PruebasDetalle,
        25: FormatoF25ResumenDiferencias,
    }


# Formatos con implementacion DOCX especifica
FORMATOS_IMPLEMENTADOS: set[int] = {1, 3, 5, 7, 12, 14, 17, 18, 20, 22, 25}


class FormatoGenericoCGR(FormatoBaseCGR):
    """Generador generico para formatos no implementados."""

    def construir(self) -> None:
        self.agregar_titulo_seccion("Contenido del Formato")
        self.agregar_parrafo_justificado(
            f"Este formato (F{self.numero_formato:02d} — {self.nombre_formato}) "
            f"sera implementado en una proxima actualizacion de CecilIA. "
            f"Por el momento, se genera la estructura basica con campos por completar."
        )
        self.agregar_campo_completar(
            "Diligencie el contenido de este formato segun las guias de auditoria de la CGR"
        )
        self.agregar_seccion_firmas()


def obtener_generador(
    numero_formato: int,
    datos: dict[str, Any] | None = None,
) -> FormatoBaseCGR:
    """Obtiene la instancia del generador para un formato dado.

    Args:
        numero_formato: Numero del formato CGR (1-30).
        datos: Diccionario con datos para pre-llenar.

    Returns:
        Instancia del generador correspondiente.

    Raises:
        ValueError: Si el numero de formato no existe en el catalogo.
    """
    if numero_formato not in CATALOGO_FORMATOS:
        raise ValueError(
            f"Formato {numero_formato} no existe. Rango valido: 1-30."
        )

    info = CATALOGO_FORMATOS[numero_formato]

    if numero_formato in FORMATOS_IMPLEMENTADOS:
        mapa = _importar_formatos()
        clase = mapa[numero_formato]
        return clase(datos=datos)

    return FormatoGenericoCGR(
        numero_formato=numero_formato,
        nombre_formato=info["nombre"],
        datos=datos,
    )
