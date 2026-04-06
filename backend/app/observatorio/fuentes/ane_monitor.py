"""
CecilIA v2 — Monitor ANE (www.ane.gov.co)
Contraloria General de la Republica de Colombia

Monitorea: espectro radioelectrico de la Agencia Nacional del Espectro.
Sprint: 8
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone

from app.observatorio.fuentes.base_monitor import ContenidoDetectado, MonitorBase

logger = logging.getLogger("cecilia.observatorio.ane")


class ANEMonitor(MonitorBase):
    """Monitor de la Agencia Nacional del Espectro."""

    nombre = "ANE"
    dominio = "www.ane.gov.co"
    urls = [
        "https://www.ane.gov.co/SitePages/index.aspx",
        "https://www.ane.gov.co/SitePages/Resoluciones.aspx",
    ]

    async def escanear(self) -> list[ContenidoDetectado]:
        resultados: list[ContenidoDetectado] = []

        for url in self.urls:
            html = await self.fetch_pagina(url)
            if not html:
                continue

            tipo = "REGULATORIA" if "Resoluciones" in url else "NOTICIA"
            items = self._extraer_items(html, url, tipo)
            resultados.extend(items)

        return resultados

    def _extraer_items(self, html: str, base_url: str, tipo: str) -> list[ContenidoDetectado]:
        items: list[ContenidoDetectado] = []

        patron = re.findall(
            r'<a\s+href="([^"]*ane\.gov\.co[^"]*)"[^>]*>\s*([^<]{10,300})\s*</a>',
            html,
            re.IGNORECASE,
        )

        patron_h = re.findall(
            r'<h[2-4][^>]*>([^<]{10,200})</h[2-4]>',
            html,
            re.IGNORECASE,
        )

        vistos: set[str] = set()

        for href, titulo in patron:
            titulo = re.sub(r'<[^>]+>', '', titulo).strip()
            titulo = re.sub(r'\s+', ' ', titulo)
            if len(titulo) < 15 or titulo in vistos:
                continue
            vistos.add(titulo)
            if not self._es_relevante_ane(titulo):
                continue

            url_completa = href if href.startswith("http") else f"https://{self.dominio}{href}"
            items.append(ContenidoDetectado(
                titulo=titulo,
                url=url_completa,
                fuente_nombre="ANE",
                tipo=tipo,
                fecha_publicacion=datetime.now(timezone.utc),
                metadata={"entidad": "Agencia Nacional del Espectro"},
            ))

        for titulo_raw in patron_h:
            titulo = titulo_raw.strip()
            if len(titulo) < 15 or titulo in vistos:
                continue
            vistos.add(titulo)
            if self._es_relevante_ane(titulo):
                items.append(ContenidoDetectado(
                    titulo=titulo,
                    url=base_url,
                    fuente_nombre="ANE",
                    tipo="REGULATORIA",
                    fecha_publicacion=datetime.now(timezone.utc),
                ))

        return items[:10]

    def _es_relevante_ane(self, titulo: str) -> bool:
        titulo_lower = titulo.lower()
        palabras = [
            "espectro", "radiofrecuencia", "asignacion", "banda",
            "licencia", "resolucion", "antena", "radiodifusion",
            "satelital", "5g", "lte", "frecuencia", "interferencia",
            "cuadro nacional de atribucion", "permiso", "concesion",
        ]
        return any(p in titulo_lower for p in palabras)
