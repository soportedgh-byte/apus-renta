"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Paquete: app/formatos
Proposito: Generador de Formatos CGR (1-30) en DOCX profesional
           con encabezado institucional y estructura normativa
Sprint: 4
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from app.formatos.formato_base import FormatoBaseCGR
from app.formatos.registro import FORMATOS_IMPLEMENTADOS, obtener_generador

__all__ = [
    "FormatoBaseCGR",
    "FORMATOS_IMPLEMENTADOS",
    "obtener_generador",
]
