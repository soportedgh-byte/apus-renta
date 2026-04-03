"""
CecilIA v2 — Endpoints de configuracion
"""

from __future__ import annotations

import logging
from fastapi import APIRouter

from app.llm import info_modelo_activo

logger = logging.getLogger("cecilia.api.config")

enrutador = APIRouter()


@enrutador.get(
    "/modelo-activo",
    summary="Modelo LLM activo",
    description="Retorna informacion del modelo LLM actualmente configurado.",
)
async def modelo_activo() -> dict[str, str]:
    """Retorna info del modelo activo para el badge del frontend."""
    return info_modelo_activo()
