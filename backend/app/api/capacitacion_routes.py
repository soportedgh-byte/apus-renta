"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/api/capacitacion_routes.py
Proposito: Endpoints REST para el modulo de capacitacion/tutor:
           rutas de aprendizaje, lecciones, progreso, quizzes, gamificacion,
           audio, flashcards, glosario, simulaciones y contenido adaptativo.
Sprint: Capacitacion 2.0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
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


# ── Schemas Capacitacion 2.0 ────────────────────────────────────────────────

class CuestionarioEstiloRequest(BaseModel):
    usuario_id: int
    respuestas: dict[str, str] = Field(
        ..., description="Respuestas del cuestionario VARK: {pregunta_1: 'a', ...}"
    )


class AgregarXPRequest(BaseModel):
    usuario_id: int
    cantidad: int = Field(..., ge=1)
    motivo: str


class GenerarAudioRequest(BaseModel):
    tema: str
    duracion: str = "5 minutos"


class GenerarFlashcardsRequest(BaseModel):
    tema: str
    num_tarjetas: int = Field(default=10, ge=3, le=30)


class GenerarInfografiaRequest(BaseModel):
    tema: str
    tipo_diagrama: str = "flowchart"


class RegistrarRepasoRequest(BaseModel):
    repaso_id: str
    aciertos: int = Field(..., ge=0)
    total: int = Field(..., ge=1)


