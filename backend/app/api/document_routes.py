"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: app/api/document_routes.py
Propósito: Endpoints de gestión documental — subida, listado, consulta,
           eliminación e ingestión de documentos para el pipeline RAG
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import configuracion
from app.main import obtener_sesion_db

logger = logging.getLogger("cecilia.api.documentos")

enrutador = APIRouter()

# ── Colecciones válidas de documentos ────────────────────────────────────────

COLECCIONES_VALIDAS: set[str] = {
    "normativa",          # Leyes, decretos, resoluciones, circulares
    "manuales",           # Guías de auditoría, manuales de procedimiento
    "informes",           # Informes de auditoría previos
    "planes",             # Planes de vigilancia y auditoría
    "jurisprudencia",     # Sentencias, conceptos jurídicos
    "contractual",        # Contratos y adiciones (SECOP)
    "financiera",         # Estados financieros, presupuestos
    "general",            # Documentos no clasificados
}

# ── Tipos de archivo permitidos ──────────────────────────────────────────────

TIPOS_MIME_PERMITIDOS: set[str] = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain",
    "text/csv",
}

TAMANO_MAXIMO_MB: int = 50


# ── Esquemas ─────────────────────────────────────────────────────────────────


class RespuestaDocumento(BaseModel):
    """Metadatos de un documento almacenado."""

    id: str
    nombre_archivo: str
    tipo_mime: str
    tamano_bytes: int
    coleccion: str
    estado: str  # subido | procesando | indexado | error
    creado_en: datetime
    usuario_id: int
    etiquetas: list[str] = Field(default_factory=list)


class SolicitudIngesta(BaseModel):
    """Solicitud para disparar el pipeline de ingestión."""

    documento_ids: list[str] = Field(
        ..., min_length=1, max_length=100,
        description="IDs de documentos a ingestar en el pipeline RAG",
    )
    coleccion: str = Field(default="general", description="Colección destino para los vectores")
    forzar_reindexado: bool = Field(default=False, description="Forzar re-procesamiento aunque ya esté indexado")


class RespuestaIngesta(BaseModel):
    """Resultado de la solicitud de ingestión."""

    tarea_id: str
    documentos_encolados: int
    mensaje: str


# ── Dependencia temporal de usuario autenticado ──────────────────────────────


async def _obtener_usuario_actual_id() -> int:
    """Dependencia temporal — será reemplazada por auth real."""
    return 1


# ── Endpoints ────────────────────────────────────────────────────────────────


