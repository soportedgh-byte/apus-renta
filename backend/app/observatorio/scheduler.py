"""
CecilIA v2 — Scheduler del Observatorio TIC
Contraloria General de la Republica de Colombia

Proposito: Orquesta la ejecucion periodica de crawlers, clasificacion LLM
           y almacenamiento de alertas. Ejecuta cada 6 horas.
Sprint: 8
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alerta_observatorio import AlertaObservatorio
from app.observatorio.clasificador import clasificar_contenido
from app.observatorio.fuentes import MONITORES
from app.observatorio.fuentes.base_monitor import ContenidoDetectado

logger = logging.getLogger("cecilia.observatorio.scheduler")

# Intervalo entre ejecuciones (6 horas)
INTERVALO_HORAS = 6


async def ejecutar_crawl(db: AsyncSession) -> dict[str, Any]:
    """Ejecuta un ciclo completo de crawl + clasificacion + almacenamiento.

    Returns:
        Resumen de la ejecucion con contadores.
    """
    inicio = datetime.now(timezone.utc)
    logger.info("=== Iniciando ciclo de crawl del Observatorio TIC ===")

    total_detectados = 0
    total_clasificados = 0
    total_alertas_creadas = 0
    total_duplicados = 0
    errores: list[str] = []
    resultados_por_fuente: dict[str, int] = {}

    # 1. Ejecutar todos los monitores
    for MonitorClass in MONITORES:
        monitor = MonitorClass()
        try:
            contenidos = await monitor.ejecutar()
            resultados_por_fuente[monitor.nombre] = len(contenidos)
            total_detectados += len(contenidos)

            # 2. Clasificar y almacenar cada contenido
            for contenido in contenidos:
                try:
                    # Verificar duplicados por hash
                    duplicado = await _es_duplicado(db, contenido)
                    if duplicado:
                        total_duplicados += 1
                        continue

                    # Clasificar con LLM
                    clasificacion = await clasificar_contenido(contenido)
                    total_clasificados += 1

                    # Solo crear alerta si relevancia >= MEDIA
                    if clasificacion.relevancia in ("ALTA", "MEDIA"):
                        alerta = AlertaObservatorio(
                            id=str(uuid.uuid4()),
                            tipo=contenido.tipo,
                            titulo=contenido.titulo[:300],
                            resumen=clasificacion.resumen_ejecutivo[:1000],
                            fuente_url=contenido.url[:500],
                            fuente_nombre=contenido.fuente_nombre[:100],
                            relevancia=clasificacion.relevancia,
                            tipo_impacto=clasificacion.tipo_impacto,
                            entidades_afectadas=clasificacion.entidades_afectadas,
                            estado="NUEVA",
                            fecha_deteccion=datetime.now(timezone.utc),
                            fecha_publicacion=contenido.fecha_publicacion,
                            hash_contenido=contenido.hash_contenido,
                            metadata_extra={
                                "clasificacion_exito": clasificacion.exito,
                                "clasificacion_error": clasificacion.error,
                                "metadata_fuente": contenido.metadata,
                            },
                        )
                        db.add(alerta)
                        total_alertas_creadas += 1

                except Exception as e:
                    logger.error("Error procesando item '%s': %s", contenido.titulo[:50], e)
                    errores.append(f"{contenido.fuente_nombre}: {str(e)[:100]}")

        except Exception as e:
            logger.error("Error en monitor %s: %s", monitor.nombre, e)
            errores.append(f"Monitor {monitor.nombre}: {str(e)[:100]}")

    # 3. Commit
    try:
        await db.commit()
    except Exception as e:
        logger.error("Error al hacer commit: %s", e)
        await db.rollback()
        errores.append(f"Commit: {str(e)[:100]}")

    duracion = (datetime.now(timezone.utc) - inicio).total_seconds()

    resumen = {
        "inicio": inicio.isoformat(),
        "duracion_segundos": round(duracion, 1),
        "total_detectados": total_detectados,
        "total_clasificados": total_clasificados,
        "total_alertas_creadas": total_alertas_creadas,
        "total_duplicados": total_duplicados,
        "por_fuente": resultados_por_fuente,
        "errores": errores[:10],
    }

    logger.info(
        "Crawl completado: %d detectados, %d clasificados, %d alertas creadas, %d duplicados (%.1fs)",
        total_detectados, total_clasificados, total_alertas_creadas, total_duplicados, duracion,
    )

    return resumen


async def _es_duplicado(db: AsyncSession, contenido: ContenidoDetectado) -> bool:
    """Verifica si el contenido ya fue procesado (por hash)."""
    resultado = await db.execute(
        select(AlertaObservatorio.id).where(
            AlertaObservatorio.hash_contenido == contenido.hash_contenido
        ).limit(1)
    )
    return resultado.scalar_one_or_none() is not None


async def ciclo_scheduler() -> None:
    """Bucle infinito que ejecuta crawls cada INTERVALO_HORAS horas.

    Usado por el servicio scheduler en Docker.
    """
    from app.main import fabrica_sesiones

    logger.info("Scheduler del Observatorio TIC iniciado (cada %dh)", INTERVALO_HORAS)

    while True:
        try:
            async with fabrica_sesiones() as db:
                resumen = await ejecutar_crawl(db)
                logger.info("Resumen del crawl: %s", resumen)
        except Exception as e:
            logger.error("Error en ciclo del scheduler: %s", e, exc_info=True)

        # Esperar hasta el proximo ciclo
        espera = INTERVALO_HORAS * 3600
        logger.info("Proximo crawl en %d horas", INTERVALO_HORAS)
        await asyncio.sleep(espera)


if __name__ == "__main__":
    """Permite ejecutar el scheduler como script independiente."""
    import sys
    sys.path.insert(0, "/app")

    async def main():
        # Importar despues de configurar path
        from app.main import fabrica_sesiones  # noqa: F811
        async with fabrica_sesiones() as db:
            resumen = await ejecutar_crawl(db)
            print(f"Crawl completado: {resumen}")

    asyncio.run(main())
