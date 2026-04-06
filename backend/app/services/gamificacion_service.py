"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/services/gamificacion_service.py
Proposito: Sistema de gamificacion — XP, niveles, rachas, insignias, repaso espaciado.
Sprint: Capacitacion 2.0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select, update, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("cecilia.services.gamificacion")

# ── Constantes de XP ───────────────────────────────────────────────────────
XP_LECCION = 100
XP_QUIZ_APROBADO = 200
XP_REPASO_DIARIO = 50
XP_SIMULACION = 300
XP_PODCAST_ESCUCHADO = 30
XP_FLASHCARD_SET = 40

# ── Niveles ────────────────────────────────────────────────────────────────
NIVELES = [
    ("Practicante", 0),
    ("Auxiliar", 500),
    ("Auditor Junior", 1500),
    ("Auditor Senior", 3000),
    ("Experto", 5000),
]

# ── Insignias disponibles ─────────────────────────────────────────────────
INSIGNIAS_CATALOGO = {
    "primera_leccion": {
        "nombre": "Primera leccion",
        "descripcion": "Completo su primera leccion",
        "icono": "📖",
    },
    "quiz_perfecto": {
        "nombre": "Quiz perfecto",
        "descripcion": "Obtuvo 100% en un quiz",
        "icono": "🎯",
    },
    "simulacion_aprobada": {
        "nombre": "Simulacion aprobada",
        "descripcion": "Completo una simulacion de auditoria",
        "icono": "🏆",
    },
    "racha_5": {
        "nombre": "Constancia",
        "descripcion": "5 dias consecutivos de aprendizaje",
        "icono": "🔥",
    },
    "racha_30": {
        "nombre": "Dedicacion",
        "descripcion": "30 dias consecutivos de aprendizaje",
        "icono": "⭐",
    },
    "ruta_completada": {
        "nombre": "Ruta completada",
        "descripcion": "Completo una ruta de aprendizaje completa",
        "icono": "🎓",
    },
    "explorador": {
        "nombre": "Explorador",
        "descripcion": "Probo todas las funcionalidades de capacitacion",
        "icono": "🧭",
    },
    "nivel_auxiliar": {
        "nombre": "Ascenso a Auxiliar",
        "descripcion": "Alcanzo 500 XP",
        "icono": "📈",
    },
    "nivel_junior": {
        "nombre": "Auditor Junior",
        "descripcion": "Alcanzo 1500 XP",
        "icono": "🏅",
    },
    "nivel_senior": {
        "nombre": "Auditor Senior",
        "descripcion": "Alcanzo 3000 XP",
        "icono": "🥇",
    },
}

# ── Intervalos de repaso espaciado ─────────────────────────────────────────
INTERVALOS_REPASO = [1, 3, 7, 14, 30, 60]


