"""
Tests para el modulo base de integraciones.
Valida circuit breaker, cache, trazabilidad y cliente HTTP.
"""

import time
import pytest


class TestCircuitBreaker:
    """Tests del circuit breaker."""

    def _crear_cb(self, **kwargs):
        """Helper para crear un CircuitBreaker importado directamente."""
        import importlib.util
        import os
        spec = importlib.util.spec_from_file_location(
            "base_mod",
            os.path.join(os.path.dirname(__file__), "..", "..", "app", "integraciones", "base.py"),
        )
        mod = importlib.util.module_from_spec(spec)
        # Need to handle the httpx import
        import sys
        if "httpx" not in sys.modules:
            # Mock httpx if not available
            import types
            mock_httpx = types.ModuleType("httpx")
            mock_httpx.AsyncClient = type("AsyncClient", (), {})
            mock_httpx.Timeout = lambda x: None
            mock_httpx.ConnectTimeout = Exception
            mock_httpx.ReadTimeout = Exception
            mock_httpx.ConnectError = Exception
            mock_httpx.Response = type("Response", (), {})
            sys.modules["httpx"] = mock_httpx
        spec.loader.exec_module(mod)
        return mod.CircuitBreaker(**kwargs)

    def test_estado_inicial_cerrado(self):
        cb = self._crear_cb(nombre_servicio="test", umbral_fallos=3, cooldown_segundos=1.0)
        assert cb.estado == "cerrado"
        assert cb._fallos_consecutivos == 0

    def test_registrar_exito_resetea_fallos(self):
        cb = self._crear_cb(nombre_servicio="test", umbral_fallos=3)
        cb._fallos_consecutivos = 2
        cb.registrar_exito()
        assert cb._fallos_consecutivos == 0
        assert cb.estado == "cerrado"

    def test_registrar_fallos_abre_circuito(self):
        cb = self._crear_cb(nombre_servicio="test", umbral_fallos=3, cooldown_segundos=5.0)
        for _ in range(3):
            cb.registrar_fallo()
        assert cb._fallos_consecutivos == 3
        assert cb.estado == "abierto"

    def test_verificar_lanza_error_cuando_abierto(self):
        from importlib.util import spec_from_file_location, module_from_spec
        import os, sys
        spec = spec_from_file_location(
            "base_mod2",
            os.path.join(os.path.dirname(__file__), "..", "..", "app", "integraciones", "base.py"),
        )
        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)

        cb = mod.CircuitBreaker(nombre_servicio="test", umbral_fallos=2, cooldown_segundos=5.0)
        cb.registrar_fallo()
        cb.registrar_fallo()
        assert cb.estado == "abierto"

        with pytest.raises(mod.ErrorCircuitoAbierto):
            cb.verificar()

    def test_circuito_pasa_a_semi_abierto_tras_cooldown(self):
        cb = self._crear_cb(nombre_servicio="test", umbral_fallos=2, cooldown_segundos=0.1)
        cb.registrar_fallo()
        cb.registrar_fallo()
        assert cb.estado == "abierto"

        # Esperar que expire el cooldown
        time.sleep(0.15)
        assert cb.estado == "semi_abierto"

    def test_reset_manual(self):
        cb = self._crear_cb(nombre_servicio="test", umbral_fallos=2)
        cb.registrar_fallo()
        cb.registrar_fallo()
        assert cb.estado == "abierto"

        cb.reset()
        assert cb.estado == "cerrado"
        assert cb._fallos_consecutivos == 0

    def test_exito_tras_fallo_resetea(self):
        cb = self._crear_cb(nombre_servicio="test", umbral_fallos=5)
        cb.registrar_fallo()
        cb.registrar_fallo()
        assert cb._fallos_consecutivos == 2

        cb.registrar_exito()
        assert cb._fallos_consecutivos == 0
        assert cb.estado == "cerrado"


