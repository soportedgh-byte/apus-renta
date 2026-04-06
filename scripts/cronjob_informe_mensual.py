#!/usr/bin/env python3
"""
CecilIA v2 — Cronjob de informe ejecutivo mensual
Contraloria General de la Republica de Colombia

Archivo: scripts/cronjob_informe_mensual.py
Proposito: Genera automaticamente el informe ejecutivo DOCX y el reporte
           Circular 023 el dia 1 de cada mes. Se ejecuta via cron o
           Windows Task Scheduler.

Sprint: 10
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026

Uso:
    python scripts/cronjob_informe_mensual.py

Cron (Linux):
    0 6 1 * * cd /opt/cecilia-v2 && python scripts/cronjob_informe_mensual.py >> /var/log/cecilia/informe_mensual.log 2>&1

Windows Task Scheduler:
    Trigger: Monthly, Day 1, 06:00
    Action: python C:\\cecilia-v2\\scripts\\cronjob_informe_mensual.py
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("cecilia.cronjob.informe")


async def generar_informes():
    """Genera informe ejecutivo y reporte Circular 023 del mes anterior."""
    from app.database import obtener_sesion_async
    from app.analytics.metricas_uso import obtener_metricas_uso
    from app.analytics.metricas_auditoria import obtener_metricas_auditoria
    from app.analytics.metricas_calidad import obtener_metricas_calidad
    from app.analytics.metricas_capacitacion import obtener_metricas_capacitacion
    from app.analytics.exportador import (
        generar_informe_ejecutivo,
        generar_reporte_circular_023_docx,
    )

    ahora = datetime.now(timezone.utc)
    # Periodo: mes anterior completo
    primer_dia_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ultimo_dia_anterior = primer_dia_mes - timedelta(days=1)
    inicio = ultimo_dia_anterior.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    fin = primer_dia_mes

    mes_nombre = inicio.strftime("%B_%Y")
    logger.info("=== Generando informes mensuales CecilIA ===")
    logger.info(f"Periodo: {inicio.isoformat()} — {fin.isoformat()}")

    # Directorio de salida
    output_dir = Path(__file__).resolve().parent.parent / "informes" / mes_nombre
    output_dir.mkdir(parents=True, exist_ok=True)

    async for db in obtener_sesion_async():
        try:
            # Obtener metricas
            logger.info("Consultando metricas de uso...")
            metricas_uso = await obtener_metricas_uso(db, inicio, fin)

            logger.info("Consultando metricas de auditoria...")
            metricas_aud = await obtener_metricas_auditoria(db, inicio, fin)

            logger.info("Consultando metricas de calidad...")
            metricas_cal = await obtener_metricas_calidad(db, inicio, fin)

            logger.info("Consultando metricas de capacitacion...")
            metricas_cap = await obtener_metricas_capacitacion(db, inicio, fin)

            # Generar informe ejecutivo DOCX
            logger.info("Generando informe ejecutivo DOCX...")
            buffer_ejecutivo = await generar_informe_ejecutivo(
                metricas_uso, metricas_aud, metricas_cal, metricas_cap
            )
            ruta_ejecutivo = output_dir / f"informe_ejecutivo_{mes_nombre}.docx"
            with open(ruta_ejecutivo, "wb") as f:
                f.write(buffer_ejecutivo.getvalue())
            logger.info(f"Informe ejecutivo guardado: {ruta_ejecutivo}")

            # Generar reporte Circular 023 DOCX
            logger.info("Generando reporte Circular 023 DOCX...")
            buffer_c023 = await generar_reporte_circular_023_docx(
                metricas_uso, metricas_aud, metricas_cal, metricas_cap
            )
            ruta_c023 = output_dir / f"reporte_circular_023_{mes_nombre}.docx"
            with open(ruta_c023, "wb") as f:
                f.write(buffer_c023.getvalue())
            logger.info(f"Reporte Circular 023 guardado: {ruta_c023}")

            logger.info("=== Informes mensuales generados exitosamente ===")
            logger.info(f"Directorio: {output_dir}")

        except Exception as e:
            logger.error(f"Error generando informes: {e}", exc_info=True)
            raise


def main():
    """Punto de entrada del cronjob."""
    try:
        asyncio.run(generar_informes())
    except Exception as e:
        logger.error(f"Cronjob fallido: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
