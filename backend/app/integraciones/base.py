"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/integraciones/base.py
Proposito: Clase base para todas las integraciones externas — incluye cliente
           HTTP asincrono con reintentos, cache Redis (TTL configurable),
           circuit breaker (5 fallos → 5 min cooldown) y trazabilidad
Sprint: 7
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

logger = logging.getLogger("cecilia.integraciones.base")


# ── Excepciones ────────────────────────────────────────────────────────────────


class ErrorIntegracion(Exception):
    """Excepcion base para errores en integraciones externas."""

    def __init__(self, servicio: str, mensaje: str, codigo_http: Optional[int] = None) -> None:
        self.servicio: str = servicio
        self.mensaje: str = mensaje
        self.codigo_http: Optional[int] = codigo_http
        super().__init__(f"[{servicio}] {mensaje} (HTTP {codigo_http})" if codigo_http else f"[{servicio}] {mensaje}")


class ErrorServicioNoDisponible(ErrorIntegracion):
    """El servicio externo no esta disponible o no responde."""
    pass


class ErrorAutenticacion(ErrorIntegracion):
    """Error de autenticacion contra el servicio externo."""
    pass


class ErrorLimiteConsultas(ErrorIntegracion):
    """Se excedio el limite de consultas (rate limiting)."""
    pass


class ErrorCircuitoAbierto(ErrorIntegracion):
    """El circuit breaker esta abierto — servicio temporalmente bloqueado."""
    pass


# ── Circuit Breaker ────────────────────────────────────────────────────────────


class CircuitBreaker:
    """Circuit breaker para proteger contra servicios inestables.

    Politica: tras ``umbral_fallos`` errores consecutivos, el circuito se abre
    durante ``cooldown_segundos``. Durante ese periodo, todas las llamadas
    fallan inmediatamente sin contactar el servicio externo.
    """

    def __init__(
        self,
        nombre_servicio: str,
        umbral_fallos: int = 5,
        cooldown_segundos: float = 300.0,
    ) -> None:
        self.nombre_servicio = nombre_servicio
        self.umbral_fallos = umbral_fallos
        self.cooldown_segundos = cooldown_segundos
        self._fallos_consecutivos: int = 0
        self._ultimo_fallo: float = 0.0
        self._estado: str = "cerrado"  # cerrado | abierto | semi_abierto

    @property
    def estado(self) -> str:
        """Estado actual del circuito."""
        if self._estado == "abierto":
            if time.monotonic() - self._ultimo_fallo >= self.cooldown_segundos:
                self._estado = "semi_abierto"
                logger.info(
                    "[%s] Circuit breaker → semi_abierto (cooldown expirado)",
                    self.nombre_servicio,
                )
        return self._estado

    def verificar(self) -> None:
        """Verifica si se permite la llamada. Lanza excepcion si el circuito esta abierto."""
        estado_actual = self.estado
        if estado_actual == "abierto":
            tiempo_restante = self.cooldown_segundos - (time.monotonic() - self._ultimo_fallo)
            raise ErrorCircuitoAbierto(
                servicio=self.nombre_servicio,
                mensaje=(
                    f"Circuit breaker ABIERTO — {self._fallos_consecutivos} fallos consecutivos. "
                    f"Reintento disponible en {tiempo_restante:.0f}s."
                ),
            )

    def registrar_exito(self) -> None:
        """Registra una llamada exitosa — resetea el contador de fallos."""
        if self._fallos_consecutivos > 0:
            logger.info(
                "[%s] Circuit breaker: exito tras %d fallos — cerrando circuito.",
                self.nombre_servicio, self._fallos_consecutivos,
            )
        self._fallos_consecutivos = 0
        self._estado = "cerrado"

    def registrar_fallo(self) -> None:
        """Registra un fallo — incrementa contador y abre circuito si supera umbral."""
        self._fallos_consecutivos += 1
        self._ultimo_fallo = time.monotonic()

        if self._fallos_consecutivos >= self.umbral_fallos:
            self._estado = "abierto"
            logger.warning(
                "[%s] Circuit breaker ABIERTO — %d fallos consecutivos. Cooldown: %ds",
                self.nombre_servicio, self._fallos_consecutivos, self.cooldown_segundos,
            )

    def reset(self) -> None:
        """Resetea el circuit breaker manualmente."""
        self._fallos_consecutivos = 0
        self._ultimo_fallo = 0.0
        self._estado = "cerrado"
        logger.info("[%s] Circuit breaker reseteado manualmente.", self.nombre_servicio)


