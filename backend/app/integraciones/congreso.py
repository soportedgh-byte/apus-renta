"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/integraciones/congreso.py
Proposito: Integracion con el Congreso de la Republica de Colombia — consulta
           de proyectos de ley, normas vigentes y verificacion de vigencia
Sprint: 7
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from app.integraciones.base import ClienteBaseIntegracion, ErrorIntegracion

logger = logging.getLogger("cecilia.integraciones.congreso")


# ── Tipos de norma para busqueda estructurada ──────────────────────────────────

TIPOS_NORMA: dict[str, str] = {
    "ley": "Ley",
    "decreto": "Decreto",
    "acto_legislativo": "Acto Legislativo",
    "resolucion": "Resolucion",
    "acuerdo": "Acuerdo",
}


class ClienteCongreso(ClienteBaseIntegracion):
    """Cliente para consulta de proyectos de ley en el Congreso de Colombia.

    Consulta la API publica del Congreso (datos.gov.co) para obtener
    informacion sobre proyectos de ley, actos legislativos y su
    estado de tramite. Util para el analisis normativo en auditorias.

    Metodos disponibles:
    - buscar_proyectos: Busqueda general de proyectos de ley
    - obtener_leyes_vigentes: Leyes sancionadas
    - buscar_norma: Busqueda especifica por tipo, numero y ano
    - verificar_vigencia: Verificar si una norma sigue vigente
    - buscar_proyectos_ley: Busqueda por tema y estado
    """

    nombre_servicio: str = "Congreso"
    url_base: str = "https://www.datos.gov.co"

    def __init__(
        self,
        app_token: Optional[str] = None,
        timeout_segundos: float = 30.0,
        max_reintentos: int = 3,
        cache_ttl_segundos: int = 7200,
        redis_url: str = "redis://localhost:6379/0",
    ) -> None:
        """Inicializa el cliente del Congreso.

        Args:
            app_token: Token de aplicacion Socrata.
            timeout_segundos: Timeout maximo por solicitud.
            max_reintentos: Numero maximo de reintentos.
            cache_ttl_segundos: TTL de cache (default 2 horas — datos legislativos cambian poco).
            redis_url: URL de conexion a Redis.
        """
        encabezados_extra: dict[str, str] = {}
        if app_token:
            encabezados_extra["X-App-Token"] = app_token

        super().__init__(
            timeout_segundos=timeout_segundos,
            max_reintentos=max_reintentos,
            encabezados_extra=encabezados_extra,
            cache_ttl_segundos=cache_ttl_segundos,
            redis_url=redis_url,
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
        """Busca proyectos de ley en el Congreso de la Republica.

        Args:
            termino_busqueda: Texto a buscar en el titulo del proyecto.
            legislatura: Legislatura (e.g., '2025-2026').
            estado: Estado del proyecto (radicado, en_debate, aprobado, etc.).
            comision: Comision asignada.
            limite: Numero maximo de resultados.
            desplazamiento: Desplazamiento para paginacion.

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
        """Normaliza un registro de proyecto de ley al esquema interno."""
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
            termino_busqueda: Texto a buscar en el titulo de la ley.
            anno: Ano de sancion.
            limite: Numero maximo de resultados.

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

    # ── Nuevos metodos Sprint 7 ────────────────────────────────────────────────

    async def buscar_norma(
        self,
        tipo: str,
        numero: Optional[int] = None,
        anio: Optional[int] = None,
        termino: Optional[str] = None,
        limite: int = 10,
    ) -> list[dict[str, Any]]:
        """Busca una norma especifica por tipo, numero y ano.

        Permite buscar normas concretas (ej: "Ley 42 de 1993") o por
        termino libre combinado con tipo.

        Args:
            tipo: Tipo de norma (ley, decreto, acto_legislativo, resolucion, acuerdo).
            numero: Numero de la norma (opcional).
            anio: Ano de la norma (opcional).
            termino: Termino de busqueda adicional (opcional).
            limite: Numero maximo de resultados.

        Returns:
            Lista de normas encontradas con su estado y datos.
        """
        tipo_normalizado = TIPOS_NORMA.get(tipo.lower(), tipo)

        condiciones: list[str] = [
            f"upper(tipo_proyecto) LIKE upper('%{tipo_normalizado}%')",
        ]

        if numero:
            condiciones.append(f"numero_proyecto LIKE '%{numero}%'")

        if anio:
            condiciones.append(f"anno='{anio}'")

        if termino:
            termino_escapado = termino.replace("'", "\\'")
            condiciones.append(f"upper(titulo_proyecto) LIKE upper('%{termino_escapado}%')")

        where_clause = " AND ".join(condiciones)

        parametros: dict[str, Any] = {
            "$where": where_clause,
            "$limit": limite,
            "$order": "fecha_radicacion DESC",
        }

        try:
            resultado: Any = await self.get("/resource/gh4g-hp3f.json", parametros=parametros)

            if not isinstance(resultado, list):
                resultado = []

            normas = []
            for proyecto in resultado:
                norma = self._normalizar_proyecto(proyecto)
                norma["tipo_norma"] = tipo_normalizado
                norma["vigente"] = proyecto.get("estado", "").lower() in ("sancionado", "vigente", "aprobado")
                normas.append(norma)

            logger.info(
                "Congreso norma: tipo=%s, numero=%s, anio=%s — %d resultados",
                tipo, numero, anio, len(normas),
            )

            return normas

        except ErrorIntegracion:
            raise
        except Exception as error:
            logger.exception("Error al buscar norma en Congreso.")
            raise ErrorIntegracion(
                servicio=self.nombre_servicio,
                mensaje=f"Error al buscar norma: {error}",
            ) from error

    async def verificar_vigencia(
        self,
        norma_id: Optional[str] = None,
        tipo: Optional[str] = None,
        numero: Optional[int] = None,
        anio: Optional[int] = None,
    ) -> dict[str, Any]:
        """Verifica si una norma sigue vigente.

        Busca la norma por su ID o por tipo/numero/ano y retorna
        su estado de vigencia con informacion de contexto.

        Args:
            norma_id: ID o numero de proyecto en la base de datos legislativa.
            tipo: Tipo de norma (ley, decreto, etc.).
            numero: Numero de la norma.
            anio: Ano de la norma.

        Returns:
            Estado de vigencia con detalle de la norma.
        """
        condiciones: list[str] = []

        if norma_id:
            condiciones.append(f"numero_proyecto='{norma_id}'")
        else:
            if tipo:
                tipo_normalizado = TIPOS_NORMA.get(tipo.lower(), tipo)
                condiciones.append(f"upper(tipo_proyecto) LIKE upper('%{tipo_normalizado}%')")
            if numero:
                condiciones.append(f"numero_proyecto LIKE '%{numero}%'")
            if anio:
                condiciones.append(f"anno='{anio}'")

        if not condiciones:
            raise ErrorIntegracion(
                servicio=self.nombre_servicio,
                mensaje="Debe especificar norma_id o al menos tipo + numero para verificar vigencia.",
            )

        where_clause = " AND ".join(condiciones)

        parametros: dict[str, Any] = {
            "$where": where_clause,
            "$limit": 5,
            "$order": "fecha_radicacion DESC",
        }

        try:
            resultado: Any = await self.get("/resource/gh4g-hp3f.json", parametros=parametros)

            if not isinstance(resultado, list) or len(resultado) == 0:
                referencia = norma_id or f"{tipo} {numero} de {anio}"
                return {
                    "norma_referencia": referencia,
                    "encontrada": False,
                    "vigente": None,
                    "mensaje": (
                        f"No se encontro la norma '{referencia}' en la base de datos legislativa. "
                        "Se recomienda verificar manualmente en el Sistema Unico de Informacion "
                        "Normativa (SUIN-Juriscol): https://www.suin-juriscol.gov.co/"
                    ),
                }

            proyecto = resultado[0]
            norma = self._normalizar_proyecto(proyecto)
            estado_proyecto = proyecto.get("estado", "").lower()

            # Determinar vigencia
            estados_vigentes = {"sancionado", "vigente", "aprobado"}
            estados_no_vigentes = {"archivado", "derogado", "retirado", "inexequible"}

            if estado_proyecto in estados_vigentes:
                vigente = True
                estado_texto = "VIGENTE"
            elif estado_proyecto in estados_no_vigentes:
                vigente = False
                estado_texto = "NO VIGENTE"
            else:
                vigente = None
                estado_texto = "INDETERMINADO"

            referencia = f"{norma.get('tipo', tipo)} {norma.get('numero', numero)}"
            if anio:
                referencia += f" de {anio}"

            resultado_vigencia: dict[str, Any] = {
                "norma_referencia": referencia,
                "encontrada": True,
                "vigente": vigente,
                "estado_legislativo": estado_proyecto,
                "estado_texto": estado_texto,
                "titulo": norma.get("titulo", ""),
                "fecha_radicacion": norma.get("fecha_radicacion"),
                "legislatura": norma.get("legislatura", ""),
                "datos_norma": norma,
                "nota": (
                    "IMPORTANTE: La verificacion de vigencia se basa en la base de datos "
                    "legislativa del Congreso. Para una verificacion definitiva, consulte "
                    "SUIN-Juriscol (https://www.suin-juriscol.gov.co/) o la Gaceta del Congreso."
                ),
            }

            logger.info(
                "Congreso vigencia: %s — estado=%s vigente=%s",
                referencia, estado_proyecto, vigente,
            )
            return resultado_vigencia

        except ErrorIntegracion:
            raise
        except Exception as error:
            logger.exception("Error al verificar vigencia de norma.")
            raise ErrorIntegracion(
                servicio=self.nombre_servicio,
                mensaje=f"Error al verificar vigencia: {error}",
            ) from error

    async def buscar_proyectos_ley(
        self,
        tema: Optional[str] = None,
        estado: Optional[str] = None,
        legislatura: Optional[str] = None,
        limite: int = 20,
    ) -> list[dict[str, Any]]:
        """Busca proyectos de ley por tema y estado.

        Wrapper convenience para buscar_proyectos con nombres
        de parametros mas claros para uso desde LangGraph tools.

        Args:
            tema: Tema o materia del proyecto de ley.
            estado: Estado del tramite (radicado, en_debate, aprobado, archivado, sancionado).
            legislatura: Legislatura (e.g., '2025-2026').
            limite: Numero maximo de resultados.

        Returns:
            Lista de proyectos de ley encontrados.
        """
        return await self.buscar_proyectos(
            termino_busqueda=tema,
            estado=estado,
            legislatura=legislatura,
            limite=limite,
        )
