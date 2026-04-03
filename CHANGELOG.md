# Registro de Cambios (Changelog)

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/),
y este proyecto sigue [Versionado Semántico](https://semver.org/lang/es/).

## [2.0.0] — En desarrollo

### Sprint 0 — Fundaciones (2026-03-31 / 2026-04-11)

#### Agregado
- Estructura inicial del monorepo con carpetas `backend/`, `frontend/`, `infra/`, `docs/`, `scripts/`, `corpus/`, `desktop-agent/` y `apus-renta/`.
- Archivo `.env.example` con configuración multi-proveedor LLM (Claude, Gemini, Groq, Ollama, vLLM).
- `docker-compose.yml` de producción con PostgreSQL 16 + pgvector, Redis 8, FastAPI y Next.js.
- `docker-compose.dev.yml` con sobreescrituras para desarrollo local y recarga en caliente.
- `.gitignore` integral para Python, Node.js, Docker e IDEs.
- Archivo `LICENSE` con aviso de propiedad intelectual de la CGR.
- `README.md` con documentación completa del proyecto.
- Este archivo `CHANGELOG.md`.

#### Notas
- Este sprint establece la infraestructura base y la documentación fundacional.
- No incluye funcionalidad de aplicación; la lógica de negocio inicia en Sprint 1.
