"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/api/sesion_routes.py
Proposito: Endpoints de memoria de sesion — cargar contexto de proyecto,
           guardar estado, generar resumen, listar proyectos del usuario.
Sprint: 11
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import obtener_sesion_db

logger = logging.getLogger("cecilia.api.sesion")

enrutador = APIRouter()


# ── Esquemas Pydantic ───────────────────────────────────────────────────────

class CrearProyectoRequest(BaseModel):
    usuario_id: int
    auditoria_id: str
    nombre_sesion: str
    sujeto_control: Optional[str] = None
    vigencia: Optional[str] = None
    tipo_auditoria: Optional[str] = None
    fase: str = "preplaneacion"
    objetivo: Optional[str] = None


class GuardarEstadoRequest(BaseModel):
    estado_json: Optional[dict[str, Any]] = None
    resumen_manual: Optional[str] = None


# ── Endpoints ───────────────────────────────────────────────────────────────

@enrutador.get("/proyectos", summary="Listar proyectos del usuario")
async def listar_proyectos(
    usuario_id: int = Query(..., description="ID del usuario"),
    solo_activos: bool = Query(default=True),
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Lista los proyectos de auditoria del usuario con su estado de memoria."""
    from app.models.proyecto_auditoria import ProyectoAuditoria

    query = select(ProyectoAuditoria).where(
        ProyectoAuditoria.usuario_id == usuario_id
    )
    if solo_activos:
        query = query.where(ProyectoAuditoria.activo == True)

    query = query.order_by(ProyectoAuditoria.updated_at.desc())
    result = await db.execute(query)
    proyectos = result.scalars().all()

    return {
        "proyectos": [
            {
                "id": p.id,
                "nombre_sesion": p.nombre_sesion,
                "auditoria_id": p.auditoria_id,
                "sujeto_control": p.sujeto_control,
                "vigencia": p.vigencia,
                "tipo_auditoria": p.tipo_auditoria,
                "fase": p.fase,
                "activo": p.activo,
                "tiene_resumen": bool(p.resumen_sesiones),
                "documentos": len(p.documentos_procesados or []),
                "hallazgos": len(p.hallazgos_vinculados or []),
                "formatos": len(p.formatos_generados or []),
                "ultima_actividad": p.ultima_actividad.isoformat() if p.ultima_actividad else None,
                "created_at": p.created_at.isoformat(),
            }
            for p in proyectos
        ],
        "total": len(proyectos),
    }


@enrutador.post("/proyectos", summary="Crear proyecto de sesion")
async def crear_proyecto(
    datos: CrearProyectoRequest,
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Crea un nuevo proyecto de auditoria con memoria de sesion."""
    from app.models.proyecto_auditoria import ProyectoAuditoria

    proyecto = ProyectoAuditoria(
        id=str(uuid.uuid4()),
        usuario_id=datos.usuario_id,
        auditoria_id=datos.auditoria_id,
        nombre_sesion=datos.nombre_sesion,
        sujeto_control=datos.sujeto_control,
        vigencia=datos.vigencia,
        tipo_auditoria=datos.tipo_auditoria,
        fase=datos.fase,
        objetivo=datos.objetivo,
        activo=True,
        estado="activo",
        ultima_actividad=datetime.now(timezone.utc),
    )

    db.add(proyecto)
    await db.flush()

    return {
        "id": proyecto.id,
        "nombre_sesion": proyecto.nombre_sesion,
        "fase": proyecto.fase,
        "mensaje": "Proyecto creado exitosamente",
    }


@enrutador.get("/proyectos/{proyecto_id}/contexto", summary="Cargar contexto del proyecto")
async def cargar_contexto(
    proyecto_id: str,
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Carga el contexto completo del proyecto para inyectar al LLM al inicio de sesion."""
    from app.services.memoria_service import MemoriaService

    servicio = MemoriaService(db_session=db)
    contexto = await servicio.cargar_contexto_proyecto(db, proyecto_id)

    if not contexto.get("existe"):
        return {"error": "Proyecto no encontrado", "proyecto_id": proyecto_id}

    # Construir prompt del sistema
    prompt_sistema = servicio.construir_system_prompt_proyecto(contexto)

    return {
        **contexto,
        "prompt_sistema": prompt_sistema,
    }


@enrutador.post("/proyectos/{proyecto_id}/guardar-estado", summary="Guardar estado de sesion")
async def guardar_estado(
    proyecto_id: str,
    datos: GuardarEstadoRequest,
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Guarda el estado del proyecto al cerrar sesion o por inactividad (30min)."""
    from app.services.memoria_service import MemoriaService

    servicio = MemoriaService(db_session=db)
    await servicio.guardar_estado_sesion(
        db, proyecto_id,
        estado=datos.estado_json,
        resumen=datos.resumen_manual,
    )

    return {"mensaje": "Estado guardado", "proyecto_id": proyecto_id}


@enrutador.post("/proyectos/{proyecto_id}/generar-resumen", summary="Generar resumen de sesion")
async def generar_resumen(
    proyecto_id: str,
    session_id: str = Query(..., description="ID de sesion de chat"),
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Genera resumen de la sesion via LLM y lo acumula al proyecto."""
    from app.services.memoria_service import MemoriaService

    servicio = MemoriaService(db_session=db)

    # Generar resumen (heuristico por defecto, LLM si disponible)
    resumen = await servicio.generar_resumen_sesion(session_id)

    # Acumular al proyecto
    await servicio.acumular_resumen(db, proyecto_id, resumen)

    return {
        "resumen": resumen,
        "proyecto_id": proyecto_id,
        "mensaje": "Resumen generado y acumulado",
    }


@enrutador.get("/proyectos/{proyecto_id}/resumen", summary="Obtener resumen de sesiones")
async def obtener_resumen(
    proyecto_id: str,
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Retorna el resumen acumulado de sesiones del proyecto."""
    from app.models.proyecto_auditoria import ProyectoAuditoria

    result = await db.execute(
        select(
            ProyectoAuditoria.resumen_sesiones,
            ProyectoAuditoria.ultima_sesion_resumen,
            ProyectoAuditoria.ultima_actividad,
        ).where(ProyectoAuditoria.id == proyecto_id)
    )
    row = result.one_or_none()

    if not row:
        return {"error": "Proyecto no encontrado"}

    return {
        "resumen_acumulado": row[0] or "",
        "ultima_sesion": row[1] or "",
        "ultima_actividad": row[2].isoformat() if row[2] else None,
    }
