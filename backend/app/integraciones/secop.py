"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: app/integraciones/secop.py
Propósito: Integración con SECOP II (Sistema Electrónico de Contratación Pública)
           — consulta de contratos públicos vía API de datos.gov.co (Socrata)
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from app.integraciones.base import ClienteBaseIntegracion, ErrorIntegracion

logger = logging.getLogger("cecilia.integraciones.secop")


# ── URLs de datasets SECOP II en datos.gov.co ────────────────────────────────

SECOP_II_CONTRATOS_URL: str = "https://www.datos.gov.co/resource/jbjy-vk9h.json"
SECOP_II_PROCESOS_URL: str = "https://www.datos.gov.co/resource/p6dx-8zbt.json"


class ClienteSECOP(ClienteBaseIntegracion):
    """Cliente para consulta de contratos públicos en SECOP II.

    Utiliza la API abierta de datos.gov.co (plataforma Socrata) para
    acceder a los registros de contratación pública de Colombia.

    Los datos incluyen: entidad compradora, contratista, objeto del
    contrato, valor, fechas, estado y tipo de proceso.
    """

    nombre_servicio: str = "SECOP II"
    url_base: str = "https://www.datos.gov.co"

    def __init__(
        self,
        app_token: Optional[str] = None,
        timeout_segundos: float = 30.0,
        max_reintentos: int = 3,
    ) -> None:
        """Inicializa el cliente SECOP.

        Args:
            app_token: Token de aplicación de Socrata (datos.gov.co) para mayor cuota.
            timeout_segundos: Timeout máximo por solicitud.
            max_reintentos: Número máximo de reintentos.
        """
        encabezados_extra: dict[str, str] = {}
        if app_token:
            encabezados_extra["X-App-Token"] = app_token

        super().__init__(
            timeout_segundos=timeout_segundos,
            max_reintentos=max_reintentos,
            encabezados_extra=encabezados_extra,
        )

    async def buscar_contratos(
        self,
        entidad: Optional[str] = None,
        contratista: Optional[str] = None,
        numero_proceso: Optional[str] = None,
        valor_minimo: Optional[float] = None,
        valor_maximo: Optional[float] = None,
        limite: int = 20,
        desplazamiento: int = 0,
    ) -> list[dict[str, Any]]:
        """Busca contratos en SECOP II con múltiples filtros.

        Args:
            entidad: Nombre (parcial) de la entidad compradora.
            contratista: Nombre o NIT del contratista.
            numero_proceso: Número del proceso de contratación.
            valor_minimo: Valor mínimo del contrato en pesos.
            valor_maximo: Valor máximo del contrato en pesos.
            limite: Número máximo de resultados.
            desplazamiento: Desplazamiento para paginación.

        Returns:
            Lista de contratos encontrados.
        """
        # Construir consulta SoQL (Socrata Query Language)
        condiciones: list[str] = []

        if entidad:
            entidad_escapada: str = entidad.replace("'", "\\'")
            condiciones.append(f"upper(nombre_entidad) LIKE upper('%{entidad_escapada}%')")

        if contratista:
            contratista_escapado: str = contratista.replace("'", "\\'")
            condiciones.append(f"upper(proveedor_adjudicado) LIKE upper('%{contratista_escapado}%')")

        if numero_proceso:
            condiciones.append(f"id_del_portafolio='{numero_proceso}'")

        if valor_minimo is not None:
            condiciones.append(f"valor_del_contrato >= {valor_minimo}")

        if valor_maximo is not None:
            condiciones.append(f"valor_del_contrato <= {valor_maximo}")

        where_clause: str = " AND ".join(condiciones) if condiciones else "1=1"

        parametros: dict[str, Any] = {
            "$where": where_clause,
            "$limit": limite,
            "$offset": desplazamiento,
            "$order": "fecha_de_firma DESC",
        }

        try:
            resultado: dict[str, Any] = await self.get(
                "/resource/jbjy-vk9h.json",
                parametros=parametros,
            )

            # La API de Socrata retorna directamente una lista
            if isinstance(resultado, list):
                contratos_normalizados: list[dict[str, Any]] = [
                    self._normalizar_contrato(contrato) for contrato in resultado
                ]
                logger.info(
                    "SECOP: %d contratos encontrados (filtros: entidad=%s, contratista=%s)",
                    len(contratos_normalizados), entidad, contratista,
                )
                return contratos_normalizados

            return []

        except ErrorIntegracion:
            raise
        except Exception as error:
            logger.exception("Error inesperado al consultar SECOP.")
            raise ErrorIntegracion(
                servicio=self.nombre_servicio,
                mensaje=f"Error inesperado: {error}",
            ) from error

    def _normalizar_contrato(self, contrato_raw: dict[str, Any]) -> dict[str, Any]:
        """Normaliza un registro de contrato SECOP al esquema interno.

        Args:
            contrato_raw: Diccionario crudo del API de Socrata.

        Returns:
            Diccionario con campos normalizados.
        """
        return {
            "id_contrato": contrato_raw.get("id_del_portafolio", ""),
            "numero_proceso": contrato_raw.get("referencia_del_contrato", ""),
            "entidad_compradora": contrato_raw.get("nombre_entidad", ""),
            "contratista": contrato_raw.get("proveedor_adjudicado", ""),
            "objeto": contrato_raw.get("descripcion_del_proceso", ""),
            "valor_total": float(contrato_raw.get("valor_del_contrato", 0)),
            "fecha_firma": contrato_raw.get("fecha_de_firma"),
            "estado": contrato_raw.get("estado_contrato", ""),
            "tipo_contrato": contrato_raw.get("tipo_de_contrato", ""),
            "url_secop": contrato_raw.get("urlproceso", {}).get("url", "") if isinstance(contrato_raw.get("urlproceso"), dict) else "",
        }

    async def buscar_procesos(
        self,
        entidad: Optional[str] = None,
        estado: Optional[str] = None,
        modalidad: Optional[str] = None,
        limite: int = 20,
    ) -> list[dict[str, Any]]:
        """Busca procesos de contratación en SECOP II.

        Args:
            entidad: Nombre de la entidad compradora.
            estado: Estado del proceso (Publicado, Adjudicado, Celebrado, etc.).
            modalidad: Modalidad de contratación.
            limite: Número máximo de resultados.

        Returns:
            Lista de procesos encontrados.
        """
        condiciones: list[str] = []

        if entidad:
            entidad_escapada: str = entidad.replace("'", "\\'")
            condiciones.append(f"upper(nombre_entidad) LIKE upper('%{entidad_escapada}%')")

        if estado:
            condiciones.append(f"estado_del_proceso='{estado}'")

        if modalidad:
            condiciones.append(f"modalidad_de_contratacion='{modalidad}'")

        where_clause: str = " AND ".join(condiciones) if condiciones else "1=1"

        parametros: dict[str, Any] = {
            "$where": where_clause,
            "$limit": limite,
            "$order": "fecha_de_publicacion_del DESC",
        }

        try:
            resultado: Any = await self.get(
                "/resource/p6dx-8zbt.json",
                parametros=parametros,
            )
            return resultado if isinstance(resultado, list) else []

        except ErrorIntegracion:
            raise
        except Exception as error:
            logger.exception("Error al consultar procesos SECOP.")
            raise ErrorIntegracion(
                servicio=self.nombre_servicio,
                mensaje=f"Error al buscar procesos: {error}",
            ) from error
