"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: app/integraciones/congreso.py
Propósito: Integración con el Congreso de la República de Colombia — consulta
           de proyectos de ley, actos legislativos y trámite legislativo
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from app.integraciones.base import ClienteBaseIntegracion, ErrorIntegracion

logger = logging.getLogger("cecilia.integraciones.congreso")


class ClienteCongreso(ClienteBaseIntegracion):
    """Cliente para consulta de proyectos de ley en el Congreso de Colombia.

    Consulta la API pública del Congreso (datos.gov.co) para obtener
    información sobre proyectos de ley, actos legislativos y su
    estado de trámite. Útil para el análisis normativo en auditorías.
    """

    nombre_servicio: str = "Congreso"
    url_base: str = "https://www.datos.gov.co"

    def __init__(
        self,
        app_token: Optional[str] = None,
        timeout_segundos: float = 30.0,
        max_reintentos: int = 3,
    ) -> None:
        """Inicializa el cliente del Congreso.

        Args:
            app_token: Token de aplicación Socrata.
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

    async def buscar_proyectos(
        self,
        termino_busqueda: Optional[str] = None,
        legislatura: Optional[str] = None,
        estado: Optional[str] = None,
        comision: Optional[str] = None,
        limite: int = 20,
        desplazamiento: int = 0,
    ) -> list[dict[str, Any]]:
        """Busca proyectos de ley en el Congreso de la República.

        Args:
            termino_busqueda: Texto a buscar en el título del proyecto.
            legislatura: Legislatura (e.g., '2025-2026').
            estado: Estado del proyecto (radicado, en_debate, aprobado, etc.).
            comision: Comisión asignada.
            limite: Número máximo de resultados.
            desplazamiento: Desplazamiento para paginación.

        Returns:
            Lista de proyectos de ley encontrados.
        """
        condiciones: list[str] = []

        if termino_busqueda:
            termino_escapado: str = termino_busqueda.replace("'", "\\'")
            condiciones.append(f"upper(titulo_proyecto) LIKE upper('%{termino_escapado}%')")

        if legislatura:
            condiciones.append(f"legislatura='{legislatura}'")

        if estado:
            condiciones.append(f"estado='{estado}'")

        if comision:
            condiciones.append(f"upper(comision) LIKE upper('%{comision}%')")

        where_clause: str = " AND ".join(condiciones) if condiciones else "1=1"

        parametros: dict[str, Any] = {
            "$where": where_clause,
            "$limit": limite,
            "$offset": desplazamiento,
            "$order": "fecha_radicacion DESC",
        }

        try:
            # Dataset de proyectos de ley en datos.gov.co
            resultado: Any = await self.get(
                "/resource/gh4g-hp3f.json",
                parametros=parametros,
            )

            if isinstance(resultado, list):
                proyectos_normalizados: list[dict[str, Any]] = [
                    self._normalizar_proyecto(proyecto) for proyecto in resultado
                ]
                logger.info(
                    "Congreso: %d proyectos encontrados (termino=%s, legislatura=%s)",
                    len(proyectos_normalizados), termino_busqueda, legislatura,
                )
                return proyectos_normalizados

            return []

        except ErrorIntegracion:
            raise
        except Exception as error:
            logger.exception("Error al consultar proyectos del Congreso.")
            raise ErrorIntegracion(
                servicio=self.nombre_servicio,
                mensaje=f"Error al buscar proyectos: {error}",
            ) from error

    def _normalizar_proyecto(self, proyecto_raw: dict[str, Any]) -> dict[str, Any]:
        """Normaliza un registro de proyecto de ley al esquema interno.

        Args:
            proyecto_raw: Diccionario crudo de la API.

        Returns:
            Diccionario con campos normalizados.
        """
        autores_raw: str = proyecto_raw.get("autores", "")
        autores: list[str] = [a.strip() for a in autores_raw.split(",") if a.strip()] if autores_raw else []

        return {
            "numero": proyecto_raw.get("numero_proyecto", ""),
            "titulo": proyecto_raw.get("titulo_proyecto", ""),
            "autores": autores,
            "estado": proyecto_raw.get("estado", ""),
            "comision": proyecto_raw.get("comision", ""),
            "fecha_radicacion": proyecto_raw.get("fecha_radicacion"),
            "legislatura": proyecto_raw.get("legislatura", ""),
            "tipo": proyecto_raw.get("tipo_proyecto", ""),
            "url": proyecto_raw.get("url_proceso", ""),
        }

    async def obtener_leyes_vigentes(
        self,
        termino_busqueda: Optional[str] = None,
        anno: Optional[int] = None,
        limite: int = 20,
    ) -> list[dict[str, Any]]:
        """Busca leyes sancionadas y vigentes.

        Args:
            termino_busqueda: Texto a buscar en el título de la ley.
            anno: Año de sanción.
            limite: Número máximo de resultados.

        Returns:
            Lista de leyes encontradas.
        """
        condiciones: list[str] = ["estado='Sancionado'"]

        if termino_busqueda:
            termino_escapado: str = termino_busqueda.replace("'", "\\'")
            condiciones.append(f"upper(titulo_proyecto) LIKE upper('%{termino_escapado}%')")

        if anno:
            condiciones.append(f"anno='{anno}'")

        where_clause: str = " AND ".join(condiciones)

        parametros: dict[str, Any] = {
            "$where": where_clause,
            "$limit": limite,
            "$order": "fecha_radicacion DESC",
        }

        try:
            resultado: Any = await self.get(
                "/resource/gh4g-hp3f.json",
                parametros=parametros,
            )
            if isinstance(resultado, list):
                return [self._normalizar_proyecto(p) for p in resultado]
            return []

        except ErrorIntegracion:
            raise
        except Exception as error:
            logger.exception("Error al consultar leyes vigentes.")
            raise ErrorIntegracion(
                servicio=self.nombre_servicio,
                mensaje=f"Error al buscar leyes: {error}",
            ) from error
