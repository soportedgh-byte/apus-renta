"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/api/capacitacion_routes.py
Proposito: Endpoints REST para el modulo de capacitacion/tutor:
           rutas de aprendizaje, lecciones, progreso, quizzes y generadores.
Sprint: 6
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import obtener_sesion_db
from app.services.capacitacion_service import CapacitacionService

logger = logging.getLogger("cecilia.api.capacitacion")

enrutador = APIRouter()


# ── Schemas Pydantic ─────────────────────────────────────────────────────────

class CompletarLeccionRequest(BaseModel):
    usuario_id: int
    ruta_id: str
    leccion_id: str


class QuizRequest(BaseModel):
    usuario_id: int
    ruta_id: str
    leccion_id: Optional[str] = None
    puntaje: float = Field(..., ge=0, le=100)
    total_preguntas: int = Field(..., ge=1)
    respuestas: list[dict[str, Any]] = Field(default_factory=list)


class GenerarManualRequest(BaseModel):
    tema: str = "auditoria"
    nivel: str = "basico"


class GenerarPodcastRequest(BaseModel):
    tema: str = "control_fiscal"


class GenerarGuiaFormatoRequest(BaseModel):
    numero_formato: int = Field(..., ge=1, le=30)


# ── Endpoints: Rutas de aprendizaje ──────────────────────────────────────────

@enrutador.get("/rutas")
async def listar_rutas(
    direccion: Optional[str] = Query(None, description="Filtrar por DES|DVF|TODOS"),
    db: AsyncSession = Depends(obtener_sesion_db),
) -> list[dict[str, Any]]:
    """Lista todas las rutas de aprendizaje activas."""
    servicio = CapacitacionService(db)
    rutas = await servicio.listar_rutas(direccion=direccion)
    return rutas


