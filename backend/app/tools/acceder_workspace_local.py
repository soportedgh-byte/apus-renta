"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: acceder_workspace_local.py
Propósito: Herramienta LangChain para acceso a archivos del workspace local (Desktop Agent)
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

from langchain_core.tools import tool

logger = logging.getLogger("cecilia.tools.workspace_local")

# Extensiones permitidas para lectura
EXTENSIONES_PERMITIDAS: set[str] = {
    ".pdf", ".docx", ".xlsx", ".xls", ".csv", ".txt", ".json", ".xml",
    ".png", ".jpg", ".jpeg", ".tiff",
}

# Tamaño máximo de archivo (50 MB)
TAMANO_MAXIMO_BYTES: int = 50 * 1024 * 1024


@tool
def acceder_workspace_local(
    ruta_archivo: str,
    operacion: str = "listar",
    directorio_workspace: Optional[str] = None,
) -> str:
    """Accede a archivos del workspace local del auditor (Desktop Agent).

    Permite listar archivos en el workspace y leer su contenido.
    Solo funciona dentro del directorio de workspace autorizado.
    Esta herramienta requiere el componente Desktop Agent activo.

    Args:
        ruta_archivo: Ruta relativa al archivo dentro del workspace.
                      Use '.' para el directorio raíz del workspace.
        operacion: Operación a realizar: 'listar' (lista archivos),
                   'leer' (lee contenido), 'info' (metadatos del archivo).
        directorio_workspace: Ruta base del workspace. Si es None,
                              usa la variable de entorno CECILIA_WORKSPACE_DIR.

    Returns:
        Resultado de la operación solicitada.
    """
    # Resolver directorio workspace
    workspace: str = directorio_workspace or os.environ.get(
        "CECILIA_WORKSPACE_DIR", ""
    )

    if not workspace:
        return (
            "No se ha configurado el directorio de workspace. "
            "Configure la variable de entorno CECILIA_WORKSPACE_DIR o "
            "proporcione el directorio como parámetro."
        )

    ruta_base: Path = Path(workspace).resolve()
    if not ruta_base.exists():
        return f"El directorio de workspace no existe: {ruta_base}"

    # Resolver ruta completa y verificar que está dentro del workspace (seguridad)
    ruta_completa: Path = (ruta_base / ruta_archivo).resolve()

    if not str(ruta_completa).startswith(str(ruta_base)):
        logger.warning(
            "Intento de acceso fuera del workspace: %s (base: %s)",
            ruta_completa, ruta_base,
        )
        return (
            "Error de seguridad: la ruta solicitada está fuera del "
            "directorio de workspace autorizado."
        )

    operacion = operacion.lower().strip()

    if operacion == "listar":
        return _listar_archivos(ruta_completa)
    elif operacion == "leer":
        return _leer_archivo(ruta_completa)
    elif operacion == "info":
        return _info_archivo(ruta_completa)
    else:
        return f"Operación '{operacion}' no soportada. Opciones: listar, leer, info."


def _listar_archivos(ruta: Path) -> str:
    """Lista archivos en el directorio especificado."""
    if not ruta.is_dir():
        return f"'{ruta.name}' no es un directorio."

    archivos: list[str] = []
    directorios: list[str] = []

    try:
        for item in sorted(ruta.iterdir()):
            if item.name.startswith("."):
                continue  # Ignorar archivos ocultos

            if item.is_dir():
                num_items: int = sum(1 for _ in item.iterdir() if not _.name.startswith("."))
                directorios.append(f"  [DIR] {item.name}/ ({num_items} elementos)")
            elif item.suffix.lower() in EXTENSIONES_PERMITIDAS:
                tamano: float = item.stat().st_size / 1024
                unidad: str = "KB"
                if tamano > 1024:
                    tamano /= 1024
                    unidad = "MB"
                archivos.append(f"  [FILE] {item.name} ({tamano:.1f} {unidad})")

    except PermissionError:
        return f"Sin permisos para acceder a: {ruta.name}"

    resultado: list[str] = [f"Contenido de: {ruta.name}/"]

    if directorios:
        resultado.append(f"\nDirectorios ({len(directorios)}):")
        resultado.extend(directorios)

    if archivos:
        resultado.append(f"\nArchivos ({len(archivos)}):")
        resultado.extend(archivos)

    if not directorios and not archivos:
        resultado.append("  (vacío o sin archivos con formato soportado)")

    return "\n".join(resultado)


def _leer_archivo(ruta: Path) -> str:
    """Lee el contenido de un archivo."""
    if not ruta.exists():
        return f"Archivo no encontrado: {ruta.name}"

    if not ruta.is_file():
        return f"'{ruta.name}' no es un archivo."

    if ruta.suffix.lower() not in EXTENSIONES_PERMITIDAS:
        return (
            f"Formato '{ruta.suffix}' no soportado. "
            f"Extensiones permitidas: {', '.join(sorted(EXTENSIONES_PERMITIDAS))}"
        )

    tamano: int = ruta.stat().st_size
    if tamano > TAMANO_MAXIMO_BYTES:
        return (
            f"Archivo demasiado grande ({tamano / 1024 / 1024:.1f} MB). "
            f"Máximo permitido: {TAMANO_MAXIMO_BYTES / 1024 / 1024:.0f} MB."
        )

    extension: str = ruta.suffix.lower()

    try:
        if extension == ".csv":
            contenido: str = ruta.read_text(encoding="utf-8")
            lineas: list[str] = contenido.split("\n")
            if len(lineas) > 100:
                return (
                    f"Archivo CSV: {ruta.name} ({len(lineas)} filas)\n"
                    f"Primeras 100 filas:\n" + "\n".join(lineas[:100]) +
                    f"\n... ({len(lineas) - 100} filas adicionales)"
                )
            return f"Archivo CSV: {ruta.name} ({len(lineas)} filas)\n{contenido}"

        elif extension in {".txt", ".json", ".xml"}:
            return ruta.read_text(encoding="utf-8")

        elif extension in {".pdf", ".docx", ".xlsx", ".xls"}:
            # Delegamos a la pipeline de ingestión
            from backend.app.rag.ingesta import ingestar_documento
            doc = ingestar_documento(ruta)
            return f"Contenido extraído de {ruta.name}:\n\n{doc.contenido}"

        elif extension in {".png", ".jpg", ".jpeg", ".tiff"}:
            return (
                f"Archivo de imagen: {ruta.name} ({tamano / 1024:.1f} KB). "
                f"Para extraer texto, use la función de OCR."
            )

        else:
            return f"Lectura de formato {extension} no implementada."

    except Exception as e:
        logger.exception("Error al leer archivo '%s'.", ruta.name)
        return f"Error al leer '{ruta.name}': {str(e)}"


def _info_archivo(ruta: Path) -> str:
    """Obtiene metadatos de un archivo."""
    if not ruta.exists():
        return f"Archivo no encontrado: {ruta.name}"

    stat = ruta.stat()
    tamano_kb: float = stat.st_size / 1024

    from datetime import datetime
    modificado: str = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    creado: str = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")

    return (
        f"Información del archivo: {ruta.name}\n"
        f"  Ruta: {ruta}\n"
        f"  Tamaño: {tamano_kb:.1f} KB ({stat.st_size:,} bytes)\n"
        f"  Tipo: {ruta.suffix}\n"
        f"  Modificado: {modificado}\n"
        f"  Creado: {creado}\n"
        f"  Es archivo: {ruta.is_file()}\n"
    )
