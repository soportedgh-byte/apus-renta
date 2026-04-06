"""
CecilIA v2 — Monitor Congreso (proyectos de ley sector TIC)
Contraloria General de la Republica de Colombia

Monitorea: proyectos de ley en tramite relacionados con el sector TIC.
Sprint: 8
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone

from app.observatorio.fuentes.base_monitor import ContenidoDetectado, MonitorBase

logger = logging.getLogger("cecilia.observatorio.congreso")


class CongresoMonitor(MonitorBase):
    """Monitor de proyectos de ley del sector TIC en el Congreso."""

    nombre = "Congreso TIC"
    dominio = "www.senado.gov.co"
    urls = [
        "https://www.senado.gov.co/index.php/az-legislativo/proyectos-de-ley",
        "https://www.camara.gov.co/proyectos-de-ley",
    ]

    PALABRAS_CLAVE_TIC = [
        "telecomunicaciones", "tecnologia", "digital", "internet",
        "espectro", "ciberseguridad", "datos personales", "habeas data",
        "inteligencia artificial", "gobierno electronico", "gobierno digital",
        "conectividad", "banda ancha", "fibra optica", "5g",
        "comercio electronico", "firma digital", "identidad digital",
        "innovacion", "emprendimiento digital", "startup",
        "plataformas digitales", "redes sociales", "contenido digital",
        "radiodifusion", "television", "streaming",
        "mintic", "crcom", "crc", "ane",
    ]

    async def escanear(self) -> list[ContenidoDetectado]:
        resultados: list[ContenidoDetectado] = []

        for url in self.urls:
            html = await self.fetch_pagina(url)
            if not html:
                continue

            items = self._extraer_proyectos(html, url)
            resultados.extend(items)

        return resultados

    def _extraer_proyectos(self, html: str, base_url: str) -> list[ContenidoDetectado]:
        items: list[ContenidoDetectado] = []

        # Buscar titulos de proyectos de ley
        patron = re.findall(
            r'<a\s+href="([^"]*)"[^>]*>\s*((?:Proyecto|PL|P\.L\.)[^<]{5,300})</a>',
            html,
            re.IGNORECASE,
        )

        # Buscar "Por medio del cual" / "Por la cual" — formula tipica de PL
        patron_formula = re.findall(
            r'<(?:a|td|li|p|span)[^>]*>\s*([^<]*(?:por (?:medio del|la) cual|por el cual)[^<]{10,300})\s*</(?:a|td|li|p|span)>',
            html,
            re.IGNORECASE,
        )

        vistos: set[str] = set()

        for href, titulo in patron:
            titulo = re.sub(r'<[^>]+>', '', titulo).strip()
            titulo = re.sub(r'\s+', ' ', titulo)
            if titulo in vistos or len(titulo) < 15:
                continue
            vistos.add(titulo)

            if self._es_tic(titulo):
                url_completa = href if href.startswith("http") else f"https://{self.dominio}{href}"
                items.append(ContenidoDetectado(
                    titulo=titulo[:200],
                    url=url_completa,
                    fuente_nombre="Congreso de la Republica",
                    tipo="LEGISLATIVA",
                    fecha_publicacion=datetime.now(timezone.utc),
                    metadata={"camara": "Senado" if "senado" in base_url else "Camara"},
                ))

        for titulo_raw in patron_formula:
            titulo = titulo_raw.strip()
            titulo = re.sub(r'\s+', ' ', titulo)
            if titulo in vistos or len(titulo) < 20:
                continue
            vistos.add(titulo)

            if self._es_tic(titulo):
                items.append(ContenidoDetectado(
                    titulo=titulo[:200],
                    url=base_url,
                    fuente_nombre="Congreso de la Republica",
                    tipo="LEGISLATIVA",
                    fecha_publicacion=datetime.now(timezone.utc),
                ))

        return items[:10]

    def _es_tic(self, texto: str) -> bool:
        texto_lower = texto.lower()
        return any(p in texto_lower for p in self.PALABRAS_CLAVE_TIC)
