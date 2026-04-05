"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/integraciones/secop.py
Proposito: Integracion con SECOP II (Sistema Electronico de Contratacion Publica)
           — consulta de contratos, contratistas y analisis de precios
Sprint: 7
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
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
    """Cliente para consulta de contratos publicos en SECOP II.

    Utiliza la API abierta de datos.gov.co (plataforma Socrata) para
    acceder a los registros de contratacion publica de Colombia.

    Metodos disponibles:
    - buscar_contratos: Busqueda con multiples filtros
    - buscar_procesos: Procesos de contratacion
    - buscar_contratista: Busca contratos por NIT o nombre de contratista
    - obtener_detalle_contrato: Detalle completo de un proceso
    - analizar_precios_mercado: Analisis de precios por objeto contractual y region
    """

    nombre_servicio: str = "SECOP II"
    url_base: str = "https://www.datos.gov.co"

    def __init__(
        self,
        app_token: Optional[str] = None,
        timeout_segundos: float = 30.0,
        max_reintentos: int = 3,
        cache_ttl_segundos: int = 3600,
        redis_url: str = "redis://localhost:6379/0",
    ) -> None:
        """Inicializa el cliente SECOP.

        Args:
            app_token: Token de aplicacion de Socrata (datos.gov.co) para mayor cuota.
            timeout_segundos: Timeout maximo por solicitud.
            max_reintentos: Numero maximo de reintentos.
            cache_ttl_segundos: TTL de cache en segundos (default 1 hora).
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
        """Busca contratos en SECOP II con multiples filtros.

        Args:
            entidad: Nombre (parcial) de la entidad compradora.
            contratista: Nombre o NIT del contratista.
            numero_proceso: Numero del proceso de contratacion.
            valor_minimo: Valor minimo del contrato en pesos.
            valor_maximo: Valor maximo del contrato en pesos.
            limite: Numero maximo de resultados.
            desplazamiento: Desplazamiento para paginacion.

        Returns:
            Lista de contratos encontrados.
        """
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
        """Normaliza un registro de contrato SECOP al esquema interno."""
        return {
            "id_contrato": contrato_raw.get("id_del_portafolio", ""),
            "numero_proceso": contrato_raw.get("referencia_del_contrato", ""),
            "entidad_compradora": contrato_raw.get("nombre_entidad", ""),
            "contratista": contrato_raw.get("proveedor_adjudicado", ""),
            "nit_contratista": contrato_raw.get("nit_del_proveedor_adjudicado", ""),
            "objeto": contrato_raw.get("descripcion_del_proceso", ""),
            "valor_total": float(contrato_raw.get("valor_del_contrato", 0)),
            "fecha_firma": contrato_raw.get("fecha_de_firma"),
            "fecha_inicio": contrato_raw.get("fecha_de_inicio_del_contrato"),
            "fecha_fin": contrato_raw.get("fecha_de_fin_del_contrato"),
            "estado": contrato_raw.get("estado_contrato", ""),
            "tipo_contrato": contrato_raw.get("tipo_de_contrato", ""),
            "modalidad": contrato_raw.get("modalidad_de_contratacion", ""),
            "departamento": contrato_raw.get("departamento", ""),
            "municipio": contrato_raw.get("ciudad", ""),
            "url_secop": contrato_raw.get("urlproceso", {}).get("url", "") if isinstance(contrato_raw.get("urlproceso"), dict) else "",
        }

    async def buscar_procesos(
        self,
        entidad: Optional[str] = None,
        estado: Optional[str] = None,
        modalidad: Optional[str] = None,
        limite: int = 20,
    ) -> list[dict[str, Any]]:
        """Busca procesos de contratacion en SECOP II.

        Args:
            entidad: Nombre de la entidad compradora.
            estado: Estado del proceso (Publicado, Adjudicado, Celebrado, etc.).
            modalidad: Modalidad de contratacion.
            limite: Numero maximo de resultados.

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

    # ── Nuevos metodos Sprint 7 ────────────────────────────────────────────────

    async def buscar_contratista(
        self,
        nit_o_nombre: str,
        limite: int = 50,
    ) -> dict[str, Any]:
        """Busca contratos de un contratista por NIT o nombre.

        Retorna un resumen con todos los contratos del contratista,
        valor total contratado y entidades con las que ha contratado.

        Args:
            nit_o_nombre: NIT o nombre (parcial) del contratista.
            limite: Numero maximo de contratos a consultar.

        Returns:
            Resumen del contratista con contratos, valor total y entidades.
        """
        # Determinar si es NIT (numerico) o nombre
        es_nit = nit_o_nombre.replace("-", "").replace(".", "").isdigit()

        if es_nit:
            nit_limpio = nit_o_nombre.replace("-", "").replace(".", "")
            where_clause = f"nit_del_proveedor_adjudicado='{nit_limpio}'"
        else:
            nombre_escapado = nit_o_nombre.replace("'", "\\'")
            where_clause = f"upper(proveedor_adjudicado) LIKE upper('%{nombre_escapado}%')"

        parametros: dict[str, Any] = {
            "$where": where_clause,
            "$limit": limite,
            "$order": "fecha_de_firma DESC",
        }

        try:
            resultado: Any = await self.get("/resource/jbjy-vk9h.json", parametros=parametros)

            if not isinstance(resultado, list):
                resultado = []

            contratos = [self._normalizar_contrato(c) for c in resultado]

            # Calcular resumen
            valor_total = sum(c.get("valor_total", 0) for c in contratos)
            entidades = list(set(c.get("entidad_compradora", "") for c in contratos if c.get("entidad_compradora")))
            tipos_contrato = list(set(c.get("tipo_contrato", "") for c in contratos if c.get("tipo_contrato")))

            resumen: dict[str, Any] = {
                "busqueda": nit_o_nombre,
                "tipo_busqueda": "NIT" if es_nit else "nombre",
                "total_contratos": len(contratos),
                "valor_total_contratado": valor_total,
                "entidades_contratantes": entidades,
                "tipos_contrato": tipos_contrato,
                "contratos": contratos,
            }

            logger.info(
                "SECOP contratista: '%s' — %d contratos, $%s total",
                nit_o_nombre, len(contratos), f"{valor_total:,.0f}",
            )
            return resumen

        except ErrorIntegracion:
            raise
        except Exception as error:
            logger.exception("Error al buscar contratista en SECOP.")
            raise ErrorIntegracion(
                servicio=self.nombre_servicio,
                mensaje=f"Error al buscar contratista '{nit_o_nombre}': {error}",
            ) from error

    async def obtener_detalle_contrato(
        self,
        numero_proceso: str,
    ) -> dict[str, Any]:
        """Obtiene el detalle completo de un contrato por numero de proceso.

        Args:
            numero_proceso: Numero o ID del proceso contractual.

        Returns:
            Detalle completo del contrato con todos los campos disponibles.
        """
        parametros: dict[str, Any] = {
            "$where": f"id_del_portafolio='{numero_proceso}' OR referencia_del_contrato='{numero_proceso}'",
            "$limit": 1,
        }

        try:
            resultado: Any = await self.get("/resource/jbjy-vk9h.json", parametros=parametros)

            if isinstance(resultado, list) and len(resultado) > 0:
                contrato_raw = resultado[0]
                detalle = self._normalizar_contrato(contrato_raw)
                # Agregar campos adicionales de detalle
                detalle["datos_completos"] = contrato_raw
                detalle["adiciones"] = float(contrato_raw.get("valor_de_pago_adelantado", 0))
                detalle["observaciones"] = contrato_raw.get("descripcion_del_proceso", "")

                logger.info("SECOP detalle: proceso '%s' encontrado.", numero_proceso)
                return detalle

            return {
                "numero_proceso": numero_proceso,
                "encontrado": False,
                "mensaje": f"No se encontro el proceso '{numero_proceso}' en SECOP II.",
            }

        except ErrorIntegracion:
            raise
        except Exception as error:
            logger.exception("Error al obtener detalle de contrato SECOP.")
            raise ErrorIntegracion(
                servicio=self.nombre_servicio,
                mensaje=f"Error al obtener detalle del proceso '{numero_proceso}': {error}",
            ) from error

    async def analizar_precios_mercado(
        self,
        objeto_contractual: str,
        region: Optional[str] = None,
        anno: Optional[int] = None,
        limite: int = 100,
    ) -> dict[str, Any]:
        """Analiza precios de mercado para un tipo de objeto contractual.

        Consulta contratos similares para establecer rangos de precios,
        promedios y desviaciones. Util para detectar sobreprecios o
        anomalias en la contratacion.

        Args:
            objeto_contractual: Descripcion del objeto contractual a analizar.
            region: Departamento o region para filtrar (opcional).
            anno: Ano de los contratos a considerar (opcional).
            limite: Numero maximo de contratos para el analisis.

        Returns:
            Analisis de precios con estadisticas, rango y contratos similares.
        """
        objeto_escapado = objeto_contractual.replace("'", "\\'")
        condiciones: list[str] = [
            f"upper(descripcion_del_proceso) LIKE upper('%{objeto_escapado}%')",
        ]

        if region:
            region_escapada = region.replace("'", "\\'")
            condiciones.append(f"upper(departamento) LIKE upper('%{region_escapada}%')")

        if anno:
            condiciones.append(f"fecha_de_firma >= '{anno}-01-01T00:00:00' AND fecha_de_firma <= '{anno}-12-31T23:59:59'")

        where_clause = " AND ".join(condiciones)

        parametros: dict[str, Any] = {
            "$where": where_clause,
            "$limit": limite,
            "$order": "fecha_de_firma DESC",
            "$select": "nombre_entidad, proveedor_adjudicado, valor_del_contrato, fecha_de_firma, departamento, tipo_de_contrato, descripcion_del_proceso",
        }

        try:
            resultado: Any = await self.get("/resource/jbjy-vk9h.json", parametros=parametros)

            if not isinstance(resultado, list):
                resultado = []

            valores = [float(c.get("valor_del_contrato", 0)) for c in resultado if c.get("valor_del_contrato")]
            valores = [v for v in valores if v > 0]

            if not valores:
                return {
                    "objeto_contractual": objeto_contractual,
                    "region": region,
                    "anno": anno,
                    "total_contratos_similares": 0,
                    "mensaje": "No se encontraron contratos similares para el analisis de precios.",
                }

            valores_ordenados = sorted(valores)
            n = len(valores_ordenados)
            promedio = sum(valores_ordenados) / n
            mediana = valores_ordenados[n // 2] if n % 2 else (valores_ordenados[n // 2 - 1] + valores_ordenados[n // 2]) / 2
            percentil_25 = valores_ordenados[int(n * 0.25)]
            percentil_75 = valores_ordenados[int(n * 0.75)]

            # Varianza y desviacion estandar
            varianza = sum((v - promedio) ** 2 for v in valores_ordenados) / n
            desviacion = varianza ** 0.5

            analisis: dict[str, Any] = {
                "objeto_contractual": objeto_contractual,
                "region": region,
                "anno": anno,
                "total_contratos_similares": n,
                "estadisticas": {
                    "valor_minimo": min(valores_ordenados),
                    "valor_maximo": max(valores_ordenados),
                    "promedio": round(promedio, 2),
                    "mediana": round(mediana, 2),
                    "desviacion_estandar": round(desviacion, 2),
                    "percentil_25": round(percentil_25, 2),
                    "percentil_75": round(percentil_75, 2),
                },
                "rango_sugerido": {
                    "minimo": round(percentil_25, 2),
                    "maximo": round(percentil_75, 2),
                    "descripcion": f"Rango intercuartil (P25-P75) basado en {n} contratos similares.",
                },
                "muestra_contratos": [
                    {
                        "entidad": c.get("nombre_entidad", ""),
                        "contratista": c.get("proveedor_adjudicado", ""),
                        "valor": float(c.get("valor_del_contrato", 0)),
                        "fecha": c.get("fecha_de_firma", ""),
                        "departamento": c.get("departamento", ""),
                    }
                    for c in resultado[:10]
                ],
            }

            logger.info(
                "SECOP precios: '%s' — %d contratos, promedio $%s, rango $%s-$%s",
                objeto_contractual, n, f"{promedio:,.0f}",
                f"{percentil_25:,.0f}", f"{percentil_75:,.0f}",
            )
            return analisis

        except ErrorIntegracion:
            raise
        except Exception as error:
            logger.exception("Error al analizar precios de mercado SECOP.")
            raise ErrorIntegracion(
                servicio=self.nombre_servicio,
                mensaje=f"Error al analizar precios: {error}",
            ) from error
