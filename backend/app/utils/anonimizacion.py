"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: anonimizacion.py
Propósito: Anonimización de datos personales (PII) conforme a la Ley 1581 de 2012
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("cecilia.utils.anonimizacion")

# ---------------------------------------------------------------------------
# Patrones de PII para Colombia
# ---------------------------------------------------------------------------

# Cédula de ciudadanía colombiana: 6-10 dígitos (con posibles puntos separadores)
PATRON_CEDULA: str = r"\b(?:C\.?C\.?\s*(?:No\.?\s*)?)?(\d{1,3}(?:\.\d{3}){1,3}|\d{6,10})\b"

# NIT colombiano: 9 dígitos + dígito de verificación
PATRON_NIT: str = r"\b(?:NIT\.?\s*(?:No\.?\s*)?)?(\d{3}\.?\d{3}\.?\d{3}[-.]?\d)\b"

# Correo electrónico
PATRON_EMAIL: str = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

# Teléfono colombiano: celular (3xx xxx xxxx) o fijo (x xxx xxxx)
PATRON_TELEFONO: str = r"\b(?:\+57\s?)?(?:3\d{2}[\s.-]?\d{3}[\s.-]?\d{4}|\(\d{1,2}\)\s?\d{3}[\s.-]?\d{4}|\d{7,10})\b"

# Nombre propio (heurística: dos o más palabras capitalizadas consecutivas)
# Se usa como heurística, no como patrón absoluto
PATRON_NOMBRE_PROPIO: str = r"\b([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,4})\b"

# Dirección colombiana
PATRON_DIRECCION: str = (
    r"\b(?:Calle|Carrera|Cra|Cl|Avenida|Av|Diagonal|Diag|Transversal|Trans|Kr|Kra)"
    r"\s*\.?\s*\d+[A-Za-z]?\s*(?:#|No\.?\s*)\s*\d+[A-Za-z]?\s*[-–]\s*\d+\b"
)

# Número de cuenta bancaria (simplificado)
PATRON_CUENTA_BANCARIA: str = r"\b(?:cuenta\s*(?:No\.?\s*)?)?(\d{4}[-\s]?\d{4}[-\s]?\d{2,4})\b"


@dataclass
class ResultadoAnonimizacion:
    """Resultado del proceso de anonimización."""

    texto_anonimizado: str
    pii_detectado: list[dict[str, str]] = field(default_factory=list)
    total_reemplazos: int = 0


def _generar_pseudonimo(valor: str, tipo: str) -> str:
    """Genera un pseudónimo determinístico para un valor PII.

    Usa SHA-256 truncado para generar un identificador único y consistente
    (el mismo valor siempre produce el mismo pseudónimo).

    Args:
        valor: Valor original a pseudonimizar.
        tipo: Tipo de dato (cedula, email, telefono, etc.).

    Returns:
        Pseudónimo en formato [TIPO_HASH].
    """
    hash_valor: str = hashlib.sha256(valor.encode("utf-8")).hexdigest()[:8].upper()
    return f"[{tipo.upper()}_{hash_valor}]"


