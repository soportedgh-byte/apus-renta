"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/models/__init__.py
Proposito: Inicializacion del paquete de modelos SQLAlchemy.
           Exporta Base y todos los modelos para que Alembic los detecte.
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from app.models.base import Base
from app.models.usuario import Usuario
from app.models.conversacion import Conversacion
from app.models.mensaje import Mensaje
from app.models.documento import Documento
from app.models.hallazgo import Hallazgo
from app.models.auditoria import Auditoria
from app.models.proyecto_auditoria import ProyectoAuditoria
from app.models.alerta import Alerta
from app.models.formato_generado import FormatoGenerado
from app.models.log_trazabilidad import LogTrazabilidad
from app.models.capacitacion import (
    RutaAprendizaje,
    Leccion,
    ProgresoUsuario,
    QuizResultado,
)

__all__: list[str] = [
    "Base",
    "Usuario",
    "Conversacion",
    "Mensaje",
    "Documento",
    "Hallazgo",
    "Auditoria",
    "ProyectoAuditoria",
    "Alerta",
    "FormatoGenerado",
    "LogTrazabilidad",
    "RutaAprendizaje",
    "Leccion",
    "ProgresoUsuario",
    "QuizResultado",
]