# ── Cache Redis ────────────────────────────────────────────────────────────────


class CacheRedisIntegracion:
    """Cache Redis para respuestas de integraciones externas.

    Almacena respuestas JSON con TTL configurable para evitar llamadas
    repetitivas a APIs externas. Usa hash MD5 de la solicitud como clave.
    """

    PREFIJO_CLAVE: str = "cecilia:integracion:cache:"

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        ttl_segundos: int = 3600,
    ) -> None:
        self._redis_url = redis_url
        self._ttl = ttl_segundos
        self._redis: Any = None
        self._disponible: bool = False

    async def conectar(self) -> bool:
        """Intenta conectar a Redis. Retorna False si no esta disponible."""
        try:
            import redis.asyncio as aioredis
            self._redis = aioredis.from_url(self._redis_url, decode_responses=True)
            await self._redis.ping()
            self._disponible = True
            logger.info("Cache Redis conectado: %s (TTL=%ds)", self._redis_url, self._ttl)
            return True
        except Exception as exc:
            logger.warning("Cache Redis no disponible (%s) — continuando sin cache.", exc)
            self._disponible = False
            return False

    async def cerrar(self) -> None:
        """Cierra la conexion a Redis."""
        if self._redis:
            await self._redis.aclose()

    def _generar_clave(self, servicio: str, metodo: str, ruta: str, params: Optional[dict] = None) -> str:
        """Genera clave unica para la cache basada en la solicitud."""
        contenido = f"{servicio}:{metodo}:{ruta}:{json.dumps(params or {}, sort_keys=True)}"
        hash_md5 = hashlib.md5(contenido.encode()).hexdigest()
        return f"{self.PREFIJO_CLAVE}{servicio}:{hash_md5}"

    async def obtener(self, servicio: str, metodo: str, ruta: str, params: Optional[dict] = None) -> Optional[Any]:
        """Busca en cache. Retorna None si no hay hit o Redis no esta disponible."""
        if not self._disponible:
            return None
        try:
            clave = self._generar_clave(servicio, metodo, ruta, params)
            datos = await self._redis.get(clave)
            if datos:
                logger.debug("[%s] Cache HIT: %s", servicio, clave[-12:])
                return json.loads(datos)
            return None
        except Exception:
            logger.debug("[%s] Cache error — ignorando.", servicio)
            return None

    async def guardar(
        self,
        servicio: str,
        metodo: str,
        ruta: str,
        params: Optional[dict],
        respuesta: Any,
        ttl_override: Optional[int] = None,
    ) -> None:
        """Guarda respuesta en cache con TTL."""
        if not self._disponible:
            return
        try:
            clave = self._generar_clave(servicio, metodo, ruta, params)
            ttl = ttl_override or self._ttl
            await self._redis.setex(clave, ttl, json.dumps(respuesta, ensure_ascii=False, default=str))
            logger.debug("[%s] Cache SET: %s (TTL=%ds)", servicio, clave[-12:], ttl)
        except Exception:
            logger.debug("[%s] Cache error al guardar — ignorando.", servicio)

    async def invalidar(self, servicio: str) -> int:
        """Invalida toda la cache de un servicio. Retorna cantidad de claves eliminadas."""
        if not self._disponible:
            return 0
        try:
            patron = f"{self.PREFIJO_CLAVE}{servicio}:*"
            claves = await self._redis.keys(patron)
            if claves:
                await self._redis.delete(*claves)
                logger.info("[%s] Cache invalidada: %d claves.", servicio, len(claves))
                return len(claves)
            return 0
        except Exception:
            return 0


# ── Cliente Base ───────────────────────────────────────────────────────────────


