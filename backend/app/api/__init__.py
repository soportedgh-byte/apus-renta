"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/api/__init__.py
Proposito: Inicializacion del paquete de rutas API — exporta todos los enrutadores
Sprint: 0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from app.api.auth_routes import enrutador as enrutador_auth

# Los siguientes enrutadores se implementaran en sprints posteriores:
# from app.api.chat_routes import enrutador as enrutador_chat
# from app.api.document_routes import enrutador as enrutador_documentos
# from app.api.audit_routes import enrutador as enrutador_auditorias
# from app.api.hallazgo_routes import enrutador as enrutador_hallazgos
# from app.api.format_routes import enrutador as enrutador_formatos
# from app.api.rag_routes import enrutador as enrutador_rag
# from app.api.integracion_routes import enrutador as enrutador_integraciones
# from app.api.analytics_routes import enrutador as enrutador_analitica
# from app.api.admin_routes import enrutador as enrutador_admin

__all__: list[str] = [
    "enrutador_auth",
    # "enrutador_chat",
    # "enrutador_documentos",
    # "enrutador_auditorias",
    # "enrutador_hallazgos",
    # "enrutador_formatos",
    # "enrutador_rag",
    # "enrutador_integraciones",
    # "enrutador_analitica",
    # "enrutador_admin",
]