@enrutador.post(
    "/subir",
    response_model=RespuestaDocumento,
    status_code=status.HTTP_201_CREATED,
    summary="Subir documento",
    description="Sube un documento al sistema para su posterior ingestión en el pipeline RAG.",
)
async def subir_documento(
    archivo: UploadFile = File(..., description="Archivo a subir (PDF, DOCX, XLSX, TXT, CSV)"),
    coleccion: str = Query(default="general", description="Colección destino del documento"),
    etiquetas: Optional[str] = Query(default=None, description="Etiquetas separadas por coma"),
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Sube un documento, valida tipo y tamaño, y lo almacena en el sistema de archivos."""

    # Validar colección
    if coleccion not in COLECCIONES_VALIDAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Colección inválida '{coleccion}'. Válidas: {sorted(COLECCIONES_VALIDAS)}",
        )

    # Validar tipo MIME
    tipo_mime: str = archivo.content_type or "application/octet-stream"
    if tipo_mime not in TIPOS_MIME_PERMITIDOS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de archivo no soportado: {tipo_mime}. Permitidos: {sorted(TIPOS_MIME_PERMITIDOS)}",
        )

    # Leer contenido y validar tamaño
    contenido: bytes = await archivo.read()
    tamano_bytes: int = len(contenido)
    tamano_maximo_bytes: int = TAMANO_MAXIMO_MB * 1024 * 1024

    if tamano_bytes > tamano_maximo_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Archivo excede el límite de {TAMANO_MAXIMO_MB} MB.",
        )

    if tamano_bytes == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo está vacío.",
        )

    # Generar identificador único y ruta de almacenamiento
    documento_id: str = str(uuid.uuid4())
    nombre_archivo: str = archivo.filename or f"documento_{documento_id}"
    lista_etiquetas: list[str] = [e.strip() for e in etiquetas.split(",")] if etiquetas else []

    # TODO: Almacenar archivo en disco y registrar en base de datos
    # ruta_destino = Path(configuracion.RUTA_ALMACENAMIENTO_DOCS) / coleccion / documento_id
    # ruta_destino.mkdir(parents=True, exist_ok=True)
    # archivo_destino = ruta_destino / nombre_archivo
    # archivo_destino.write_bytes(contenido)

    logger.info(
        "Documento subido: id=%s, nombre=%s, coleccion=%s, tamano=%d bytes, usuario=%d",
        documento_id, nombre_archivo, coleccion, tamano_bytes, usuario_id,
    )

    return {
        "id": documento_id,
        "nombre_archivo": nombre_archivo,
        "tipo_mime": tipo_mime,
        "tamano_bytes": tamano_bytes,
        "coleccion": coleccion,
        "estado": "subido",
        "creado_en": datetime.now(timezone.utc),
        "usuario_id": usuario_id,
        "etiquetas": lista_etiquetas,
    }


@enrutador.get(
    "/",
    response_model=list[RespuestaDocumento],
    summary="Listar documentos",
    description="Lista documentos filtrados opcionalmente por colección.",
)
async def listar_documentos(
    coleccion: Optional[str] = Query(default=None, description="Filtrar por colección"),
    limite: int = Query(default=50, ge=1, le=200, description="Número máximo de resultados"),
    desplazamiento: int = Query(default=0, ge=0, description="Desplazamiento para paginación"),
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> list[dict[str, Any]]:
    """Lista documentos con filtrado opcional por colección y paginación."""

    if coleccion and coleccion not in COLECCIONES_VALIDAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Colección inválida '{coleccion}'.",
        )

    # TODO: Implementar consulta real contra tabla documentos
    logger.info(
        "Listando documentos: coleccion=%s, limite=%d, offset=%d, usuario=%d",
        coleccion, limite, desplazamiento, usuario_id,
    )
    return []


@enrutador.get(
    "/{documento_id}",
    response_model=RespuestaDocumento,
    summary="Obtener metadatos de documento",
    description="Retorna los metadatos de un documento específico.",
)
async def obtener_documento(
    documento_id: str,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Obtiene los metadatos de un documento por su ID."""

    # TODO: Consultar base de datos real
    logger.info("Consultando documento %s para usuario %d", documento_id, usuario_id)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Documento {documento_id} no encontrado.",
    )


@enrutador.delete(
    "/{documento_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar documento",
    description="Elimina un documento del sistema y su índice vectorial.",
)
async def eliminar_documento(
    documento_id: str,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> None:
    """Elimina un documento, sus vectores asociados y el archivo físico."""

    # TODO: Implementar eliminación real (BD + vectores + archivo)
    logger.info("Solicitud de eliminación de documento %s por usuario %d", documento_id, usuario_id)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Documento {documento_id} no encontrado.",
    )


@enrutador.post(
    "/ingestar",
    response_model=RespuestaIngesta,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Disparar pipeline de ingestión",
    description="Encola documentos para procesamiento e indexación en el pipeline RAG.",
)
async def ingestar_documentos(
    solicitud: SolicitudIngesta,
    db: AsyncSession = Depends(obtener_sesion_db),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Encola documentos para el pipeline de ingestión RAG.

    El pipeline incluye:
    1. Extracción de texto (PDF, DOCX, XLSX).
    2. Fragmentación (chunking) con solapamiento.
    3. Generación de embeddings.
    4. Almacenamiento en pgvector.
    """

    if solicitud.coleccion not in COLECCIONES_VALIDAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Colección inválida '{solicitud.coleccion}'.",
        )

    tarea_id: str = str(uuid.uuid4())

    # TODO: Encolar tarea en Redis/Celery para procesamiento asíncrono
    logger.info(
        "Ingestión encolada: tarea=%s, documentos=%d, coleccion=%s, forzar=%s, usuario=%d",
        tarea_id, len(solicitud.documento_ids), solicitud.coleccion,
        solicitud.forzar_reindexado, usuario_id,
    )

    return {
        "tarea_id": tarea_id,
        "documentos_encolados": len(solicitud.documento_ids),
        "mensaje": f"Se encolaron {len(solicitud.documento_ids)} documento(s) para ingestión en '{solicitud.coleccion}'.",
    }
