"""
CecilIA v2 — Punto de entrada del Scheduler del Observatorio TIC
Contraloria General de la Republica de Colombia

Ejecuta los crawlers del observatorio cada 6 horas.
Uso: python scheduler_main.py
Docker: entrypoint del servicio 'scheduler'
Sprint: 8
"""

import asyncio
import logging
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger("cecilia.scheduler")


async def main() -> None:
    """Punto de entrada principal del scheduler."""
    logger.info("=" * 60)
    logger.info("CecilIA v2 — Scheduler del Observatorio TIC")
    logger.info("Contraloria General de la Republica de Colombia")
    logger.info("=" * 60)

    # Esperar a que el backend este listo (30 segundos)
    import httpx

    for intento in range(10):
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get("http://backend:8000/salud", timeout=5)
                if r.status_code == 200:
                    logger.info("Backend disponible, iniciando scheduler")
                    break
        except Exception:
            logger.info("Esperando backend... (intento %d/10)", intento + 1)
            await asyncio.sleep(5)
    else:
        logger.warning("Backend no disponible despues de 50s, iniciando de todas formas")

    from app.observatorio.scheduler import ciclo_scheduler
    await ciclo_scheduler()


if __name__ == "__main__":
    asyncio.run(main())
