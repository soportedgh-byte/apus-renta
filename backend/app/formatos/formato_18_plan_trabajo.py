"""
CecilIA v2 — Formato F18: Plan de Trabajo de Auditoria
Sprint: 4 | Fase: Planeacion
"""

from __future__ import annotations
from typing import Any
from app.formatos.formato_base import FormatoBaseCGR


class FormatoF18PlanTrabajo(FormatoBaseCGR):
    """F18 — Plan de Trabajo con cronograma y asignacion de recursos."""

    def __init__(self, datos: dict[str, Any] | None = None) -> None:
        super().__init__(
            numero_formato=18,
            nombre_formato="Plan de Trabajo de Auditoria",
            datos=datos,
        )

    def construir(self) -> None:
        # Objetivo
        self.agregar_titulo_seccion("1. Objetivo de la Auditoria")
        self.agregar_campo_completar(
            "Defina el objetivo general de la auditoria conforme al Plan de "
            "Vigilancia y Control Fiscal"
        )

        # Alcance
        self.agregar_titulo_seccion("2. Alcance")
        self.crear_tabla_clave_valor([
            ("Tipo de auditoria",
             self.datos.get("tipo_auditoria", "[COMPLETAR]")),
            ("Vigencia auditada",
             self.datos.get("vigencia", "[COMPLETAR]")),
            ("Periodo de ejecucion",
             self.datos.get("periodo_ejecucion", "[COMPLETAR]")),
            ("Procesos/Temas a auditar",
             self.datos.get("procesos_auditar", "[COMPLETAR]")),
            ("Normas aplicables",
             self.datos.get("normas_aplicables", "[COMPLETAR]")),
        ])

        # Equipo auditor
        self.agregar_titulo_seccion("3. Equipo Auditor")
        equipo = self.datos.get("equipo", [])
        if not equipo:
            equipo = [
                {"nombre": "[COMPLETAR]", "cargo": "Director Tecnico",
                 "rol": "Direccion", "horas": "[COMPLETAR]"},
                {"nombre": "[COMPLETAR]", "cargo": "Supervisor",
                 "rol": "Supervision", "horas": "[COMPLETAR]"},
                {"nombre": "[COMPLETAR]", "cargo": "Auditor Senior",
                 "rol": "Ejecucion", "horas": "[COMPLETAR]"},
                {"nombre": "[COMPLETAR]", "cargo": "Auditor",
                 "rol": "Ejecucion", "horas": "[COMPLETAR]"},
            ]

        filas_equipo = [[
            e.get("nombre", "[COMPLETAR]"),
            e.get("cargo", "[COMPLETAR]"),
            e.get("rol", "[COMPLETAR]"),
            e.get("horas", "[COMPLETAR]"),
        ] for e in equipo]

        self.crear_tabla(
            encabezados=["Nombre", "Cargo", "Rol en la Auditoria", "Horas Asignadas"],
            filas=filas_equipo,
            anchos=[4.5, 3.5, 4.0, 3.0],
        )

        # Cronograma
        self.agregar_titulo_seccion("4. Cronograma de Actividades")
        actividades = self.datos.get("actividades", [])
        if not actividades:
            actividades = [
                {"fase": "Pre-planeacion", "actividad": "Conocimiento de la entidad",
                 "responsable": "[COMPLETAR]", "inicio": "[COMPLETAR]",
                 "fin": "[COMPLETAR]", "producto": "Memorando de planeacion"},
                {"fase": "Pre-planeacion", "actividad": "Analisis de riesgos",
                 "responsable": "[COMPLETAR]", "inicio": "[COMPLETAR]",
                 "fin": "[COMPLETAR]", "producto": "Matriz de riesgos"},
                {"fase": "Planeacion", "actividad": "Elaboracion plan de trabajo",
                 "responsable": "[COMPLETAR]", "inicio": "[COMPLETAR]",
                 "fin": "[COMPLETAR]", "producto": "Plan de trabajo"},
                {"fase": "Planeacion", "actividad": "Calculo de materialidad",
                 "responsable": "[COMPLETAR]", "inicio": "[COMPLETAR]",
                 "fin": "[COMPLETAR]", "producto": "F17 Materialidad"},
                {"fase": "Ejecucion", "actividad": "Pruebas sustantivas",
                 "responsable": "[COMPLETAR]", "inicio": "[COMPLETAR]",
                 "fin": "[COMPLETAR]", "producto": "Papeles de trabajo"},
                {"fase": "Ejecucion", "actividad": "Pruebas de cumplimiento",
                 "responsable": "[COMPLETAR]", "inicio": "[COMPLETAR]",
                 "fin": "[COMPLETAR]", "producto": "Papeles de trabajo"},
                {"fase": "Informe", "actividad": "Elaboracion informe preliminar",
                 "responsable": "[COMPLETAR]", "inicio": "[COMPLETAR]",
                 "fin": "[COMPLETAR]", "producto": "Informe preliminar"},
                {"fase": "Informe", "actividad": "Contradiccion y respuestas",
                 "responsable": "[COMPLETAR]", "inicio": "[COMPLETAR]",
                 "fin": "[COMPLETAR]", "producto": "Informe final"},
            ]

        filas_crono = [[
            a.get("fase", "[COMPLETAR]"),
            a.get("actividad", "[COMPLETAR]"),
            a.get("responsable", "[COMPLETAR]"),
            a.get("inicio", "[COMPLETAR]"),
            a.get("fin", "[COMPLETAR]"),
            a.get("producto", "[COMPLETAR]"),
        ] for a in actividades]

        self.crear_tabla(
            encabezados=["Fase", "Actividad", "Responsable",
                         "Fecha Inicio", "Fecha Fin", "Producto"],
            filas=filas_crono,
        )

        # Recursos
        self.agregar_titulo_seccion("5. Recursos Requeridos")
        self.crear_tabla_clave_valor([
            ("Total horas auditor",
             self.datos.get("total_horas", "[COMPLETAR]")),
            ("Recursos tecnologicos",
             self.datos.get("recursos_tecnologicos", "[COMPLETAR]")),
            ("Viaticos y desplazamientos",
             self.datos.get("viaticos", "[COMPLETAR]")),
            ("Apoyo especializado",
             self.datos.get("apoyo_especializado", "[COMPLETAR — Peritos, consultores]")),
        ])

        self.agregar_seccion_firmas()
