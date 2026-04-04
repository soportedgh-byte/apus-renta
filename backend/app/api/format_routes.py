"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/api/format_routes.py
Proposito: Endpoints de generacion de formatos CGR (1-30) en DOCX profesional.
           Generacion, descarga, previsualizacion, catalogo y historial.
Sprint: 4
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import io
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.formatos.registro import (
    CATALOGO_FORMATOS,
    FORMATOS_IMPLEMENTADOS,
    obtener_generador,
)
from app.main import obtener_sesion_db
from app.models.formato_generado import FormatoGenerado

logger = logging.getLogger("cecilia.api.formatos")

enrutador = APIRouter()


# ── Esquemas ─────────────────────────────────────────────────────────────────


class SolicitudGenerarFormato(BaseModel):
    """Esquema para solicitar la generacion de un formato CGR."""

    numero_formato: int = Field(..., ge=1, le=30, description="Numero del formato CGR (1-30)")
    auditoria_id: str = Field(default="", description="ID de la auditoria asociada")
    parametros: dict[str, Any] = Field(
        default_factory=dict,
        description="Parametros especificos del formato (varian segun tipo)",
    )
    generar_con_ia: bool = Field(
        default=True,
        description="Si True, CecilIA genera contenido sugerido. Si False, solo estructura vacia.",
    )


class RespuestaFormato(BaseModel):
    """Respuesta con datos de un formato generado."""

    id: str
    numero_formato: int
    nombre_formato: str
    auditoria_id: str
    estado: str
    generado_con_ia: bool
    ruta_archivo: Optional[str] = None
    creado_en: datetime
    usuario_id: int


class InfoPlantilla(BaseModel):
    """Informacion de una plantilla de formato."""

    numero: int
    nombre: str
    fase: str
    implementado: bool


class RespuestaHistorial(BaseModel):
    """Respuesta de historial de formatos."""

    id: str
    numero_formato: int
    nombre_formato: str
    estado: str
    generado_con_ia: bool
    creado_en: datetime


# ── Dependencia temporal de usuario autenticado ──────────────────────────────


async def _obtener_usuario_actual_id() -> int:
    """Dependencia temporal — sera reemplazada por auth real."""
    return 1


# ── Endpoints ────────────────────────────────────────────────────────────────


