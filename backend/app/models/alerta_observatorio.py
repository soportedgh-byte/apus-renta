"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/models/alerta_observatorio.py
Proposito: Modelo de alertas del Observatorio TIC — contenido clasificado
           por IA desde fuentes del sector de telecomunicaciones.
Sprint: 8
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    DateTime, ForeignKey, Integer, String, Text, func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AlertaObservatorio(Base):
    """Alerta del Observatorio TIC — contenido clasificado por IA."""

    __tablename__ = "alertas_observatorio"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # Tipo de contenido
    tipo: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True,
        comment="REGULATORIA | LEGISLATIVA | NOTICIA | INDICADOR",
    )

    # Contenido
    titulo: Mapped[str] = mapped_column(String(300), nullable=False)
    resumen: Mapped[str] = mapped_column(Text, nullable=False, server_default="")

    # Fuente
    fuente_url: Mapped[str] = mapped_column(String(500), nullable=False, server_default="")
    fuente_nombre: Mapped[str] = mapped_column(
        String(100), nullable=False, server_default="",
        comment="MinTIC | CRC | ANE | Congreso | Noticias",
    )

    # Clasificacion LLM
    relevancia: Mapped[str] = mapped_column(
        String(10), nullable=False, server_default="BAJA", index=True,
        comment="ALTA | MEDIA | BAJA",
    )
    tipo_impacto: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default="regulatorio",
        comment="presupuestal | regulatorio | contractual",
    )
    entidades_afectadas: Mapped[Optional[list[Any]]] = mapped_column(
        JSONB, nullable=True,
        comment="Lista de entidades del sector TIC afectadas",
    )

    # Estado del workflow
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="NUEVA", index=True,
        comment="NUEVA | VISTA | EN_ANALISIS | ARCHIVADA",
    )

    # Asignacion
    asignada_a: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )

    # Fechas
    fecha_deteccion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    fecha_publicacion: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    # Deduplicacion
    hash_contenido: Mapped[str] = mapped_column(
        String(16), nullable=False, server_default="", index=True, unique=True,
        comment="Hash SHA256 truncado para detectar duplicados",
    )

    # Metadata flexible
    metadata_extra: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )

    def __repr__(self) -> str:
        return f"<AlertaObservatorio(id={self.id}, tipo={self.tipo}, titulo='{self.titulo[:40]}...')>"

    def a_dict(self) -> dict[str, Any]:
        """Convierte la alerta a diccionario serializable."""
        return {
            "id": self.id,
            "tipo": self.tipo,
            "titulo": self.titulo,
            "resumen": self.resumen,
            "fuente_url": self.fuente_url,
            "fuente_nombre": self.fuente_nombre,
            "relevancia": self.relevancia,
            "tipo_impacto": self.tipo_impacto,
            "entidades_afectadas": self.entidades_afectadas or [],
            "estado": self.estado,
            "asignada_a": self.asignada_a,
            "fecha_deteccion": self.fecha_deteccion.isoformat() if self.fecha_deteccion else None,
            "fecha_publicacion": self.fecha_publicacion.isoformat() if self.fecha_publicacion else None,
            "hash_contenido": self.hash_contenido,
            "metadata_extra": self.metadata_extra,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