class IniciarSimulacionRequest(BaseModel):
    simulacion_id: str
    paso: int = Field(default=1, ge=1)
    contexto_previo: str = ""


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
    """Genera un manual DOCX profesional con logos CGR y contenido generado por IA."""
    from app.services.capacitacion_service import generar_manual_docx
    import base64

    llm = _obtener_llm_capacitacion()
    docx_bytes = generar_manual_docx(tema=datos.tema, nivel=datos.nivel, llm=llm)
    nombre_limpio = datos.tema.replace(" ", "_").replace("/", "_")[:50]
    return {
        "tipo": "manual_docx",
        "tema": datos.tema,
        "nivel": datos.nivel,
        "contenido_base64": base64.b64encode(docx_bytes).decode("utf-8"),
        "nombre_archivo": f"Manual_CGR_{nombre_limpio}_{datos.nivel}.docx",
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


# ═══════════════════════════════════════════════════════════════════════════════
# CAPACITACION 2.0 — Aprendizaje adaptativo, gamificacion, audio, simulaciones
# ═══════════════════════════════════════════════════════════════════════════════


# ── Perfil de aprendizaje (cuestionario VARK) ────────────────────────────────

@enrutador.post("/perfil-aprendizaje")
async def registrar_perfil_aprendizaje(
    datos: CuestionarioEstiloRequest,
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Registra respuestas del cuestionario de estilos y calcula perfil VARK."""
    from app.models.capacitacion import PerfilAprendizaje
    from sqlalchemy import select
    import uuid

    # Clasificar por estilo
    conteo = {"lector": 0, "auditivo": 0, "visual": 0, "kinestesico": 0}
    mapa_opciones = {
        "a": "lector", "b": "auditivo", "c": "visual", "d": "kinestesico",
    }
    for pregunta, respuesta in datos.respuestas.items():
        estilo = mapa_opciones.get(respuesta.lower(), "lector")
        conteo[estilo] += 1

    estilo_predominante = max(conteo, key=conteo.get)  # type: ignore[arg-type]

    # Guardar o actualizar perfil
    result = await db.execute(
        select(PerfilAprendizaje).where(
            PerfilAprendizaje.usuario_id == datos.usuario_id
        )
    )
    perfil = result.scalar_one_or_none()

    if perfil:
        perfil.estilo_predominante = estilo_predominante
        perfil.respuestas_cuestionario = datos.respuestas
        perfil.puntajes = conteo
    else:
        perfil = PerfilAprendizaje(
            id=str(uuid.uuid4()),
            usuario_id=datos.usuario_id,
            estilo_predominante=estilo_predominante,
            respuestas_cuestionario=datos.respuestas,
            puntajes=conteo,
        )
        db.add(perfil)

    await db.commit()

    return {
        "usuario_id": datos.usuario_id,
        "estilo_predominante": estilo_predominante,
        "puntajes": conteo,
        "descripcion": _DESCRIPCIONES_ESTILO.get(estilo_predominante, ""),
    }


@enrutador.get("/perfil-aprendizaje/{usuario_id}")
async def obtener_perfil_aprendizaje(
    usuario_id: int,
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Obtiene el perfil de estilo de aprendizaje del usuario."""
    from app.models.capacitacion import PerfilAprendizaje
    from sqlalchemy import select

    result = await db.execute(
        select(PerfilAprendizaje).where(
            PerfilAprendizaje.usuario_id == usuario_id
        )
    )
    perfil = result.scalar_one_or_none()

    if not perfil:
        return {"tiene_perfil": False, "usuario_id": usuario_id}

    return {
        "tiene_perfil": True,
        "usuario_id": usuario_id,
        "estilo_predominante": perfil.estilo_predominante,
        "puntajes": perfil.puntajes,
        "respuestas": perfil.respuestas_cuestionario,
        "descripcion": _DESCRIPCIONES_ESTILO.get(perfil.estilo_predominante, ""),
    }


# ── Gamificacion: XP, niveles, rachas, insignias ───────────────────────────

@enrutador.get("/gamificacion/{usuario_id}")
async def obtener_gamificacion(
    usuario_id: int,
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Obtiene perfil de gamificacion: XP, nivel, racha, insignias."""
    from app.services.gamificacion_service import GamificacionService
    servicio = GamificacionService()
    return await servicio.obtener_o_crear_perfil(db, usuario_id)


@enrutador.post("/gamificacion/xp")
async def agregar_xp(
    datos: AgregarXPRequest,
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Agrega XP al usuario y actualiza nivel/racha/insignias."""
    from app.services.gamificacion_service import GamificacionService
    servicio = GamificacionService()
    resultado = await servicio.agregar_xp(
        db, datos.usuario_id, datos.cantidad, datos.motivo
    )
    await db.commit()
    return resultado


# ── Repaso espaciado (spaced repetition) ─────────────────────────────────────

@enrutador.get("/repasos/{usuario_id}")
async def obtener_repasos_pendientes(
    usuario_id: int,
    db: AsyncSession = Depends(obtener_sesion_db),
) -> list[dict[str, Any]]:
    """Obtiene repasos programados pendientes para el usuario."""
    from app.services.gamificacion_service import GamificacionService
    servicio = GamificacionService()
    return await servicio.obtener_repasos_pendientes(db, usuario_id)


@enrutador.post("/repasos/registrar")
async def registrar_resultado_repaso(
    datos: RegistrarRepasoRequest,
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Registra resultado de un repaso y reprograma el siguiente."""
    from app.services.gamificacion_service import GamificacionService
    servicio = GamificacionService()
    resultado = await servicio.registrar_resultado_repaso(
        db, datos.repaso_id, datos.aciertos, datos.total
    )
    await db.commit()
    return resultado


# ── Audio: podcasts y explicaciones con edge-tts ─────────────────────────────

def _obtener_llm_capacitacion():
    """Obtiene instancia del LLM configurado para capacitacion."""
    try:
        from app.llm import obtener_llm
        return obtener_llm()
    except Exception as e:
        logger.warning("No se pudo obtener LLM para capacitacion: %s", e)
        return None


@enrutador.post("/generar-audio")
async def generar_audio_podcast(
    datos: GenerarAudioRequest,
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Genera audio MP3 tipo podcast con 2 voces sobre un tema."""
    from app.services.audio_service import AudioService
    import base64

    llm = _obtener_llm_capacitacion()
    servicio = AudioService(llm=llm)

    # Generar script con LLM + RAG
    script = await servicio.generar_script_podcast(
        tema=datos.tema, duracion=datos.duracion
    )

    # Intentar generar audio MP3 con edge-tts
    try:
        audio_bytes, duracion = await servicio.generar_audio_podcast(script)
        return {
            "tipo": "podcast_audio",
            "tema": datos.tema,
            "script": script,
            "audio_base64": base64.b64encode(audio_bytes).decode("utf-8"),
            "duracion_segundos": duracion,
            "formato": "mp3",
        }
    except Exception as e:
        logger.warning("Audio no generado (edge-tts): %s — retornando solo script", e)
        return {
            "tipo": "podcast_script",
            "tema": datos.tema,
            "script": script,
            "audio_base64": None,
            "duracion_segundos": 0,
            "formato": "text",
            "nota": "Audio no disponible — se retorna solo el script del podcast",
        }


@enrutador.post("/generar-explicacion-audio")
async def generar_explicacion_audio(
    tema: str = Query(...),
    voz: str = Query(default="DON_CARLOS"),
) -> dict[str, Any]:
    """Genera explicacion narrada de un solo locutor."""
    from app.services.audio_service import AudioService
    import base64

    llm = _obtener_llm_capacitacion()
    servicio = AudioService(llm=llm)

    try:
        audio_bytes, duracion = await servicio.generar_explicacion_audio(tema, voz)
        return {
            "tipo": "explicacion_audio",
            "tema": tema,
            "voz": voz,
            "audio_base64": base64.b64encode(audio_bytes).decode("utf-8"),
            "duracion_segundos": duracion,
            "formato": "mp3",
        }
    except Exception as e:
        logger.warning("Audio explicacion no generado: %s", e)
        return {
            "tipo": "explicacion_audio",
            "tema": tema,
            "audio_base64": None,
            "nota": f"Audio no disponible: {e}",
        }


# ── Flashcards ───────────────────────────────────────────────────────────────

@enrutador.post("/generar-flashcards")
async def generar_flashcards(
    datos: GenerarFlashcardsRequest,
) -> dict[str, Any]:
    """Genera set de flashcards sobre un tema con taxonomia de Bloom."""
    from app.services.contenido_leccion_service import ContenidoLeccionService
    llm = _obtener_llm_capacitacion()
    servicio = ContenidoLeccionService(llm=llm)
    tarjetas = await servicio.generar_flashcards(
        tema=datos.tema, num_tarjetas=datos.num_tarjetas
    )
    return {
        "tipo": "flashcards",
        "tema": datos.tema,
        "total": len(tarjetas),
        "tarjetas": tarjetas,
    }


# ── Infografia Mermaid ───────────────────────────────────────────────────────

@enrutador.post("/generar-infografia")
async def generar_infografia(
    datos: GenerarInfografiaRequest,
) -> dict[str, Any]:
    """Genera diagrama Mermaid como imagen renderizada (SVG inline)."""
    from app.services.contenido_leccion_service import ContenidoLeccionService
    import base64 as b64

    llm = _obtener_llm_capacitacion()
    servicio = ContenidoLeccionService(llm=llm)
    mermaid_code = await servicio.generar_infografia_mermaid(
        tema=datos.tema, tipo_diagrama=datos.tipo_diagrama
    )

    # Generar URL de mermaid.ink para renderizado de imagen
    mermaid_b64 = b64.urlsafe_b64encode(mermaid_code.encode("utf-8")).decode("utf-8")
    imagen_url = f"https://mermaid.ink/img/base64:{mermaid_b64}"

    return {
        "tipo": "infografia_mermaid",
        "tema": datos.tema,
        "tipo_diagrama": datos.tipo_diagrama,
        "mermaid": mermaid_code,
        "imagen_url": imagen_url,
    }


# ── Contenido de leccion adaptativo ──────────────────────────────────────────

@enrutador.get("/lecciones/{leccion_id}/contenido-adaptativo")
async def obtener_contenido_adaptativo(
    leccion_id: str,
    usuario_id: int = Query(...),
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Genera contenido de leccion adaptado al estilo de aprendizaje del usuario."""
    from app.services.contenido_leccion_service import ContenidoLeccionService
    from app.models.capacitacion import PerfilAprendizaje
    from sqlalchemy import select

    # Obtener estilo del usuario
    estilo = "lector"
    result = await db.execute(
        select(PerfilAprendizaje).where(
            PerfilAprendizaje.usuario_id == usuario_id
        )
    )
    perfil = result.scalar_one_or_none()
    if perfil:
        estilo = perfil.estilo_predominante

    servicio = ContenidoLeccionService()
    contenido = await servicio.generar_contenido_leccion(
        db, leccion_id, estilo_usuario=estilo
    )
    contenido["estilo_usuario"] = estilo
    return contenido


# ── Glosario interactivo ─────────────────────────────────────────────────────

@enrutador.get("/glosario")
async def listar_glosario(
    categoria: Optional[str] = Query(None),
    busqueda: Optional[str] = Query(None),
    db: AsyncSession = Depends(obtener_sesion_db),
) -> list[dict[str, Any]]:
    """Lista entradas del glosario con filtros opcionales."""
    from app.services.contenido_leccion_service import ContenidoLeccionService
    servicio = ContenidoLeccionService()
    return await servicio.obtener_glosario(db, categoria=categoria, busqueda=busqueda)


@enrutador.post("/glosario/seed")
async def seed_glosario(
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Puebla el glosario con terminos base (solo desarrollo)."""
    from app.services.contenido_leccion_service import ContenidoLeccionService
    servicio = ContenidoLeccionService()
    count = await servicio.seed_glosario(db)
    await db.commit()
    return {"mensaje": f"Glosario poblado con {count} terminos nuevos", "nuevos": count}


# ── Simulaciones guiadas ─────────────────────────────────────────────────────

@enrutador.get("/simulaciones")
async def listar_simulaciones() -> list[dict[str, Any]]:
    """Lista las simulaciones guiadas disponibles."""
    from app.services.contenido_leccion_service import ContenidoLeccionService
    servicio = ContenidoLeccionService()
    return servicio.obtener_simulaciones_disponibles()


@enrutador.post("/simulaciones/paso")
async def obtener_paso_simulacion(
    datos: IniciarSimulacionRequest,
) -> dict[str, Any]:
    """Obtiene contenido de un paso de simulacion (generado con IA)."""
    from app.services.contenido_leccion_service import ContenidoLeccionService
    servicio = ContenidoLeccionService()
    return await servicio.obtener_paso_simulacion(
        simulacion_id=datos.simulacion_id,
        paso=datos.paso,
        contexto_previo=datos.contexto_previo,
    )


# ── Dashboard del aprendiz (resumen completo) ────────────────────────────────

@enrutador.get("/mi-progreso/{usuario_id}")
async def obtener_mi_progreso_completo(
    usuario_id: int,
    db: AsyncSession = Depends(obtener_sesion_db),
) -> dict[str, Any]:
    """Dashboard completo del aprendiz: progreso + gamificacion + repasos."""
    from app.services.gamificacion_service import GamificacionService

    servicio_cap = CapacitacionService(db)
    servicio_gam = GamificacionService()

    # Obtener datos en paralelo
    progreso = await servicio_cap.obtener_resumen_progreso(usuario_id)
    gamificacion = await servicio_gam.obtener_o_crear_perfil(db, usuario_id)
    repasos = await servicio_gam.obtener_repasos_pendientes(db, usuario_id)

    return {
        "usuario_id": usuario_id,
        "progreso": progreso,
        "gamificacion": gamificacion,
        "repasos_pendientes": repasos,
        "total_repasos_pendientes": len(repasos),
    }


# ── Biblioteca de recursos generados ─────────────────────────────────────────

@enrutador.get("/biblioteca")
async def listar_recursos(
    tipo: Optional[str] = Query(None, description="podcast|infografia|flashcard|manual"),
    db: AsyncSession = Depends(obtener_sesion_db),
) -> list[dict[str, Any]]:
    """Lista recursos generados (podcasts, infografias, flashcards, etc.)."""
    from app.models.capacitacion import RecursoGenerado
    from sqlalchemy import select

    query = select(RecursoGenerado).order_by(RecursoGenerado.created_at.desc()).limit(50)
    if tipo:
        query = query.where(RecursoGenerado.tipo == tipo)

    result = await db.execute(query)
    recursos = result.scalars().all()

    return [
        {
            "id": r.id,
            "tipo": r.tipo,
            "tema": r.tema,
            "formato": r.formato,
            "duracion_segundos": r.duracion_segundos,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in recursos
    ]


# ── Constantes internas ──────────────────────────────────────────────────────

_DESCRIPCIONES_ESTILO = {
    "lector": "Aprendes mejor leyendo textos detallados, tomando notas y revisando documentos escritos.",
    "auditivo": "Aprendes mejor escuchando explicaciones, podcasts y discusiones en grupo.",
    "visual": "Aprendes mejor con diagramas, tablas, infografias y organizadores visuales.",
    "kinestesico": "Aprendes mejor haciendo ejercicios practicos, simulaciones y actividades interactivas.",
}
