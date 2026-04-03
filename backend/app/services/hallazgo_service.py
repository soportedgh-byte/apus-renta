"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: hallazgo_service.py
Propósito: Servicio CRUD de hallazgos con estructura de 5 elementos y flujo de trabajo
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

logger = logging.getLogger("cecilia.services.hallazgo")

# Tipos de incidencia del hallazgo
TIPOS_INCIDENCIA: list[str] = [
    "administrativo",
    "fiscal",
    "disciplinario",
    "penal",
    "fiscal_y_disciplinario",
    "fiscal_y_penal",
    "disciplinario_y_penal",
    "fiscal_disciplinario_y_penal",
]

# Estados del flujo de trabajo del hallazgo
ESTADOS_HALLAZGO: list[str] = [
    "borrador",
    "en_revision",
    "aprobado_supervisor",
    "comunicado",
    "con_respuesta",
    "evaluado",
    "definitivo",
    "trasladado",
    "archivado",
]

# Transiciones válidas de estado
TRANSICIONES_VALIDAS: dict[str, list[str]] = {
    "borrador": ["en_revision"],
    "en_revision": ["borrador", "aprobado_supervisor"],
    "aprobado_supervisor": ["comunicado"],
    "comunicado": ["con_respuesta"],
    "con_respuesta": ["evaluado"],
    "evaluado": ["definitivo", "archivado"],
    "definitivo": ["trasladado", "archivado"],
    "trasladado": ["archivado"],
    "archivado": [],
}


