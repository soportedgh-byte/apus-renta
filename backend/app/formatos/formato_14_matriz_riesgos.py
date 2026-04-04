"""
CecilIA v2 — Formato F14: Matriz de Riesgos de Auditoria
Sprint: 4 | Fase: Planeacion
"""

from __future__ import annotations
from typing import Any
from app.formatos.formato_base import FormatoBaseCGR


class FormatoF14MatrizRiesgos(FormatoBaseCGR):
    """F14 — Matriz de Riesgos de Auditoria completa.

    Incluye identificacion, valoracion inherente, controles existentes,
    riesgo residual y respuesta del auditor.
    """

    def __init__(self, datos: dict[str, Any] | None = None) -> None:
        super().__init__(
            numero_formato=14,
            nombre_formato="Matriz de Riesgos de Auditoria",
            datos=datos,
        )

    def construir(self) -> None:
        # Objetivo
        self.agregar_titulo_seccion("1. Objetivo")
        self.agregar_parrafo_justificado(
            "Identificar, evaluar y documentar los riesgos de auditoria que puedan "
            "afectar la emision de una opinion incorrecta sobre los estados financieros "
            "o la gestion fiscal de la entidad, determinando la respuesta apropiada "
            "del auditor conforme a las NIA y normas de auditoria gubernamental."
        )

        # Escala de valoracion
        self.agregar_titulo_seccion("2. Escalas de Valoracion")
        self.agregar_subtitulo("2.1. Probabilidad")
        self.crear_tabla(
            encabezados=["Nivel", "Valor", "Descripcion"],
            filas=[
                ["Rara vez", "1", "Puede ocurrir solo en circunstancias excepcionales"],
                ["Improbable", "2", "Podria ocurrir en algun momento"],
                ["Posible", "3", "Podria ocurrir en cualquier momento"],
                ["Probable", "4", "Probablemente ocurrira en la mayoria de las circunstancias"],
                ["Casi seguro", "5", "Se espera que ocurra en la mayoria de las circunstancias"],
            ],
            anchos=[3.0, 1.5, 12.0],
        )

        self.agregar_subtitulo("2.2. Impacto")
        self.crear_tabla(
            encabezados=["Nivel", "Valor", "Descripcion"],
            filas=[
                ["Insignificante", "1", "Impacto minimo, errores no materiales"],
                ["Menor", "2", "Impacto bajo, errores menores al umbral de materialidad"],
                ["Moderado", "3", "Impacto medio, errores cercanos a la materialidad"],
                ["Mayor", "4", "Impacto alto, errores superiores a la materialidad"],
                ["Catastrofico", "5", "Impacto critico, fraude o error generalizado"],
            ],
            anchos=[3.0, 1.5, 12.0],
        )

        # Matriz de riesgos
        self.agregar_titulo_seccion("3. Matriz de Riesgos Identificados")

        riesgos = self.datos.get("riesgos", [])
        if not riesgos:
            riesgos = [
                {
                    "id": "R01",
                    "proceso": "[COMPLETAR]",
                    "descripcion": "[COMPLETAR — Describa el riesgo identificado]",
                    "tipo": "[COMPLETAR — Inherente/Control/Deteccion]",
                    "probabilidad": "[COMPLETAR]",
                    "impacto": "[COMPLETAR]",
                    "riesgo_inherente": "[COMPLETAR]",
                    "control_existente": "[COMPLETAR]",
                    "efectividad_control": "[COMPLETAR]",
                    "riesgo_residual": "[COMPLETAR]",
                    "nivel_riesgo": "[COMPLETAR — Alto/Medio/Bajo]",
                    "respuesta_auditor": "[COMPLETAR]",
                },
                {
                    "id": "R02",
                    "proceso": "[COMPLETAR]",
                    "descripcion": "[COMPLETAR]",
                    "tipo": "[COMPLETAR]",
                    "probabilidad": "[COMPLETAR]",
                    "impacto": "[COMPLETAR]",
                    "riesgo_inherente": "[COMPLETAR]",
                    "control_existente": "[COMPLETAR]",
                    "efectividad_control": "[COMPLETAR]",
                    "riesgo_residual": "[COMPLETAR]",
                    "nivel_riesgo": "[COMPLETAR]",
                    "respuesta_auditor": "[COMPLETAR]",
                },
                {
                    "id": "R03",
                    "proceso": "[COMPLETAR]",
                    "descripcion": "[COMPLETAR]",
                    "tipo": "[COMPLETAR]",
                    "probabilidad": "[COMPLETAR]",
                    "impacto": "[COMPLETAR]",
                    "riesgo_inherente": "[COMPLETAR]",
                    "control_existente": "[COMPLETAR]",
                    "efectividad_control": "[COMPLETAR]",
                    "riesgo_residual": "[COMPLETAR]",
                    "nivel_riesgo": "[COMPLETAR]",
                    "respuesta_auditor": "[COMPLETAR]",
                },
            ]

        filas_riesgos = []
        for r in riesgos:
            filas_riesgos.append([
                r.get("id", "[COMPLETAR]"),
                r.get("proceso", "[COMPLETAR]"),
                r.get("descripcion", "[COMPLETAR]"),
                r.get("tipo", "[COMPLETAR]"),
                r.get("probabilidad", "[COMPLETAR]"),
                r.get("impacto", "[COMPLETAR]"),
                r.get("riesgo_inherente", "[COMPLETAR]"),
                r.get("control_existente", "[COMPLETAR]"),
                r.get("efectividad_control", "[COMPLETAR]"),
                r.get("riesgo_residual", "[COMPLETAR]"),
                r.get("nivel_riesgo", "[COMPLETAR]"),
                r.get("respuesta_auditor", "[COMPLETAR]"),
            ])

        self.crear_tabla(
            encabezados=[
                "ID", "Proceso/Cuenta", "Descripcion del Riesgo", "Tipo",
                "Prob.", "Imp.", "R. Inherente",
                "Control Existente", "Efect. Control", "R. Residual",
                "Nivel", "Respuesta Auditor",
            ],
            filas=filas_riesgos,
        )

        # Riesgos significativos
        self.agregar_titulo_seccion("4. Riesgos Significativos")
        self.agregar_parrafo_justificado(
            "De acuerdo con la NIA 315, los siguientes riesgos han sido identificados "
            "como significativos y requieren atencion especial del equipo auditor:"
        )
        self.agregar_campo_completar(
            "Liste los riesgos significativos identificados, "
            "incluyendo riesgos de fraude (NIA 240)"
        )

        # Mapa de calor
        self.agregar_titulo_seccion("5. Mapa de Calor de Riesgos")
        self.crear_tabla(
            encabezados=["Probabilidad / Impacto", "1-Insignif.", "2-Menor",
                         "3-Moderado", "4-Mayor", "5-Catastrofico"],
            filas=[
                ["5 - Casi seguro", "Medio", "Alto", "Alto", "Extremo", "Extremo"],
                ["4 - Probable", "Medio", "Medio", "Alto", "Alto", "Extremo"],
                ["3 - Posible", "Bajo", "Medio", "Medio", "Alto", "Alto"],
                ["2 - Improbable", "Bajo", "Bajo", "Medio", "Medio", "Alto"],
                ["1 - Rara vez", "Bajo", "Bajo", "Bajo", "Medio", "Medio"],
            ],
            anchos=[3.5, 2.5, 2.5, 2.5, 2.5, 2.5],
        )

        # Conclusion
        self.agregar_titulo_seccion("6. Conclusion y Plan de Respuesta")
        self.agregar_campo_completar(
            "Resuma los riesgos criticos, las respuestas planificadas "
            "y el impacto en el alcance de la auditoria"
        )

        self.agregar_seccion_firmas()
