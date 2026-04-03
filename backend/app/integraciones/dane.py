"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: app/integraciones/dane.py
Propósito: Integración con el DANE (Departamento Administrativo Nacional de
           Estadística) — consulta de indicadores económicos y sociales
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from app.integraciones.base import ClienteBaseIntegracion, ErrorIntegracion

logger = logging.getLogger("cecilia.integraciones.dane")


# ── Catálogo de indicadores DANE disponibles ─────────────────────────────────

INDICADORES_DANE: dict[str, dict[str, str]] = {
    "ipc": {
        "nombre": "Índice de Precios al Consumidor",
        "recurso": "resource/e3bh-7i6m.json",
        "descripcion": "Variación mensual y anual del IPC",
    },
    "pib": {
        "nombre": "Producto Interno Bruto",
        "recurso": "resource/b2nx-ptt9.json",
        "descripcion": "PIB trimestral a precios constantes y corrientes",
    },
    "desempleo": {
        "nombre": "Tasa de Desempleo",
        "recurso": "resource/bxi4-jqqq.json",
        "descripcion": "Tasa de desempleo por dominios geográficos",
    },
    "pobreza": {
        "nombre": "Pobreza Monetaria",
        "recurso": "resource/357w-gfwf.json",
        "descripcion": "Incidencia de pobreza y pobreza extrema",
    },
    "poblacion": {
        "nombre": "Proyecciones de Población",
        "recurso": "resource/nlxt-nnu6.json",
        "descripcion": "Proyecciones de población por departamento y municipio",
    },
}


class ClienteDANE(ClienteBaseIntegracion):
    """Cliente para consulta de indicadores estadísticos del DANE.

    Accede a la API pública del DANE hospedada en datos.gov.co
    para obtener indicadores económicos, sociales y demográficos
    de Colombia, útiles como contexto para procesos de auditoría.
    """

    nombre_servicio: str = "DANE"
    url_base: str = "https://www.datos.gov.co"

    def __init__(
        self,
        app_token: Optional[str] = None,
        timeout_segundos: float = 30.0,
        max_reintentos: int = 3,
    ) -> None:
        """Inicializa el cliente DANE.

        Args:
            app_token: Token de aplicación Socrata para mayor cuota de consultas.
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

    def obtener_indicadores_disponibles(self) -> dict[str, dict[str, str]]:
        """Retorna el catálogo de indicadores disponibles.

        Returns:
            Diccionario con código, nombre y descripción de cada indicador.
        """
        return INDICADORES_DANE.copy()

    async def obtener_indicador(
        self,
        codigo_indicador: str,
        periodo: Optional[str] = None,
        departamento: Optional[str] = None,
        limite: int = 20,
    ) -> list[dict[str, Any]]:
        """Consulta un indicador DANE específico.

        Args:
            codigo_indicador: Código del indicador (ipc, pib, desempleo, etc.).
            periodo: Periodo de consulta (formato libre, depende del indicador).
            departamento: Código DIVIPOLA del departamento para filtrado geográfico.
            limite: Número máximo de registros a retornar.

        Returns:
            Lista de registros del indicador.

        Raises:
            ErrorIntegracion: Si el código de indicador no es válido o hay error de consulta.
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
        """Normaliza un registro de indicador DANE al esquema interno.

        Args:
            codigo: Código del indicador.
            registro_raw: Diccionario crudo de la API.

        Returns:
            Diccionario con campos normalizados.
        """
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
        """Busca indicadores por categoría temática.

        Args:
            categoria: Categoría: pib | ipc | desempleo | pobreza | poblacion.
            limite: Número máximo de registros.

        Returns:
            Lista de registros del indicador de la categoría solicitada.
        """
        # La categoría mapea directamente a un indicador en nuestro catálogo
        if categoria.lower() not in INDICADORES_DANE:
            categorias_validas: list[str] = list(INDICADORES_DANE.keys())
            raise ErrorIntegracion(
                servicio=self.nombre_servicio,
                mensaje=f"Categoría '{categoria}' no válida. Disponibles: {categorias_validas}",
            )

        return await self.obtener_indicador(
            codigo_indicador=categoria.lower(),
            limite=limite,
        )
