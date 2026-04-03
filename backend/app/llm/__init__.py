"""
CecilIA v2 — Fábrica de modelos LLM multi-proveedor
Detecta el proveedor desde variables de entorno y retorna el cliente correcto.
"""
import logging
import time
from typing import Any
from langchain_core.language_models import BaseChatModel

logger = logging.getLogger("cecilia.llm")

def _detectar_proveedor(base_url: str) -> str:
    """Detecta el proveedor LLM según la URL base."""
    url = base_url.lower()
    if "anthropic" in url:
        return "anthropic"
    if "generativelanguage.googleapis" in url:
        return "google"
    if "groq" in url:
        return "groq"
    if "localhost:11434" in url or "host.docker.internal:11434" in url:
        return "ollama"
    return "openai"

def _crear_cliente(base_url: str, model: str, api_key: str, temperature: float = 0.2, max_tokens: int = 4096, timeout: int = 120) -> BaseChatModel:
    """Crea el cliente LLM según el proveedor detectado."""
    proveedor = _detectar_proveedor(base_url)
    logger.info("Creando cliente LLM: proveedor=%s, modelo=%s", proveedor, model)

    if proveedor == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=float(timeout),
            default_headers={"anthropic-beta": "max-tokens-3-5-sonnet-2024-07-15"},
        )

    # For google, groq, ollama, openai — all use ChatOpenAI with base_url
    from langchain_openai import ChatOpenAI
    kwargs: dict[str, Any] = {
        "model": model,
        "api_key": api_key,
        "temperature": temperature,
        "timeout": float(timeout),
    }
    # Google Gemini via OpenAI-compatible API: don't send max_tokens (causes issues)
    if proveedor != "google":
        kwargs["max_tokens"] = max_tokens
    if proveedor != "openai":
        kwargs["base_url"] = base_url

    return ChatOpenAI(**kwargs)

def crear_llm(backup: bool = False) -> BaseChatModel:
    """Factory principal. Lee config del .env y retorna el cliente correcto.

    Args:
        backup: Si True, usa las variables LLM_BACKUP_* en lugar de las principales.
    """
    from app.config import configuracion

    if backup:
        base_url = configuracion.LLM_BACKUP_BASE_URL
        model = configuracion.LLM_BACKUP_MODEL
        api_key = configuracion.LLM_BACKUP_API_KEY
        if not base_url or not model:
            raise ValueError("LLM backup no configurado en .env")
    else:
        base_url = configuracion.LLM_BASE_URL
        model = configuracion.LLM_MODEL
        api_key = configuracion.LLM_API_KEY

    return _crear_cliente(
        base_url=base_url,
        model=model,
        api_key=api_key,
        temperature=configuracion.LLM_TEMPERATURA,
        max_tokens=configuracion.LLM_MAX_TOKENS,
        timeout=configuracion.LLM_TIMEOUT_SEGUNDOS,
    )

def obtener_llm() -> BaseChatModel:
    """Alias para crear_llm() — retorna el LLM principal."""
    return crear_llm(backup=False)

def invocar_con_fallback(llm_principal: BaseChatModel, mensajes: list, reintentos: int = 2) -> Any:
    """Invoca el LLM principal con fallback al backup si falla.

    Returns:
        Tuple (respuesta, modelo_usado: str, es_backup: bool)
    """
    from app.config import configuracion

    for intento in range(reintentos):
        try:
            inicio = time.time()
            respuesta = llm_principal.invoke(mensajes)
            duracion = time.time() - inicio
            logger.info("LLM principal respondió en %.1fs (intento %d)", duracion, intento + 1)
            return respuesta, configuracion.LLM_MODEL, False
        except Exception as e:
            logger.warning("LLM principal falló (intento %d/%d): %s", intento + 1, reintentos, e)
            if intento < reintentos - 1:
                time.sleep(1)

    # Fallback al backup
    try:
        logger.info("Activando LLM backup: %s", configuracion.LLM_BACKUP_MODEL)
        llm_backup = crear_llm(backup=True)
        inicio = time.time()
        respuesta = llm_backup.invoke(mensajes)
        duracion = time.time() - inicio
        logger.info("LLM backup respondió en %.1fs", duracion)
        return respuesta, configuracion.LLM_BACKUP_MODEL, True
    except Exception as e:
        logger.error("LLM backup también falló: %s", e)
        raise

def info_modelo_activo() -> dict[str, str]:
    """Retorna info del modelo activo para el endpoint /api/config/modelo-activo."""
    from app.config import configuracion
    proveedor = _detectar_proveedor(configuracion.LLM_BASE_URL)

    nombres_proveedor = {
        "anthropic": "Anthropic Claude",
        "google": "Google Gemini",
        "groq": "Groq",
        "ollama": "Ollama Local",
        "openai": "OpenAI",
    }

    # Friendly model name
    model = configuracion.LLM_MODEL
    nombre_display = model
    if "claude" in model.lower():
        parts = model.split("-")
        # claude-sonnet-4-20250514 -> Claude Sonnet 4
        if len(parts) >= 3:
            nombre_display = f"Claude {parts[1].capitalize()} {parts[2]}"
    elif "gemini" in model.lower():
        nombre_display = model.replace("-", " ").title()
    elif "gpt" in model.lower():
        nombre_display = model.upper()

    return {
        "proveedor": nombres_proveedor.get(proveedor, proveedor),
        "modelo": model,
        "nombre_display": nombre_display,
        "estado": "conectado",
    }
