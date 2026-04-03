"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/models/base.py
Proposito: Clase base declarativa para todos los modelos SQLAlchemy
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Base(DeclarativeBase):
    """Clase base declarativa para todos los modelos del sistema CecilIA v2."""

    pass
