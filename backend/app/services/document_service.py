"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: document_service.py
Propósito: Servicio de gestión documental — carga, ingestión, metadatos
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

from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.ingesta import DocumentoIngestado, ingestar_documento
from app.rag.chunking import Fragmento, dividir_en_fragmentos
from app.rag.embeddings import generar_embeddings

logger = logging.getLogger("cecilia.services.document")


class DocumentService:
    """Servicio de gestión documental.

    Responsabilidades:
    - Recepción y validación de archivos cargados.
    - Pipeline de ingestión: extracción -> chunking -> embeddings -> almacenamiento.
    - Gestión de metadatos documentales.
    - Asociación de documentos a proyectos de auditoría.
    """

    def __init__(self, db_session: Optional[AsyncSession] = None) -> None:
        """Inicializa el servicio documental.

        Args:
            db_session: Sesión de base de datos asíncrona.
        """
        self._db = db_session

    async def cargar_documento(
        self,
        ruta_archivo: Path | str,
        usuario_id: str,
        proyecto_auditoria_id: Optional[str] = None,
        coleccion: str = "general",
        metadata_extra: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Carga y procesa un documento completo a través del pipeline RAG.

        Pipeline: Archivo -> Extracción texto -> Chunking -> Embeddings -> pgvector

        Args:
            ruta_archivo: Ruta al archivo a cargar.
            usuario_id: ID del usuario que carga el documento.
            proyecto_auditoria_id: ID del proyecto de auditoría asociado.
            coleccion: Nombre de la colección en la base vectorial.
            metadata_extra: Metadatos adicionales.

        Returns:
            Diccionario con resultado de la carga.
        """
        documento_id: str = str(uuid.uuid4())
        inicio: datetime = datetime.now(timezone.utc)
        ruta: Path = Path(ruta_archivo)

        logger.info(
            "Cargando documento [%s]: %s (usuario=%s, proyecto=%s)",
            documento_id[:8], ruta.name, usuario_id, proyecto_auditoria_id,
        )

        # 1. Ingestión — extracción de texto
        try:
            doc: DocumentoIngestado = ingestar_documento(
                ruta=ruta,
                metadata_extra={
                    "documento_id": documento_id,
                    "usuario_id": usuario_id,
                    "proyecto_auditoria_id": proyecto_auditoria_id,
                    **(metadata_extra or {}),
                },
                coleccion=coleccion,
            )
        except (FileNotFoundError, ValueError) as e:
            logger.error("Error en ingestión: %s", e)
            return {"exito": False, "error": str(e), "documento_id": documento_id}

        if not doc.contenido.strip():
            return {
                "exito": False,
                "error": "No se pudo extraer texto del documento.",
                "documento_id": documento_id,
            }

        # 2. Chunking
        coleccion_final: str = (
            f"proyecto_{proyecto_auditoria_id}" if proyecto_auditoria_id else coleccion
        )

        fragmentos: list[Fragmento] = dividir_en_fragmentos(
            texto=doc.contenido,
            tamano=1000,
            solapamiento=200,
            metadata_base={
                "documento_id": documento_id,
                "nombre_archivo": ruta.name,
                "coleccion": coleccion_final,
                "usuario_id": usuario_id,
                "proyecto_auditoria_id": proyecto_auditoria_id,
                "fecha_carga": inicio.isoformat(),
            },
        )

        # 3. Embeddings
        textos: list[str] = [f.contenido for f in fragmentos]
        try:
            embeddings: list[list[float]] = generar_embeddings(textos)
        except Exception:
            logger.exception("Error al generar embeddings para '%s'.", ruta.name)
            return {
                "exito": False,
                "error": "Error al generar embeddings.",
                "documento_id": documento_id,
            }

        # 4. Almacenamiento en pgvector
        fragmentos_almacenados: int = 0
        if self._db:
            try:
                fragmentos_almacenados = await self._almacenar_en_pgvector(
                    fragmentos, embeddings, coleccion_final
                )
            except Exception:
                logger.exception("Error al almacenar en pgvector.")
                return {
                    "exito": False,
                    "error": "Error al almacenar en base de datos vectorial.",
                    "documento_id": documento_id,
                }
        else:
            fragmentos_almacenados = len(fragmentos)
            logger.warning("Sin sesión de BD; embeddings no almacenados en pgvector.")

        duracion: float = (datetime.now(timezone.utc) - inicio).total_seconds()

        resultado: dict[str, Any] = {
            "exito": True,
            "documento_id": documento_id,
            "nombre_archivo": ruta.name,
            "tipo": doc.tipo,
            "paginas": doc.paginas,
            "caracteres": len(doc.contenido),
            "fragmentos": len(fragmentos),
            "fragmentos_almacenados": fragmentos_almacenados,
            "coleccion": coleccion_final,
            "duracion_segundos": round(duracion, 3),
        }

        logger.info(
            "Documento cargado [%s]: %d fragmentos en %.2fs",
            documento_id[:8], fragmentos_almacenados, duracion,
        )

        return resultado

    async def _almacenar_en_pgvector(
        self,
        fragmentos: list[Fragmento],
        embeddings: list[list[float]],
        coleccion: str,
    ) -> int:
        """Almacena fragmentos con embeddings en pgvector.

        Args:
            fragmentos: Lista de fragmentos de texto.
            embeddings: Lista de vectores de embedding.
            coleccion: Nombre de la colección.

        Returns:
            Número de fragmentos almacenados.
        """
        import json as json_lib

        count: int = 0
        for fragmento, embedding in zip(fragmentos, embeddings):
            query: str = """
                INSERT INTO embeddings_documentos (id, contenido, metadata, coleccion, embedding)
                VALUES (:id, :contenido, :metadata, :coleccion, :embedding)
            """
            from sqlalchemy import text
            await self._db.execute(
                text(query),
                {
                    "id": str(uuid.uuid4()),
                    "contenido": fragmento.contenido,
                    "metadata": json_lib.dumps(fragmento.metadata),
                    "coleccion": coleccion,
                    "embedding": str(embedding),
                },
            )
            count += 1

        await self._db.commit()
        return count

    async def obtener_documentos_proyecto(
        self,
        proyecto_auditoria_id: str,
    ) -> list[dict[str, Any]]:
        """Obtiene los documentos asociados a un proyecto de auditoría.

        Args:
            proyecto_auditoria_id: ID del proyecto.

        Returns:
            Lista de metadatos de documentos.
        """
        if not self._db:
            return []

        from sqlalchemy import text
        result = await self._db.execute(
            text("""
                SELECT DISTINCT metadata->>'documento_id' as doc_id,
                       metadata->>'nombre_archivo' as nombre,
                       metadata->>'fecha_carga' as fecha,
                       COUNT(*) as fragmentos
                FROM embeddings_documentos
                WHERE coleccion = :coleccion
                GROUP BY metadata->>'documento_id', metadata->>'nombre_archivo', metadata->>'fecha_carga'
                ORDER BY metadata->>'fecha_carga' DESC
            """),
            {"coleccion": f"proyecto_{proyecto_auditoria_id}"},
        )

        return [dict(row._mapping) for row in result.fetchall()]

    async def eliminar_documento(
        self,
        documento_id: str,
    ) -> bool:
        """Elimina un documento y todos sus fragmentos.

        Args:
            documento_id: ID del documento a eliminar.

        Returns:
            True si se eliminó correctamente.
        """
        if not self._db:
            return False

        from sqlalchemy import text
        await self._db.execute(
            text("""
                DELETE FROM embeddings_documentos
                WHERE metadata->>'documento_id' = :documento_id
            """),
            {"documento_id": documento_id},
        )
        await self._db.commit()

        logger.info("Documento eliminado: %s", documento_id)
        return True
