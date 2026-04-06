"""
CecilIA v2 — Monitor de noticias TIC (RSS feeds)
Contraloria General de la Republica de Colombia

Monitorea: RSS feeds de medios especializados en TIC y economia.
Sprint: 8
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Optional
from xml.etree import ElementTree as ET

from app.observatorio.fuentes.base_monitor import ContenidoDetectado, MonitorBase

logger = logging.getLogger("cecilia.observatorio.noticias")


class NoticiasMonitor(MonitorBase):
    """Monitor de noticias TIC via RSS feeds."""

    nombre = "Noticias TIC"
    dominio = "feeds"

    # Feeds RSS de medios colombianos e internacionales sector TIC
    FEEDS: list[dict[str, str]] = [
        {
            "url": "https://www.portafolio.co/rss/tecnologia.xml",
            "nombre": "Portafolio Tecnologia",
        },
        {
            "url": "https://www.dinero.com/rss/tecnologia.xml",
            "nombre": "Revista Dinero Tecnologia",
        },
        {
            "url": "https://www.telesemana.com/feed/",
            "nombre": "TeleSemana",
        },
        {
            "url": "https://www.elespectador.com/rss/tecnologia.xml",
            "nombre": "El Espectador Tecnologia",
        },
        {
            "url": "https://www.eltiempo.com/rss/tecnosfera.xml",
            "nombre": "El Tiempo Tecnosfera",
        },
    ]

    PALABRAS_CLAVE_TIC_COLOMBIA = [
        "mintic", "ministerio tic", "espectro", "5g", "telecomunicaciones",
        "conectividad", "banda ancha", "gobierno digital", "ciberseguridad",
        "contraloria", "control fiscal", "presupuesto tic",
        "contratacion", "secop", "licitacion", "adjudicacion",
        "colombia digital", "transformacion digital", "fibra optica",
        "operador", "claro", "movistar", "tigo", "wom", "etb",
        "ane", "crc", "crcom", "comision de regulacion",
        "datos personales", "habeas data", "sic",
        "inteligencia artificial", "blockchain", "computacion nube",
    ]

    async def escanear(self) -> list[ContenidoDetectado]:
        resultados: list[ContenidoDetectado] = []

        for feed_info in self.FEEDS:
            xml_text = await self.fetch_rss(feed_info["url"])
            if not xml_text:
                continue

            items = self._parsear_rss(xml_text, feed_info["nombre"])
            resultados.extend(items)

        return resultados

    def _parsear_rss(self, xml_text: str, nombre_fuente: str) -> list[ContenidoDetectado]:
        items: list[ContenidoDetectado] = []

        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as e:
            logger.warning("Error parseando RSS de %s: %s", nombre_fuente, e)
            return []

        # Buscar items en RSS 2.0 y Atom
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        rss_items = root.findall(".//item")
        atom_entries = root.findall(".//atom:entry", ns)

        for item in rss_items:
            titulo_elem = item.find("title")
            link_elem = item.find("link")
            desc_elem = item.find("description")
            pub_date_elem = item.find("pubDate")

            if titulo_elem is None or not titulo_elem.text:
                continue

            titulo = titulo_elem.text.strip()
            if not self._es_relevante_tic(titulo):
                # Tambien verificar en la descripcion
                desc = desc_elem.text if desc_elem is not None and desc_elem.text else ""
                if not self._es_relevante_tic(desc):
                    continue

            url = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
            resumen = self._limpiar_html(
                desc_elem.text if desc_elem is not None and desc_elem.text else ""
            )[:500]

            fecha = self._parsear_fecha(
                pub_date_elem.text if pub_date_elem is not None and pub_date_elem.text else ""
            )

            items.append(ContenidoDetectado(
                titulo=titulo[:200],
                resumen=resumen,
                url=url,
                fuente_nombre=nombre_fuente,
                tipo="NOTICIA",
                fecha_publicacion=fecha,
                metadata={"feed": nombre_fuente},
            ))

        for entry in atom_entries:
            titulo_elem = entry.find("atom:title", ns)
            link_elem = entry.find("atom:link", ns)
            summary_elem = entry.find("atom:summary", ns)
            published_elem = entry.find("atom:published", ns)

            if titulo_elem is None or not titulo_elem.text:
                continue

            titulo = titulo_elem.text.strip()
            if not self._es_relevante_tic(titulo):
                continue

            url = ""
            if link_elem is not None:
                url = link_elem.get("href", "")

            resumen = self._limpiar_html(
                summary_elem.text if summary_elem is not None and summary_elem.text else ""
            )[:500]

            fecha = self._parsear_fecha(
                published_elem.text if published_elem is not None and published_elem.text else ""
            )

            items.append(ContenidoDetectado(
                titulo=titulo[:200],
                resumen=resumen,
                url=url,
                fuente_nombre=nombre_fuente,
                tipo="NOTICIA",
                fecha_publicacion=fecha,
                metadata={"feed": nombre_fuente},
            ))

        return items[:15]  # Max 15 por feed

    def _es_relevante_tic(self, texto: str) -> bool:
        texto_lower = texto.lower()
        return any(p in texto_lower for p in self.PALABRAS_CLAVE_TIC_COLOMBIA)

    def _limpiar_html(self, texto: str) -> str:
        texto = re.sub(r'<[^>]+>', '', texto)
        texto = re.sub(r'\s+', ' ', texto)
        return texto.strip()

    def _parsear_fecha(self, fecha_str: str) -> Optional[datetime]:
        if not fecha_str:
            return datetime.now(timezone.utc)
        formatos = [
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S %Z",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
        ]
        for fmt in formatos:
            try:
                return datetime.strptime(fecha_str.strip(), fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        return datetime.now(timezone.utc)
