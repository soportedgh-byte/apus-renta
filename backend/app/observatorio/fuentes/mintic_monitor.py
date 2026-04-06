"""
CecilIA v2 — Monitor MinTIC (www.mintic.gov.co)
Contraloria General de la Republica de Colombia

Monitorea: resoluciones, circulares y noticias del Ministerio TIC.
Sprint: 8
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Optional

from app.observatorio.fuentes.base_monitor import ContenidoDetectado, MonitorBase

logger = logging.getLogger("cecilia.observatorio.mintic")


class MinTICMonitor(MonitorBase):
    """Monitor del Ministerio de Tecnologias de la Informacion y las Comunicaciones."""

    nombre = "MinTIC"
    dominio = "www.mintic.gov.co"
    urls = [
        "https://www.mintic.gov.co/portal/inicio/Sala-de-prensa/Noticias/",
        "https://www.mintic.gov.co/portal/inicio/Normatividad/Resoluciones/",
        "https://www.mintic.gov.co/portal/inicio/Normatividad/Circulares/",
    ]

    async def escanear(self) -> list[ContenidoDetectado]:
        resultados: list[ContenidoDetectado] = []

        for url in self.urls:
            html = await self.fetch_pagina(url)
            if not html:
                continue

            tipo = self._detectar_tipo(url)
            items = self._extraer_items(html, url, tipo)
            resultados.extend(items)

        return resultados

    def _detectar_tipo(self, url: str) -> str:
        if "Resoluciones" in url or "Circulares" in url:
            return "REGULATORIA"
        return "NOTICIA"

    def _extraer_items(self, html: str, base_url: str, tipo: str) -> list[ContenidoDetectado]:
        items: list[ContenidoDetectado] = []

        # Buscar titulos en patrones comunes de MinTIC
        # Pattern: <a href="..." class="...">Titulo</a> dentro de divs de noticias
        patron_enlaces = re.findall(
            r'<a\s+href="([^"]*mintic\.gov\.co[^"]*)"[^>]*>\s*([^<]{10,200})\s*</a>',
            html,
            re.IGNORECASE,
        )

        # Patron alternativo: titulos en h2/h3 con enlaces
        patron_titulos = re.findall(
            r'<h[23][^>]*>\s*<a\s+href="([^"]*)"[^>]*>\s*(.+?)\s*</a>\s*</h[23]>',
            html,
            re.IGNORECASE | re.DOTALL,
        )

        todos_enlaces = patron_enlaces + patron_titulos
        vistos: set[str] = set()

        for href, titulo in todos_enlaces:
            titulo = re.sub(r'<[^>]+>', '', titulo).strip()
            titulo = re.sub(r'\s+', ' ', titulo)

            if len(titulo) < 15 or titulo in vistos:
                continue
            vistos.add(titulo)

            # Filtrar solo contenido relevante TIC
            if not self._es_relevante(titulo):
                continue

            url_completa = href if href.startswith("http") else f"https://{self.dominio}{href}"

            items.append(ContenidoDetectado(
                titulo=titulo,
                url=url_completa,
                fuente_nombre="MinTIC",
                tipo=tipo,
                fecha_publicacion=datetime.now(timezone.utc),
                metadata={"seccion": base_url.split("/")[-2] if "/" in base_url else "general"},
            ))

        return items[:10]  # Max 10 items por seccion

    def _es_relevante(self, titulo: str) -> bool:
        """Filtro basico de relevancia para contenido TIC."""
        titulo_lower = titulo.lower()
        palabras_clave = [
            "resolucion", "circular", "decreto", "ley", "proyecto",
            "telecomunicaciones", "espectro", "banda ancha", "5g", "fibra",
            "conectividad", "digital", "ciberseguridad", "datos personales",
            "gobierno digital", "transformacion", "innovacion", "contratacion",
            "presupuesto", "inversion", "tic", "internet", "mintic",
            "regalias", "fondo", "plan nacional",
        ]
        return any(p in titulo_lower for p in palabras_clave)
