"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/integraciones/dane.py
Proposito: Integracion con el DANE (Departamento Administrativo Nacional de
           Estadistica) — indicadores economicos, IPC, PIB sectorial, TIC
Sprint: 7
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from app.integraciones.base import ClienteBaseIntegracion, ErrorIntegracion

logger = logging.getLogger("cecilia.integraciones.dane")


# ── Catalogo de indicadores DANE disponibles ─────────────────────────────────

INDICADORES_DANE: dict[str, dict[str, str]] = {
    "ipc": {
        "nombre": "Indice de Precios al Consumidor",
        "recurso": "resource/e3bh-7i6m.json",
        "descripcion": "Variacion mensual y anual del IPC",
    },
    "pib": {
        "nombre": "Producto Interno Bruto",
        "recurso": "resource/b2nx-ptt9.json",
        "descripcion": "PIB trimestral a precios constantes y corrientes",
    },
    "desempleo": {
        "nombre": "Tasa de Desempleo",
        "recurso": "resource/bxi4-jqqq.json",
        "descripcion": "Tasa de desempleo por dominios geograficos",
    },
    "pobreza": {
        "nombre": "Pobreza Monetaria",
        "recurso": "resource/357w-gfwf.json",
        "descripcion": "Incidencia de pobreza y pobreza extrema",
    },
    "poblacion": {
        "nombre": "Proyecciones de Poblacion",
        "recurso": "resource/nlxt-nnu6.json",
        "descripcion": "Proyecciones de poblacion por departamento y municipio",
    },
    "tic": {
        "nombre": "Indicadores TIC",
        "recurso": "resource/mc84-bphe.json",
        "descripcion": "Indicadores de tecnologias de la informacion y las comunicaciones",
    },
}

# ── Sectores economicos para PIB sectorial ────────────────────────────────────

SECTORES_PIB: dict[str, str] = {
    "agricultura": "Agricultura, ganaderia, caza, silvicultura y pesca",
    "mineria": "Explotacion de minas y canteras",
    "manufactura": "Industrias manufactureras",
    "energia": "Suministro de electricidad, gas, vapor y aire acondicionado",
    "agua": "Distribucion de agua, evacuacion y tratamiento de aguas residuales",
    "construccion": "Construccion",
    "comercio": "Comercio al por mayor y al por menor",
    "transporte": "Transporte y almacenamiento",
    "alojamiento": "Alojamiento y servicios de comida",
    "informacion": "Informacion y comunicaciones",
    "financiero": "Actividades financieras y de seguros",
    "inmobiliario": "Actividades inmobiliarias",
    "profesional": "Actividades profesionales, cientificas y tecnicas",
    "administracion_publica": "Administracion publica y defensa",
    "educacion": "Educacion",
    "salud": "Actividades de atencion de la salud humana",
    "entretenimiento": "Actividades artisticas, de entretenimiento y recreacion",
}


