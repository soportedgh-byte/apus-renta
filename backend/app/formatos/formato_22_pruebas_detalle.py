"""
CecilIA v2 — Formato F22: Pruebas de Detalle
Sprint: 4 | Fase: Ejecucion
"""

from __future__ import annotations
from typing import Any
from app.formatos.formato_base import FormatoBaseCGR


class FormatoF22PruebasDetalle(FormatoBaseCGR):
    """F22 — Cedula de Pruebas de Detalle con resultados y conclusiones."""

    def __init__(self, datos: dict[str, Any] | None = None) -> None:
        super().__init__(
            numero_formato=22,
            nombre_formato="Pruebas de Detalle",
            datos=datos,
        )

    def construir(self) -> None:
        # Informacion de la prueba
        self.agregar_titulo_seccion("1. Informacion de la Prueba")
        self.crear_tabla_clave_valor([
            ("Componente/Cuenta auditada",
             self.datos.get("componente", "[COMPLETAR]")),
            ("Objetivo de la prueba",
             self.datos.get("objetivo_prueba", "[COMPLETAR]")),
            ("Asercion(es) relacionada(s)",
             self.datos.get("aserciones",
                           "[COMPLETAR — Existencia/Integridad/Valoracion/Derechos/Presentacion]")),
            ("Referencia al programa de auditoria",
             self.datos.get("ref_programa", "[COMPLETAR]")),
            ("Periodo de prueba",
             self.datos.get("periodo_prueba", "[COMPLETAR]")),
        ])

        # Diseno del muestreo
        self.agregar_titulo_seccion("2. Diseno del Muestreo")
        self.crear_tabla_clave_valor([
            ("Poblacion (N)",
             self.datos.get("poblacion", "[COMPLETAR]")),
            ("Valor total de la poblacion (COP)",
             self.datos.get("valor_poblacion", "[COMPLETAR]")),
            ("Metodo de muestreo",
             self.datos.get("metodo_muestreo",
                           "[COMPLETAR — Aleatorio/Sistematico/Monetario/Criterio]")),
            ("Tamano de muestra (n)",
             self.datos.get("tamano_muestra", "[COMPLETAR]")),
            ("Valor de la muestra (COP)",
             self.datos.get("valor_muestra", "[COMPLETAR]")),
            ("Nivel de confianza",
             self.datos.get("nivel_confianza", "[COMPLETAR — 90%/95%/99%]")),
            ("Materialidad de ejecucion (COP)",
             self.datos.get("materialidad_ejecucion", "[COMPLETAR]")),
        ])

        # Detalle de la prueba
        self.agregar_titulo_seccion("3. Detalle de la Prueba")
        items = self.datos.get("items_prueba", [])
        if not items:
            items = [
                {"no": "1", "documento": "[COMPLETAR]", "valor_registrado": "[COMPLETAR]",
                 "valor_auditado": "[COMPLETAR]", "diferencia": "[COMPLETAR]",
                 "observacion": "[COMPLETAR]"},
                {"no": "2", "documento": "[COMPLETAR]", "valor_registrado": "[COMPLETAR]",
                 "valor_auditado": "[COMPLETAR]", "diferencia": "[COMPLETAR]",
                 "observacion": "[COMPLETAR]"},
                {"no": "3", "documento": "[COMPLETAR]", "valor_registrado": "[COMPLETAR]",
                 "valor_auditado": "[COMPLETAR]", "diferencia": "[COMPLETAR]",
                 "observacion": "[COMPLETAR]"},
            ]

        filas_items = [[
            it.get("no", "[COMPLETAR]"),
            it.get("documento", "[COMPLETAR]"),
            it.get("valor_registrado", "[COMPLETAR]"),
            it.get("valor_auditado", "[COMPLETAR]"),
            it.get("diferencia", "[COMPLETAR]"),
            it.get("observacion", "[COMPLETAR]"),
        ] for it in items]

        self.crear_tabla(
            encabezados=["No.", "Documento/Ref.", "Valor Registrado (COP)",
                         "Valor Auditado (COP)", "Diferencia (COP)", "Observacion"],
            filas=filas_items,
            anchos=[1.0, 3.5, 3.0, 3.0, 2.5, 4.0],
        )

        # Resumen de resultados
        self.agregar_titulo_seccion("4. Resumen de Resultados")
        self.crear_tabla_clave_valor([
            ("Total items examinados",
             self.datos.get("total_items", "[COMPLETAR]")),
            ("Items con diferencia",
             self.datos.get("items_diferencia", "[COMPLETAR]")),
            ("Valor total de diferencias (COP)",
             self.datos.get("total_diferencias", "[COMPLETAR]")),
            ("Diferencia proyectada a la poblacion (COP)",
             self.datos.get("diferencia_proyectada", "[COMPLETAR]")),
            ("Comparacion con materialidad",
             self.datos.get("comparacion_materialidad",
                           "[COMPLETAR — Superior/Inferior a materialidad]")),
        ])

        # Conclusion
        self.agregar_titulo_seccion("5. Conclusion de la Prueba")
        self.agregar_campo_completar(
            "Concluya sobre los resultados de la prueba, indicando si se "
            "obtiene evidencia suficiente y adecuada sobre la asercion evaluada"
        )

        # Hallazgos identificados
        self.agregar_titulo_seccion("6. Hallazgos Identificados")
        self.agregar_campo_completar(
            "Referencie los hallazgos de auditoria derivados de esta prueba, "
            "incluyendo numero de hallazgo y referencia al formato F08"
        )

        self.agregar_seccion_firmas()
