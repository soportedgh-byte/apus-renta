"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: app/integraciones/sigeci.py
Propósito: Stub de integración con SIGECI (Sistema de Gestión del Control
           e Investigación) — sistema interno de la CGR para gestión del
           proceso auditor y seguimiento a planes de mejoramiento
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from app.integraciones.base import ClienteBaseIntegracion, ErrorIntegracion

logger = logging.getLogger("cecilia.integraciones.sigeci")


class ClienteSIGECI(ClienteBaseIntegracion):
    """Stub de integración con el sistema SIGECI de la CGR.

    SIGECI (Sistema de Gestión del Control e Investigación) es el
    sistema interno de la CGR que gestiona:
    - Asignación de auditorías a equipos.
    - Seguimiento al proceso auditor por fases.
    - Registro de hallazgos y planes de mejoramiento.
    - Gestión de procesos de responsabilidad fiscal.

    NOTA: Requiere acceso a la VPN interna de la CGR y credenciales
    de servicio proporcionadas por la Oficina de Sistemas.
    """

    nombre_servicio: str = "SIGECI"
    url_base: str = "https://sigeci.contraloria.gov.co/api"

    def __init__(
        self,
        url_base_override: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout_segundos: float = 60.0,
    ) -> None:
        """Inicializa el cliente SIGECI.

        Args:
            url_base_override: URL base alternativa para ambientes de prueba.
            api_key: Clave API de servicio.
            timeout_segundos: Timeout máximo por solicitud.
        """
        super().__init__(
            url_base_override=url_base_override,
            api_key=api_key,
            timeout_segundos=timeout_segundos,
        )

    async def obtener_auditoria(self, codigo_auditoria: str) -> dict[str, Any]:
        """Obtiene los datos de una auditoría registrada en SIGECI.

        Args:
            codigo_auditoria: Código único de la auditoría en SIGECI.

        Returns:
            Datos de la auditoría.

        Raises:
            ErrorIntegracion: Integración aún no implementada.
        """
        logger.warning("SIGECI: obtener_auditoria() — STUB (codigo=%s)", codigo_auditoria)
        return {
            "servicio": "SIGECI",
            "estado": "pendiente",
            "mensaje": (
                "Integracion con SIGECI pendiente. Requiere VPN y credenciales CGR. "
                "Contacto: Oficina de Sistemas — CD-TIC-CGR — sistemas@contraloria.gov.co"
            ),
        }

    async def consultar_plan_mejoramiento(
        self,
        nit_entidad: str,
        vigencia: Optional[str] = None,
    ) -> dict[str, Any]:
        """Consulta el estado del plan de mejoramiento de un sujeto de control.

        Args:
            nit_entidad: NIT del sujeto de control.
            vigencia: Vigencia del plan de mejoramiento.

        Returns:
            Estado y acciones del plan de mejoramiento.

        Raises:
            ErrorIntegracion: Integración aún no implementada.
        """
        logger.warning(
            "SIGECI: consultar_plan_mejoramiento() — STUB (nit=%s, vigencia=%s)",
            nit_entidad, vigencia,
        )
        return {
            "servicio": "SIGECI",
            "estado": "pendiente",
            "mensaje": (
                "Integracion con SIGECI pendiente. Requiere VPN y credenciales CGR. "
                "Contacto: Oficina de Sistemas — CD-TIC-CGR — sistemas@contraloria.gov.co"
            ),
        }

    async def registrar_hallazgo(
        self,
        codigo_auditoria: str,
        datos_hallazgo: dict[str, Any],
    ) -> dict[str, Any]:
        """Registra un hallazgo en SIGECI desde CecilIA.

        Args:
            codigo_auditoria: Código de la auditoría en SIGECI.
            datos_hallazgo: Datos del hallazgo (cinco elementos, cuantía, tipo).

        Returns:
            Confirmación del registro en SIGECI.

        Raises:
            ErrorIntegracion: Integración aún no implementada.
        """
        logger.warning(
            "SIGECI: registrar_hallazgo() — STUB (auditoria=%s)",
            codigo_auditoria,
        )
        return {
            "servicio": "SIGECI",
            "estado": "pendiente",
            "mensaje": (
                "Integracion con SIGECI pendiente. Requiere VPN y credenciales CGR. "
                "Contacto: Oficina de Sistemas — CD-TIC-CGR — sistemas@contraloria.gov.co"
            ),
        }

    async def obtener_equipo_auditoria(self, codigo_auditoria: str) -> dict[str, Any]:
        """Obtiene el equipo asignado a una auditoría en SIGECI.

        Args:
            codigo_auditoria: Código de la auditoría.

        Returns:
            Equipo auditor con roles y responsabilidades.

        Raises:
            ErrorIntegracion: Integración aún no implementada.
        """
        logger.warning("SIGECI: obtener_equipo_auditoria() — STUB (codigo=%s)", codigo_auditoria)
        return {
            "servicio": "SIGECI",
            "estado": "pendiente",
            "mensaje": (
                "Integracion con SIGECI pendiente. Requiere VPN y credenciales CGR. "
                "Contacto: Oficina de Sistemas — CD-TIC-CGR — sistemas@contraloria.gov.co"
            ),
        }
