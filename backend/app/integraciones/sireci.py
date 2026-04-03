"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: app/integraciones/sireci.py
Propósito: Stub de integración con SIRECI (Sistema de Rendición Electrónica
           de la Cuenta e Informes) — sistema interno de la CGR para recepción
           de rendición de cuentas de sujetos de control
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from app.integraciones.base import ClienteBaseIntegracion, ErrorIntegracion

logger = logging.getLogger("cecilia.integraciones.sireci")


class ClienteSIRECI(ClienteBaseIntegracion):
    """Stub de integración con el sistema SIRECI de la CGR.

    SIRECI (Sistema de Rendición Electrónica de la Cuenta e Informes)
    es el sistema interno de la CGR donde los sujetos de control rinden
    su cuenta (estados financieros, ejecución presupuestal, contratación).

    NOTA: Esta integración requiere acceso a la VPN interna de la CGR
    y credenciales de servicio proporcionadas por la Oficina de Sistemas.
    Los endpoints y estructura de datos se definirán en coordinación
    con el equipo técnico de SIRECI.
    """

    nombre_servicio: str = "SIRECI"
    url_base: str = "https://sireci.contraloria.gov.co/api"

    def __init__(
        self,
        url_base_override: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout_segundos: float = 60.0,
    ) -> None:
        """Inicializa el cliente SIRECI.

        Args:
            url_base_override: URL base alternativa para ambientes de prueba.
            api_key: Clave API de servicio para autenticación interna.
            timeout_segundos: Timeout máximo por solicitud.
        """
        super().__init__(
            url_base_override=url_base_override,
            api_key=api_key,
            timeout_segundos=timeout_segundos,
        )

    async def consultar_rendicion(
        self,
        nit_entidad: str,
        vigencia: str,
        tipo_cuenta: Optional[str] = None,
    ) -> dict[str, Any]:
        """Consulta la rendición de cuentas de un sujeto de control.

        Args:
            nit_entidad: NIT del sujeto de control.
            vigencia: Vigencia de la rendición (e.g., '2025').
            tipo_cuenta: Tipo de cuenta (mensual, trimestral, anual).

        Returns:
            Datos de la rendición consultada.

        Raises:
            ErrorIntegracion: Integración aún no implementada.
        """
        logger.warning(
            "SIRECI: consultar_rendicion() — STUB (nit=%s, vigencia=%s, tipo=%s)",
            nit_entidad, vigencia, tipo_cuenta,
        )
        raise ErrorIntegracion(
            servicio=self.nombre_servicio,
            mensaje=(
                "Integración con SIRECI pendiente de implementación. "
                "Requiere acceso a VPN interna de la CGR y credenciales de servicio."
            ),
        )

    async def obtener_estados_financieros(
        self,
        nit_entidad: str,
        vigencia: str,
    ) -> dict[str, Any]:
        """Obtiene los estados financieros rendidos por un sujeto de control.

        Args:
            nit_entidad: NIT del sujeto de control.
            vigencia: Vigencia fiscal.

        Returns:
            Estados financieros del sujeto de control.

        Raises:
            ErrorIntegracion: Integración aún no implementada.
        """
        logger.warning(
            "SIRECI: obtener_estados_financieros() — STUB (nit=%s, vigencia=%s)",
            nit_entidad, vigencia,
        )
        raise ErrorIntegracion(
            servicio=self.nombre_servicio,
            mensaje="Integración con SIRECI pendiente. Requiere VPN y credenciales CGR.",
        )

    async def obtener_ejecucion_presupuestal(
        self,
        nit_entidad: str,
        vigencia: str,
    ) -> dict[str, Any]:
        """Obtiene la ejecución presupuestal de un sujeto de control.

        Args:
            nit_entidad: NIT del sujeto de control.
            vigencia: Vigencia fiscal.

        Returns:
            Datos de ejecución presupuestal.

        Raises:
            ErrorIntegracion: Integración aún no implementada.
        """
        logger.warning(
            "SIRECI: obtener_ejecucion_presupuestal() — STUB (nit=%s, vigencia=%s)",
            nit_entidad, vigencia,
        )
        raise ErrorIntegracion(
            servicio=self.nombre_servicio,
            mensaje="Integración con SIRECI pendiente. Requiere VPN y credenciales CGR.",
        )
