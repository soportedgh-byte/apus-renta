"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/services/hallazgo_service.py
Proposito: Servicio de gestion de hallazgos con workflow de aprobacion,
           oficios de traslado DOCX y cumplimiento Circular 023
Sprint: 5
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import io
import logging
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.formatos.formato_base import FormatoBaseCGR
from app.models.hallazgo import Hallazgo

logger = logging.getLogger("cecilia.services.hallazgo")

# ── Estados y transiciones del workflow ─────────────────────────────────────

ESTADOS_HALLAZGO = [
    "BORRADOR",
    "EN_REVISION",
    "OBSERVACION_TRASLADADA",
    "RESPUESTA_RECIBIDA",
    "HALLAZGO_CONFIGURADO",
    "APROBADO",
    "TRASLADADO",
]

TRANSICIONES_VALIDAS: dict[str, list[str]] = {
    "BORRADOR": ["EN_REVISION"],
    "EN_REVISION": ["BORRADOR", "OBSERVACION_TRASLADADA", "HALLAZGO_CONFIGURADO"],
    "OBSERVACION_TRASLADADA": ["RESPUESTA_RECIBIDA"],
    "RESPUESTA_RECIBIDA": ["HALLAZGO_CONFIGURADO", "EN_REVISION"],
    "HALLAZGO_CONFIGURADO": ["APROBADO", "EN_REVISION"],
    "APROBADO": ["TRASLADADO"],
    "TRASLADADO": [],
}

# Permisos por fase del workflow
FASE_REQUERIDA: dict[str, str] = {
    "EN_REVISION": "auditor",
    "OBSERVACION_TRASLADADA": "supervisor",
    "HALLAZGO_CONFIGURADO": "coordinador",
    "APROBADO": "director",
    "TRASLADADO": "director",
}

TIPOS_CONNOTACION = {"administrativo", "fiscal", "disciplinario", "penal"}

# Destinos de traslado por connotacion
DESTINO_TRASLADO: dict[str, dict[str, str]] = {
    "fiscal": {
        "entidad": "Contraloria Delegada para Investigaciones, Juicios Fiscales y Jurisdiccion Coactiva",
        "fundamentacion": "Ley 610 de 2000, Articulos 9 y 41",
    },
    "disciplinario": {
        "entidad": "Procuraduria General de la Nacion",
        "fundamentacion": "Ley 734 de 2002 (Codigo Disciplinario Unico)",
    },
    "penal": {
        "entidad": "Fiscalia General de la Nacion",
        "fundamentacion": "Articulos 397-403 del Codigo Penal Colombiano",
    },
}


