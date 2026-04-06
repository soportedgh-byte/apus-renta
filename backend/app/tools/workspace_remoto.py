"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/tools/workspace_remoto.py
Proposito: Herramienta LangChain para acceder al workspace local del auditor
           a traves del Desktop Agent conectado via WebSocket.
           Complementa acceder_workspace_local.py (que opera localmente)
           con operaciones remotas: listar, leer, escribir, crear_carpeta.
Sprint: 11
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from langchain_core.tools import tool

logger = logging.getLogger("cecilia.tools.workspace_remoto")


@tool
async def workspace_remoto(
    accion: str,
    ruta: str,
    contenido: Optional[str] = None,
    usuario_id: int = 0,
) -> str:
    """Accede al workspace local del auditor via Desktop Agent (WebSocket).

    Esta herramienta permite que CecilIA interactue con los archivos locales
    del auditor a traves del agente de escritorio Electron conectado.
    Requiere que el Desktop Agent este activo y conectado.

    SANDBOX ESTRICTO: Solo opera dentro de las carpetas autorizadas por el
    auditor en su Desktop Agent. No se permite path traversal.

    Los archivos se procesan en streaming sin copiarse permanentemente al servidor.

    Args:
        accion: Operacion a realizar:
            - "listar": Lista archivos en un directorio
            - "leer": Lee el contenido de un archivo
            - "escribir": Escribe contenido en un archivo (borradores, reportes)
            - "crear_carpeta": Crea una nueva carpeta
        ruta: Ruta del archivo o directorio dentro del workspace autorizado.
        contenido: Contenido a escribir (solo para accion "escribir").
        usuario_id: ID del usuario (inyectado automaticamente por el agente).

    Returns:
        Resultado de la operacion o mensaje de error descriptivo.
    """
    from app.api.agent_ws import ejecutar_comando_workspace

    if accion not in ("listar", "leer", "escribir", "crear_carpeta"):
        return f"Accion '{accion}' no soportada. Opciones: listar, leer, escribir, crear_carpeta."

    if not ruta:
        return "Se requiere una ruta para la operacion."

    if accion == "escribir" and not contenido:
        return "Se requiere contenido para la operacion de escritura."

    resultado = await ejecutar_comando_workspace(
        usuario_id=usuario_id,
        accion=accion,
        ruta=ruta,
        contenido=contenido,
    )

    if not resultado.get("exito", False):
        error = resultado.get("error", "Error desconocido")
        if "No hay agente" in error:
            return (
                "El Desktop Agent no esta conectado. "
                "El auditor debe iniciar CecilIA Agent en su computador "
                "y autenticarse para poder acceder a archivos locales."
            )
        return f"Error en workspace: {error}"

    # Formatear respuesta segun accion
    if accion == "listar":
        archivos = resultado.get("archivos", [])
        if not archivos:
            return "Directorio vacio o sin acceso."
        lineas = [f"Contenido de {ruta}:"]
        for a in archivos:
            if a.get("es_directorio"):
                lineas.append(f"  [DIR]  {a['nombre']}/")
            else:
                tam = a.get("tamano", 0)
                if tam and tam > 1024 * 1024:
                    tam_str = f"{tam / 1024 / 1024:.1f} MB"
                elif tam and tam > 1024:
                    tam_str = f"{tam / 1024:.1f} KB"
                else:
                    tam_str = f"{tam} B" if tam else ""
                lineas.append(f"  [FILE] {a['nombre']} ({tam_str})")
        return "\n".join(lineas)

    elif accion == "leer":
        contenido_leido = resultado.get("contenido", "")
        nombre = resultado.get("nombre", ruta)
        encoding = resultado.get("encoding", "utf-8")
        if encoding == "base64":
            return (
                f"Archivo binario: {nombre} ({resultado.get('tamano', 0)} bytes). "
                f"Para archivos binarios, use la pipeline de ingesta de documentos."
            )
        return f"Contenido de {nombre}:\n\n{contenido_leido}"

    elif accion == "escribir":
        tamano = resultado.get("tamano", 0)
        return f"Archivo escrito exitosamente ({tamano} bytes) en: {resultado.get('ruta', ruta)}"

    elif accion == "crear_carpeta":
        return f"Carpeta creada: {resultado.get('ruta', ruta)}"

    return str(resultado)
