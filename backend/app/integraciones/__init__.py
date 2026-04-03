"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: app/integraciones/__init__.py
Propósito: Inicialización del paquete de integraciones externas — clientes HTTP
           para SECOP, DANE, Congreso y sistemas internos CGR
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from app.integraciones.base import ClienteBaseIntegracion
from app.integraciones.secop import ClienteSECOP
from app.integraciones.dane import ClienteDANE
from app.integraciones.congreso import ClienteCongreso
from app.integraciones.sireci import ClienteSIRECI
from app.integraciones.sigeci import ClienteSIGECI
from app.integraciones.apa import ClienteAPA
from app.integraciones.diari import ClienteDIARI

__all__: list[str] = [
    "ClienteBaseIntegracion",
    "ClienteSECOP",
    "ClienteDANE",
    "ClienteCongreso",
    "ClienteSIRECI",
    "ClienteSIGECI",
    "ClienteAPA",
    "ClienteDIARI",
]