@enrutador.get("/rutas/{ruta_id}")
async def obtener_ruta(
    ruta_id: str,
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Obtiene una ruta de aprendizaje por su ID."""
    servicio = CapacitacionService(db)
    ruta = await servicio.obtener_ruta(ruta_id)
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return ruta


@enrutador.get("/rutas/{ruta_id}/lecciones")
async def listar_lecciones(
    ruta_id: str,
    db: AsyncSession = Depends(obtener_sesion_db),
) -> list[dict[str, Any]]:
    """Lista las lecciones de una ruta de aprendizaje."""
    servicio = CapacitacionService(db)
    lecciones = await servicio.listar_lecciones(ruta_id)
    return lecciones


@enrutador.get("/lecciones/{leccion_id}")
async def obtener_leccion(
    leccion_id: str,
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Obtiene una leccion por su ID con contenido Markdown."""
    servicio = CapacitacionService(db)
    leccion = await servicio.obtener_leccion(leccion_id)
    if not leccion:
        raise HTTPException(status_code=404, detail="Leccion no encontrada")
    return leccion


# ── Endpoints: Progreso ──────────────────────────────────────────────────────

@enrutador.post("/progreso/completar")
async def marcar_completada(
    datos: CompletarLeccionRequest,
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Marca una leccion como completada para un usuario."""
    servicio = CapacitacionService(db)
    progreso = await servicio.marcar_leccion_completada(
        usuario_id=datos.usuario_id,
        ruta_id=datos.ruta_id,
        leccion_id=datos.leccion_id,
    )
    return progreso


@enrutador.get("/progreso")
async def obtener_progreso(
    usuario_id: int = Query(...),
    ruta_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Obtiene el progreso de un usuario en las rutas de aprendizaje."""
    servicio = CapacitacionService(db)
    if ruta_id:
        progreso = await servicio.obtener_progreso_usuario(usuario_id, ruta_id)
    else:
        progreso = await servicio.obtener_resumen_progreso(usuario_id)
    return progreso


# ── Endpoints: Quizzes ───────────────────────────────────────────────────────

@enrutador.post("/quiz")
async def registrar_quiz(
    datos: QuizRequest,
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Registra el resultado de un quiz de evaluacion."""
    servicio = CapacitacionService(db)
    resultado = await servicio.registrar_quiz(
        usuario_id=datos.usuario_id,
        ruta_id=datos.ruta_id,
        leccion_id=datos.leccion_id,
        puntaje=datos.puntaje,
        total_preguntas=datos.total_preguntas,
        respuestas=datos.respuestas,
    )
    return resultado


@enrutador.get("/quiz/resultados")
async def obtener_quizzes(
    usuario_id: int = Query(...),
    ruta_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(obtener_sesion_db),
) -> list[dict[str, Any]]:
    """Obtiene los resultados de quizzes de un usuario."""
    servicio = CapacitacionService(db)
    resultados = await servicio.obtener_quizzes_usuario(usuario_id, ruta_id=ruta_id)
    return resultados


# ── Endpoints: Generadores de contenido ──────────────────────────────────────

@enrutador.post("/generar-manual")
async def generar_manual(datos: GenerarManualRequest) -> dict[str, Any]:
    """Genera un manual DOCX didactico sobre el tema solicitado."""
    from app.services.capacitacion_service import generar_manual_docx
    import base64

    docx_bytes = generar_manual_docx(tema=datos.tema, nivel=datos.nivel)
    return {
        "tipo": "manual_docx",
        "tema": datos.tema,
        "nivel": datos.nivel,
        "contenido_base64": base64.b64encode(docx_bytes).decode("utf-8"),
        "nombre_archivo": f"Manual_{datos.tema}_{datos.nivel}.docx",
    }


@enrutador.post("/generar-podcast-script")
async def generar_podcast(datos: GenerarPodcastRequest) -> dict[str, Any]:
    """Genera un guion conversacional estilo podcast sobre el tema."""
    from app.services.capacitacion_service import generar_podcast_script

    script = generar_podcast_script(tema=datos.tema)
    return {
        "tipo": "podcast_script",
        "tema": datos.tema,
        "script": script,
    }


@enrutador.post("/generar-glosario")
async def generar_glosario() -> dict[str, Any]:
    """Genera un glosario DOCX con terminos de control fiscal."""
    from app.services.capacitacion_service import generar_glosario_docx
    import base64

    docx_bytes = generar_glosario_docx()
    return {
        "tipo": "glosario_docx",
        "contenido_base64": base64.b64encode(docx_bytes).decode("utf-8"),
        "nombre_archivo": "Glosario_Control_Fiscal_CGR.docx",
    }


@enrutador.post("/generar-guia-formato")
async def generar_guia_formato(datos: GenerarGuiaFormatoRequest) -> dict[str, Any]:
    """Genera una guia DOCX para un formato especifico de la GAF."""
    from app.services.capacitacion_service import generar_guia_formato_docx
    import base64

    docx_bytes = generar_guia_formato_docx(numero_formato=datos.numero_formato)
    return {
        "tipo": "guia_formato_docx",
        "numero_formato": datos.numero_formato,
        "contenido_base64": base64.b64encode(docx_bytes).decode("utf-8"),
        "nombre_archivo": f"Guia_Formato_{datos.numero_formato:02d}_CGR.docx",
    }


# ── Endpoints: Metricas ─────────────────────────────────────────────────────

@enrutador.get("/metricas")
async def obtener_metricas(
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Obtiene metricas globales del modulo de capacitacion."""
    servicio = CapacitacionService(db)
    metricas = await servicio.obtener_metricas_globales()
    return metricas


# ── Endpoints: Seed ──────────────────────────────────────────────────────────

@enrutador.post("/seed")
async def seed_datos(
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, str]:
    """Puebla las rutas y lecciones iniciales (solo desarrollo)."""
    servicio = CapacitacionService(db)
    await servicio.seed_rutas_y_lecciones()
    return {"mensaje": "Rutas y lecciones de capacitacion cargadas exitosamente"}
