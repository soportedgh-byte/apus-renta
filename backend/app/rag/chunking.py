"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: chunking.py
Proposito: Division de texto en fragmentos con solapamiento, preservacion
           de metadatos y modo juridico especializado para normativa CGR
Sprint: 1
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Literal, Optional

logger = logging.getLogger("cecilia.rag.chunking")

# Configuracion por defecto
TAMANO_FRAGMENTO_DEFAULT: int = 1000  # caracteres
SOLAPAMIENTO_DEFAULT: int = 200  # caracteres
TAMANO_MINIMO: int = 50  # caracteres minimos para considerar un fragmento

# Modo juridico: fragmentos mas grandes para preservar contexto legal
TAMANO_JURIDICO: int = 1500
SOLAPAMIENTO_JURIDICO: int = 300

# Modo institucional: fragmentos medianos
TAMANO_INSTITUCIONAL: int = 1200
SOLAPAMIENTO_INSTITUCIONAL: int = 250

ModoChunking = Literal["general", "juridico", "institucional"]


@dataclass
class Fragmento:
    """Representa un fragmento de texto con sus metadatos."""

    contenido: str
    metadata: dict[str, Any] = field(default_factory=dict)
    indice: int = 0
    total_fragmentos: int = 0

    @property
    def longitud(self) -> int:
        return len(self.contenido)


# ── Patrones para deteccion de limites juridicos ────────────────────────────

# Articulos de ley: "Articulo 1.", "ARTICULO 123", "Art. 45"
_RE_ARTICULO = re.compile(
    r"(?:^|\n)\s*(?:ART[IÍ]CULO|Art\.?)\s+\d+", re.IGNORECASE
)

# Titulos y capitulos: "TITULO I", "CAPITULO 2", "SECCION TERCERA"
_RE_TITULO_CAPITULO = re.compile(
    r"(?:^|\n)\s*(?:T[IÍ]TULO|CAP[IÍ]TULO|SECCI[OÓ]N)\s+(?:\d+|[IVXLCDM]+|PRIMER|SEGUND|TERCER|CUART|QUINT)",
    re.IGNORECASE,
)

# Numerales: "1.", "1.1.", "a)", "i)"
_RE_NUMERAL = re.compile(r"(?:^|\n)\s*(?:\d+\.[\d.]*\s|\(?[a-z]\)|\(?[ivxlc]+\))\s*", re.IGNORECASE)

# Considerandos / Resoluciones
_RE_CONSIDERANDO = re.compile(
    r"(?:^|\n)\s*(?:CONSIDERANDO|RESUELVE|POR TANTO|DECRETA|PAR[AÁ]GRAFO)",
    re.IGNORECASE,
)


def _encontrar_punto_corte(
    texto: str,
    posicion_ideal: int,
    margen: int = 100,
) -> int:
    """Encuentra el mejor punto de corte cercano a la posicion ideal."""
    inicio_busqueda = max(0, posicion_ideal - margen)
    fin_busqueda = min(len(texto), posicion_ideal + margen)
    segmento = texto[inicio_busqueda:fin_busqueda]

    # Buscar fin de parrafo
    pos_parrafo = segmento.rfind("\n\n", 0, margen * 2)
    if pos_parrafo != -1:
        return inicio_busqueda + pos_parrafo + 2

    # Buscar fin de oracion
    for patron in [r"\.\s+", r"\?\s+", r"!\s+"]:
        match = None
        for m in re.finditer(patron, segmento):
            if m.end() <= margen * 2:
                match = m
        if match:
            return inicio_busqueda + match.end()

    return posicion_ideal


def _encontrar_punto_corte_juridico(
    texto: str,
    posicion_ideal: int,
    margen: int = 200,
) -> int:
    """Punto de corte para texto juridico: prioriza limites de articulo/seccion."""
    inicio = max(0, posicion_ideal - margen)
    fin = min(len(texto), posicion_ideal + margen)
    segmento = texto[inicio:fin]

    # Prioridad 1: inicio de articulo
    for m in _RE_ARTICULO.finditer(segmento):
        pos = inicio + m.start()
        if abs(pos - posicion_ideal) <= margen:
            return pos

    # Prioridad 2: titulo/capitulo
    for m in _RE_TITULO_CAPITULO.finditer(segmento):
        pos = inicio + m.start()
        if abs(pos - posicion_ideal) <= margen:
            return pos

    # Prioridad 3: considerando/resuelve
    for m in _RE_CONSIDERANDO.finditer(segmento):
        pos = inicio + m.start()
        if abs(pos - posicion_ideal) <= margen:
            return pos

    # Fallback a corte general
    return _encontrar_punto_corte(texto, posicion_ideal, margen)


