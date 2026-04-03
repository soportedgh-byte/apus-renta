"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: app/integraciones/base.py
Propósito: Clase base para todas las integraciones externas — incluye cliente
           HTTP asíncrono con reintentos, manejo de errores, logging y timeouts
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
import time
from typing import Any, Optional

import httpx

logger = logging.getLogger("cecilia.integraciones.base")


class ErrorIntegracion(Exception):
    """Excepción base para errores en integraciones externas."""

    def __init__(self, servicio: str, mensaje: str, codigo_http: Optional[int] = None) -> None:
        self.servicio: str = servicio
        self.mensaje: str = mensaje
        self.codigo_http: Optional[int] = codigo_http
        super().__init__(f"[{servicio}] {mensaje} (HTTP {codigo_http})" if codigo_http else f"[{servicio}] {mensaje}")


class ErrorServicioNoDisponible(ErrorIntegracion):
    """El servicio externo no está disponible o no responde."""
    pass


class ErrorAutenticacion(ErrorIntegracion):
    """Error de autenticación contra el servicio externo."""
    pass


class ErrorLimiteConsultas(ErrorIntegracion):
    """Se excedió el límite de consultas (rate limiting)."""
    pass


class ClienteBaseIntegracion:
    """Clase base para clientes de integración con servicios externos.

    Proporciona:
    - Cliente HTTP asíncrono (httpx.AsyncClient) con pool de conexiones.
    - Lógica de reintentos con retroceso exponencial.
    - Manejo uniforme de errores HTTP.
    - Logging estructurado de solicitudes y respuestas.
    - Medición de latencia para métricas.

    Las subclases deben definir:
    - ``nombre_servicio``: Nombre legible del servicio.
    - ``url_base``: URL base del API del servicio.
    """

    nombre_servicio: str = "base"
    url_base: str = ""

    def __init__(
        self,
        url_base_override: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout_segundos: float = 30.0,
        max_reintentos: int = 3,
        factor_retroceso: float = 1.5,
        encabezados_extra: Optional[dict[str, str]] = None,
    ) -> None:
        """Inicializa el cliente de integración.

        Args:
            url_base_override: URL base alternativa (override de la default).
            api_key: Clave API para autenticación (si aplica).
            timeout_segundos: Timeout máximo por solicitud en segundos.
            max_reintentos: Número máximo de reintentos ante errores transitorios.
            factor_retroceso: Factor multiplicador para retroceso exponencial.
            encabezados_extra: Encabezados HTTP adicionales.
        """
        self._url_base: str = url_base_override or self.url_base
        self._api_key: Optional[str] = api_key
        self._timeout: float = timeout_segundos
        self._max_reintentos: int = max_reintentos
        self._factor_retroceso: float = factor_retroceso

        encabezados_base: dict[str, str] = {
            "User-Agent": "CecilIA-v2/2.0.0 (CGR-Colombia)",
            "Accept": "application/json",
        }
        if api_key:
            encabezados_base["Authorization"] = f"Bearer {api_key}"
        if encabezados_extra:
            encabezados_base.update(encabezados_extra)

        self._cliente: httpx.AsyncClient = httpx.AsyncClient(
            base_url=self._url_base,
            headers=encabezados_base,
            timeout=httpx.Timeout(timeout_segundos),
            follow_redirects=True,
        )

    async def cerrar(self) -> None:
        """Cierra el cliente HTTP y libera recursos."""
        await self._cliente.aclose()
        logger.info("[%s] Cliente HTTP cerrado.", self.nombre_servicio)

    async def __aenter__(self) -> ClienteBaseIntegracion:
        """Soporte para uso con ``async with``."""
        return self

    async def __aexit__(self, tipo_exc: Any, valor_exc: Any, traza: Any) -> None:
        """Cierra el cliente al salir del contexto."""
        await self.cerrar()

    def _clasificar_error_http(self, respuesta: httpx.Response) -> ErrorIntegracion:
        """Clasifica un error HTTP en una excepción específica.

        Args:
            respuesta: Respuesta HTTP con código de error.

        Returns:
            Excepción tipada según el código de error.
        """
        codigo: int = respuesta.status_code
        cuerpo: str = respuesta.text[:500]

        if codigo == 401 or codigo == 403:
            return ErrorAutenticacion(
                servicio=self.nombre_servicio,
                mensaje=f"Autenticación fallida: {cuerpo}",
                codigo_http=codigo,
            )
        elif codigo == 429:
            return ErrorLimiteConsultas(
                servicio=self.nombre_servicio,
                mensaje=f"Límite de consultas excedido: {cuerpo}",
                codigo_http=codigo,
            )
        elif codigo >= 500:
            return ErrorServicioNoDisponible(
                servicio=self.nombre_servicio,
                mensaje=f"Servicio no disponible: {cuerpo}",
                codigo_http=codigo,
            )
        else:
            return ErrorIntegracion(
                servicio=self.nombre_servicio,
                mensaje=f"Error HTTP {codigo}: {cuerpo}",
                codigo_http=codigo,
            )

    def _es_error_reintentable(self, error: Exception) -> bool:
        """Determina si un error justifica un reintento.

        Args:
            error: Excepción capturada.

        Returns:
            True si el error es transitorio y vale la pena reintentar.
        """
        if isinstance(error, (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError)):
            return True
        if isinstance(error, ErrorServicioNoDisponible):
            return True
        if isinstance(error, ErrorLimiteConsultas):
            return True
        return False

    async def _solicitud_con_reintentos(
        self,
        metodo: str,
        ruta: str,
        parametros: Optional[dict[str, Any]] = None,
        cuerpo_json: Optional[dict[str, Any]] = None,
        encabezados: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Ejecuta una solicitud HTTP con lógica de reintentos.

        Args:
            metodo: Método HTTP (GET, POST, PUT, DELETE).
            ruta: Ruta relativa al URL base.
            parametros: Parámetros de consulta (query string).
            cuerpo_json: Cuerpo de la solicitud en formato JSON.
            encabezados: Encabezados HTTP adicionales para esta solicitud.

        Returns:
            Respuesta deserializada como diccionario.

        Raises:
            ErrorIntegracion: Si la solicitud falla después de todos los reintentos.
        """
        ultimo_error: Optional[Exception] = None

        for intento in range(self._max_reintentos + 1):
            inicio: float = time.monotonic()
            try:
                respuesta: httpx.Response = await self._cliente.request(
                    method=metodo,
                    url=ruta,
                    params=parametros,
                    json=cuerpo_json,
                    headers=encabezados,
                )

                duracion_ms: float = (time.monotonic() - inicio) * 1000

                logger.info(
                    "[%s] %s %s → %d (%0.1fms)",
                    self.nombre_servicio, metodo, ruta, respuesta.status_code, duracion_ms,
                )

                if respuesta.is_success:
                    try:
                        return respuesta.json()
                    except Exception:
                        return {"contenido_texto": respuesta.text}

                error_tipado: ErrorIntegracion = self._clasificar_error_http(respuesta)

                if not self._es_error_reintentable(error_tipado) or intento == self._max_reintentos:
                    raise error_tipado

                ultimo_error = error_tipado

            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError) as error_conexion:
                duracion_ms = (time.monotonic() - inicio) * 1000
                logger.warning(
                    "[%s] %s %s → Error de conexión (%0.1fms, intento %d/%d): %s",
                    self.nombre_servicio, metodo, ruta, duracion_ms,
                    intento + 1, self._max_reintentos + 1, str(error_conexion),
                )
                ultimo_error = error_conexion

                if intento == self._max_reintentos:
                    raise ErrorServicioNoDisponible(
                        servicio=self.nombre_servicio,
                        mensaje=f"Servicio no accesible después de {self._max_reintentos + 1} intentos: {error_conexion}",
                    ) from error_conexion

            # Retroceso exponencial entre reintentos
            import asyncio
            espera_segundos: float = self._factor_retroceso ** intento
            logger.info(
                "[%s] Reintentando en %0.1f segundos (intento %d/%d)...",
                self.nombre_servicio, espera_segundos, intento + 2, self._max_reintentos + 1,
            )
            await asyncio.sleep(espera_segundos)

        # No debería llegar aquí, pero por seguridad
        raise ErrorIntegracion(
            servicio=self.nombre_servicio,
            mensaje=f"Falló después de {self._max_reintentos + 1} intentos: {ultimo_error}",
        )

    # ── Métodos de conveniencia ──────────────────────────────────────────────

    async def get(
        self,
        ruta: str,
        parametros: Optional[dict[str, Any]] = None,
        encabezados: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Realiza una solicitud GET.

        Args:
            ruta: Ruta relativa al URL base.
            parametros: Parámetros de consulta.
            encabezados: Encabezados adicionales.

        Returns:
            Respuesta deserializada.
        """
        return await self._solicitud_con_reintentos("GET", ruta, parametros=parametros, encabezados=encabezados)

    async def post(
        self,
        ruta: str,
        cuerpo_json: Optional[dict[str, Any]] = None,
        parametros: Optional[dict[str, Any]] = None,
        encabezados: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Realiza una solicitud POST.

        Args:
            ruta: Ruta relativa al URL base.
            cuerpo_json: Cuerpo JSON de la solicitud.
            parametros: Parámetros de consulta.
            encabezados: Encabezados adicionales.

        Returns:
            Respuesta deserializada.
        """
        return await self._solicitud_con_reintentos(
            "POST", ruta, parametros=parametros, cuerpo_json=cuerpo_json, encabezados=encabezados,
        )

    async def verificar_salud(self) -> dict[str, Any]:
        """Verifica la conectividad y salud del servicio externo.

        Returns:
            Diccionario con estado, latencia y mensaje del servicio.
        """
        inicio: float = time.monotonic()
        try:
            respuesta: httpx.Response = await self._cliente.get("/", timeout=10.0)
            duracion_ms: float = (time.monotonic() - inicio) * 1000

            estado: str = "disponible" if respuesta.is_success else "degradado"
            return {
                "servicio": self.nombre_servicio,
                "estado": estado,
                "latencia_ms": round(duracion_ms, 1),
                "codigo_http": respuesta.status_code,
            }
        except Exception as error:
            duracion_ms = (time.monotonic() - inicio) * 1000
            return {
                "servicio": self.nombre_servicio,
                "estado": "no_disponible",
                "latencia_ms": round(duracion_ms, 1),
                "error": str(error),
            }
