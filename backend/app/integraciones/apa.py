"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: app/integraciones/apa.py
Propósito: Stub de integración con APA (Aplicativo de Planeación de Auditorías)
           — sistema interno de la CGR para la planeación del proceso auditor
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from app.integraciones.base import ClienteBaseIntegracion, ErrorIntegracion

logger = logging.getLogger("cecilia.integraciones.apa")


class ClienteAPA(ClienteBaseIntegracion):
    """Stub de integración con el sistema APA de la CGR.

    APA (Aplicativo de Planeación de Auditorías) es el sistema
    interno de la CGR que gestiona:
    - Plan de Vigilancia y Control Fiscal (PVCF).
    - Asignación de universos auditables.
    - Priorización de sujetos de control.
    - Cronogramas de auditoría.

    NOTA: Requiere acceso a la VPN interna de la CGR y credenciales
    de servicio proporcionadas por la Oficina de Sistemas.
    """

    nombre_servicio: str = "APA"
    url_base: str = "https://apa.contraloria.gov.co/api"

    def __init__(
        self,
        url_base_override: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout_segundos: float = 60.0,
    ) -> None:
        """Inicializa el cliente APA.

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

    async def obtener_plan_vigilancia(self, vigencia: str) -> dict[str, Any]:
        """Obtiene el Plan de Vigilancia y Control Fiscal para una vigencia.

        Args:
            vigencia: Vigencia del plan (e.g., '2026').

        Returns:
            Datos del plan de vigilancia y control fiscal.

        Raises:
            ErrorIntegracion: Integración aún no implementada.
        """
        logger.warning("APA: obtener_plan_vigilancia() — STUB (vigencia=%s)", vigencia)
        raise ErrorIntegracion(
            servicio=self.nombre_servicio,
            mensaje="Integración con APA pendiente. Requiere VPN y credenciales CGR.",
        )

    async def obtener_universo_auditable(
        self,
        vigencia: str,
        direccion: Optional[str] = None,
    ) -> dict[str, Any]:
        """Obtiene el universo de sujetos auditables.

        Args:
            vigencia: Vigencia del universo auditable.
            direccion: Dirección responsable (DES, DVF).

        Returns:
            Lista de sujetos de control priorizados.

        Raises:
            ErrorIntegracion: Integración aún no implementada.
        """
        logger.warning(
            "APA: obtener_universo_auditable() — STUB (vigencia=%s, direccion=%s)",
            vigencia, direccion,
        )
        raise ErrorIntegracion(
            servicio=self.nombre_servicio,
            mensaje="Integración con APA pendiente. Requiere VPN y credenciales CGR.",
        )

    async def obtener_cronograma(
        self,
        vigencia: str,
        direccion: Optional[str] = None,
    ) -> dict[str, Any]:
        """Obtiene el cronograma de auditorías para una vigencia.

        Args:
            vigencia: Vigencia del cronograma.
            direccion: Dirección responsable.

        Returns:
            Cronograma de auditorías con fechas y asignaciones.

        Raises:
            ErrorIntegracion: Integración aún no implementada.
        """
        logger.warning(
            "APA: obtener_cronograma() — STUB (vigencia=%s, direccion=%s)",
            vigencia, direccion,
        )
        raise ErrorIntegracion(
            servicio=self.nombre_servicio,
            mensaje="Integración con APA pendiente. Requiere VPN y credenciales CGR.",
        )
