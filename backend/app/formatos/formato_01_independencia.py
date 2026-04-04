"""
CecilIA v2 — Formato F01: Declaracion de Independencia
Sprint: 4 | Fase: Pre-planeacion
"""

from __future__ import annotations
from typing import Any
from app.formatos.formato_base import FormatoBaseCGR


class FormatoF01Independencia(FormatoBaseCGR):
    """F01 — Declaracion de Independencia del equipo auditor.

    Tabla de declarantes con nombre, cargo, relacion con entidad y firma.
    Cumple con ISSAI 130 y normas de etica del auditor.
    """

    def __init__(self, datos: dict[str, Any] | None = None) -> None:
        super().__init__(
            numero_formato=1,
            nombre_formato="Declaracion de Independencia",
            datos=datos,
        )

    def construir(self) -> None:
        entidad = self.datos.get("nombre_entidad", "[COMPLETAR]")
        vigencia = self.datos.get("vigencia", "[COMPLETAR]")

        # Fundamentacion
        self.agregar_titulo_seccion("1. Fundamentacion")
        self.agregar_parrafo_justificado(
            "De conformidad con las Normas Internacionales de Auditoria (ISSAI 130) "
            "y las Normas de Auditoria Gubernamental adoptadas por la Contraloria General "
            "de la Republica, cada miembro del equipo auditor debe declarar su independencia "
            "respecto de la entidad auditada, manifestando que no posee relaciones personales, "
            "financieras ni profesionales que puedan comprometer su objetividad e imparcialidad."
        )

        # Datos de la auditoria
        self.agregar_titulo_seccion("2. Datos de la Auditoria")
        self.crear_tabla_clave_valor([
            ("Entidad auditada", entidad),
            ("Vigencia", vigencia),
            ("Tipo de auditoria", self.datos.get("tipo_auditoria", "[COMPLETAR]")),
            ("Director Tecnico", self.datos.get("director_tecnico", "[COMPLETAR]")),
            ("Supervisor", self.datos.get("supervisor", "[COMPLETAR]")),
        ])

        # Tabla de declarantes
        self.agregar_titulo_seccion("3. Declaracion del Equipo Auditor")
        self.agregar_parrafo(
            "Cada miembro del equipo auditor declara bajo juramento que:"
        )
        self.agregar_parrafo(
            "a) No tiene parentesco dentro del cuarto grado de consanguinidad, "
            "segundo de afinidad o primero civil con directivos de la entidad."
        )
        self.agregar_parrafo(
            "b) No tiene interes economico directo o indirecto en la entidad."
        )
        self.agregar_parrafo(
            "c) No ha prestado servicios a la entidad en los ultimos dos anos."
        )
        self.agregar_parrafo(
            "d) No tiene relacion de amistad intima o enemistad manifiesta "
            "con directivos de la entidad."
        )

        # Tabla de declarantes
        declarantes = self.datos.get("declarantes", [])
        if not declarantes:
            declarantes = [
                {"nombre": "[COMPLETAR]", "cargo": "[COMPLETAR]",
                 "relacion": "Ninguna", "independiente": "Si"},
                {"nombre": "[COMPLETAR]", "cargo": "[COMPLETAR]",
                 "relacion": "Ninguna", "independiente": "Si"},
                {"nombre": "[COMPLETAR]", "cargo": "[COMPLETAR]",
                 "relacion": "Ninguna", "independiente": "Si"},
            ]

        encabezados = [
            "No.", "Nombre Completo", "Cargo / Rol",
            "Relacion con la Entidad", "Declara Independencia", "Firma"
        ]
        filas = []
        for i, d in enumerate(declarantes, 1):
            filas.append([
                str(i),
                d.get("nombre", "[COMPLETAR]"),
                d.get("cargo", "[COMPLETAR]"),
                d.get("relacion", "Ninguna"),
                d.get("independiente", "Si"),
                "________________________",
            ])

        self.crear_tabla(encabezados, filas, anchos=[1.0, 4.0, 3.0, 3.5, 2.5, 3.0])

        # Observaciones
        self.agregar_titulo_seccion("4. Observaciones")
        self.agregar_campo_completar(
            "Incluya cualquier situacion especial o salvedad respecto de la independencia"
        )

        # Firmas
        self.agregar_seccion_firmas()