class HallazgoService:
    """Servicio de gestión de hallazgos de auditoría.

    Implementa el CRUD con la estructura de 5 elementos requerida
    por la CGR (condición, criterio, causa, efecto, recomendación)
    y el flujo de trabajo desde borrador hasta traslado/archivo.
    """

    def __init__(self, db_session: AsyncSession) -> None:
        """Inicializa el servicio de hallazgos.

        Args:
            db_session: Sesión de base de datos asíncrona.
        """
        self._db: AsyncSession = db_session

    async def crear_hallazgo(
        self,
        proyecto_auditoria_id: str,
        titulo: str,
        condicion: str,
        criterio: str,
        causa: str,
        efecto: str,
        recomendacion: str,
        tipo_incidencia: str = "administrativo",
        cuantia: Optional[float] = None,
        evidencia_soporte: Optional[str] = None,
        creado_por: str = "",
    ) -> dict[str, Any]:
        """Crea un nuevo hallazgo de auditoría con los 5 elementos.

        Args:
            proyecto_auditoria_id: ID del proyecto de auditoría.
            titulo: Título descriptivo del hallazgo.
            condicion: Lo que se encontró (situación actual).
            criterio: Norma o estándar aplicable.
            causa: Razones por las cuales se presenta la diferencia.
            efecto: Impacto o consecuencia (cuantificación si aplica).
            recomendacion: Acción correctiva propuesta.
            tipo_incidencia: Tipo de incidencia (administrativo, fiscal, etc.).
            cuantia: Cuantía del presunto detrimento patrimonial en COP.
            evidencia_soporte: Referencia a papeles de trabajo y evidencia.
            creado_por: ID del usuario que crea el hallazgo.

        Returns:
            Datos del hallazgo creado.
        """
        if tipo_incidencia not in TIPOS_INCIDENCIA:
            raise ValueError(
                f"Tipo de incidencia '{tipo_incidencia}' no válido. "
                f"Opciones: {', '.join(TIPOS_INCIDENCIA)}"
            )

        # Validar campos obligatorios de los 5 elementos
        campos_obligatorios: dict[str, str] = {
            "condicion": condicion,
            "criterio": criterio,
            "causa": causa,
            "efecto": efecto,
            "recomendacion": recomendacion,
        }
        faltantes: list[str] = [k for k, v in campos_obligatorios.items() if not v.strip()]
        if faltantes:
            raise ValueError(
                f"Los siguientes elementos del hallazgo son obligatorios y están vacíos: "
                f"{', '.join(faltantes)}. Conforme a las guías de auditoría de la CGR, "
                f"todo hallazgo debe tener los 5 elementos."
            )

        hallazgo_id: str = str(uuid.uuid4())
        ahora: datetime = datetime.now(timezone.utc)

        await self._db.execute(
            text("""
                INSERT INTO hallazgos
                    (id, proyecto_auditoria_id, titulo, condicion, criterio,
                     causa, efecto, recomendacion, tipo_incidencia, cuantia,
                     evidencia_soporte, estado, creado_por, creado_en, actualizado_en)
                VALUES
                    (:id, :proyecto, :titulo, :condicion, :criterio,
                     :causa, :efecto, :recomendacion, :tipo, :cuantia,
                     :evidencia, 'borrador', :creado_por, :creado, :actualizado)
            """),
            {
                "id": hallazgo_id,
                "proyecto": proyecto_auditoria_id,
                "titulo": titulo,
                "condicion": condicion,
                "criterio": criterio,
                "causa": causa,
                "efecto": efecto,
                "recomendacion": recomendacion,
                "tipo": tipo_incidencia,
                "cuantia": cuantia,
                "evidencia": evidencia_soporte or "",
                "creado_por": creado_por,
                "creado": ahora.isoformat(),
                "actualizado": ahora.isoformat(),
            },
        )
        await self._db.commit()

        logger.info(
            "Hallazgo creado [%s]: '%s' — tipo=%s cuantía=%s",
            hallazgo_id[:8], titulo[:50], tipo_incidencia,
            f"${cuantia:,.0f}" if cuantia else "N/A",
        )

        return {
            "id": hallazgo_id,
            "proyecto_auditoria_id": proyecto_auditoria_id,
            "titulo": titulo,
            "tipo_incidencia": tipo_incidencia,
            "cuantia": cuantia,
            "estado": "borrador",
            "creado_en": ahora.isoformat(),
        }

    async def obtener_hallazgo(self, hallazgo_id: str) -> Optional[dict[str, Any]]:
        """Obtiene un hallazgo por su ID.

        Args:
            hallazgo_id: ID del hallazgo.

        Returns:
            Datos completos del hallazgo o None.
        """
        result = await self._db.execute(
            text("SELECT * FROM hallazgos WHERE id = :id"),
            {"id": hallazgo_id},
        )
        row = result.fetchone()
        return dict(row._mapping) if row else None

    async def listar_hallazgos(
        self,
        proyecto_auditoria_id: str,
        tipo_incidencia: Optional[str] = None,
        estado: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Lista hallazgos de un proyecto de auditoría.

        Args:
            proyecto_auditoria_id: ID del proyecto.
            tipo_incidencia: Filtro por tipo de incidencia.
            estado: Filtro por estado.

        Returns:
            Lista de hallazgos.
        """
        condiciones: list[str] = ["proyecto_auditoria_id = :proyecto"]
        params: dict[str, Any] = {"proyecto": proyecto_auditoria_id}

        if tipo_incidencia:
            condiciones.append("tipo_incidencia = :tipo")
            params["tipo"] = tipo_incidencia
        if estado:
            condiciones.append("estado = :estado")
            params["estado"] = estado

        where: str = " AND ".join(condiciones)

        result = await self._db.execute(
            text(f"""
                SELECT * FROM hallazgos
                WHERE {where}
                ORDER BY creado_en DESC
            """),
            params,
        )

        return [dict(row._mapping) for row in result.fetchall()]

    async def actualizar_hallazgo(
        self,
        hallazgo_id: str,
        campos: dict[str, Any],
    ) -> dict[str, Any]:
        """Actualiza campos de un hallazgo existente.

        Solo se pueden actualizar hallazgos en estado 'borrador' o 'en_revision'.

        Args:
            hallazgo_id: ID del hallazgo.
            campos: Diccionario con los campos a actualizar.

        Returns:
            Datos actualizados.
        """
        hallazgo: Optional[dict[str, Any]] = await self.obtener_hallazgo(hallazgo_id)
        if hallazgo is None:
            raise ValueError(f"Hallazgo no encontrado: {hallazgo_id}")

        if hallazgo["estado"] not in ("borrador", "en_revision"):
            raise ValueError(
                f"No se puede editar un hallazgo en estado '{hallazgo['estado']}'. "
                f"Solo se pueden editar hallazgos en estado 'borrador' o 'en_revision'."
            )

        campos_permitidos: set[str] = {
            "titulo", "condicion", "criterio", "causa", "efecto",
            "recomendacion", "tipo_incidencia", "cuantia", "evidencia_soporte",
        }
        campos_validos: dict[str, Any] = {
            k: v for k, v in campos.items() if k in campos_permitidos
        }

        if not campos_validos:
            raise ValueError("No se proporcionaron campos válidos para actualizar.")

        sets: str = ", ".join(f"{k} = :{k}" for k in campos_validos)
        campos_validos["id"] = hallazgo_id
        campos_validos["ahora"] = datetime.now(timezone.utc).isoformat()

        await self._db.execute(
            text(f"""
                UPDATE hallazgos
                SET {sets}, actualizado_en = :ahora
                WHERE id = :id
            """),
            campos_validos,
        )
        await self._db.commit()

        logger.info("Hallazgo actualizado [%s]", hallazgo_id[:8])
        return await self.obtener_hallazgo(hallazgo_id)  # type: ignore

    async def cambiar_estado(
        self,
        hallazgo_id: str,
        nuevo_estado: str,
        usuario_id: str,
        comentario: Optional[str] = None,
    ) -> dict[str, Any]:
        """Cambia el estado de un hallazgo siguiendo el flujo de trabajo.

        Args:
            hallazgo_id: ID del hallazgo.
            nuevo_estado: Nuevo estado deseado.
            usuario_id: ID del usuario que realiza el cambio.
            comentario: Comentario opcional sobre el cambio.

        Returns:
            Datos actualizados del hallazgo.
        """
        hallazgo: Optional[dict[str, Any]] = await self.obtener_hallazgo(hallazgo_id)
        if hallazgo is None:
            raise ValueError(f"Hallazgo no encontrado: {hallazgo_id}")

        estado_actual: str = hallazgo["estado"]
        transiciones: list[str] = TRANSICIONES_VALIDAS.get(estado_actual, [])

        if nuevo_estado not in transiciones:
            raise ValueError(
                f"Transición inválida: '{estado_actual}' → '{nuevo_estado}'. "
                f"Transiciones permitidas: {', '.join(transiciones) or 'ninguna'}"
            )

        ahora: datetime = datetime.now(timezone.utc)

        await self._db.execute(
            text("""
                UPDATE hallazgos
                SET estado = :estado, actualizado_en = :ahora
                WHERE id = :id
            """),
            {"estado": nuevo_estado, "ahora": ahora.isoformat(), "id": hallazgo_id},
        )

        # Registrar el cambio de estado en el historial
        await self._db.execute(
            text("""
                INSERT INTO hallazgos_historial
                    (id, hallazgo_id, estado_anterior, estado_nuevo,
                     usuario_id, comentario, fecha)
                VALUES
                    (:id, :hallazgo_id, :anterior, :nuevo,
                     :usuario, :comentario, :fecha)
            """),
            {
                "id": str(uuid.uuid4()),
                "hallazgo_id": hallazgo_id,
                "anterior": estado_actual,
                "nuevo": nuevo_estado,
                "usuario": usuario_id,
                "comentario": comentario or "",
                "fecha": ahora.isoformat(),
            },
        )

        await self._db.commit()

        logger.info(
            "Hallazgo [%s] cambió de '%s' a '%s' (por %s)",
            hallazgo_id[:8], estado_actual, nuevo_estado, usuario_id,
        )

        return {
            "id": hallazgo_id,
            "estado_anterior": estado_actual,
            "estado_actual": nuevo_estado,
            "actualizado_en": ahora.isoformat(),
        }

    async def resumen_hallazgos(
        self,
        proyecto_auditoria_id: str,
    ) -> dict[str, Any]:
        """Genera un resumen estadístico de hallazgos del proyecto.

        Args:
            proyecto_auditoria_id: ID del proyecto.

        Returns:
            Resumen con conteos por tipo y estado.
        """
        result = await self._db.execute(
            text("""
                SELECT
                    tipo_incidencia,
                    estado,
                    COUNT(*) as cantidad,
                    COALESCE(SUM(cuantia), 0) as cuantia_total
                FROM hallazgos
                WHERE proyecto_auditoria_id = :proyecto
                GROUP BY tipo_incidencia, estado
            """),
            {"proyecto": proyecto_auditoria_id},
        )

        filas = result.fetchall()
        resumen: dict[str, Any] = {
            "proyecto_auditoria_id": proyecto_auditoria_id,
            "total_hallazgos": 0,
            "cuantia_total": 0.0,
            "por_tipo": {},
            "por_estado": {},
        }

        for fila in filas:
            row = fila._mapping
            cantidad: int = row["cantidad"]
            cuantia: float = float(row["cuantia_total"])
            tipo: str = row["tipo_incidencia"]
            estado: str = row["estado"]

            resumen["total_hallazgos"] += cantidad
            resumen["cuantia_total"] += cuantia

            if tipo not in resumen["por_tipo"]:
                resumen["por_tipo"][tipo] = {"cantidad": 0, "cuantia": 0.0}
            resumen["por_tipo"][tipo]["cantidad"] += cantidad
            resumen["por_tipo"][tipo]["cuantia"] += cuantia

            if estado not in resumen["por_estado"]:
                resumen["por_estado"][estado] = 0
            resumen["por_estado"][estado] += cantidad

        return resumen
