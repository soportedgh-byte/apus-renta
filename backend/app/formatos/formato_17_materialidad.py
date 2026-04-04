"""
CecilIA v2 — Formato F17: Calculo de Materialidad
Sprint: 4 | Fase: Planeacion
"""

from __future__ import annotations
from typing import Any
from app.formatos.formato_base import FormatoBaseCGR


class FormatoF17Materialidad(FormatoBaseCGR):
    """F17 — Calculo de Materialidad y Error Tolerable.

    Incluye base de calculo, materialidad global, de ejecucion,
    umbral de errores insignificantes y fundamentacion NIA 320/450.
    """

    def __init__(self, datos: dict[str, Any] | None = None) -> None:
        super().__init__(
            numero_formato=17,
            nombre_formato="Calculo de Materialidad",
            datos=datos,
        )

    def construir(self) -> None:
        # Marco normativo
        self.agregar_titulo_seccion("1. Marco Normativo")
        self.agregar_parrafo_justificado(
            "El calculo de materialidad se fundamenta en la NIA 320 'Importancia Relativa "
            "o Materialidad en la Planificacion y Ejecucion de la Auditoria' y la NIA 450 "
            "'Evaluacion de las Incorrecciones Identificadas durante la Realizacion de la "
            "Auditoria', adoptadas por la Contraloria General de la Republica."
        )
        self.agregar_parrafo_justificado(
            "La materialidad es el importe o importes determinados por el auditor, por debajo "
            "del nivel de materialidad establecido para los estados financieros en su conjunto, "
            "al objeto de reducir a un nivel adecuadamente bajo la probabilidad de que la suma "
            "de las incorrecciones no corregidas y no detectadas supere la materialidad."
        )

        # Seleccion de la base de calculo
        self.agregar_titulo_seccion("2. Seleccion de la Base de Calculo")
        bases_calculo = self.datos.get("bases_calculo", [])
        if not bases_calculo:
            bases_calculo = [
                {"base": "Total Activos", "valor": self.datos.get("total_activos", "[COMPLETAR]"),
                 "porcentaje": "1% - 2%", "seleccionada": "[COMPLETAR — Si/No]"},
                {"base": "Total Ingresos", "valor": self.datos.get("total_ingresos", "[COMPLETAR]"),
                 "porcentaje": "0.5% - 1%", "seleccionada": "[COMPLETAR]"},
                {"base": "Total Gastos", "valor": self.datos.get("total_gastos", "[COMPLETAR]"),
                 "porcentaje": "0.5% - 1%", "seleccionada": "[COMPLETAR]"},
                {"base": "Patrimonio", "valor": self.datos.get("patrimonio", "[COMPLETAR]"),
                 "porcentaje": "2% - 5%", "seleccionada": "[COMPLETAR]"},
                {"base": "Presupuesto aprobado", "valor": self.datos.get("presupuesto", "[COMPLETAR]"),
                 "porcentaje": "0.5% - 2%", "seleccionada": "[COMPLETAR]"},
            ]

        filas_bases = []
        for b in bases_calculo:
            filas_bases.append([
                b.get("base", "[COMPLETAR]"),
                b.get("valor", "[COMPLETAR]"),
                b.get("porcentaje", "[COMPLETAR]"),
                b.get("seleccionada", "[COMPLETAR]"),
            ])

        self.crear_tabla(
            encabezados=["Base de Calculo", "Valor (COP)", "Rango %", "Seleccionada"],
            filas=filas_bases,
            anchos=[4.5, 4.5, 3.0, 3.0],
        )

        self.agregar_subtitulo("Justificacion de la base seleccionada")
        self.agregar_campo_completar(
            "Justifique la seleccion de la base de calculo considerando: "
            "naturaleza de la entidad, usuarios de los estados financieros, "
            "volatilidad de la base, y comparabilidad con vigencias anteriores"
        )

        # Calculo de materialidad
        self.agregar_titulo_seccion("3. Calculo de Materialidad")
        self.crear_tabla_clave_valor([
            ("Base seleccionada",
             self.datos.get("base_seleccionada", "[COMPLETAR]")),
            ("Valor de la base (COP)",
             self.datos.get("valor_base", "[COMPLETAR]")),
            ("Porcentaje aplicado",
             self.datos.get("porcentaje_aplicado", "[COMPLETAR]")),
            ("MATERIALIDAD GLOBAL (COP)",
             self.datos.get("materialidad_global", "[COMPLETAR]")),
        ])

        # Materialidad de ejecucion
        self.agregar_titulo_seccion("4. Materialidad de Ejecucion")
        self.agregar_parrafo_justificado(
            "La materialidad de ejecucion se establece para reducir a un nivel "
            "adecuadamente bajo la probabilidad de que el conjunto de incorrecciones "
            "no corregidas y no detectadas supere la materialidad. Se determina entre "
            "el 50% y 75% de la materialidad global."
        )
        self.crear_tabla_clave_valor([
            ("Materialidad global (COP)",
             self.datos.get("materialidad_global", "[COMPLETAR]")),
            ("Porcentaje para ejecucion",
             self.datos.get("pct_ejecucion", "[COMPLETAR — 50% a 75%]")),
            ("MATERIALIDAD DE EJECUCION (COP)",
             self.datos.get("materialidad_ejecucion", "[COMPLETAR]")),
            ("Justificacion del porcentaje",
             self.datos.get("justificacion_pct", "[COMPLETAR]")),
        ])

        # Umbral de errores insignificantes
        self.agregar_titulo_seccion("5. Umbral de Errores Claramente Insignificantes")
        self.agregar_parrafo_justificado(
            "El umbral de errores claramente insignificantes es el importe por debajo "
            "del cual las incorrecciones acumuladas no necesitan ser consideradas. "
            "Se establece generalmente entre el 3% y 5% de la materialidad global."
        )
        self.crear_tabla_clave_valor([
            ("Materialidad global (COP)",
             self.datos.get("materialidad_global", "[COMPLETAR]")),
            ("Porcentaje para umbral",
             self.datos.get("pct_umbral", "[COMPLETAR — 3% a 5%]")),
            ("UMBRAL INSIGNIFICANTE (COP)",
             self.datos.get("umbral_insignificante", "[COMPLETAR]")),
        ])

        # Resumen
        self.agregar_titulo_seccion("6. Resumen de Niveles de Materialidad")
        self.crear_tabla(
            encabezados=["Concepto", "Valor (COP)", "% de la Base"],
            filas=[
                ["Materialidad global",
                 self.datos.get("materialidad_global", "[COMPLETAR]"),
                 self.datos.get("porcentaje_aplicado", "[COMPLETAR]")],
                ["Materialidad de ejecucion",
                 self.datos.get("materialidad_ejecucion", "[COMPLETAR]"),
                 self.datos.get("pct_ejecucion", "[COMPLETAR]")],
                ["Umbral de errores insignificantes",
                 self.datos.get("umbral_insignificante", "[COMPLETAR]"),
                 self.datos.get("pct_umbral", "[COMPLETAR]")],
            ],
            anchos=[6.0, 5.0, 4.0],
        )

        # Factores de ajuste
        self.agregar_titulo_seccion("7. Factores que Pueden Modificar la Materialidad")
        self.agregar_campo_completar(
            "Identifique factores que pueden requerir revision de la materialidad "
            "durante la ejecucion: hallazgos nuevos, cambios en la entidad, "
            "errores acumulados, cambios normativos"
        )

        self.agregar_seccion_firmas()
