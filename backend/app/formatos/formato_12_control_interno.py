"""
CecilIA v2 — Formato F12: Evaluacion de Control Interno (COSO)
Sprint: 4 | Fase: Planeacion
"""

from __future__ import annotations
from typing import Any
from app.formatos.formato_base import FormatoBaseCGR


class FormatoF12ControlInterno(FormatoBaseCGR):
    """F12 — Evaluacion de Control Interno basada en COSO (5 componentes)."""

    def __init__(self, datos: dict[str, Any] | None = None) -> None:
        super().__init__(
            numero_formato=12,
            nombre_formato="Evaluacion de Control Interno (COSO)",
            datos=datos,
        )

    def construir(self) -> None:
        self.agregar_titulo_seccion("1. Marco de Referencia")
        self.agregar_parrafo_justificado(
            "La evaluacion del Sistema de Control Interno se realiza con base en el "
            "Marco Integrado de Control Interno COSO (Committee of Sponsoring Organizations "
            "of the Treadway Commission), adoptado por la Contraloria General de la Republica "
            "como referente para la evaluacion de los sistemas de control interno de las "
            "entidades sujetas de vigilancia y control fiscal."
        )

        # Componentes COSO
        componentes = [
            {
                "nombre": "Ambiente de Control",
                "descripcion": "Conjunto de normas, procesos y estructuras que constituyen "
                               "la base para llevar a cabo el control interno.",
                "campo_calificacion": "calif_ambiente_control",
                "campo_observaciones": "obs_ambiente_control",
                "aspectos": [
                    "Integridad y valores eticos",
                    "Estructura organizacional",
                    "Competencia profesional",
                    "Autoridad y responsabilidad",
                    "Filosofia y estilo de direccion",
                ],
            },
            {
                "nombre": "Evaluacion de Riesgos",
                "descripcion": "Proceso dinamico e iterativo para identificar y evaluar "
                               "los riesgos que afectan el logro de objetivos.",
                "campo_calificacion": "calif_eval_riesgos",
                "campo_observaciones": "obs_eval_riesgos",
                "aspectos": [
                    "Identificacion de riesgos",
                    "Valoracion de riesgos",
                    "Respuesta a riesgos",
                    "Evaluacion de cambios significativos",
                    "Riesgo de fraude",
                ],
            },
            {
                "nombre": "Actividades de Control",
                "descripcion": "Acciones establecidas a traves de politicas y procedimientos "
                               "que contribuyen a mitigar los riesgos.",
                "campo_calificacion": "calif_actividades_control",
                "campo_observaciones": "obs_actividades_control",
                "aspectos": [
                    "Segregacion de funciones",
                    "Autorizaciones y aprobaciones",
                    "Controles sobre TI",
                    "Conciliaciones",
                    "Verificaciones",
                ],
            },
            {
                "nombre": "Informacion y Comunicacion",
                "descripcion": "Informacion necesaria para que la entidad lleve a cabo "
                               "sus responsabilidades de control interno.",
                "campo_calificacion": "calif_informacion",
                "campo_observaciones": "obs_informacion",
                "aspectos": [
                    "Calidad de la informacion",
                    "Comunicacion interna",
                    "Comunicacion externa",
                    "Sistemas de informacion",
                    "Canales de reporte",
                ],
            },
            {
                "nombre": "Actividades de Monitoreo",
                "descripcion": "Evaluaciones continuas, independientes o una combinacion "
                               "de ambas, para verificar la efectividad del control interno.",
                "campo_calificacion": "calif_monitoreo",
                "campo_observaciones": "obs_monitoreo",
                "aspectos": [
                    "Evaluaciones continuas",
                    "Evaluaciones independientes",
                    "Reporte de deficiencias",
                    "Seguimiento a acciones correctivas",
                    "Oficina de Control Interno",
                ],
            },
        ]

        for i, comp in enumerate(componentes, 2):
            self.agregar_titulo_seccion(
                f"{i}. Componente: {comp['nombre']}"
            )
            self.agregar_parrafo_justificado(comp["descripcion"])

            # Tabla de evaluacion por aspecto
            filas_aspectos = []
            for aspecto in comp["aspectos"]:
                filas_aspectos.append([
                    aspecto,
                    "[COMPLETAR]",
                    "[COMPLETAR]",
                    "[COMPLETAR]",
                ])

            self.crear_tabla(
                encabezados=["Aspecto Evaluado", "Calificacion (1-5)",
                             "Evidencia", "Observaciones"],
                filas=filas_aspectos,
                anchos=[4.5, 2.5, 4.5, 5.0],
            )

            # Calificacion del componente
            self.agregar_subtitulo(f"Calificacion del Componente: {comp['nombre']}")
            self.crear_tabla_clave_valor([
                ("Calificacion global",
                 self.datos.get(comp["campo_calificacion"], "[COMPLETAR — 1 a 5]")),
                ("Nivel de madurez",
                 self.datos.get(f"nivel_{comp['campo_calificacion']}",
                               "[COMPLETAR — Inicial/Repetible/Definido/Administrado/Optimizado]")),
                ("Observaciones",
                 self.datos.get(comp["campo_observaciones"], "[COMPLETAR]")),
            ])

        # Resumen consolidado
        self.agregar_titulo_seccion("7. Resumen Consolidado")
        self.crear_tabla(
            encabezados=["Componente COSO", "Calificacion", "Nivel", "Riesgo Asociado"],
            filas=[
                ["Ambiente de Control",
                 self.datos.get("calif_ambiente_control", "[COMPLETAR]"),
                 "[COMPLETAR]", "[COMPLETAR]"],
                ["Evaluacion de Riesgos",
                 self.datos.get("calif_eval_riesgos", "[COMPLETAR]"),
                 "[COMPLETAR]", "[COMPLETAR]"],
                ["Actividades de Control",
                 self.datos.get("calif_actividades_control", "[COMPLETAR]"),
                 "[COMPLETAR]", "[COMPLETAR]"],
                ["Informacion y Comunicacion",
                 self.datos.get("calif_informacion", "[COMPLETAR]"),
                 "[COMPLETAR]", "[COMPLETAR]"],
                ["Actividades de Monitoreo",
                 self.datos.get("calif_monitoreo", "[COMPLETAR]"),
                 "[COMPLETAR]", "[COMPLETAR]"],
            ],
            anchos=[5.0, 3.0, 4.0, 4.5],
        )

        # Conclusion
        self.agregar_titulo_seccion("8. Conclusion General")
        self.agregar_campo_completar(
            "Emita una conclusion general sobre la efectividad del Sistema de "
            "Control Interno y su impacto en la planeacion de la auditoria"
        )

        self.agregar_seccion_firmas()
