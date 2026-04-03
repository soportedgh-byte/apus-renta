"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: chunking.py
Propósito: División de texto en fragmentos (chunks) con solapamiento y preservación de metadatos
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger("cecilia.rag.chunking")

# Configuración por defecto
TAMANO_FRAGMENTO_DEFAULT: int = 1000  # caracteres
SOLAPAMIENTO_DEFAULT: int = 200  # caracteres
TAMANO_MINIMO: int = 50  # caracteres mínimos para considerar un fragmento


@dataclass
class Fragmento:
    """Representa un fragmento de texto con sus metadatos."""

    contenido: str
    metadata: dict[str, Any] = field(default_factory=dict)
    indice: int = 0
    total_fragmentos: int = 0

    @property
    def longitud(self) -> int:
        """Número de caracteres del fragmento."""
        return len(self.contenido)


def _detectar_limites_naturales(texto: str) -> list[int]:
    """Detecta posiciones de límites naturales para corte.

    Prioriza párrafos, luego oraciones, luego separadores de sección.

    Args:
        texto: Texto completo a analizar.

    Returns:
        Lista de posiciones (índices) donde es preferible cortar.
    """
    limites: list[int] = []

    # Doble salto de línea (cambio de párrafo)
    for match in re.finditer(r"\n\n", texto):
        limites.append(match.end())

    # Fin de oración
    for match in re.finditer(r"[.!?]\s+", texto):
        limites.append(match.end())

    # Separadores de sección
    for match in re.finditer(r"---+\s*\n", texto):
        limites.append(match.end())

    return sorted(set(limites))


def _encontrar_punto_corte(
    texto: str,
    posicion_ideal: int,
    margen: int = 100,
) -> int:
    """Encuentra el mejor punto de corte cercano a la posición ideal.

    Busca un límite natural (fin de párrafo, oración) dentro del margen.

    Args:
        texto: Texto completo.
        posicion_ideal: Posición donde idealmente se cortaría.
        margen: Rango de búsqueda alrededor de la posición ideal.

    Returns:
        Posición de corte óptima.
    """
    inicio_busqueda: int = max(0, posicion_ideal - margen)
    fin_busqueda: int = min(len(texto), posicion_ideal + margen)

    segmento: str = texto[inicio_busqueda:fin_busqueda]

    # Buscar fin de párrafo
    pos_parrafo: int = segmento.rfind("\n\n", 0, margen + margen)
    if pos_parrafo != -1:
        return inicio_busqueda + pos_parrafo + 2

    # Buscar fin de oración
    for patron in [r"\.\s+", r"\?\s+", r"!\s+"]:
        match = None
        for m in re.finditer(patron, segmento):
            if m.end() <= margen + margen:
                match = m
        if match:
            return inicio_busqueda + match.end()

    # Sin límite natural — cortar en la posición ideal
    return posicion_ideal


def dividir_en_fragmentos(
    texto: str,
    tamano: int = TAMANO_FRAGMENTO_DEFAULT,
    solapamiento: int = SOLAPAMIENTO_DEFAULT,
    metadata_base: Optional[dict[str, Any]] = None,
) -> list[Fragmento]:
    """Divide un texto en fragmentos con solapamiento y metadatos.

    Intenta cortar en límites naturales (párrafos, oraciones) para
    preservar la coherencia semántica de cada fragmento.

    Args:
        texto: Texto completo a fragmentar.
        tamano: Tamaño objetivo de cada fragmento en caracteres.
        solapamiento: Caracteres de solapamiento entre fragmentos consecutivos.
        metadata_base: Metadatos base que se copian a cada fragmento.

    Returns:
        Lista de fragmentos con sus metadatos.
    """
    if not texto or not texto.strip():
        logger.warning("Texto vacío proporcionado para chunking.")
        return []

    if tamano <= solapamiento:
        raise ValueError(
            f"El tamaño ({tamano}) debe ser mayor que el solapamiento ({solapamiento})."
        )

    metadata_base = metadata_base or {}
    fragmentos: list[Fragmento] = []
    inicio: int = 0
    longitud_texto: int = len(texto)

    while inicio < longitud_texto:
        fin_ideal: int = min(inicio + tamano, longitud_texto)

        if fin_ideal < longitud_texto:
            fin: int = _encontrar_punto_corte(texto, fin_ideal)
        else:
            fin = fin_ideal

        contenido_fragmento: str = texto[inicio:fin].strip()

        if len(contenido_fragmento) >= TAMANO_MINIMO:
            metadata_fragmento: dict[str, Any] = {
                **metadata_base,
                "inicio_char": inicio,
                "fin_char": fin,
            }

            fragmentos.append(
                Fragmento(
                    contenido=contenido_fragmento,
                    metadata=metadata_fragmento,
                    indice=len(fragmentos),
                )
            )

        # Avanzar con solapamiento
        avance: int = max(fin - inicio - solapamiento, 1)
        inicio += avance

    # Asignar total de fragmentos
    total: int = len(fragmentos)
    for fragmento in fragmentos:
        fragmento.total_fragmentos = total
        fragmento.metadata["total_fragmentos"] = total
        fragmento.metadata["indice_fragmento"] = fragmento.indice

    logger.info(
        "Texto dividido en %d fragmentos (tamaño=%d, solapamiento=%d).",
        total, tamano, solapamiento,
    )

    return fragmentos