@enrutador.post(
    "/generar",
    status_code=status.HTTP_200_OK,
    summary="Generar formato CGR en DOCX",
    description="Genera un formato CGR (1-30) como documento DOCX profesional con encabezado institucional.",
)
async def generar_formato(
    solicitud: SolicitudGenerarFormato,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> StreamingResponse:
    """Genera un formato CGR y lo retorna como stream DOCX.

    El proceso incluye:
    1. Validar que el formato exista en el catalogo.
    2. Generar el documento DOCX con python-docx.
    3. Persistir metadatos en la base de datos.
    4. Retornar como StreamingResponse para descarga.
    """

    if solicitud.numero_formato not in CATALOGO_FORMATOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato {solicitud.numero_formato} no existe. Rango valido: 1-30.",
        )

    info = CATALOGO_FORMATOS[solicitud.numero_formato]
    formato_id = str(uuid.uuid4())

    try:
        # Generar el DOCX
        generador = obtener_generador(
            numero_formato=solicitud.numero_formato,
            datos=solicitud.parametros,
        )
        docx_bytes = generador.generar_bytes()

        # Persistir metadatos en BD
        try:
            registro = FormatoGenerado(
                id=formato_id,
                numero_formato=solicitud.numero_formato,
                nombre_formato=info["nombre"],
                auditoria_id=solicitud.auditoria_id or None,
                usuario_id=usuario_id,
                estado="completado",
                generado_con_ia=solicitud.generar_con_ia,
                parametros=solicitud.parametros,
                contenido_generado=f"DOCX generado ({len(docx_bytes)} bytes)",
            )
            db.add(registro)
            await db.flush()
        except Exception as exc_db:
            logger.warning("No se pudo persistir formato en BD: %s", exc_db)

        logger.info(
            "Formato F%02d generado: id=%s, bytes=%d, usuario=%d",
            solicitud.numero_formato, formato_id, len(docx_bytes), usuario_id,
        )

        # Retornar como stream
        nombre_archivo = (
            f"F{solicitud.numero_formato:02d}_{info['nombre'].replace(' ', '_')}.docx"
        )

        return StreamingResponse(
            io.BytesIO(docx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f'attachment; filename="{nombre_archivo}"',
                "X-Formato-Id": formato_id,
                "X-Formato-Nombre": info["nombre"],
            },
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        logger.error("Error generando formato F%02d: %s", solicitud.numero_formato, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar el formato: {str(exc)}",
        )


@enrutador.get(
    "/plantillas",
    response_model=list[InfoPlantilla],
    summary="Catalogo de plantillas de formatos",
    description="Retorna el catalogo completo de formatos CGR (1-30) con estado de implementacion.",
)
async def listar_plantillas() -> list[dict[str, Any]]:
    """Lista todas las plantillas de formatos disponibles."""
    plantillas = []
    for numero, info in CATALOGO_FORMATOS.items():
        plantillas.append({
            "numero": numero,
            "nombre": info["nombre"],
            "fase": info["fase"],
            "implementado": numero in FORMATOS_IMPLEMENTADOS,
        })
    return plantillas


@enrutador.post(
    "/previsualizar",
    summary="Previsualizar formato en HTML",
    description="Genera una previsualizacion HTML del formato para mostrar en el frontend.",
)
async def previsualizar_formato(
    solicitud: SolicitudGenerarFormato,
) -> dict[str, Any]:
    """Genera previsualizacion HTML basica del formato."""

    if solicitud.numero_formato not in CATALOGO_FORMATOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato {solicitud.numero_formato} no existe.",
        )

    info = CATALOGO_FORMATOS[solicitud.numero_formato]
    implementado = solicitud.numero_formato in FORMATOS_IMPLEMENTADOS

    # Generar HTML de previsualizacion
    entidad = solicitud.parametros.get("nombre_entidad", "[COMPLETAR]")
    vigencia = solicitud.parametros.get("vigencia", "[COMPLETAR]")

    html = f"""
    <div style="font-family: Georgia, serif; max-width: 800px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="color: #1A5276; margin: 0;">CONTRALORIA GENERAL DE LA REPUBLICA</h2>
            <p style="color: #5F6368; font-size: 12px; margin: 4px 0;">Sistema de Control Fiscal — CecilIA v2</p>
            <hr style="border: 1.5px solid #C9A84C; margin: 10px 40px;" />
            <h3 style="color: #1A5276;">FORMATO F{solicitud.numero_formato:02d} — {info['nombre'].upper()}</h3>
        </div>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <tr>
                <td style="background: #1A5276; color: white; padding: 6px 10px; font-weight: bold; font-size: 13px; width: 30%;">Entidad auditada</td>
                <td style="border: 1px solid #ccc; padding: 6px 10px; font-size: 13px;">{entidad}</td>
            </tr>
            <tr>
                <td style="background: #1A5276; color: white; padding: 6px 10px; font-weight: bold; font-size: 13px;">Vigencia</td>
                <td style="border: 1px solid #ccc; padding: 6px 10px; font-size: 13px;">{vigencia}</td>
            </tr>
            <tr>
                <td style="background: #1A5276; color: white; padding: 6px 10px; font-weight: bold; font-size: 13px;">Fase</td>
                <td style="border: 1px solid #ccc; padding: 6px 10px; font-size: 13px;">{info['fase'].replace('-', ' ').title()}</td>
            </tr>
            <tr>
                <td style="background: #1A5276; color: white; padding: 6px 10px; font-weight: bold; font-size: 13px;">Estado</td>
                <td style="border: 1px solid #ccc; padding: 6px 10px; font-size: 13px;">{'Implementado' if implementado else 'Estructura basica'}</td>
            </tr>
        </table>
        <p style="color: #5F6368; font-style: italic; font-size: 11px; text-align: center;">
            Vista previa — El documento DOCX final incluye estilos profesionales,
            tablas con formato y encabezado institucional CGR.
        </p>
    </div>
    """

    return {
        "numero_formato": solicitud.numero_formato,
        "nombre_formato": info["nombre"],
        "fase": info["fase"],
        "implementado": implementado,
        "html": html,
    }