class HallazgoService:
    """Servicio de gestion de hallazgos de auditoria.

    Implementa CRUD, workflow de aprobacion, validacion Circular 023,
    generacion de oficios de traslado y estadisticas.
    """

    def __init__(self, db_session: AsyncSession) -> None:
        self._db = db_session

    # ── CRUD ────────────────────────────────────────────────────────────────

    async def crear_hallazgo(
        self,
        auditoria_id: str,
        datos: dict[str, Any],
        usuario_id: int,
    ) -> Hallazgo:
        """Crea hallazgo en estado BORRADOR con numero secuencial."""

        # Obtener siguiente numero secuencial
        resultado = await self._db.execute(
            select(func.coalesce(func.max(Hallazgo.numero_hallazgo), 0))
            .where(Hallazgo.auditoria_id == auditoria_id)
        )
        siguiente_numero = resultado.scalar() + 1

        hallazgo_id = str(uuid.uuid4())

        hallazgo = Hallazgo(
            id=hallazgo_id,
            auditoria_id=auditoria_id,
            numero_hallazgo=siguiente_numero,
            titulo=datos.get("titulo", f"Hallazgo H-{siguiente_numero:03d}"),
            condicion=datos.get("condicion", ""),
            criterio=datos.get("criterio", ""),
            causa=datos.get("causa", ""),
            efecto=datos.get("efecto", ""),
            recomendacion=datos.get("recomendacion"),
            connotaciones=datos.get("connotaciones", []),
            cuantia_presunto_dano=datos.get("cuantia_presunto_dano"),
            presuntos_responsables=datos.get("presuntos_responsables", []),
            evidencias=datos.get("evidencias", []),
            estado="BORRADOR",
            fase_actual_workflow="auditor",
            historial_workflow=[{
                "usuario_id": usuario_id,
                "usuario_nombre": datos.get("usuario_nombre", ""),
                "accion": "Creacion",
                "estado_anterior": "",
                "estado_nuevo": "BORRADOR",
                "fecha": datetime.now(timezone.utc).isoformat(),
                "comentarios": "Hallazgo creado",
            }],
            redaccion_validada_humano=False,
            generado_por_ia=datos.get("generado_por_ia", False),
            created_by=usuario_id,
            updated_by=usuario_id,
        )

        self._db.add(hallazgo)
        await self._db.flush()

        logger.info(
            "Hallazgo H-%03d creado en auditoria %s por usuario %d",
            siguiente_numero, auditoria_id, usuario_id,
        )
        return hallazgo

    async def actualizar_hallazgo(
        self,
        hallazgo_id: str,
        datos: dict[str, Any],
        usuario_id: int,
    ) -> Hallazgo:
        """Actualiza campos del hallazgo. Solo en BORRADOR o EN_REVISION."""
        hallazgo = await self._obtener_o_error(hallazgo_id)

        if hallazgo.estado not in ("BORRADOR", "EN_REVISION"):
            raise ValueError(
                f"No se puede editar un hallazgo en estado '{hallazgo.estado}'. "
                f"Solo es posible en BORRADOR o EN_REVISION."
            )

        campos_permitidos = {
            "titulo", "condicion", "criterio", "causa", "efecto",
            "recomendacion", "connotaciones", "cuantia_presunto_dano",
            "presuntos_responsables", "evidencias",
        }

        for campo, valor in datos.items():
            if campo in campos_permitidos:
                setattr(hallazgo, campo, valor)

        hallazgo.updated_by = usuario_id
        await self._db.flush()

        logger.info("Hallazgo %s actualizado por usuario %d", hallazgo_id, usuario_id)
        return hallazgo

    async def obtener_hallazgo(self, hallazgo_id: str) -> Optional[Hallazgo]:
        """Obtiene un hallazgo por ID."""
        resultado = await self._db.execute(
            select(Hallazgo).where(Hallazgo.id == hallazgo_id)
        )
        return resultado.scalar_one_or_none()

    async def listar_hallazgos(
        self,
        auditoria_id: Optional[str] = None,
        estado: Optional[str] = None,
        connotacion: Optional[str] = None,
        cuantia_minima: Optional[float] = None,
        limite: int = 50,
        desplazamiento: int = 0,
    ) -> list[Hallazgo]:
        """Lista hallazgos con filtros."""
        query = select(Hallazgo)

        if auditoria_id:
            query = query.where(Hallazgo.auditoria_id == auditoria_id)
        if estado:
            query = query.where(Hallazgo.estado == estado.upper())
        if cuantia_minima:
            query = query.where(Hallazgo.cuantia_presunto_dano >= cuantia_minima)

        query = query.order_by(Hallazgo.created_at.desc()).limit(limite).offset(desplazamiento)

        resultado = await self._db.execute(query)
        return list(resultado.scalars().all())

    # ── Workflow ────────────────────────────────────────────────────────────

    async def cambiar_estado(
        self,
        hallazgo_id: str,
        nuevo_estado: str,
        usuario_id: int,
        usuario_nombre: str = "",
        comentarios: str = "",
    ) -> Hallazgo:
        """Transiciona el estado del hallazgo con validaciones."""
        hallazgo = await self._obtener_o_error(hallazgo_id)
        nuevo_estado = nuevo_estado.upper()

        # Validar transicion
        transiciones = TRANSICIONES_VALIDAS.get(hallazgo.estado, [])
        if nuevo_estado not in transiciones:
            raise ValueError(
                f"Transicion invalida: '{hallazgo.estado}' -> '{nuevo_estado}'. "
                f"Transiciones permitidas: {', '.join(transiciones) or 'ninguna'}"
            )

        estado_anterior = hallazgo.estado
        hallazgo.estado = nuevo_estado

        # Actualizar fase del workflow
        if nuevo_estado in FASE_REQUERIDA:
            hallazgo.fase_actual_workflow = FASE_REQUERIDA[nuevo_estado]

        # Registrar en historial
        historial = hallazgo.historial_workflow or []
        historial.append({
            "usuario_id": usuario_id,
            "usuario_nombre": usuario_nombre,
            "accion": f"Cambio de estado: {estado_anterior} -> {nuevo_estado}",
            "estado_anterior": estado_anterior,
            "estado_nuevo": nuevo_estado,
            "fecha": datetime.now(timezone.utc).isoformat(),
            "comentarios": comentarios,
        })
        hallazgo.historial_workflow = historial
        hallazgo.updated_by = usuario_id

        await self._db.flush()

        logger.info(
            "Hallazgo %s: %s -> %s (por usuario %d)",
            hallazgo_id, estado_anterior, nuevo_estado, usuario_id,
        )
        return hallazgo

    async def aprobar_hallazgo(
        self,
        hallazgo_id: str,
        usuario_id: int,
        usuario_nombre: str = "",
        rol_usuario: str = "",
    ) -> Hallazgo:
        """Aprueba un hallazgo. Solo DIRECTOR_DVF puede aprobar.

        Verifica que redaccion_validada_humano sea True (Circular 023).
        """
        hallazgo = await self._obtener_o_error(hallazgo_id)

        # Verificar rol (solo director_dvf)
        if rol_usuario and "director" not in rol_usuario.lower():
            raise PermissionError(
                "Solo el Director DVF puede aprobar hallazgos."
            )

        # Verificar Circular 023
        if not hallazgo.redaccion_validada_humano:
            raise ValueError(
                "No se puede aprobar: la redaccion no ha sido validada por un humano. "
                "Conforme a la Circular 023 de la CGR, la redaccion final de hallazgos "
                "NO puede basarse unicamente en IA (Art. VI.1.4)."
            )

        # Verificar estado
        if hallazgo.estado != "HALLAZGO_CONFIGURADO":
            raise ValueError(
                f"Solo se pueden aprobar hallazgos en estado HALLAZGO_CONFIGURADO. "
                f"Estado actual: {hallazgo.estado}"
            )

        return await self.cambiar_estado(
            hallazgo_id, "APROBADO", usuario_id, usuario_nombre,
            "Hallazgo aprobado por Director DVF"
        )

    async def validar_redaccion(
        self,
        hallazgo_id: str,
        usuario_id: int,
    ) -> Hallazgo:
        """Marca la redaccion como validada por humano (Circular 023)."""
        hallazgo = await self._obtener_o_error(hallazgo_id)

        hallazgo.redaccion_validada_humano = True
        hallazgo.validado_por = usuario_id
        hallazgo.fecha_validacion = datetime.now(timezone.utc)
        hallazgo.updated_by = usuario_id

        # Registrar en historial
        historial = hallazgo.historial_workflow or []
        historial.append({
            "usuario_id": usuario_id,
            "usuario_nombre": "",
            "accion": "Redaccion validada por humano (Circular 023)",
            "estado_anterior": hallazgo.estado,
            "estado_nuevo": hallazgo.estado,
            "fecha": datetime.now(timezone.utc).isoformat(),
            "comentarios": "Redaccion revisada y validada conforme a Circular 023",
        })
        hallazgo.historial_workflow = historial

        await self._db.flush()

        logger.info(
            "Hallazgo %s: redaccion validada por usuario %d",
            hallazgo_id, usuario_id,
        )
        return hallazgo

    # ── Oficio de traslado ──────────────────────────────────────────────────

    async def generar_oficio_traslado(
        self,
        hallazgo_id: str,
        destino: str,
    ) -> bytes:
        """Genera DOCX de oficio de traslado segun connotacion.

        Args:
            hallazgo_id: ID del hallazgo.
            destino: Tipo de destino (fiscal, disciplinario, penal).

        Returns:
            Bytes del documento DOCX.
        """
        hallazgo = await self._obtener_o_error(hallazgo_id)

        if hallazgo.estado != "APROBADO":
            raise ValueError(
                f"Solo se pueden generar oficios para hallazgos APROBADOS. "
                f"Estado actual: {hallazgo.estado}"
            )

        if destino not in DESTINO_TRASLADO:
            raise ValueError(
                f"Destino '{destino}' no valido. "
                f"Opciones: {', '.join(DESTINO_TRASLADO.keys())}"
            )

        info_destino = DESTINO_TRASLADO[destino]
        generador = _OficioTrasladoDocx(hallazgo, destino, info_destino)
        return generador.generar_bytes()

    # ── Estadisticas ────────────────────────────────────────────────────────

    async def obtener_estadisticas(
        self,
        auditoria_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Retorna KPIs de hallazgos."""
        query = select(Hallazgo)
        if auditoria_id:
            query = query.where(Hallazgo.auditoria_id == auditoria_id)

        resultado = await self._db.execute(query)
        hallazgos = list(resultado.scalars().all())

        total = len(hallazgos)
        por_estado: dict[str, int] = {}
        por_connotacion: dict[str, int] = {}
        cuantia_total = Decimal("0")

        for h in hallazgos:
            # Por estado
            por_estado[h.estado] = por_estado.get(h.estado, 0) + 1

            # Por connotacion
            for c in (h.connotaciones or []):
                tipo = c.get("tipo", "sin_tipo")
                por_connotacion[tipo] = por_connotacion.get(tipo, 0) + 1

            # Cuantia
            if h.cuantia_presunto_dano:
                cuantia_total += Decimal(str(h.cuantia_presunto_dano))

        return {
            "total_hallazgos": total,
            "por_estado": por_estado,
            "por_connotacion": por_connotacion,
            "cuantia_total_presunto_dano": float(cuantia_total),
            "borradores": por_estado.get("BORRADOR", 0),
            "en_revision": por_estado.get("EN_REVISION", 0),
            "aprobados": por_estado.get("APROBADO", 0),
            "trasladados": por_estado.get("TRASLADADO", 0),
        }

    # ── Helpers ─────────────────────────────────────────────────────────────

    async def _obtener_o_error(self, hallazgo_id: str) -> Hallazgo:
        """Obtiene hallazgo o lanza ValueError."""
        hallazgo = await self.obtener_hallazgo(hallazgo_id)
        if not hallazgo:
            raise ValueError(f"Hallazgo no encontrado: {hallazgo_id}")
        return hallazgo


# ── Generador de Oficio de Traslado ─────────────────────────────────────────


class _OficioTrasladoDocx(FormatoBaseCGR):
    """Genera oficio de traslado como documento DOCX profesional."""

    def __init__(
        self,
        hallazgo: Hallazgo,
        destino: str,
        info_destino: dict[str, str],
    ) -> None:
        self._hallazgo = hallazgo
        self._destino = destino
        self._info_destino = info_destino
        super().__init__(
            numero_formato=0,
            nombre_formato=f"Oficio de Traslado — Connotacion {destino.title()}",
            datos={
                "nombre_entidad": "Contraloria General de la Republica",
                "vigencia": datetime.now().strftime("%Y"),
            },
        )

    def construir(self) -> None:
        h = self._hallazgo

        # Datos del oficio
        self.agregar_titulo_seccion("Oficio de Traslado de Hallazgo")
        self.crear_tabla_clave_valor([
            ("Hallazgo No.", f"H-{h.numero_hallazgo:03d}"),
            ("Titulo", h.titulo),
            ("Connotacion", self._destino.title()),
            ("Entidad destino", self._info_destino["entidad"]),
            ("Fundamentacion legal", self._info_destino["fundamentacion"]),
            ("Fecha de traslado", datetime.now().strftime("%d/%m/%Y")),
        ])

        # 4 elementos
        self.agregar_titulo_seccion("1. Condicion (Situacion Factica)")
        self.agregar_parrafo_justificado(h.condicion)

        self.agregar_titulo_seccion("2. Criterio (Norma Incumplida)")
        self.agregar_parrafo_justificado(h.criterio)

        self.agregar_titulo_seccion("3. Causa")
        self.agregar_parrafo_justificado(h.causa)

        self.agregar_titulo_seccion("4. Efecto")
        self.agregar_parrafo_justificado(h.efecto)

        # Cuantificacion
        if h.cuantia_presunto_dano:
            self.agregar_titulo_seccion("5. Cuantificacion del Presunto Dano Patrimonial")
            self.crear_tabla_clave_valor([
                ("Cuantia estimada (COP)",
                 f"${h.cuantia_presunto_dano:,.2f}"),
                ("Tipo de dano",
                 "Presunto detrimento patrimonial"),
                ("Fundamentacion",
                 self._info_destino.get("fundamentacion", "")),
            ])

        # Presuntos responsables
        if h.presuntos_responsables:
            self.agregar_titulo_seccion("6. Presuntos Responsables")
            filas = []
            for i, resp in enumerate(h.presuntos_responsables, 1):
                filas.append([
                    str(i),
                    resp.get("nombre", "[COMPLETAR]"),
                    resp.get("cargo", "[COMPLETAR]"),
                    resp.get("periodo", "[COMPLETAR]"),
                    resp.get("fundamentacion", ""),
                ])
            self.crear_tabla(
                encabezados=["No.", "Nombre", "Cargo", "Periodo", "Fundamentacion"],
                filas=filas,
            )

        # Evidencias
        if h.evidencias:
            self.agregar_titulo_seccion("7. Evidencias Anexas")
            filas_ev = []
            for i, ev in enumerate(h.evidencias, 1):
                filas_ev.append([
                    str(i),
                    ev.get("descripcion", "[COMPLETAR]"),
                    ev.get("folio", ""),
                    ev.get("tipo", "documental"),
                ])
            self.crear_tabla(
                encabezados=["No.", "Descripcion", "Folio", "Tipo"],
                filas=filas_ev,
            )

        # Firma
        self.agregar_titulo_seccion("Firma")
        self.crear_tabla_clave_valor([
            ("Director DVF", "[COMPLETAR — Firma del Director]"),
            ("Fecha", datetime.now().strftime("%d/%m/%Y")),
        ])
