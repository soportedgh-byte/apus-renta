"""
CecilIA v2 — Monitor CRC (www.crcom.gov.co)
Contraloria General de la Republica de Colombia

Monitorea: regulacion de telecomunicaciones de la Comision de Regulacion de Comunicaciones.
Sprint: 8
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone

from app.observatorio.fuentes.base_monitor import ContenidoDetectado, MonitorBase

logger = logging.getLogger("cecilia.observatorio.crc")


class CRCMonitor(MonitorBase):
    """Monitor de la Comision de Regulacion de Comunicaciones."""

    nombre = "CRC"
    dominio = "www.crcom.gov.co"
    urls = [
        "https://www.crcom.gov.co/es/pagina/resoluciones",
        "https://www.crcom.gov.co/es/pagina/noticias",
        "https://www.crcom.gov.co/es/pagina/agenda-regulatoria",
    ]

    async def escanear(self) -> list[ContenidoDetectado]:
        resultados: list[ContenidoDetectado] = []

        for url in self.urls:
            html = await self.fetch_pagina(url)
            if not html:
                continue

            tipo = "REGULATORIA" if "resoluciones" in url or "regulatoria" in url else "NOTICIA"
            items = self._extraer_items(html, url, tipo)
            resultados.extend(items)

        return resultados

    def _extraer_items(self, html: str, base_url: str, tipo: str) -> list[ContenidoDetectado]:
        items: list[ContenidoDetectado] = []

        # Buscar resoluciones CRC
        patron = re.findall(
            r'<a\s+href="([^"]*crcom[^"]*)"[^>]*>\s*([^<]{10,300})\s*</a>',
            html,
            re.IGNORECASE,
        )

        # Patron para titulos en contenedores
        patron2 = re.findall(
            r'<h[2-4][^>]*>\s*(?:<a[^>]*>)?\s*(.+?)\s*(?:</a>)?\s*</h[2-4]>',
            html,
            re.IGNORECASE | re.DOTALL,
        )

        vistos: set[str] = set()

        for href, titulo in patron:
            titulo = re.sub(r'<[^>]+>', '', titulo).strip()
            titulo = re.sub(r'\s+', ' ', titulo)

            if len(titulo) < 15 or titulo in vistos:
                continue
            vistos.add(titulo)

            if not self._es_relevante_crc(titulo):
                continue

            url_completa = href if href.startswith("http") else f"https://{self.dominio}{href}"
            items.append(ContenidoDetectado(
                titulo=titulo,
                url=url_completa,
                fuente_nombre="CRC",
                tipo=tipo,
                fecha_publicacion=datetime.now(timezone.utc),
                metadata={"entidad": "Comision de Regulacion de Comunicaciones"},
            ))

        # Agregar titulos sueltos (sin href)
        for titulo_raw in patron2:
            titulo = re.sub(r'<[^>]+>', '', titulo_raw).strip()
            titulo = re.sub(r'\s+', ' ', titulo)
            if len(titulo) < 15 or titulo in vistos:
                continue
            vistos.add(titulo)
            if self._es_relevante_crc(titulo):
                items.append(ContenidoDetectado(
                    titulo=titulo,
                    url=base_url,
                    fuente_nombre="CRC",
                    tipo=tipo,
                    fecha_publicacion=datetime.now(timezone.utc),
                ))

        return items[:10]

    def _es_relevante_crc(self, titulo: str) -> bool:
        titulo_lower = titulo.lower()
        palabras = [
            "resolucion", "regulacion", "telecomunicaciones", "espectro",
            "tarifas", "interconexion", "operador", "banda ancha",
            "movil", "internet", "portabilidad", "competencia",
            "convergencia", "television", "radio", "postal",
            "consumidor", "calidad", "cobertura", "5g",
        ]
        return any(p in titulo_lower for p in palabras)