@enrutador.get(
    "/historial",
    response_model=list[RespuestaHistorial],
    summary="Historial de formatos generados",
    description="Lista los formatos generados previamente con paginacion.",
)
async def obtener_historial(
    limite: int = Query(default=50, ge=1, le=200),
    desplazamiento: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> list[dict[str, Any]]:
    """Obtiene el historial de formatos generados."""
    try:
        resultado = await db.execute(
            select(FormatoGenerado)
            .where(FormatoGenerado.usuario_id == usuario_id)
            .order_by(FormatoGenerado.created_at.desc())
            .limit(limite)
            .offset(desplazamiento)
        )
        formatos = resultado.scalars().all()

        return [
            {
                "id": f.id,
                "numero_formato": f.numero_formato,
                "nombre_formato": f.nombre_formato,
                "estado": f.estado,
                "generado_con_ia": f.generado_con_ia,
                "creado_en": f.created_at,
            }
            for f in formatos
        ]
    except Exception as exc:
        logger.warning("Error consultando historial: %s", exc)
        return []


@enrutador.get(
    "/",
    response_model=list[RespuestaFormato],
    summary="Listar formatos generados",
    description="Lista los formatos CGR generados con filtros opcionales.",
)
async def listar_formatos(
    auditoria_id: Optional[str] = Query(default=None),
    numero_formato: Optional[int] = Query(default=None, ge=1, le=30),
    limite: int = Query(default=50, ge=1, le=200),
    desplazamiento: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> list[dict[str, Any]]:
    """Lista formatos generados con filtrado y paginacion."""
    try:
        query = select(FormatoGenerado).where(
            FormatoGenerado.usuario_id == usuario_id
        )
        if auditoria_id:
            query = query.where(FormatoGenerado.auditoria_id == auditoria_id)
        if numero_formato:
            query = query.where(FormatoGenerado.numero_formato == numero_formato)

        query = query.order_by(FormatoGenerado.created_at.desc()).limit(limite).offset(desplazamiento)
        resultado = await db.execute(query)
        formatos = resultado.scalars().all()

        return [
            {
                "id": f.id,
                "numero_formato": f.numero_formato,
                "nombre_formato": f.nombre_formato,
                "auditoria_id": f.auditoria_id or "",
                "estado": f.estado,
                "generado_con_ia": f.generado_con_ia,
                "ruta_archivo": f.ruta_archivo,
                "creado_en": f.created_at,
                "usuario_id": f.usuario_id or 0,
            }
            for f in formatos
        ]
    except Exception as exc:
        logger.warning("Error listando formatos: %s", exc)
        return []


@enrutador.get(
    "/{formato_id}",
    response_model=RespuestaFormato,
    summary="Obtener detalle de formato",
)
async def obtener_formato(
    formato_id: str,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Obtiene un formato generado por su ID."""
    try:
        resultado = await db.execute(
            select(FormatoGenerado).where(FormatoGenerado.id == formato_id)
        )
        f = resultado.scalar_one_or_none()
        if not f:
            raise HTTPException(status_code=404, detail="Formato no encontrado.")

        return {
            "id": f.id,
            "numero_formato": f.numero_formato,
            "nombre_formato": f.nombre_formato,
            "auditoria_id": f.auditoria_id or "",
            "estado": f.estado,
            "generado_con_ia": f.generado_con_ia,
            "ruta_archivo": f.ruta_archivo,
            "creado_en": f.created_at,
            "usuario_id": f.usuario_id or 0,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("Error obteniendo formato: %s", exc)
        raise HTTPException(status_code=404, detail="Formato no encontrado.")
