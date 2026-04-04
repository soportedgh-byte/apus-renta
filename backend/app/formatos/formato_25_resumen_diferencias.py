"""
CecilIA v2 — Formato F25: Resumen de Diferencias de Auditoria
Sprint: 4 | Fase: Ejecucion
"""

from __future__ import annotations
from typing import Any
from app.formatos.formato_base import FormatoBaseCGR


class FormatoF25ResumenDiferencias(FormatoBaseCGR):
    """F25 — Consolidado de Diferencias e Incorrecciones de Auditoria."""

    def __init__(self, datos: dict[str, Any] | None = None) -> None:
        super().__init__(
            numero_formato=25,
            nombre_formato="Resumen de Diferencias de Auditoria",
            datos=datos,
        )

    def construir(self) -> None:
        # Niveles de materialidad
        self.agregar_titulo_seccion("1. Niveles de Materialidad Establecidos")
        self.crear_tabla_clave_valor([
            ("Materialidad global (COP)",
             self.datos.get("materialidad_global", "[COMPLETAR]")),
            ("Materialidad de ejecucion (COP)",
             self.datos.get("materialidad_ejecucion", "[COMPLETAR]")),
            ("Umbral de errores insignificantes (COP)",
             self.datos.get("umbral_insignificante", "[COMPLETAR]")),
        ])

        # Incorrecciones identificadas
        self.agregar_titulo_seccion("2. Incorrecciones Identificadas")
        incorrecciones = self.datos.get("incorrecciones", [])
        if not incorrecciones:
            incorrecciones = [
                {"no": "1", "componente": "[COMPLETAR]",
                 "descripcion": "[COMPLETAR — Describa la incorreccion]",
                 "tipo": "[COMPLETAR — Factual/De juicio/Proyectada]",
                 "monto": "[COMPLETAR]", "efecto_activos": "[COMPLETAR]",
                 "efecto_resultados": "[COMPLETAR]",
                 "corregida": "[COMPLETAR — Si/No]"},
                {"no": "2", "componente": "[COMPLETAR]",
                 "descripcion": "[COMPLETAR]", "tipo": "[COMPLETAR]",
                 "monto": "[COMPLETAR]", "efecto_activos": "[COMPLETAR]",
                 "efecto_resultados": "[COMPLETAR]",
                 "corregida": "[COMPLETAR]"},
            ]

        filas_inc = [[
            inc.get("no", "[COMPLETAR]"),
            inc.get("componente", "[COMPLETAR]"),
            inc.get("descripcion", "[COMPLETAR]"),
            inc.get("tipo", "[COMPLETAR]"),
            inc.get("monto", "[COMPLETAR]"),
            inc.get("efecto_activos", "[COMPLETAR]"),
            inc.get("efecto_resultados", "[COMPLETAR]"),
            inc.get("corregida", "[COMPLETAR]"),
        ] for inc in incorrecciones]

        self.crear_tabla(
            encabezados=["No.", "Componente", "Descripcion", "Tipo",
                         "Monto (COP)", "Efecto Activos", "Efecto Resultados",
                         "Corregida"],
            filas=filas_inc,
        )

        # Resumen acumulado
        self.agregar_titulo_seccion("3. Resumen Acumulado de Incorrecciones")
        self.crear_tabla(
            encabezados=["Concepto", "Monto (COP)"],
            filas=[
                ["Total incorrecciones corregidas",
                 self.datos.get("total_corregidas", "[COMPLETAR]")],
                ["Total incorrecciones no corregidas",
                 self.datos.get("total_no_corregidas", "[COMPLETAR]")],
                ["Total incorrecciones proyectadas",
                 self.datos.get("total_proyectadas", "[COMPLETAR]")],
                ["TOTAL ACUMULADO",
                 self.datos.get("total_acumulado", "[COMPLETAR]")],
                ["Materialidad global",
                 self.datos.get("materialidad_global", "[COMPLETAR]")],
                ["Diferencia (Materialidad - Acumulado)",
                 self.datos.get("diferencia_materialidad", "[COMPLETAR]")],
            ],
            anchos=[8.0, 6.0],
        )

        # Evaluacion NIA 450
        self.agregar_titulo_seccion("4. Evaluacion conforme NIA 450")
        self.agregar_parrafo_justificado(
            "El auditor debe evaluar si las incorrecciones no corregidas son "
            "materiales, individualmente o de forma agregada, considerando "
            "el tamano y la naturaleza de las incorrecciones y las circunstancias "
            "particulares en las que se hayan producido."
        )
        self.crear_tabla_clave_valor([
            ("Las incorrecciones no corregidas superan la materialidad?",
             self.datos.get("supera_materialidad", "[COMPLETAR — Si/No]")),
            ("Se requiere modificacion del dictamen?",
             self.datos.get("modificar_dictamen", "[COMPLETAR — Si/No]")),
            ("Tipo de opinion propuesta",
             self.datos.get("tipo_opinion",
                           "[COMPLETAR — Limpia/Con salvedades/Adversa/Abstencion]")),
        ])

        # Conclusion
        self.agregar_titulo_seccion("5. Conclusion")
        self.agregar_campo_completar(
            "Concluya sobre el efecto acumulado de las incorrecciones "
            "no corregidas en los estados financieros y su impacto "
            "en la opinion de auditoria"
        )

        self.agregar_seccion_firmas()