def anonimizar_texto(
    texto: str,
    anonimizar_cedulas: bool = True,
    anonimizar_nit: bool = True,
    anonimizar_emails: bool = True,
    anonimizar_telefonos: bool = True,
    anonimizar_nombres: bool = False,
    anonimizar_direcciones: bool = True,
    anonimizar_cuentas: bool = True,
    usar_pseudonimos: bool = True,
) -> ResultadoAnonimizacion:
    """Anonimiza datos personales (PII) en un texto conforme a la Ley 1581/2012.

    Detecta y reemplaza datos personales sensibles con marcadores o pseudónimos
    determinísticos. La anonimización de nombres está desactivada por defecto
    debido a la alta tasa de falsos positivos con heurísticas.

    Args:
        texto: Texto a anonimizar.
        anonimizar_cedulas: Si True, anonimiza números de cédula.
        anonimizar_nit: Si True, anonimiza números de NIT.
        anonimizar_emails: Si True, anonimiza correos electrónicos.
        anonimizar_telefonos: Si True, anonimiza números de teléfono.
        anonimizar_nombres: Si True, intenta anonimizar nombres propios (heurístico).
        anonimizar_direcciones: Si True, anonimiza direcciones.
        anonimizar_cuentas: Si True, anonimiza números de cuenta bancaria.
        usar_pseudonimos: Si True, usa pseudónimos determinísticos; si False, usa genéricos.

    Returns:
        Resultado con texto anonimizado y metadatos de PII encontrado.
    """
    if not texto:
        return ResultadoAnonimizacion(texto_anonimizado="", total_reemplazos=0)

    pii_detectado: list[dict[str, str]] = []
    texto_resultado: str = texto
    total_reemplazos: int = 0

    def _reemplazar(
        patron: str,
        tipo: str,
        texto_actual: str,
        flags: int = 0,
    ) -> tuple[str, int]:
        """Función interna para buscar y reemplazar PII."""
        nonlocal pii_detectado
        count: int = 0

        def _reemplazo(match: re.Match) -> str:
            nonlocal count
            valor_original: str = match.group(0)
            reemplazo: str = (
                _generar_pseudonimo(valor_original, tipo)
                if usar_pseudonimos
                else f"[{tipo.upper()}_ANONIMIZADO]"
            )

            pii_detectado.append({
                "tipo": tipo,
                "posicion": match.start(),
                "longitud_original": len(valor_original),
                "reemplazo": reemplazo,
            })
            count += 1
            return reemplazo

        texto_nuevo: str = re.sub(patron, _reemplazo, texto_actual, flags=flags)
        return texto_nuevo, count

    # Aplicar anonimización en orden de especificidad (más específico primero)
    if anonimizar_nit:
        texto_resultado, n = _reemplazar(PATRON_NIT, "nit", texto_resultado, re.IGNORECASE)
        total_reemplazos += n

    if anonimizar_cedulas:
        texto_resultado, n = _reemplazar(PATRON_CEDULA, "cedula", texto_resultado, re.IGNORECASE)
        total_reemplazos += n

    if anonimizar_emails:
        texto_resultado, n = _reemplazar(PATRON_EMAIL, "email", texto_resultado)
        total_reemplazos += n

    if anonimizar_direcciones:
        texto_resultado, n = _reemplazar(PATRON_DIRECCION, "direccion", texto_resultado, re.IGNORECASE)
        total_reemplazos += n

    if anonimizar_telefonos:
        texto_resultado, n = _reemplazar(PATRON_TELEFONO, "telefono", texto_resultado)
        total_reemplazos += n

    if anonimizar_cuentas:
        texto_resultado, n = _reemplazar(PATRON_CUENTA_BANCARIA, "cuenta", texto_resultado, re.IGNORECASE)
        total_reemplazos += n

    if anonimizar_nombres:
        texto_resultado, n = _reemplazar(PATRON_NOMBRE_PROPIO, "nombre", texto_resultado)
        total_reemplazos += n

    if total_reemplazos > 0:
        logger.info(
            "Anonimización completada: %d datos personales detectados y reemplazados.",
            total_reemplazos,
        )

    return ResultadoAnonimizacion(
        texto_anonimizado=texto_resultado,
        pii_detectado=pii_detectado,
        total_reemplazos=total_reemplazos,
    )


def verificar_pii_presente(texto: str) -> list[dict[str, str]]:
    """Verifica si un texto contiene datos personales sin anonimizar.

    Útil para validar que un texto que va a ser almacenado o transmitido
    no contiene PII sensible.

    Args:
        texto: Texto a verificar.

    Returns:
        Lista de tipos de PII encontrados con sus posiciones.
    """
    pii_encontrado: list[dict[str, str]] = []

    patrones: dict[str, str] = {
        "cedula": PATRON_CEDULA,
        "nit": PATRON_NIT,
        "email": PATRON_EMAIL,
        "telefono": PATRON_TELEFONO,
        "direccion": PATRON_DIRECCION,
    }

    for tipo, patron in patrones.items():
        coincidencias = re.finditer(patron, texto, re.IGNORECASE)
        for match in coincidencias:
            pii_encontrado.append({
                "tipo": tipo,
                "posicion": str(match.start()),
                "longitud": str(len(match.group(0))),
                "fragmento": match.group(0)[:20] + "..." if len(match.group(0)) > 20 else match.group(0),
            })

    return pii_encontrado
