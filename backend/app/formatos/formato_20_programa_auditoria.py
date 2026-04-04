"""
CecilIA v2 — Formato F20: Programa de Auditoria
Sprint: 4 | Fase: Planeacion
"""

from __future__ import annotations
from typing import Any
from app.formatos.formato_base import FormatoBaseCGR


class FormatoF20ProgramaAuditoria(FormatoBaseCGR):
    """F20 — Programa de Auditoria con procedimientos por componente."""

    def __init__(self, datos: dict[str, Any] | None = None) -> None:
        super().__init__(
            numero_formato=20,
            nombre_formato="Programa de Auditoria",
            datos=datos,
        )

    def construir(self) -> None:
        # Objetivo
        self.agregar_titulo_seccion("1. Objetivo General")
        self.agregar_campo_completar("Defina el objetivo general del programa de auditoria")

        self.agregar_titulo_seccion("2. Objetivos Especificos")
        self.agregar_campo_completar("Liste los objetivos especificos de la auditoria")

        # Componentes y procedimientos
        self.agregar_titulo_seccion("3. Procedimientos de Auditoria por Componente")

        componentes = self.datos.get("componentes", [])
        if not componentes:
            componentes = [
                {
                    "nombre": "[COMPLETAR — Nombre del componente]",
                    "objetivo": "[COMPLETAR]",
                    "procedimientos": [
                        {"tipo": "Sustantivo", "descripcion": "[COMPLETAR]",
                         "muestra": "[COMPLETAR]", "responsable": "[COMPLETAR]",
                         "ref_pt": "[COMPLETAR]", "resultado": "[COMPLETAR]"},
                        {"tipo": "Cumplimiento", "descripcion": "[COMPLETAR]",
                         "muestra": "[COMPLETAR]", "responsable": "[COMPLETAR]",
                         "ref_pt": "[COMPLETAR]", "resultado": "[COMPLETAR]"},
                    ],
                },
            ]

        for idx, comp in enumerate(componentes, 1):
            self.agregar_subtitulo(f"3.{idx}. Componente: {comp.get('nombre', '[COMPLETAR]')}")
            self.agregar_parrafo(f"Objetivo: {comp.get('objetivo', '[COMPLETAR]')}")

            procedimientos = comp.get("procedimientos", [])
            filas_proc = [[
                p.get("tipo", "[COMPLETAR]"),
                p.get("descripcion", "[COMPLETAR]"),
                p.get("muestra", "[COMPLETAR]"),
                p.get("responsable", "[COMPLETAR]"),
                p.get("ref_pt", "[COMPLETAR]"),
                p.get("resultado", "[COMPLETAR]"),
            ] for p in procedimientos]

            if not filas_proc:
                filas_proc = [["[COMPLETAR]"] * 6]

            self.crear_tabla(
                encabezados=["Tipo Prueba", "Descripcion del Procedimiento",
                             "Muestra", "Responsable", "Ref. P/T", "Resultado"],
                filas=filas_proc,
            )

        # Procedimientos adicionales
        self.agregar_titulo_seccion("4. Procedimientos Analiticos")
        self.agregar_campo_completar(
            "Describa los procedimientos analiticos a realizar: "
            "analisis de tendencias, ratios, comparaciones"
        )

        self.agregar_titulo_seccion("5. Procedimientos sobre Estimaciones Contables")
        self.agregar_campo_completar(
            "Describa los procedimientos para evaluar las estimaciones "
            "contables significativas de la entidad"
        )

        self.agregar_seccion_firmas()