class TestErrores:
    """Tests de las excepciones de integracion."""

    def _cargar_modulo(self):
        import importlib.util, os
        spec = importlib.util.spec_from_file_location(
            "base_mod3",
            os.path.join(os.path.dirname(__file__), "..", "..", "app", "integraciones", "base.py"),
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_error_integracion_basico(self):
        mod = self._cargar_modulo()
        err = mod.ErrorIntegracion(servicio="TEST", mensaje="algo fallo")
        assert err.servicio == "TEST"
        assert err.mensaje == "algo fallo"
        assert err.codigo_http is None
        assert "[TEST]" in str(err)

    def test_error_integracion_con_codigo(self):
        mod = self._cargar_modulo()
        err = mod.ErrorIntegracion(servicio="SECOP", mensaje="timeout", codigo_http=504)
        assert err.codigo_http == 504
        assert "HTTP 504" in str(err)

    def test_error_servicio_no_disponible(self):
        mod = self._cargar_modulo()
        err = mod.ErrorServicioNoDisponible(servicio="DANE", mensaje="sin respuesta")
        assert isinstance(err, mod.ErrorIntegracion)

    def test_error_circuito_abierto(self):
        mod = self._cargar_modulo()
        err = mod.ErrorCircuitoAbierto(servicio="Congreso", mensaje="circuito abierto")
        assert isinstance(err, mod.ErrorIntegracion)

    def test_error_autenticacion(self):
        mod = self._cargar_modulo()
        err = mod.ErrorAutenticacion(servicio="SIRECI", mensaje="credenciales invalidas", codigo_http=401)
        assert isinstance(err, mod.ErrorIntegracion)
        assert err.codigo_http == 401

    def test_error_limite_consultas(self):
        mod = self._cargar_modulo()
        err = mod.ErrorLimiteConsultas(servicio="SECOP", mensaje="rate limit", codigo_http=429)
        assert err.codigo_http == 429


class TestCacheRedisIntegracion:
    """Tests de la cache Redis (sin Redis real)."""

    def _cargar_modulo(self):
        import importlib.util, os
        spec = importlib.util.spec_from_file_location(
            "base_mod4",
            os.path.join(os.path.dirname(__file__), "..", "..", "app", "integraciones", "base.py"),
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_generar_clave_unica(self):
        mod = self._cargar_modulo()
        cache = mod.CacheRedisIntegracion()

        clave1 = cache._generar_clave("SECOP", "GET", "/resource/abc.json", {"$limit": 20})
        clave2 = cache._generar_clave("SECOP", "GET", "/resource/abc.json", {"$limit": 20})
        clave3 = cache._generar_clave("SECOP", "GET", "/resource/abc.json", {"$limit": 50})

        assert clave1 == clave2  # Mismos params → misma clave
        assert clave1 != clave3  # Diferentes params → diferente clave
        assert clave1.startswith("cecilia:integracion:cache:SECOP:")

    def test_cache_no_disponible_retorna_none(self):
        mod = self._cargar_modulo()
        cache = mod.CacheRedisIntegracion()
        # Sin conectar a Redis, _disponible = False
        import asyncio
        resultado = asyncio.get_event_loop().run_until_complete(
            cache.obtener("SECOP", "GET", "/test", {})
        )
        assert resultado is None

    def test_guardar_sin_redis_no_falla(self):
        mod = self._cargar_modulo()
        cache = mod.CacheRedisIntegracion()
        import asyncio
        # No debe lanzar excepcion
        asyncio.get_event_loop().run_until_complete(
            cache.guardar("SECOP", "GET", "/test", {}, {"dato": 123})
        )

    def test_invalidar_sin_redis_retorna_cero(self):
        mod = self._cargar_modulo()
        cache = mod.CacheRedisIntegracion()
        import asyncio
        resultado = asyncio.get_event_loop().run_until_complete(
            cache.invalidar("SECOP")
        )
        assert resultado == 0
