"""
CecilIA v2 — Monitor base para crawlers del Observatorio TIC
Contraloria General de la Republica de Colombia

Proposito: Clase abstracta con rate limiting, robots.txt y manejo de errores.
Sprint: 8
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx

logger = logging.getLogger("cecilia.observatorio.monitor")

# Rate limiting global: max 1 req / 5s por dominio
_ULTIMO_REQUEST: dict[str, float] = {}
_INTERVALO_MINIMO = 5.0  # segundos
_LOCK = asyncio.Lock()


@dataclass
class ContenidoDetectado:
    """Contenido nuevo detectado por un monitor."""

    titulo: str
    resumen: str = ""
    url: str = ""
    fuente_nombre: str = ""
    tipo: str = "NOTICIA"  # REGULATORIA | LEGISLATIVA | NOTICIA | INDICADOR
    fecha_publicacion: Optional[datetime] = None
    contenido_completo: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def hash_contenido(self) -> str:
        """Hash unico para detectar duplicados."""
        texto = f"{self.titulo}|{self.url}|{self.fuente_nombre}"
        return hashlib.sha256(texto.encode()).hexdigest()[:16]


class MonitorBase(ABC):
    """Clase base para monitores de fuentes TIC."""

    nombre: str = "Base"
    dominio: str = ""
    urls: list[str] = []
    user_agent: str = "CecilIA-Observatorio/2.0 (+https://cecilia.cgr.gov.co)"

    def __init__(self) -> None:
        self._robots_cache: dict[str, RobotFileParser] = {}
        self._cliente: Optional[httpx.AsyncClient] = None

    async def _obtener_cliente(self) -> httpx.AsyncClient:
        if self._cliente is None or self._cliente.is_closed:
            self._cliente = httpx.AsyncClient(
                headers={
                    "User-Agent": self.user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "es-CO,es;q=0.9",
                },
                timeout=httpx.Timeout(30.0),
                follow_redirects=True,
            )
        return self._cliente

    async def cerrar(self) -> None:
        if self._cliente and not self._cliente.is_closed:
            await self._cliente.aclose()

    # ── Rate limiting ────────────────────────────────────────────────────────

    async def _esperar_rate_limit(self, dominio: str) -> None:
        """Asegura al menos _INTERVALO_MINIMO segundos entre requests al mismo dominio."""
        async with _LOCK:
            ahora = time.monotonic()
            ultimo = _ULTIMO_REQUEST.get(dominio, 0)
            espera = _INTERVALO_MINIMO - (ahora - ultimo)
            if espera > 0:
                logger.debug("Rate limit: esperando %.1fs para %s", espera, dominio)
                await asyncio.sleep(espera)
            _ULTIMO_REQUEST[dominio] = time.monotonic()

    # ── Robots.txt ───────────────────────────────────────────────────────────

    async def _verificar_robots(self, url: str) -> bool:
        """Verifica si la URL esta permitida segun robots.txt."""
        parsed = urlparse(url)
        dominio_base = f"{parsed.scheme}://{parsed.netloc}"
        robots_url = f"{dominio_base}/robots.txt"

        if dominio_base not in self._robots_cache:
            rp = RobotFileParser()
            try:
                cliente = await self._obtener_cliente()
                resp = await cliente.get(robots_url)
                if resp.status_code == 200:
                    rp.parse(resp.text.splitlines())
                else:
                    # Si no hay robots.txt, todo permitido
                    rp.allow_all = True
            except Exception:
                rp.allow_all = True
            self._robots_cache[dominio_base] = rp

        rp = self._robots_cache[dominio_base]
        return rp.can_fetch(self.user_agent, url)

    # ── Fetch seguro ─────────────────────────────────────────────────────────

    async def fetch_pagina(self, url: str) -> Optional[str]:
        """Descarga una pagina respetando rate limit y robots.txt."""
        parsed = urlparse(url)
        dominio = parsed.netloc

        # Verificar robots.txt
        permitida = await self._verificar_robots(url)
        if not permitida:
            logger.info("Bloqueada por robots.txt: %s", url)
            return None

        # Rate limiting
        await self._esperar_rate_limit(dominio)

        try:
            cliente = await self._obtener_cliente()
            resp = await cliente.get(url)
            resp.raise_for_status()
            return resp.text
        except httpx.HTTPStatusError as e:
            logger.warning("HTTP %d al acceder a %s", e.response.status_code, url)
            return None
        except Exception as e:
            logger.error("Error al acceder a %s: %s", url, e)
            return None

    async def fetch_rss(self, url: str) -> Optional[str]:
        """Descarga un feed RSS."""
        return await self.fetch_pagina(url)

    # ── Metodo abstracto ─────────────────────────────────────────────────────

    @abstractmethod
    async def escanear(self) -> list[ContenidoDetectado]:
        """Escanea la fuente y retorna contenido nuevo detectado."""
        ...

    async def ejecutar(self) -> list[ContenidoDetectado]:
        """Ejecuta el escaneo con manejo de errores."""
        try:
            logger.info("Iniciando escaneo: %s", self.nombre)
            resultados = await self.escanear()
            logger.info("Escaneo %s completado: %d items", self.nombre, len(resultados))
            return resultados
        except Exception as e:
            logger.error("Error en escaneo %s: %s", self.nombre, e, exc_info=True)
            return []
        finally:
            await self.cerrar()