class GamificacionService:
    """Servicio de gamificacion: XP, niveles, rachas, insignias."""

    async def obtener_o_crear_perfil(
        self, db: AsyncSession, usuario_id: int
    ) -> dict[str, Any]:
        """Obtiene o crea el perfil de gamificacion del usuario."""
        from app.models.capacitacion import Gamificacion

        result = await db.execute(
            select(Gamificacion).where(Gamificacion.usuario_id == usuario_id)
        )
        perfil = result.scalar_one_or_none()

        if not perfil:
            perfil = Gamificacion(
                id=str(uuid.uuid4()),
                usuario_id=usuario_id,
                xp_total=0,
                nivel="Practicante",
                racha_dias=0,
                mejor_racha=0,
                insignias=[],
                ultima_actividad=datetime.now(timezone.utc),
            )
            db.add(perfil)
            await db.flush()

        return {
            "xp_total": perfil.xp_total,
            "nivel": perfil.nivel,
            "racha_dias": perfil.racha_dias,
            "mejor_racha": perfil.mejor_racha,
            "insignias": perfil.insignias or [],
            "ultima_actividad": perfil.ultima_actividad.isoformat() if perfil.ultima_actividad else None,
            "xp_siguiente_nivel": self._xp_siguiente_nivel(perfil.xp_total),
            "progreso_nivel": self._progreso_nivel(perfil.xp_total),
        }

    async def agregar_xp(
        self, db: AsyncSession, usuario_id: int, cantidad: int, motivo: str
    ) -> dict[str, Any]:
        """Agrega XP al usuario y actualiza nivel/racha/insignias."""
        from app.models.capacitacion import Gamificacion

        result = await db.execute(
            select(Gamificacion).where(Gamificacion.usuario_id == usuario_id)
        )
        perfil = result.scalar_one_or_none()

        if not perfil:
            perfil = Gamificacion(
                id=str(uuid.uuid4()),
                usuario_id=usuario_id,
                xp_total=0,
                nivel="Practicante",
                racha_dias=0,
                mejor_racha=0,
                insignias=[],
            )
            db.add(perfil)
            await db.flush()

        xp_anterior = perfil.xp_total
        perfil.xp_total += cantidad

        # Actualizar nivel
        nivel_anterior = perfil.nivel
        perfil.nivel = self._calcular_nivel(perfil.xp_total)

        # Actualizar racha
        ahora = datetime.now(timezone.utc)
        if perfil.ultima_actividad:
            diff = (ahora.date() - perfil.ultima_actividad.date()).days
            if diff == 1:
                perfil.racha_dias += 1
            elif diff > 1:
                perfil.racha_dias = 1
            # Si diff == 0, mismo dia, no cambiar racha
        else:
            perfil.racha_dias = 1

        if perfil.racha_dias > perfil.mejor_racha:
            perfil.mejor_racha = perfil.racha_dias

        perfil.ultima_actividad = ahora

        # Verificar insignias nuevas
        nuevas_insignias = self._verificar_insignias(
            perfil, xp_anterior, motivo
        )
        if nuevas_insignias:
            insignias_actuales = list(perfil.insignias or [])
            for ins in nuevas_insignias:
                if not any(i.get("id") == ins["id"] for i in insignias_actuales):
                    insignias_actuales.append({
                        **ins,
                        "fecha": ahora.isoformat(),
                    })
            perfil.insignias = insignias_actuales

        await db.flush()

        subio_nivel = perfil.nivel != nivel_anterior

        return {
            "xp_ganado": cantidad,
            "xp_total": perfil.xp_total,
            "nivel": perfil.nivel,
            "subio_nivel": subio_nivel,
            "racha_dias": perfil.racha_dias,
            "nuevas_insignias": nuevas_insignias,
            "motivo": motivo,
        }

    async def programar_repaso(
        self, db: AsyncSession, usuario_id: int, leccion_id: str
    ) -> dict[str, Any]:
        """Programa el primer repaso espaciado para una leccion completada."""
        from app.models.capacitacion import RepasoProgramado

        ahora = datetime.now(timezone.utc)
        repaso = RepasoProgramado(
            id=str(uuid.uuid4()),
            usuario_id=usuario_id,
            leccion_id=leccion_id,
            fecha_proximo_repaso=ahora + timedelta(days=1),
            intervalo_dias=1,
            intentos=0,
            aciertos=0,
            estado="pendiente",
        )
        db.add(repaso)
        await db.flush()

        return {
            "repaso_id": repaso.id,
            "fecha_proximo": repaso.fecha_proximo_repaso.isoformat(),
            "intervalo_dias": 1,
        }

    async def obtener_repasos_pendientes(
        self, db: AsyncSession, usuario_id: int
    ) -> list[dict[str, Any]]:
        """Obtiene repasos programados pendientes para hoy o vencidos."""
        from app.models.capacitacion import RepasoProgramado, Leccion

        ahora = datetime.now(timezone.utc)
        result = await db.execute(
            select(RepasoProgramado, Leccion.titulo)
            .join(Leccion, RepasoProgramado.leccion_id == Leccion.id)
            .where(
                and_(
                    RepasoProgramado.usuario_id == usuario_id,
                    RepasoProgramado.estado == "pendiente",
                    RepasoProgramado.fecha_proximo_repaso <= ahora,
                )
            )
            .order_by(RepasoProgramado.fecha_proximo_repaso)
        )
        rows = result.all()

        return [
            {
                "repaso_id": r.id,
                "leccion_id": r.leccion_id,
                "leccion_titulo": titulo,
                "fecha_programada": r.fecha_proximo_repaso.isoformat(),
                "intervalo_dias": r.intervalo_dias,
                "intentos": r.intentos,
            }
            for r, titulo in rows
        ]

    async def registrar_resultado_repaso(
        self, db: AsyncSession, repaso_id: str, aciertos: int, total: int
    ) -> dict[str, Any]:
        """Registra resultado de un repaso y reprograma el siguiente."""
        from app.models.capacitacion import RepasoProgramado

        result = await db.execute(
            select(RepasoProgramado).where(RepasoProgramado.id == repaso_id)
        )
        repaso = result.scalar_one_or_none()
        if not repaso:
            return {"error": "Repaso no encontrado"}

        repaso.intentos += 1
        repaso.aciertos += aciertos
        aprobado = aciertos >= (total * 0.7)

        if aprobado:
            # Duplicar intervalo
            idx_actual = INTERVALOS_REPASO.index(repaso.intervalo_dias) if repaso.intervalo_dias in INTERVALOS_REPASO else 0
            nuevo_intervalo = INTERVALOS_REPASO[min(idx_actual + 1, len(INTERVALOS_REPASO) - 1)]
            repaso.intervalo_dias = nuevo_intervalo
            repaso.fecha_proximo_repaso = datetime.now(timezone.utc) + timedelta(days=nuevo_intervalo)

            if nuevo_intervalo >= 60:
                repaso.estado = "completado"
        else:
            # Reiniciar intervalo
            repaso.intervalo_dias = 1
            repaso.fecha_proximo_repaso = datetime.now(timezone.utc) + timedelta(days=1)

        await db.flush()

        return {
            "aprobado": aprobado,
            "nuevo_intervalo": repaso.intervalo_dias,
            "proximo_repaso": repaso.fecha_proximo_repaso.isoformat(),
            "estado": repaso.estado,
        }

    # ── Metodos internos ───────────────────────────────────────────────────

    def _calcular_nivel(self, xp: int) -> str:
        nivel = "Practicante"
        for nombre, umbral in NIVELES:
            if xp >= umbral:
                nivel = nombre
        return nivel

    def _xp_siguiente_nivel(self, xp: int) -> int:
        for nombre, umbral in NIVELES:
            if xp < umbral:
                return umbral
        return NIVELES[-1][1]

    def _progreso_nivel(self, xp: int) -> float:
        nivel_actual_umbral = 0
        siguiente_umbral = NIVELES[-1][1]

        for i, (nombre, umbral) in enumerate(NIVELES):
            if xp >= umbral:
                nivel_actual_umbral = umbral
                if i + 1 < len(NIVELES):
                    siguiente_umbral = NIVELES[i + 1][1]
                else:
                    return 100.0

        rango = siguiente_umbral - nivel_actual_umbral
        if rango == 0:
            return 100.0
        return round(((xp - nivel_actual_umbral) / rango) * 100, 1)

    def _verificar_insignias(
        self, perfil, xp_anterior: int, motivo: str
    ) -> list[dict]:
        nuevas = []
        xp = perfil.xp_total
        ids_existentes = {i.get("id") for i in (perfil.insignias or [])}

        # Primera leccion
        if motivo == "leccion_completada" and "primera_leccion" not in ids_existentes:
            nuevas.append({**INSIGNIAS_CATALOGO["primera_leccion"], "id": "primera_leccion"})

        # Quiz perfecto
        if motivo == "quiz_perfecto" and "quiz_perfecto" not in ids_existentes:
            nuevas.append({**INSIGNIAS_CATALOGO["quiz_perfecto"], "id": "quiz_perfecto"})

        # Simulacion
        if motivo == "simulacion_completada" and "simulacion_aprobada" not in ids_existentes:
            nuevas.append({**INSIGNIAS_CATALOGO["simulacion_aprobada"], "id": "simulacion_aprobada"})

        # Rachas
        if perfil.racha_dias >= 5 and "racha_5" not in ids_existentes:
            nuevas.append({**INSIGNIAS_CATALOGO["racha_5"], "id": "racha_5"})
        if perfil.racha_dias >= 30 and "racha_30" not in ids_existentes:
            nuevas.append({**INSIGNIAS_CATALOGO["racha_30"], "id": "racha_30"})

        # Niveles
        if xp >= 500 and xp_anterior < 500 and "nivel_auxiliar" not in ids_existentes:
            nuevas.append({**INSIGNIAS_CATALOGO["nivel_auxiliar"], "id": "nivel_auxiliar"})
        if xp >= 1500 and xp_anterior < 1500 and "nivel_junior" not in ids_existentes:
            nuevas.append({**INSIGNIAS_CATALOGO["nivel_junior"], "id": "nivel_junior"})
        if xp >= 3000 and xp_anterior < 3000 and "nivel_senior" not in ids_existentes:
            nuevas.append({**INSIGNIAS_CATALOGO["nivel_senior"], "id": "nivel_senior"})

        return nuevas
