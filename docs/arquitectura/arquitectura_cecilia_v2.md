# Arquitectura de CecilIA v2

> Sistema de IA para Control Fiscal
> Contraloría General de la República de Colombia

## 1. Visión General

CecilIA v2 es un sistema de inteligencia artificial diseñado para asistir a los auditores de la Contraloría General de la República (CGR) en procesos de control fiscal. La arquitectura sigue un patrón de **microservicios desacoplados** con un núcleo de IA basado en **RAG (Retrieval-Augmented Generation)** y herramientas especializadas de auditoría.

## 2. Principios Arquitectónicos

- **Seguridad primero:** Autenticación JWT, RBAC por dirección técnica, cifrado en tránsito y en reposo.
- **Soberanía de datos:** Toda la información permanece en infraestructura controlada por la CGR.
- **Trazabilidad:** Cada acción del sistema queda registrada con auditoría completa (OpenTelemetry).
- **Modularidad:** Componentes independientes que pueden evolucionar y escalarse por separado.
- **Resiliencia:** Tolerancia a fallos con circuit breakers y reintentos automáticos.

## 3. Componentes Principales

### 3.1 Frontend (Next.js)

```
frontend/
├── src/
│   ├── app/          → Rutas y páginas (App Router)
│   ├── components/   → Componentes React reutilizables
│   ├── lib/          → Lógica de negocio y utilidades
│   └── stores/       → Estado global (Zustand)
```

- **Framework:** Next.js 14+ con App Router
- **UI:** Tailwind CSS + shadcn/ui
- **Estado:** Zustand para estado global, React Query para cache de servidor
- **Comunicación:** REST + WebSocket para chat en tiempo real

### 3.2 Backend (FastAPI)

```
backend/
├── app/
│   ├── api/          → Endpoints REST y WebSocket
│   ├── core/         → Configuración, seguridad, middleware
│   ├── models/       → Modelos SQLAlchemy (ORM)
│   ├── schemas/      → Esquemas Pydantic (validación)
│   ├── services/     → Lógica de negocio
│   ├── rag/          → Motor RAG (retrieval, generación)
│   └── tools/        → Herramientas de auditoría
```

- **Framework:** FastAPI con soporte async
- **ORM:** SQLAlchemy 2.0+ con migraciones Alembic
- **Autenticación:** JWT con RBAC (roles por dirección técnica)
- **WebSocket:** Comunicación bidireccional para el chat

### 3.3 Motor RAG

El motor RAG es el corazón de CecilIA v2. Combina recuperación semántica de documentos con generación de respuestas contextualizadas.

**Flujo:**

```
Pregunta del auditor
       │
       ▼
┌──────────────────┐
│  Reformulación   │ ← Mejora la consulta para búsqueda
│  de consulta     │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Recuperación    │ ← pgvector (búsqueda semántica)
│  de documentos   │   + BM25 (búsqueda léxica)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Re-ranking      │ ← Cross-encoder para reordenar
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Generación      │ ← LLM con contexto recuperado
│  de respuesta    │
└──────┬───────────┘
       │
       ▼
  Respuesta con citas
```

**Almacenamiento vectorial:** PostgreSQL + pgvector (extensión)

**Modelo de embeddings:** `text-embedding-3-small` (configurable)

**Estrategia de chunking:**
- Tamaño: 1024 tokens con solapamiento de 128
- Respeta límites de párrafo y sección

### 3.4 Herramientas de Auditoría

| Herramienta | Descripción |
|-------------|-------------|
| `materialidad` | Cálculo de materialidad global y de ejecución según NIA 320 |
| `benford` | Análisis de Ley de Benford sobre registros financieros |
| `muestreo` | Cálculo de tamaños de muestra estadística |
| `hallazgo` | Generación asistida de hallazgos con estructura CCCE |
| `comparador` | Comparación de ejecución presupuestal vs. programación |

### 3.5 Base de Datos

```
PostgreSQL 16 + pgvector
├── usuarios           → Autenticación y perfiles
├── sesiones_chat      → Historial de conversaciones
├── mensajes           → Mensajes individuales
├── corpus_chunks      → Fragmentos del corpus con embeddings
├── auditorias         → Metadatos de procesos auditores
├── hallazgos          → Hallazgos generados
└── logs_auditoria     → Registro de actividad del sistema
```

### 3.6 Agente de Escritorio (Electron)

Aplicación de escritorio que permite:
- Acceso a archivos locales del auditor
- Vigilancia de cambios en carpetas de trabajo
- Integración con el backend vía WebSocket
- Bandeja del sistema para acceso rápido

## 4. Diagrama de Despliegue

```
┌─────────────────────────────────────────────────────┐
│                    Servidor CGR                      │
│                                                      │
│  ┌─────────┐   ┌──────────┐   ┌──────────────────┐ │
│  │  Nginx   │──▶│ Frontend │   │    Grafana        │ │
│  │ (proxy)  │   │ (Next.js)│   │   + Loki          │ │
│  └────┬─────┘   └──────────┘   └──────────────────┘ │
│       │                                              │
│       ▼                                              │
│  ┌──────────┐   ┌──────────┐   ┌──────────────────┐ │
│  │ Backend  │──▶│PostgreSQL│   │ OpenTelemetry     │ │
│  │ (FastAPI)│   │+ pgvector│   │   Collector       │ │
│  └──────────┘   └──────────┘   └──────────────────┘ │
│                                                      │
└─────────────────────────────────────────────────────┘
         ▲
         │ WebSocket + REST (HTTPS)
         ▼
┌──────────────────┐
│ Agente Escritorio│
│   (Electron)     │
└──────────────────┘
```

## 5. Seguridad

### 5.1 Autenticación y Autorización

- **JWT** con expiración configurable (por defecto 8 horas)
- **RBAC** con roles: ADMIN, DIRECTOR_DES, DIRECTOR_DVF, AUDITOR_DES, AUDITOR_DVF, LIDER_TECNICO, COORDINADOR, OBSERVADOR
- **Segregación por dirección:** Cada dirección técnica (DES, DVF) solo accede a sus procesos

### 5.2 Protección de Datos

- Cumplimiento de Ley 1581 de 2012 (Protección de Datos Personales)
- Cifrado TLS 1.3 en tránsito
- Contraseñas hasheadas con bcrypt (12 rondas)
- Logs de acceso con retención configurable

### 5.3 Infraestructura

- Firewall UFW con solo puertos 22, 80, 443 abiertos
- Fail2Ban para protección contra fuerza bruta
- Certificados SSL vía Let's Encrypt con renovación automática
- Rate limiting en Nginx

## 6. Observabilidad

- **Trazas:** OpenTelemetry con exportación a Grafana Loki
- **Métricas:** Dashboard de Grafana con tasas de solicitud, tiempos de respuesta, errores
- **Logs:** Estructurados en JSON, centralizados en Loki

## 7. Stack Tecnológico

| Capa | Tecnología |
|------|------------|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS |
| Backend | Python 3.12, FastAPI, SQLAlchemy 2, Pydantic v2 |
| Base de datos | PostgreSQL 16, pgvector |
| IA / LLM | OpenAI GPT-4o, Anthropic Claude, modelos locales (Ollama) |
| Embeddings | text-embedding-3-small |
| Contenedores | Docker, Docker Compose |
| Proxy | Nginx |
| Observabilidad | OpenTelemetry, Grafana, Loki |
| CI/CD | GitHub Actions |
| Escritorio | Electron |

---

*Documento de arquitectura — CecilIA v2 — Sprint 0 — Abril 2026*
