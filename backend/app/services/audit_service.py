"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: audit_service.py
Propósito: Servicio CRUD de proyectos de auditoría y gestión de fases
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("cecilia.services.audit")

# Fases válidas del proceso auditor
FASES_VALIDAS: list[str] = [
    "preplaneacion",
    "planeacion",
    "ejecucion",
    "informe",
    "seguimiento",
]

# Estados válidos de un proyecto de auditoría
ESTADOS_PROYECTO: list[str] = [
    "borrador",
    "en_curso",
    "suspendido",
    "finalizado",
    "archivado",
]

# Tipos de auditoría según Decreto 403/2020
TIPOS_AUDITORIA: list[str] = [
    "financiera",
    "desempeno",
    "cumplimiento",
    "financiera_y_desempeno",
    "actuacion_especial",
]


class AuditService:
    """Servicio de gestión de proyectos de auditoría.

    Responsabilidades:
    - CRUD de proyectos de auditoría.
    - Gestión de fases del proceso auditor.
    - Control de transiciones entre fases.
    - Asignación de equipos auditores.
    """

    def __init__(self, db_session: AsyncSession) -> None:
        """Inicializa el servicio de auditoría.

        Args:
            db_session: Sesión de base de datos asíncrona.
        """
        self._db: AsyncSession = db_session

    async def crear_proyecto(
        self,
        nombre: str,
        sujeto_control: str,
        tipo_auditoria: str,
        vigencia: str,
        direccion: str,
        responsable_id: str,
        equipo: Optional[list[str]] = None,
        descripcion: Optional[str] = None,
    ) -> dict[str, Any]:
        """Crea un nuevo proyecto de auditoría.

        Args:
            nombre: Nombre del proyecto.
            sujeto_control: Nombre de la entidad a auditar.
            tipo_auditoria: Tipo de auditoría (financiera, desempeno, etc.).
            vigencia: Vigencia fiscal (ej: '2025').
            direccion: Dirección responsable (DES o DVF).
            responsable_id: ID del auditor responsable.
            equipo: Lista de IDs de miembros del equipo.
            descripcion: Descripción adicional del proyecto.

        Returns:
            Datos del proyecto creado.
        """
        if tipo_auditoria not in TIPOS_AUDITORIA:
            raise ValueError(
                f"Tipo de auditoría '{tipo_auditoria}' no válido. "
                f"Opciones: {', '.join(TIPOS_AUDITORIA)}"
            )

        if direccion not in ("DES", "DVF"):
            raise ValueError("Dirección debe ser 'DES' o 'DVF'.")

        proyecto_id: str = str(uuid.uuid4())
        ahora: datetime = datetime.now(timezone.utc)

        await self._db.execute(
            text("""
                INSERT INTO proyectos_auditoria
                    (id, nombre, sujeto_control, tipo_auditoria, vigencia,
                     direccion, fase_actual, estado, responsable_id, equipo,
                     descripcion, creado_en, actualizado_en)
                VALUES
                    (:id, :nombre, :sujeto, :tipo, :vigencia,
                     :direccion, 'preplaneacion', 'borrador', :responsable, :equipo,
                     :descripcion, :creado, :actualizado)
            """),
            {
                "id": proyecto_id,
                "nombre": nombre,
                "sujeto": sujeto_control,
                "tipo": tipo_auditoria,
                "vigencia": vigencia,
                "direccion": direccion,
                "responsable": responsable_id,
                "equipo": ",".join(equipo) if equipo else "",
                "descripcion": descripcion or "",
                "creado": ahora.isoformat(),
                "actualizado": ahora.isoformat(),
            },
        )
        await self._db.commit()

        logger.info(
            "Proyecto creado [%s]: %s — %s (%s)",
            proyecto_id[:8], nombre, sujeto_control, tipo_auditoria,
        )

        return {
            "id": proyecto_id,
            "nombre": nombre,
            "sujeto_control": sujeto_control,
            "tipo_auditoria": tipo_auditoria,
            "vigencia": vigencia,
            "direccion": direccion,
            "fase_actual": "preplaneacion",
            "estado": "borrador",
            "responsable_id": responsable_id,
            "creado_en": ahora.isoformat(),
        }

    async def obtener_proyecto(self, proyecto_id: str) -> Optional[dict[str, Any]]:
        """Obtiene un proyecto de auditoría por su ID.

        Args:
            proyecto_id: ID del proyecto.

        Returns:
            Datos del proyecto o None si no existe.
        """
        result = await self._db.execute(
            text("SELECT * FROM proyectos_auditoria WHERE id = :id"),
            {"id": proyecto_id},
        )
        row = result.fetchone()
        return dict(row._mapping) if row else None

    async def listar_proyectos(
        self,
        direccion: Optional[str] = None,
        estado: Optional[str] = None,
        responsable_id: Optional[str] = None,
        limite: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Lista proyectos de auditoría con filtros opcionales.

        Args:
            direccion: Filtrar por dirección (DES/DVF).
            estado: Filtrar por estado.
            responsable_id: Filtrar por responsable.
            limite: Número máximo de resultados.
            offset: Desplazamiento para paginación.

        Returns:
            Lista de proyectos.
        """
        condiciones: list[str] = []
        params: dict[str, Any] = {"limite": limite, "offset": offset}

        if direccion:
            condiciones.append("direccion = :direccion")
            params["direccion"] = direccion
        if estado:
            condiciones.append("estado = :estado")
            params["estado"] = estado
        if responsable_id:
            condiciones.append("responsable_id = :responsable_id")
            params["responsable_id"] = responsable_id

        where: str = "WHERE " + " AND ".join(condiciones) if condiciones else ""

        result = await self._db.execute(
            text(f"""
                SELECT * FROM proyectos_auditoria
                {where}
                ORDER BY actualizado_en DESC
                LIMIT :limite OFFSET :offset
            """),
            params,
        )

        return [dict(row._mapping) for row in result.fetchall()]

    async def avanzar_fase(
        self,
        proyecto_id: str,
        usuario_id: str,
    ) -> dict[str, Any]:
        """Avanza el proyecto a la siguiente fase del proceso auditor.

        Args:
            proyecto_id: ID del proyecto.
            usuario_id: ID del usuario que autoriza el avance.

        Returns:
            Datos actualizados del proyecto.

        Raises:
            ValueError: Si no se puede avanzar de fase.
        """
        proyecto: Optional[dict[str, Any]] = await self.obtener_proyecto(proyecto_id)

        if proyecto is None:
            raise ValueError(f"Proyecto no encontrado: {proyecto_id}")

        fase_actual: str = proyecto["fase_actual"]
        indice_actual: int = FASES_VALIDAS.index(fase_actual) if fase_actual in FASES_VALIDAS else -1

        if indice_actual == -1:
            raise ValueError(f"Fase actual inválida: {fase_actual}")

        if indice_actual >= len(FASES_VALIDAS) - 1:
            raise ValueError(f"El proyecto ya está en la última fase: {fase_actual}")

        nueva_fase: str = FASES_VALIDAS[indice_actual + 1]
        ahora: datetime = datetime.now(timezone.utc)

        await self._db.execute(
            text("""
                UPDATE proyectos_auditoria
                SET fase_actual = :nueva_fase,
                    estado = 'en_curso',
                    actualizado_en = :ahora
                WHERE id = :id
            """),
            {"nueva_fase": nueva_fase, "ahora": ahora.isoformat(), "id": proyecto_id},
        )
        await self._db.commit()

        logger.info(
            "Proyecto [%s] avanzó de '%s' a '%s' (autorizado por %s)",
            proyecto_id[:8], fase_actual, nueva_fase, usuario_id,
        )

        return {
            "id": proyecto_id,
            "fase_anterior": fase_actual,
            "fase_actual": nueva_fase,
            "estado": "en_curso",
            "actualizado_en": ahora.isoformat(),
        }

    async def actualizar_estado(
        self,
        proyecto_id: str,
        nuevo_estado: str,
    ) -> dict[str, Any]:
        """Actualiza el estado de un proyecto.

        Args:
            proyecto_id: ID del proyecto.
            nuevo_estado: Nuevo estado (borrador, en_curso, suspendido, finalizado, archivado).

        Returns:
            Datos actualizados.
        """
        if nuevo_estado not in ESTADOS_PROYECTO:
            raise ValueError(
                f"Estado '{nuevo_estado}' no válido. "
                f"Opciones: {', '.join(ESTADOS_PROYECTO)}"
            )

        ahora: datetime = datetime.now(timezone.utc)

        await self._db.execute(
            text("""
                UPDATE proyectos_auditoria
                SET estado = :estado, actualizado_en = :ahora
                WHERE id = :id
            """),
            {"estado": nuevo_estado, "ahora": ahora.isoformat(), "id": proyecto_id},
        )
        await self._db.commit()

        return {"id": proyecto_id, "estado": nuevo_estado, "actualizado_en": ahora.isoformat()}