def _parametros_modo(modo: ModoChunking) -> tuple[int, int, int]:
    """Retorna (tamano, solapamiento, margen_corte) segun el modo."""
    if modo == "juridico":
        return TAMANO_JURIDICO, SOLAPAMIENTO_JURIDICO, 200
    elif modo == "institucional":
        return TAMANO_INSTITUCIONAL, SOLAPAMIENTO_INSTITUCIONAL, 150
    else:
        return TAMANO_FRAGMENTO_DEFAULT, SOLAPAMIENTO_DEFAULT, 100


def detectar_modo_por_coleccion(coleccion: str) -> ModoChunking:
    """Detecta el modo de chunking apropiado segun la coleccion.

    Args:
        coleccion: Nombre de la coleccion del documento.

    Returns:
        Modo de chunking recomendado.
    """
    coleccion_lower = coleccion.lower()

    if coleccion_lower in {"normativo", "jurisprudencial"}:
        return "juridico"
    elif coleccion_lower in {"institucional", "auditoria"}:
        return "institucional"
    else:
        return "general"


def dividir_en_fragmentos(
    texto: str,
    tamano: int | None = None,
    solapamiento: int | None = None,
    metadata_base: Optional[dict[str, Any]] = None,
    modo: ModoChunking = "general",
) -> list[Fragmento]:
    """Divide un texto en fragmentos con solapamiento y metadatos.

    Soporta tres modos:
    - general: fragmentos estandar con cortes en oraciones/parrafos
    - juridico: fragmentos mas grandes, cortes en articulos/secciones
    - institucional: fragmentos medianos, cortes en secciones

    Args:
        texto: Texto completo a fragmentar.
        tamano: Tamano objetivo en caracteres (override del modo).
        solapamiento: Solapamiento en caracteres (override del modo).
        metadata_base: Metadatos base que se copian a cada fragmento.
        modo: Modo de fragmentacion.

    Returns:
        Lista de fragmentos con sus metadatos.
    """
    if not texto or not texto.strip():
        return []

    tamano_modo, solap_modo, margen = _parametros_modo(modo)
    tamano = tamano or tamano_modo
    solapamiento = solapamiento or solap_modo

    if tamano <= solapamiento:
        raise ValueError(
            f"El tamano ({tamano}) debe ser mayor que el solapamiento ({solapamiento})."
        )

    fn_corte = _encontrar_punto_corte_juridico if modo == "juridico" else _encontrar_punto_corte
    metadata_base = metadata_base or {}
    fragmentos: list[Fragmento] = []
    inicio = 0
    longitud_texto = len(texto)

    while inicio < longitud_texto:
        fin_ideal = min(inicio + tamano, longitud_texto)

        if fin_ideal < longitud_texto:
            fin = fn_corte(texto, fin_ideal, margen)
        else:
            fin = fin_ideal

        contenido_fragmento = texto[inicio:fin].strip()

        if len(contenido_fragmento) >= TAMANO_MINIMO:
            metadata_fragmento = {
                **metadata_base,
                "inicio_char": inicio,
                "fin_char": fin,
                "modo_chunking": modo,
            }

            fragmentos.append(
                Fragmento(
                    contenido=contenido_fragmento,
                    metadata=metadata_fragmento,
                    indice=len(fragmentos),
                )
            )

        avance = max(fin - inicio - solapamiento, 1)
        inicio += avance

    total = len(fragmentos)
    for fragmento in fragmentos:
        fragmento.total_fragmentos = total
        fragmento.metadata["total_fragmentos"] = total
        fragmento.metadata["indice_fragmento"] = fragmento.indice

    logger.info(
        "Texto dividido en %d fragmentos (modo=%s, tamano=%d, solapamiento=%d).",
        total, modo, tamano, solapamiento,
    )

    return fragmentos
