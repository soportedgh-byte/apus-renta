"""
CecilIA v2 — Fuentes del Observatorio TIC
Crawlers para monitoreo de entidades del sector TIC colombiano.
"""

from app.observatorio.fuentes.base_monitor import MonitorBase
from app.observatorio.fuentes.mintic_monitor import MinTICMonitor
from app.observatorio.fuentes.crc_monitor import CRCMonitor
from app.observatorio.fuentes.ane_monitor import ANEMonitor
from app.observatorio.fuentes.congreso_monitor import CongresoMonitor
from app.observatorio.fuentes.noticias_monitor import NoticiasMonitor

MONITORES: list[type[MonitorBase]] = [
    MinTICMonitor,
    CRCMonitor,
    ANEMonitor,
    CongresoMonitor,
    NoticiasMonitor,
]

__all__ = [
    "MonitorBase",
    "MinTICMonitor",
    "CRCMonitor",
    "ANEMonitor",
    "CongresoMonitor",
    "NoticiasMonitor",
    "MONITORES",
]
