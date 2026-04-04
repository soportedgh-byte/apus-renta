"""
CecilIA v2 — Formato F05: Analisis Financiero
Sprint: 4 | Fase: Pre-planeacion
"""

from __future__ import annotations
from typing import Any
from app.formatos.formato_base import FormatoBaseCGR


class FormatoF05AnalisisFinanciero(FormatoBaseCGR):
    """F05 — Analisis Financiero con balance general, indicadores y graficos."""

    def __init__(self, datos: dict[str, Any] | None = None) -> None:
        super().__init__(
            numero_formato=5,
            nombre_formato="Analisis Financiero",
            datos=datos,
        )

    def construir(self) -> None:
        # Balance general
        self.agregar_titulo_seccion("1. Balance General Resumido")
        self.crear_tabla(
            encabezados=["Cuenta", "Vigencia Actual (COP)", "Vigencia Anterior (COP)", "Variacion %"],
            filas=[
                ["ACTIVOS", "", "", ""],
                ["  Activos corrientes",
                 self.datos.get("activos_corrientes", "[COMPLETAR]"),
                 self.datos.get("activos_corrientes_ant", "[COMPLETAR]"),
                 self.datos.get("var_activos_corrientes", "[COMPLETAR]")],
                ["  Activos no corrientes",
                 self.datos.get("activos_no_corrientes", "[COMPLETAR]"),
                 self.datos.get("activos_no_corrientes_ant", "[COMPLETAR]"),
                 self.datos.get("var_activos_no_corrientes", "[COMPLETAR]")],
                ["  Total Activos",
                 self.datos.get("total_activos", "[COMPLETAR]"),
                 self.datos.get("total_activos_ant", "[COMPLETAR]"),
                 self.datos.get("var_total_activos", "[COMPLETAR]")],
                ["PASIVOS", "", "", ""],
                ["  Pasivos corrientes",
                 self.datos.get("pasivos_corrientes", "[COMPLETAR]"),
                 self.datos.get("pasivos_corrientes_ant", "[COMPLETAR]"),
                 self.datos.get("var_pasivos_corrientes", "[COMPLETAR]")],
                ["  Pasivos no corrientes",
                 self.datos.get("pasivos_no_corrientes", "[COMPLETAR]"),
                 self.datos.get("pasivos_no_corrientes_ant", "[COMPLETAR]"),
                 self.datos.get("var_pasivos_no_corrientes", "[COMPLETAR]")],
                ["  Total Pasivos",
                 self.datos.get("total_pasivos", "[COMPLETAR]"),
                 self.datos.get("total_pasivos_ant", "[COMPLETAR]"),
                 self.datos.get("var_total_pasivos", "[COMPLETAR]")],
                ["PATRIMONIO",
                 self.datos.get("patrimonio", "[COMPLETAR]"),
                 self.datos.get("patrimonio_ant", "[COMPLETAR]"),
                 self.datos.get("var_patrimonio", "[COMPLETAR]")],
            ],
            anchos=[5.0, 4.0, 4.0, 2.5],
        )

        # Estado de resultados
        self.agregar_titulo_seccion("2. Estado de Resultados")
        self.crear_tabla(
            encabezados=["Concepto", "Vigencia Actual (COP)", "Vigencia Anterior (COP)", "Variacion %"],
            filas=[
                ["Ingresos operacionales",
                 self.datos.get("ingresos_operacionales", "[COMPLETAR]"),
                 self.datos.get("ingresos_operacionales_ant", "[COMPLETAR]"),
                 self.datos.get("var_ingresos_op", "[COMPLETAR]")],
                ["Gastos operacionales",
                 self.datos.get("gastos_operacionales", "[COMPLETAR]"),
                 self.datos.get("gastos_operacionales_ant", "[COMPLETAR]"),
                 self.datos.get("var_gastos_op", "[COMPLETAR]")],
                ["Resultado operacional",
                 self.datos.get("resultado_operacional", "[COMPLETAR]"),
                 self.datos.get("resultado_operacional_ant", "[COMPLETAR]"),
                 self.datos.get("var_resultado_op", "[COMPLETAR]")],
                ["Resultado del ejercicio",
                 self.datos.get("resultado_ejercicio", "[COMPLETAR]"),
                 self.datos.get("resultado_ejercicio_ant", "[COMPLETAR]"),
                 self.datos.get("var_resultado_ej", "[COMPLETAR]")],
            ],
            anchos=[5.0, 4.0, 4.0, 2.5],
        )

        # Indicadores financieros
        self.agregar_titulo_seccion("3. Indicadores Financieros")
        self.crear_tabla(
            encabezados=["Indicador", "Formula", "Resultado", "Interpretacion"],
            filas=[
                ["Razon corriente", "Activos corrientes / Pasivos corrientes",
                 self.datos.get("razon_corriente", "[COMPLETAR]"),
                 self.datos.get("interp_razon_corriente", "[COMPLETAR]")],
                ["Endeudamiento", "Total Pasivos / Total Activos",
                 self.datos.get("endeudamiento", "[COMPLETAR]"),
                 self.datos.get("interp_endeudamiento", "[COMPLETAR]")],
                ["Rentabilidad sobre activos", "Resultado / Total Activos",
                 self.datos.get("roa", "[COMPLETAR]"),
                 self.datos.get("interp_roa", "[COMPLETAR]")],
                ["Solvencia", "Patrimonio / Total Activos",
                 self.datos.get("solvencia", "[COMPLETAR]"),
                 self.datos.get("interp_solvencia", "[COMPLETAR]")],
                ["Capital de trabajo", "Activo corriente - Pasivo corriente",
                 self.datos.get("capital_trabajo", "[COMPLETAR]"),
                 self.datos.get("interp_capital_trabajo", "[COMPLETAR]")],
            ],
            anchos=[3.5, 5.0, 3.0, 5.0],
        )

        # Analisis
        self.agregar_titulo_seccion("4. Analisis y Conclusiones")
        self.agregar_campo_completar(
            "Incluya el analisis de la situacion financiera de la entidad, "
            "tendencias identificadas, riesgos financieros y aspectos relevantes "
            "para la planeacion de la auditoria"
        )

        self.agregar_seccion_firmas()
