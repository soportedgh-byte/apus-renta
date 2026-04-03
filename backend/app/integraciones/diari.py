"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: app/integraciones/diari.py
Propósito: Stub de integración con DIARI (Directorio de Informes de Auditoría
           y Reportes Institucionales) — sistema interno de la CGR para
           publicación y consulta de informes de auditoría finales
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from app.integraciones.base import ClienteBaseIntegracion, ErrorIntegracion

logger = logging.getLogger("cecilia.integraciones.diari")


class ClienteDIARI(ClienteBaseIntegracion):
    """Stub de integración con el sistema DIARI de la CGR.

    DIARI (Directorio de Informes de Auditoría y Reportes Institucionales)
    es el sistema interno de la CGR que gestiona:
    - Publicación de informes finales de auditoría.
    - Repositorio de dictámenes y conceptos.
    - Consulta de informes históricos por entidad y vigencia.
    - Estadísticas de hallazgos y cuantías.

    NOTA: Requiere acceso a la VPN interna de la CGR y credenciales
    de servicio proporcionadas por la Oficina de Sistemas.
    """

    nombre_servicio: str = "DIARI"
    url_base: str = "https://diari.contraloria.gov.co/api"

    def __init__(
        self,
        url_base_override: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout_segundos: float = 60.0,
    ) -> None:
        """Inicializa el cliente DIARI.

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

    async def buscar_informes(
        self,
        entidad: Optional[str] = None,
        vigencia: Optional[str] = None,
        tipo_informe: Optional[str] = None,
        limite: int = 20,
    ) -> list[dict[str, Any]]:
        """Busca informes de auditoría publicados en DIARI.

        Args:
            entidad: Nombre o NIT de la entidad auditada.
            vigencia: Vigencia del informe.
            tipo_informe: Tipo de informe (financiero, cumplimiento, desempeno, etc.).
            limite: Número máximo de resultados.

        Returns:
            Lista de informes encontrados.

        Raises:
            ErrorIntegracion: Integración aún no implementada.
        """
        logger.warning(
            "DIARI: buscar_informes() — STUB (entidad=%s, vigencia=%s, tipo=%s)",
            entidad, vigencia, tipo_informe,
        )
        raise ErrorIntegracion(
            servicio=self.nombre_servicio,
            mensaje="Integración con DIARI pendiente. Requiere VPN y credenciales CGR.",
        )

    async def obtener_informe(self, codigo_informe: str) -> dict[str, Any]:
        """Obtiene un informe de auditoría específico.

        Args:
            codigo_informe: Código único del informe en DIARI.

        Returns:
            Datos completos del informe.

        Raises:
            ErrorIntegracion: Integración aún no implementada.
        """
        logger.warning("DIARI: obtener_informe() — STUB (codigo=%s)", codigo_informe)
        raise ErrorIntegracion(
            servicio=self.nombre_servicio,
            mensaje="Integración con DIARI pendiente. Requiere VPN y credenciales CGR.",
        )

    async def publicar_informe(
        self,
        datos_informe: dict[str, Any],
        archivo_pdf: Optional[bytes] = None,
    ) -> dict[str, Any]:
        """Publica un informe de auditoría en DIARI.

        Args:
            datos_informe: Metadatos del informe (tipo, entidad, vigencia, etc.).
            archivo_pdf: Contenido binario del archivo PDF del informe.

        Returns:
            Confirmación de publicación con código asignado.

        Raises:
            ErrorIntegracion: Integración aún no implementada.
        """
        logger.warning("DIARI: publicar_informe() — STUB")
        raise ErrorIntegracion(
            servicio=self.nombre_servicio,
            mensaje="Integración con DIARI pendiente. Requiere VPN y credenciales CGR.",
        )

    async def obtener_estadisticas_hallazgos(
        self,
        entidad: Optional[str] = None,
        vigencia: Optional[str] = None,
    ) -> dict[str, Any]:
        """Obtiene estadísticas de hallazgos por entidad y vigencia.

        Args:
            entidad: Nombre o NIT de la entidad.
            vigencia: Vigencia para filtrar estadísticas.

        Returns:
            Estadísticas de hallazgos (conteo por tipo, cuantías, etc.).

        Raises:
            ErrorIntegracion: Integración aún no implementada.
        """
        logger.warning(
            "DIARI: obtener_estadisticas_hallazgos() — STUB (entidad=%s, vigencia=%s)",
            entidad, vigencia,
        )
        raise ErrorIntegracion(
            servicio=self.nombre_servicio,
            mensaje="Integración con DIARI pendiente. Requiere VPN y credenciales CGR.",
        )