class ClienteDANE(ClienteBaseIntegracion):
    """Cliente para consulta de indicadores estadisticos del DANE.

    Accede a la API publica del DANE hospedada en datos.gov.co
    para obtener indicadores economicos, sociales y demograficos
    de Colombia, utiles como contexto para procesos de auditoria.

    Metodos disponibles:
    - obtener_indicador: Consulta generica de cualquier indicador
    - buscar_por_categoria: Busqueda por categoria tematica
    - obtener_ipc: IPC para un periodo especifico
    - obtener_pib_sectorial: PIB por sector economico
    - obtener_estadisticas_tic: Indicadores de TIC
    """

    nombre_servicio: str = "DANE"
    url_base: str = "https://www.datos.gov.co"

    def __init__(
        self,
        app_token: Optional[str] = None,
        timeout_segundos: float = 30.0,
        max_reintentos: int = 3,
        cache_ttl_segundos: int = 7200,
        redis_url: str = "redis://localhost:6379/0",
    ) -> None:
        """Inicializa el cliente DANE.

        Args:
            app_token: Token de aplicacion Socrata para mayor cuota de consultas.
            timeout_segundos: Timeout maximo por solicitud.
            max_reintentos: Numero maximo de reintentos.
            cache_ttl_segundos: TTL de cache (default 2 horas — datos estadisticos cambian poco).
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

    def obtener_indicadores_disponibles(self) -> dict[str, dict[str, str]]:
        """Retorna el catalogo de indicadores disponibles."""
        return INDICADORES_DANE.copy()

    async def obtener_indicador(
        self,
        codigo_indicador: str,
        periodo: Optional[str] = None,
        departamento: Optional[str] = None,
        limite: int = 20,
    ) -> list[dict[str, Any]]:
        """Consulta un indicador DANE especifico.

        Args:
            codigo_indicador: Codigo del indicador (ipc, pib, desempleo, etc.).
            periodo: Periodo de consulta (formato libre, depende del indicador).
            departamento: Codigo DIVIPOLA del departamento para filtrado geografico.
            limite: Numero maximo de registros a retornar.

        Returns:
            Lista de registros del indicador.

        Raises:
            ErrorIntegracion: Si el codigo de indicador no es valido o hay error de consulta.
        """
        if codigo_indicador not in INDICADORES_DANE:
            raise ErrorIntegracion(
                servicio=self.nombre_servicio,
                mensaje=f"Indicador '{codigo_indicador}' no existe. Disponibles: {list(INDICADORES_DANE.keys())}",
            )

        info_indicador: dict[str, str] = INDICADORES_DANE[codigo_indicador]
        ruta: str = f"/{info_indicador['recurso']}"

        parametros: dict[str, Any] = {"$limit": limite}

        if periodo:
            parametros["$where"] = f"anno='{periodo}'" if len(periodo) == 4 else f"periodo='{periodo}'"

        if departamento:
            clave_depto: str = "codigo_departamento" if codigo_indicador != "pib" else "departamento"
            if "$where" in parametros:
                parametros["$where"] += f" AND {clave_depto}='{departamento}'"
            else:
                parametros["$where"] = f"{clave_depto}='{departamento}'"

        try:
            resultado: Any = await self.get(ruta, parametros=parametros)

            if isinstance(resultado, list):
                registros_normalizados: list[dict[str, Any]] = [
                    self._normalizar_indicador(codigo_indicador, registro)
                    for registro in resultado
                ]
                logger.info(
                    "DANE: %d registros obtenidos para indicador '%s' (periodo=%s, depto=%s)",
                    len(registros_normalizados), codigo_indicador, periodo, departamento,
                )
                return registros_normalizados

            return []

        except ErrorIntegracion:
            raise
        except Exception as error:
            logger.exception("Error al consultar indicador DANE '%s'.", codigo_indicador)
            raise ErrorIntegracion(
                servicio=self.nombre_servicio,
                mensaje=f"Error al consultar '{codigo_indicador}': {error}",
            ) from error

    def _normalizar_indicador(self, codigo: str, registro_raw: dict[str, Any]) -> dict[str, Any]:
        """Normaliza un registro de indicador DANE al esquema interno."""
        info: dict[str, str] = INDICADORES_DANE[codigo]
        return {
            "codigo": codigo,
            "nombre": info["nombre"],
            "valor": float(registro_raw.get("valor", registro_raw.get("dato", 0))),
            "unidad": registro_raw.get("unidad_medida", ""),
            "periodo": registro_raw.get("anno", registro_raw.get("periodo", "")),
            "fuente": f"DANE — {info['nombre']}",
            "fecha_publicacion": registro_raw.get("fecha_publicacion"),
            "datos_completos": registro_raw,
        }

    async def buscar_por_categoria(
        self,
        categoria: str,
        limite: int = 20,
    ) -> list[dict[str, Any]]:
        """Busca indicadores por categoria tematica.

        Args:
            categoria: Categoria: pib | ipc | desempleo | pobreza | poblacion | tic.
            limite: Numero maximo de registros.

        Returns:
            Lista de registros del indicador de la categoria solicitada.
        """
        if categoria.lower() not in INDICADORES_DANE:
            categorias_validas: list[str] = list(INDICADORES_DANE.keys())
            raise ErrorIntegracion(
                servicio=self.nombre_servicio,
                mensaje=f"Categoria '{categoria}' no valida. Disponibles: {categorias_validas}",
            )

        return await self.obtener_indicador(
            codigo_indicador=categoria.lower(),
            limite=limite,
        )

    # ── Nuevos metodos Sprint 7 ────────────────────────────────────────────────

    async def obtener_ipc(
        self,
        periodo: Optional[str] = None,
        departamento: Optional[str] = None,
        limite: int = 12,
    ) -> dict[str, Any]:
        """Obtiene el Indice de Precios al Consumidor (IPC).

        Retorna los datos del IPC para un periodo especifico o los ultimos
        12 meses, con variaciones mensuales y anuales.

        Args:
            periodo: Ano (e.g., '2025') o periodo especifico.
            departamento: Codigo DIVIPOLA del departamento.
            limite: Numero de registros (default 12 = ultimo ano).

        Returns:
            Datos del IPC con valores, variaciones y contexto.
        """
        registros = await self.obtener_indicador(
            codigo_indicador="ipc",
            periodo=periodo,
            departamento=departamento,
            limite=limite,
        )

        if not registros:
            return {
                "indicador": "IPC",
                "periodo": periodo,
                "datos_encontrados": False,
                "mensaje": "No se encontraron datos de IPC para el periodo solicitado.",
            }

        # Extraer valores para calcular estadisticas
        valores = [r.get("valor", 0) for r in registros]
        ultimo_valor = valores[0] if valores else 0

        resultado: dict[str, Any] = {
            "indicador": "Indice de Precios al Consumidor (IPC)",
            "periodo_consultado": periodo or "ultimos registros",
            "departamento": departamento,
            "datos_encontrados": True,
            "ultimo_valor": ultimo_valor,
            "total_registros": len(registros),
            "registros": registros,
            "fuente": "DANE — Indice de Precios al Consumidor",
            "nota": (
                "El IPC mide la variacion promedio de los precios de una "
                "canasta de bienes y servicios representativa del consumo "
                "final de los hogares. Base 100 = Dic 2018."
            ),
        }

        logger.info("DANE IPC: periodo=%s — %d registros, ultimo=%s", periodo, len(registros), ultimo_valor)
        return resultado

    async def obtener_pib_sectorial(
        self,
        sector: Optional[str] = None,
        periodo: Optional[str] = None,
        limite: int = 20,
    ) -> dict[str, Any]:
        """Obtiene el PIB desglosado por sector economico.

        Permite consultar el PIB de un sector especifico o el desglose
        general por sectores para un periodo dado.

        Args:
            sector: Codigo del sector (agricultura, mineria, manufactura, etc.).
                    Si es None, retorna todos los sectores.
            periodo: Ano o trimestre de consulta.
            limite: Numero maximo de registros.

        Returns:
            Datos del PIB sectorial con valores y participacion.
        """
        condiciones: list[str] = []

        if periodo:
            condiciones.append(f"anno='{periodo}'" if len(periodo) == 4 else f"periodo='{periodo}'")

        if sector:
            sector_lower = sector.lower()
            nombre_sector = SECTORES_PIB.get(sector_lower, sector)
            nombre_escapado = nombre_sector.replace("'", "\\'")
            condiciones.append(f"upper(actividad_economica) LIKE upper('%{nombre_escapado}%')")

        info_pib = INDICADORES_DANE["pib"]
        ruta = f"/{info_pib['recurso']}"

        parametros: dict[str, Any] = {
            "$limit": limite,
            "$order": "anno DESC",
        }
        if condiciones:
            parametros["$where"] = " AND ".join(condiciones)

        try:
            resultado: Any = await self.get(ruta, parametros=parametros)

            if not isinstance(resultado, list):
                resultado = []

            registros = [self._normalizar_indicador("pib", r) for r in resultado]

            resultado_pib: dict[str, Any] = {
                "indicador": "Producto Interno Bruto",
                "sector": sector or "todos",
                "sector_nombre": SECTORES_PIB.get(sector.lower(), sector) if sector else "Todos los sectores",
                "periodo_consultado": periodo or "ultimos registros",
                "datos_encontrados": len(registros) > 0,
                "total_registros": len(registros),
                "registros": registros,
                "sectores_disponibles": list(SECTORES_PIB.keys()),
                "fuente": "DANE — Cuentas Nacionales Trimestrales",
            }

            logger.info("DANE PIB sectorial: sector=%s, periodo=%s — %d registros", sector, periodo, len(registros))
            return resultado_pib

        except ErrorIntegracion:
            raise
        except Exception as error:
            logger.exception("Error al consultar PIB sectorial.")
            raise ErrorIntegracion(
                servicio=self.nombre_servicio,
                mensaje=f"Error al consultar PIB sectorial: {error}",
            ) from error

    async def obtener_estadisticas_tic(
        self,
        indicador: Optional[str] = None,
        periodo: Optional[str] = None,
        departamento: Optional[str] = None,
        limite: int = 20,
    ) -> dict[str, Any]:
        """Obtiene estadisticas de Tecnologias de la Informacion y Comunicaciones.

        Indicadores TIC relevantes para auditorias del sector TIC:
        penetracion de internet, suscriptores, inversion en TIC, etc.

        Args:
            indicador: Indicador TIC especifico (internet, movil, fijo, inversion).
            periodo: Ano o periodo de consulta.
            departamento: Codigo DIVIPOLA del departamento.
            limite: Numero maximo de registros.

        Returns:
            Estadisticas TIC con valores y contexto.
        """
        info_tic = INDICADORES_DANE.get("tic")
        if not info_tic:
            raise ErrorIntegracion(
                servicio=self.nombre_servicio,
                mensaje="Indicador TIC no configurado en el catalogo.",
            )

        ruta = f"/{info_tic['recurso']}"
        condiciones: list[str] = []

        if periodo:
            condiciones.append(f"anno='{periodo}'" if len(periodo) == 4 else f"periodo='{periodo}'")

        if indicador:
            indicador_escapado = indicador.replace("'", "\\'")
            condiciones.append(f"upper(indicador) LIKE upper('%{indicador_escapado}%')")

        if departamento:
            condiciones.append(f"codigo_departamento='{departamento}'")

        parametros: dict[str, Any] = {
            "$limit": limite,
            "$order": "anno DESC",
        }
        if condiciones:
            parametros["$where"] = " AND ".join(condiciones)

        try:
            resultado: Any = await self.get(ruta, parametros=parametros)

            if not isinstance(resultado, list):
                resultado = []

            registros = [self._normalizar_indicador("tic", r) for r in resultado]

            resultado_tic: dict[str, Any] = {
                "indicador": "Estadisticas TIC",
                "indicador_especifico": indicador or "todos",
                "periodo_consultado": periodo or "ultimos registros",
                "departamento": departamento,
                "datos_encontrados": len(registros) > 0,
                "total_registros": len(registros),
                "registros": registros,
                "fuente": "DANE — Indicadores de TIC",
                "nota": (
                    "Indicadores de penetracion, uso y acceso a tecnologias "
                    "de la informacion y las comunicaciones en Colombia. "
                    "Datos relevantes para auditorias del sector TIC y "
                    "evaluacion de programas de gobierno digital."
                ),
            }

            logger.info(
                "DANE TIC: indicador=%s, periodo=%s — %d registros",
                indicador, periodo, len(registros),
            )
            return resultado_tic

        except ErrorIntegracion:
            raise
        except Exception as error:
            logger.exception("Error al consultar estadisticas TIC.")
            raise ErrorIntegracion(
                servicio=self.nombre_servicio,
                mensaje=f"Error al consultar estadisticas TIC: {error}",
            ) from error
