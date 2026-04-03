# CecilIA v2 — Dockerfile Backend
# Contraloria General de la Republica de Colombia
# Multi-stage build — Python 3.12

# ---------- Etapa 1: Dependencias ----------
FROM python:3.12-slim AS dependencias

WORKDIR /tmp

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        tesseract-ocr \
        tesseract-ocr-spa && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/instalar -r requirements.txt

# ---------- Etapa 2: Produccion ----------
FROM python:3.12-slim AS produccion

LABEL maintainer="Equipo Tecnico CecilIA — CD-TIC-CGR"
LABEL description="CecilIA v2 — Sistema de IA para Control Fiscal"

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq5 \
        tesseract-ocr \
        tesseract-ocr-spa && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd --gid 1001 cecilia && \
    useradd --uid 1001 --gid cecilia --shell /bin/bash --create-home cecilia

COPY --from=dependencias /instalar /usr/local

COPY . .

RUN chown -R cecilia:cecilia /app

USER cecilia

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import httpx; r = httpx.get('http://localhost:8000/salud'); r.raise_for_status()"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
