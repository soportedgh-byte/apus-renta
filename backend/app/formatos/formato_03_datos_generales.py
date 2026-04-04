"""
CecilIA v2 — Formato F03: Datos Generales de la Entidad
Sprint: 4 | Fase: Pre-planeacion
"""

from __future__ import annotations
from typing import Any
from app.formatos.formato_base import FormatoBaseCGR


class FormatoF03DatosGenerales(FormatoBaseCGR):
    """F03 — Ficha de Datos Generales de la Entidad Auditada."""

    def __init__(self, datos: dict[str, Any] | None = None) -> None:
        super().__init__(
            numero_formato=3,
            nombre_formato="Datos Generales de la Entidad",
            datos=datos,
        )

    def construir(self) -> None:
        # Identificacion
        self.agregar_titulo_seccion("1. Identificacion de la Entidad")
        self.crear_tabla_clave_valor([
            ("Nombre de la entidad", self.datos.get("nombre_entidad", "[COMPLETAR]")),
            ("NIT", self.datos.get("nit", "[COMPLETAR]")),
            ("Naturaleza juridica", self.datos.get("naturaleza_juridica", "[COMPLETAR]")),
            ("Sector", self.datos.get("sector", "[COMPLETAR]")),
            ("Direccion", self.datos.get("direccion_entidad", "[COMPLETAR]")),
            ("Ciudad", self.datos.get("ciudad", "[COMPLETAR]")),
            ("Telefono", self.datos.get("telefono", "[COMPLETAR]")),
            ("Pagina web", self.datos.get("pagina_web", "[COMPLETAR]")),
        ])

        # Representante legal
        self.agregar_titulo_seccion("2. Representante Legal")
        self.crear_tabla_clave_valor([
            ("Nombre", self.datos.get("representante_legal", "[COMPLETAR]")),
            ("Cargo", self.datos.get("cargo_representante", "[COMPLETAR]")),
            ("Periodo", self.datos.get("periodo_representante", "[COMPLETAR]")),
            ("Correo electronico", self.datos.get("correo_representante", "[COMPLETAR]")),
        ])

        # Estructura organizacional
        self.agregar_titulo_seccion("3. Estructura Organizacional")
        self.crear_tabla_clave_valor([
            ("No. de empleados", self.datos.get("num_empleados", "[COMPLETAR]")),
            ("No. de contratistas", self.datos.get("num_contratistas", "[COMPLETAR]")),
            ("Tipo de entidad", self.datos.get("tipo_entidad", "[COMPLETAR]")),
            ("Orden", self.datos.get("orden", "[COMPLETAR — Nacional/Territorial]")),
            ("Adscrita a", self.datos.get("adscrita_a", "[COMPLETAR]")),
        ])

        # Informacion financiera
        self.agregar_titulo_seccion("4. Informacion Financiera Basica")
        self.crear_tabla(
            encabezados=["Concepto", "Vigencia Actual", "Vigencia Anterior", "Variacion %"],
            filas=[
                ["Presupuesto aprobado",
                 self.datos.get("presupuesto_actual", "[COMPLETAR]"),
                 self.datos.get("presupuesto_anterior", "[COMPLETAR]"),
                 self.datos.get("var_presupuesto", "[COMPLETAR]")],
                ["Ingresos totales",
                 self.datos.get("ingresos_actual", "[COMPLETAR]"),
                 self.datos.get("ingresos_anterior", "[COMPLETAR]"),
                 self.datos.get("var_ingresos", "[COMPLETAR]")],
                ["Gastos totales",
                 self.datos.get("gastos_actual", "[COMPLETAR]"),
                 self.datos.get("gastos_anterior", "[COMPLETAR]"),
                 self.datos.get("var_gastos", "[COMPLETAR]")],
                ["Activos totales",
                 self.datos.get("activos_actual", "[COMPLETAR]"),
                 self.datos.get("activos_anterior", "[COMPLETAR]"),
                 self.datos.get("var_activos", "[COMPLETAR]")],
                ["Pasivos totales",
                 self.datos.get("pasivos_actual", "[COMPLETAR]"),
                 self.datos.get("pasivos_anterior", "[COMPLETAR]"),
                 self.datos.get("var_pasivos", "[COMPLETAR]")],
                ["Patrimonio",
                 self.datos.get("patrimonio_actual", "[COMPLETAR]"),
                 self.datos.get("patrimonio_anterior", "[COMPLETAR]"),
                 self.datos.get("var_patrimonio", "[COMPLETAR]")],
            ],
            anchos=[4.0, 4.0, 4.0, 3.0],
        )

        # Antecedentes de control fiscal
        self.agregar_titulo_seccion("5. Antecedentes de Control Fiscal")
        self.agregar_campo_completar(
            "Describa los antecedentes de auditorias anteriores, "
            "hallazgos relevantes y estado de planes de mejoramiento"
        )

        self.agregar_seccion_firmas()