class ClienteBaseIntegracion:
    """Clase base para clientes de integracion con servicios externos.

    Proporciona:
    - Cliente HTTP asincrono (httpx.AsyncClient) con pool de conexiones.
    - Logica de reintentos con retroceso exponencial.
    - Cache Redis con TTL configurable (default 1 hora).
    - Circuit breaker (5 fallos → 5 min cooldown).
    - Trazabilidad: logging de cada consulta externa.
    - Manejo uniforme de errores HTTP.
    - Medicion de latencia para metricas.

    Las subclases deben definir:
    - ``nombre_servicio``: Nombre legible del servicio.
    - ``url_base``: URL base del API del servicio.
    """

    nombre_servicio: str = "base"
    url_base: str = ""

    # Cache y circuit breaker compartidos entre instancias del mismo servicio
    _caches: dict[str, CacheRedisIntegracion] = {}
    _circuit_breakers: dict[str, CircuitBreaker] = {}

    def __init__(
        self,
        url_base_override: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout_segundos: float = 30.0,
        max_reintentos: int = 3,
        factor_retroceso: float = 1.5,
        encabezados_extra: Optional[dict[str, str]] = None,
        cache_ttl_segundos: int = 3600,
        cache_habilitado: bool = True,
        circuit_breaker_habilitado: bool = True,
        circuit_breaker_umbral: int = 5,
        circuit_breaker_cooldown: float = 300.0,
        redis_url: str = "redis://localhost:6379/0",
    ) -> None:
        """Inicializa el cliente de integracion.

        Args:
            url_base_override: URL base alternativa (override de la default).
            api_key: Clave API para autenticacion (si aplica).
            timeout_segundos: Timeout maximo por solicitud en segundos.
            max_reintentos: Numero maximo de reintentos ante errores transitorios.
            factor_retroceso: Factor multiplicador para retroceso exponencial.
            encabezados_extra: Encabezados HTTP adicionales.
            cache_ttl_segundos: TTL de la cache Redis en segundos (default 3600 = 1h).
            cache_habilitado: Activar/desactivar cache Redis.
            circuit_breaker_habilitado: Activar/desactivar circuit breaker.
            circuit_breaker_umbral: Numero de fallos antes de abrir el circuito.
            circuit_breaker_cooldown: Segundos de cooldown cuando el circuito se abre.
            redis_url: URL de conexion a Redis.
        """
        self._url_base: str = url_base_override or self.url_base
        self._api_key: Optional[str] = api_key
        self._timeout: float = timeout_segundos
        self._max_reintentos: int = max_reintentos
        self._factor_retroceso: float = factor_retroceso
        self._cache_habilitado: bool = cache_habilitado
        self._cache_ttl: int = cache_ttl_segundos
        self._redis_url: str = redis_url
        self._cb_habilitado: bool = circuit_breaker_habilitado

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

        # Circuit breaker por servicio (singleton)
        if self._cb_habilitado and self.nombre_servicio not in self._circuit_breakers:
            self._circuit_breakers[self.nombre_servicio] = CircuitBreaker(
                nombre_servicio=self.nombre_servicio,
                umbral_fallos=circuit_breaker_umbral,
                cooldown_segundos=circuit_breaker_cooldown,
            )

    @property
    def circuit_breaker(self) -> Optional[CircuitBreaker]:
        """Retorna el circuit breaker del servicio."""
        return self._circuit_breakers.get(self.nombre_servicio)

    async def _obtener_cache(self) -> Optional[CacheRedisIntegracion]:
        """Obtiene o inicializa la cache Redis para este servicio."""
        if not self._cache_habilitado:
            return None

        if self.nombre_servicio not in self._caches:
            cache = CacheRedisIntegracion(
                redis_url=self._redis_url,
                ttl_segundos=self._cache_ttl,
            )
            conectado = await cache.conectar()
            if conectado:
                self._caches[self.nombre_servicio] = cache
            else:
                return None

        return self._caches.get(self.nombre_servicio)

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
        """Clasifica un error HTTP en una excepcion especifica."""
        codigo: int = respuesta.status_code
        cuerpo: str = respuesta.text[:500]

        if codigo == 401 or codigo == 403:
            return ErrorAutenticacion(
                servicio=self.nombre_servicio,
                mensaje=f"Autenticacion fallida: {cuerpo}",
                codigo_http=codigo,
            )
        elif codigo == 429:
            return ErrorLimiteConsultas(
                servicio=self.nombre_servicio,
                mensaje=f"Limite de consultas excedido: {cuerpo}",
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
        """Determina si un error justifica un reintento."""
        if isinstance(error, (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError)):
            return True
        if isinstance(error, ErrorServicioNoDisponible):
            return True
        if isinstance(error, ErrorLimiteConsultas):
            return True
        return False

    async def _registrar_trazabilidad(
        self,
        metodo: str,
        ruta: str,
        parametros: Optional[dict[str, Any]],
        duracion_ms: float,
        exitoso: bool,
        codigo_http: Optional[int] = None,
        error_mensaje: Optional[str] = None,
        desde_cache: bool = False,
    ) -> None:
        """Registra la consulta externa en el log de trazabilidad.

        Cada consulta queda registrada con timestamp, servicio, metodo, ruta,
        duracion, resultado y si provino de cache.
        """
        registro = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "servicio": self.nombre_servicio,
            "metodo": metodo,
            "ruta": ruta,
            "parametros": parametros,
            "duracion_ms": round(duracion_ms, 1),
            "exitoso": exitoso,
            "codigo_http": codigo_http,
            "desde_cache": desde_cache,
            "error": error_mensaje,
        }

        if exitoso:
            logger.info(
                "[TRAZABILIDAD][%s] %s %s → %s (%0.1fms)%s",
                self.nombre_servicio,
                metodo,
                ruta,
                f"HTTP {codigo_http}" if codigo_http else "OK",
                duracion_ms,
                " [CACHE]" if desde_cache else "",
            )
        else:
            logger.warning(
                "[TRAZABILIDAD][%s] %s %s → ERROR (%0.1fms): %s",
                self.nombre_servicio, metodo, ruta, duracion_ms, error_mensaje,
            )

    async def _solicitud_con_reintentos(
        self,
        metodo: str,
        ruta: str,
        parametros: Optional[dict[str, Any]] = None,
        cuerpo_json: Optional[dict[str, Any]] = None,
        encabezados: Optional[dict[str, str]] = None,
        usar_cache: bool = True,
        cache_ttl_override: Optional[int] = None,
    ) -> dict[str, Any]:
        """Ejecuta una solicitud HTTP con cache, circuit breaker y reintentos.

        Args:
            metodo: Metodo HTTP (GET, POST, PUT, DELETE).
            ruta: Ruta relativa al URL base.
            parametros: Parametros de consulta (query string).
            cuerpo_json: Cuerpo de la solicitud en formato JSON.
            encabezados: Encabezados HTTP adicionales para esta solicitud.
            usar_cache: Si True, intenta leer/escribir cache (solo GET).
            cache_ttl_override: TTL especifico para esta consulta.

        Returns:
            Respuesta deserializada como diccionario.

        Raises:
            ErrorCircuitoAbierto: Si el circuit breaker esta abierto.
            ErrorIntegracion: Si la solicitud falla despues de todos los reintentos.
        """
        inicio_total: float = time.monotonic()

        # 1. Circuit breaker — verificar si se permite la llamada
        cb = self.circuit_breaker
        if cb:
            cb.verificar()

        # 2. Cache — solo para GET sin cuerpo JSON
        if usar_cache and metodo.upper() == "GET" and not cuerpo_json:
            cache = await self._obtener_cache()
            if cache:
                datos_cache = await cache.obtener(self.nombre_servicio, metodo, ruta, parametros)
                if datos_cache is not None:
                    duracion = (time.monotonic() - inicio_total) * 1000
                    await self._registrar_trazabilidad(
                        metodo, ruta, parametros, duracion, True, desde_cache=True,
                    )
                    return datos_cache

        # 3. Solicitud HTTP con reintentos
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
                        resultado = respuesta.json()
                    except Exception:
                        resultado = {"contenido_texto": respuesta.text}

                    # Registrar exito en circuit breaker
                    if cb:
                        cb.registrar_exito()

                    # Guardar en cache (solo GET)
                    if usar_cache and metodo.upper() == "GET":
                        cache = await self._obtener_cache()
                        if cache:
                            await cache.guardar(
                                self.nombre_servicio, metodo, ruta, parametros,
                                resultado, cache_ttl_override,
                            )

                    # Trazabilidad
                    duracion_total = (time.monotonic() - inicio_total) * 1000
                    await self._registrar_trazabilidad(
                        metodo, ruta, parametros, duracion_total, True,
                        codigo_http=respuesta.status_code,
                    )

                    return resultado

                error_tipado: ErrorIntegracion = self._clasificar_error_http(respuesta)

                if not self._es_error_reintentable(error_tipado) or intento == self._max_reintentos:
                    if cb:
                        cb.registrar_fallo()
                    duracion_total = (time.monotonic() - inicio_total) * 1000
                    await self._registrar_trazabilidad(
                        metodo, ruta, parametros, duracion_total, False,
                        codigo_http=respuesta.status_code,
                        error_mensaje=str(error_tipado),
                    )
                    raise error_tipado

                ultimo_error = error_tipado

            except ErrorCircuitoAbierto:
                raise
            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError) as error_conexion:
                duracion_ms = (time.monotonic() - inicio) * 1000
                logger.warning(
                    "[%s] %s %s → Error de conexion (%0.1fms, intento %d/%d): %s",
                    self.nombre_servicio, metodo, ruta, duracion_ms,
                    intento + 1, self._max_reintentos + 1, str(error_conexion),
                )
                ultimo_error = error_conexion

                if intento == self._max_reintentos:
                    if cb:
                        cb.registrar_fallo()
                    duracion_total = (time.monotonic() - inicio_total) * 1000
                    await self._registrar_trazabilidad(
                        metodo, ruta, parametros, duracion_total, False,
                        error_mensaje=str(error_conexion),
                    )
                    raise ErrorServicioNoDisponible(
                        servicio=self.nombre_servicio,
                        mensaje=f"Servicio no accesible despues de {self._max_reintentos + 1} intentos: {error_conexion}",
                    ) from error_conexion

            # Retroceso exponencial entre reintentos
            espera_segundos: float = self._factor_retroceso ** intento
            logger.info(
                "[%s] Reintentando en %0.1f segundos (intento %d/%d)...",
                self.nombre_servicio, espera_segundos, intento + 2, self._max_reintentos + 1,
            )
            await asyncio.sleep(espera_segundos)

        # No deberia llegar aqui, pero por seguridad
        raise ErrorIntegracion(
            servicio=self.nombre_servicio,
            mensaje=f"Fallo despues de {self._max_reintentos + 1} intentos: {ultimo_error}",
        )

    # ── Metodos de conveniencia ──────────────────────────────────────────────

    async def get(
        self,
        ruta: str,
        parametros: Optional[dict[str, Any]] = None,
        encabezados: Optional[dict[str, str]] = None,
        usar_cache: bool = True,
        cache_ttl: Optional[int] = None,
    ) -> dict[str, Any]:
        """Realiza una solicitud GET con cache y circuit breaker."""
        return await self._solicitud_con_reintentos(
            "GET", ruta, parametros=parametros, encabezados=encabezados,
            usar_cache=usar_cache, cache_ttl_override=cache_ttl,
        )

    async def post(
        self,
        ruta: str,
        cuerpo_json: Optional[dict[str, Any]] = None,
        parametros: Optional[dict[str, Any]] = None,
        encabezados: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Realiza una solicitud POST (sin cache)."""
        return await self._solicitud_con_reintentos(
            "POST", ruta, parametros=parametros, cuerpo_json=cuerpo_json,
            encabezados=encabezados, usar_cache=False,
        )

    async def verificar_salud(self) -> dict[str, Any]:
        """Verifica la conectividad y salud del servicio externo.

        Returns:
            Diccionario con estado, latencia, circuit breaker y mensaje.
        """
        inicio: float = time.monotonic()

        # Verificar circuit breaker primero
        cb = self.circuit_breaker
        if cb and cb.estado == "abierto":
            return {
                "servicio": self.nombre_servicio,
                "estado": "circuito_abierto",
                "latencia_ms": 0,
                "circuit_breaker": {
                    "estado": cb.estado,
                    "fallos_consecutivos": cb._fallos_consecutivos,
                    "cooldown_segundos": cb.cooldown_segundos,
                },
                "mensaje": f"Circuit breaker abierto ({cb._fallos_consecutivos} fallos consecutivos).",
            }

        try:
            respuesta: httpx.Response = await self._cliente.get("/", timeout=10.0)
            duracion_ms: float = (time.monotonic() - inicio) * 1000

            estado: str = "disponible" if respuesta.is_success else "degradado"
            resultado: dict[str, Any] = {
                "servicio": self.nombre_servicio,
                "estado": estado,
                "latencia_ms": round(duracion_ms, 1),
                "codigo_http": respuesta.status_code,
            }

            if cb:
                resultado["circuit_breaker"] = {
                    "estado": cb.estado,
                    "fallos_consecutivos": cb._fallos_consecutivos,
                }

            return resultado
        except Exception as error:
            duracion_ms = (time.monotonic() - inicio) * 1000
            return {
                "servicio": self.nombre_servicio,
                "estado": "no_disponible",
                "latencia_ms": round(duracion_ms, 1),
                "error": str(error),
            }

    async def invalidar_cache(self) -> int:
        """Invalida toda la cache de este servicio."""
        cache = await self._obtener_cache()
        if cache:
            return await cache.invalidar(self.nombre_servicio)
        return 0

    def obtener_estado_circuit_breaker(self) -> dict[str, Any]:
        """Retorna informacion del circuit breaker."""
        cb = self.circuit_breaker
        if not cb:
            return {"habilitado": False}
        return {
            "habilitado": True,
            "estado": cb.estado,
            "fallos_consecutivos": cb._fallos_consecutivos,
            "umbral_fallos": cb.umbral_fallos,
            "cooldown_segundos": cb.cooldown_segundos,
        }
