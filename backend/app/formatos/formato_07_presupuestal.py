"""
CecilIA v2 — Formato F07: Analisis Presupuestal
Sprint: 4 | Fase: Pre-planeacion
"""

from __future__ import annotations
from typing import Any
from app.formatos.formato_base import FormatoBaseCGR


class FormatoF07Presupuestal(FormatoBaseCGR):
    """F07 — Analisis de Ejecucion Presupuestal con tabla de ejecucion."""

    def __init__(self, datos: dict[str, Any] | None = None) -> None:
        super().__init__(
            numero_formato=7,
            nombre_formato="Analisis Presupuestal",
            datos=datos,
        )

    def construir(self) -> None:
        # Presupuesto de ingresos
        self.agregar_titulo_seccion("1. Presupuesto de Ingresos")
        rubros_ingresos = self.datos.get("rubros_ingresos", [])
        if not rubros_ingresos:
            rubros_ingresos = [
                {"rubro": "Ingresos corrientes", "apropiacion_inicial": "[COMPLETAR]",
                 "apropiacion_definitiva": "[COMPLETAR]", "recaudo": "[COMPLETAR]",
                 "porcentaje": "[COMPLETAR]"},
                {"rubro": "Recursos de capital", "apropiacion_inicial": "[COMPLETAR]",
                 "apropiacion_definitiva": "[COMPLETAR]", "recaudo": "[COMPLETAR]",
                 "porcentaje": "[COMPLETAR]"},
                {"rubro": "Transferencias", "apropiacion_inicial": "[COMPLETAR]",
                 "apropiacion_definitiva": "[COMPLETAR]", "recaudo": "[COMPLETAR]",
                 "porcentaje": "[COMPLETAR]"},
            ]

        filas_ing = []
        for r in rubros_ingresos:
            filas_ing.append([
                r.get("rubro", "[COMPLETAR]"),
                r.get("apropiacion_inicial", "[COMPLETAR]"),
                r.get("apropiacion_definitiva", "[COMPLETAR]"),
                r.get("recaudo", "[COMPLETAR]"),
                r.get("porcentaje", "[COMPLETAR]"),
            ])
        filas_ing.append([
            "TOTAL INGRESOS",
            self.datos.get("total_ingresos_inicial", "[COMPLETAR]"),
            self.datos.get("total_ingresos_definitiva", "[COMPLETAR]"),
            self.datos.get("total_recaudo", "[COMPLETAR]"),
            self.datos.get("pct_total_recaudo", "[COMPLETAR]"),
        ])

        self.crear_tabla(
            encabezados=["Rubro", "Aprop. Inicial (COP)", "Aprop. Definitiva (COP)",
                         "Recaudo (COP)", "% Ejecucion"],
            filas=filas_ing,
            anchos=[4.0, 3.5, 3.5, 3.5, 2.5],
        )

        # Presupuesto de gastos
        self.agregar_titulo_seccion("2. Presupuesto de Gastos")
        rubros_gastos = self.datos.get("rubros_gastos", [])
        if not rubros_gastos:
            rubros_gastos = [
                {"rubro": "Gastos de funcionamiento", "apropiacion_inicial": "[COMPLETAR]",
                 "apropiacion_definitiva": "[COMPLETAR]", "compromisos": "[COMPLETAR]",
                 "obligaciones": "[COMPLETAR]", "pagos": "[COMPLETAR]", "porcentaje": "[COMPLETAR]"},
                {"rubro": "Gastos de inversion", "apropiacion_inicial": "[COMPLETAR]",
                 "apropiacion_definitiva": "[COMPLETAR]", "compromisos": "[COMPLETAR]",
                 "obligaciones": "[COMPLETAR]", "pagos": "[COMPLETAR]", "porcentaje": "[COMPLETAR]"},
                {"rubro": "Servicio de la deuda", "apropiacion_inicial": "[COMPLETAR]",
                 "apropiacion_definitiva": "[COMPLETAR]", "compromisos": "[COMPLETAR]",
                 "obligaciones": "[COMPLETAR]", "pagos": "[COMPLETAR]", "porcentaje": "[COMPLETAR]"},
            ]

        filas_gas = []
        for r in rubros_gastos:
            filas_gas.append([
                r.get("rubro", "[COMPLETAR]"),
                r.get("apropiacion_definitiva", "[COMPLETAR]"),
                r.get("compromisos", "[COMPLETAR]"),
                r.get("obligaciones", "[COMPLETAR]"),
                r.get("pagos", "[COMPLETAR]"),
                r.get("porcentaje", "[COMPLETAR]"),
            ])
        filas_gas.append([
            "TOTAL GASTOS",
            self.datos.get("total_gastos_definitiva", "[COMPLETAR]"),
            self.datos.get("total_compromisos", "[COMPLETAR]"),
            self.datos.get("total_obligaciones", "[COMPLETAR]"),
            self.datos.get("total_pagos", "[COMPLETAR]"),
            self.datos.get("pct_total_gastos", "[COMPLETAR]"),
        ])

        self.crear_tabla(
            encabezados=["Rubro", "Aprop. Definitiva", "Compromisos",
                         "Obligaciones", "Pagos", "% Ejec."],
            filas=filas_gas,
            anchos=[3.5, 3.0, 2.5, 2.5, 2.5, 2.0],
        )

        # Analisis de ejecucion
        self.agregar_titulo_seccion("3. Analisis de Ejecucion Presupuestal")
        self.agregar_campo_completar(
            "Analice el comportamiento de la ejecucion presupuestal: "
            "nivel de recaudo vs apropiacion, nivel de compromisos, "
            "rezago presupuestal, vigencias expiradas, y riesgos identificados"
        )

        # Reservas y cuentas por pagar
        self.agregar_titulo_seccion("4. Reservas Presupuestales y Cuentas por Pagar")
        self.crear_tabla(
            encabezados=["Concepto", "Valor (COP)", "% del Total", "Observaciones"],
            filas=[
                ["Reservas presupuestales",
                 self.datos.get("reservas", "[COMPLETAR]"),
                 self.datos.get("pct_reservas", "[COMPLETAR]"),
                 self.datos.get("obs_reservas", "[COMPLETAR]")],
                ["Cuentas por pagar",
                 self.datos.get("cxp", "[COMPLETAR]"),
                 self.datos.get("pct_cxp", "[COMPLETAR]"),
                 self.datos.get("obs_cxp", "[COMPLETAR]")],
                ["Vigencias expiradas",
                 self.datos.get("vig_expiradas", "[COMPLETAR]"),
                 self.datos.get("pct_vig_exp", "[COMPLETAR]"),
                 self.datos.get("obs_vig_exp", "[COMPLETAR]")],
            ],
            anchos=[4.0, 3.5, 2.5, 6.0],
        )

        self.agregar_seccion_firmas()
