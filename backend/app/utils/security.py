"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: security.py
Propósito: Utilidades de seguridad — hashing de contraseñas (bcrypt), sanitización de entrada
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import html
import logging
import re
from typing import Optional

import bcrypt

logger = logging.getLogger("cecilia.utils.security")

# Configuración de bcrypt
BCRYPT_ROUNDS: int = 12

# Longitud máxima de entrada para sanitización
MAX_LONGITUD_MENSAJE: int = 10_000
MAX_LONGITUD_CAMPO: int = 500

# Patrones de inyección comunes a detectar
PATRONES_INYECCION: list[str] = [
    r"<script\b[^>]*>",
    r"javascript:",
    r"on\w+\s*=",
    r"eval\s*\(",
    r"expression\s*\(",
    r"url\s*\(",
    r"import\s*\(",
]

# Patrones de prompt injection a detectar
PATRONES_PROMPT_INJECTION: list[str] = [
    r"ignore\s+(?:all\s+)?(?:previous|above|prior)\s+instructions",
    r"olvida\s+(?:todas?\s+)?(?:las\s+)?instrucciones\s+anteriores",
    r"ignora\s+(?:todas?\s+)?(?:las\s+)?instrucciones\s+anteriores",
    r"you\s+are\s+now\s+(?:a\s+)?(?:new|different)",
    r"ahora\s+eres\s+(?:un\s+)?(?:nuevo|diferente)",
    r"system\s*:\s*",
    r"<\|(?:im_start|im_end|system|endoftext)\|>",
    r"\[INST\]",
    r"###\s*(?:System|Human|Assistant)\s*:",
]


def hashear_contrasena(contrasena: str) -> str:
    """Genera un hash bcrypt de la contraseña.

    Args:
        contrasena: Contraseña en texto plano.

    Returns:
        Hash bcrypt de la contraseña.

    Raises:
        ValueError: Si la contraseña no cumple los requisitos mínimos.
    """
    _validar_fortaleza_contrasena(contrasena)

    sal: bytes = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hash_bytes: bytes = bcrypt.hashpw(contrasena.encode("utf-8"), sal)

    return hash_bytes.decode("utf-8")


def verificar_contrasena(contrasena: str, hash_almacenado: str) -> bool:
    """Verifica una contraseña contra su hash bcrypt.

    Args:
        contrasena: Contraseña en texto plano a verificar.
        hash_almacenado: Hash bcrypt almacenado.

    Returns:
        True si la contraseña coincide con el hash.
    """
    try:
        return bcrypt.checkpw(
            contrasena.encode("utf-8"),
            hash_almacenado.encode("utf-8"),
        )
    except Exception:
        logger.exception("Error al verificar contraseña.")
        return False


def _validar_fortaleza_contrasena(contrasena: str) -> None:
    """Valida la fortaleza mínima de una contraseña.

    Requisitos:
    - Mínimo 12 caracteres.
    - Al menos una mayúscula.
    - Al menos una minúscula.
    - Al menos un dígito.
    - Al menos un carácter especial.

    Args:
        contrasena: Contraseña a validar.

    Raises:
        ValueError: Si la contraseña no cumple los requisitos.
    """
    errores: list[str] = []

    if len(contrasena) < 12:
        errores.append("Mínimo 12 caracteres.")
    if not re.search(r"[A-Z]", contrasena):
        errores.append("Al menos una letra mayúscula.")
    if not re.search(r"[a-z]", contrasena):
        errores.append("Al menos una letra minúscula.")
    if not re.search(r"\d", contrasena):
        errores.append("Al menos un dígito.")
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", contrasena):
        errores.append("Al menos un carácter especial (!@#$%^&*...).")

    if errores:
        raise ValueError(
            "La contraseña no cumple los requisitos de seguridad:\n"
            + "\n".join(f"  - {e}" for e in errores)
        )


def sanitizar_entrada(
    texto: str,
    max_longitud: int = MAX_LONGITUD_MENSAJE,
    permitir_html: bool = False,
) -> str:
    """Sanitiza una entrada de texto para prevenir inyección.

    Realiza:
    1. Truncamiento a longitud máxima.
    2. Escape de HTML (prevención de XSS).
    3. Detección de patrones de inyección.
    4. Normalización de espacios.

    Args:
        texto: Texto de entrada a sanitizar.
        max_longitud: Longitud máxima permitida.
        permitir_html: Si True, no escapa caracteres HTML.

    Returns:
        Texto sanitizado.
    """
    if not texto:
        return ""

    # Truncar
    texto = texto[:max_longitud]

    # Escape de HTML
    if not permitir_html:
        texto = html.escape(texto, quote=True)

    # Normalizar espacios
    texto = re.sub(r"\s+", " ", texto).strip()

    return texto


def detectar_inyeccion(texto: str) -> tuple[bool, list[str]]:
    """Detecta posibles intentos de inyección en el texto.

    Busca patrones de:
    - Inyección XSS.
    - Inyección SQL.
    - Prompt injection.

    Args:
        texto: Texto a analizar.

    Returns:
        Tupla (hay_inyeccion, patrones_detectados).
    """
    texto_lower: str = texto.lower()
    patrones_encontrados: list[str] = []

    # Buscar patrones de inyección general
    for patron in PATRONES_INYECCION:
        if re.search(patron, texto_lower, re.IGNORECASE):
            patrones_encontrados.append(f"inyeccion_general: {patron}")

    # Buscar patrones de prompt injection
    for patron in PATRONES_PROMPT_INJECTION:
        if re.search(patron, texto_lower, re.IGNORECASE):
            patrones_encontrados.append(f"prompt_injection: {patron}")

    if patrones_encontrados:
        logger.warning(
            "Posible inyección detectada (%d patrones): %s",
            len(patrones_encontrados),
            ", ".join(patrones_encontrados),
        )

    return bool(patrones_encontrados), patrones_encontrados


def sanitizar_nombre_archivo(nombre: str) -> str:
    """Sanitiza un nombre de archivo para prevenir path traversal.

    Args:
        nombre: Nombre de archivo original.

    Returns:
        Nombre de archivo sanitizado.
    """
    # Eliminar componentes de ruta
    nombre = nombre.replace("\\", "/")
    nombre = nombre.split("/")[-1]

    # Eliminar caracteres peligrosos
    nombre = re.sub(r"[^\w\s\-.]", "", nombre)

    # Eliminar doble punto (path traversal)
    nombre = nombre.replace("..", "")

    # Limitar longitud
    nombre = nombre[:255]

    return nombre.strip() or "archivo_sin_nombre"
