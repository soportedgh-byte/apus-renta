# CecilIA v2 — Sistema de Inteligencia Artificial para Control Fiscal

> **Contraloría General de la República de Colombia (CGR)**
> Contraloría Delegada para el Sector TIC (CD-TIC)

---

## Descripción

**CecilIA v2** es una plataforma de inteligencia artificial diseñada para apoyar las funciones de control fiscal de la Contraloría General de la República de Colombia. El sistema integra modelos de lenguaje de gran escala (LLM), recuperación aumentada por generación (RAG) y flujos de trabajo especializados para automatizar y asistir en:

- **Análisis de hallazgos fiscales** mediante procesamiento de lenguaje natural.
- **Generación de informes** con base en normatividad vigente.
- **Consulta inteligente** del corpus normativo y jurisprudencial de la CGR.
- **Revisión asistida de APUS de renta** (Análisis de Precios Unitarios).
- **Agente de escritorio** para captura y análisis de información desde aplicaciones locales.

El sistema está diseñado para funcionar con múltiples proveedores LLM (Claude, Gemini, Groq, Ollama, vLLM), lo que permite operar tanto en la nube como completamente offline en la infraestructura propia de la CGR.

---

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| **Frontend** | Next.js 15, React 19, TypeScript, Tailwind CSS, shadcn/ui |
| **Backend** | Python 3.12+, FastAPI, SQLAlchemy 2.0, Alembic |
| **Base de datos** | PostgreSQL 16 + pgvector |
| **Caché / Colas** | Redis 8 |
| **LLM** | Claude (Anthropic), Gemini (Google), Groq, Ollama, vLLM |
| **Embeddings** | nomic-embed-text (via Ollama) |
| **Infraestructura** | Docker, Docker Compose |
| **Observabilidad** | OpenTelemetry, Loki, Grafana |
| **Desktop Agent** | Electron (para captura local) |

---

## Prerrequisitos

Antes de iniciar, asegúrese de tener instalado:

- **Docker** >= 24.0 y **Docker Compose** >= 2.20
- **Node.js** >= 22 (para desarrollo local del frontend)
- **Python** >= 3.12 (para desarrollo local del backend)
- **Git** >= 2.40

Para desarrollo sin Docker, adicionalmente:

- **PostgreSQL** 16 con extensión `pgvector`
- **Redis** 8+
- **Ollama** (opcional, para LLM y embeddings locales)

---

## Inicio Rápido

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio> cecilia-v2
cd cecilia-v2
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con las credenciales y configuración requerida
```

### 3. Levantar todos los servicios con Docker

```bash
# Producción
docker compose up -d

# Desarrollo (con recarga en caliente)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### 4. Verificar que los servicios estén activos

```bash
# Estado de los contenedores
docker compose ps

# Salud del backend
curl http://localhost:8000/api/v1/health

# Frontend
# Abrir http://localhost:3000 en el navegador
```

---

## Migraciones y Datos Iniciales

### Ejecutar migraciones de base de datos

```bash
# Desde el contenedor del backend
docker compose exec backend alembic upgrade head
```

### Crear usuarios semilla (seed)

```bash
docker compose exec backend python -m scripts.seed_users
```

Este comando crea los usuarios iniciales para pruebas y desarrollo.

---

## Cambiar Proveedor LLM

CecilIA v2 soporta múltiples proveedores LLM. Para cambiar de proveedor, edite el archivo `.env` y descomente el bloque correspondiente:

### Claude (Anthropic) — Recomendado para MVP

```env
LLM_BASE_URL=https://api.anthropic.com/v1
LLM_MODEL=claude-sonnet-4-20250514
LLM_API_KEY=sk-ant-XXXXXXXX
```

### Gemini (Google)

```env
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
LLM_MODEL=gemini-2.0-flash
LLM_API_KEY=tu_key_google
```

### Groq (Gratuito)

```env
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.3-70b-versatile
LLM_API_KEY=gsk_XXXXXXXX
```

### Ollama (Local, sin conexión a internet)

```env
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen3:14b
LLM_API_KEY=ollama
```

### vLLM (Producción CGR con GPU)

```env
LLM_BASE_URL=http://gpu-server:8000/v1
LLM_MODEL=Qwen/Qwen3-32B
LLM_API_KEY=no-key
```

Después de cambiar el proveedor, reinicie el backend:

```bash
docker compose restart backend
```

---

## Estructura del Proyecto

```
cecilia-v2/
├── backend/              # API REST — FastAPI (Python 3.12)
│   ├── app/              #   Código fuente principal
│   │   ├── api/          #     Rutas y endpoints
│   │   ├── core/         #     Configuración, seguridad, LLM
│   │   ├── models/       #     Modelos SQLAlchemy
│   │   ├── schemas/      #     Esquemas Pydantic
│   │   ├── services/     #     Lógica de negocio
│   │   └── main.py       #     Punto de entrada FastAPI
│   ├── alembic/          #   Migraciones de base de datos
│   ├── tests/            #   Pruebas unitarias e integración
│   ├── Dockerfile        #   Imagen Docker del backend
│   └── requirements.txt  #   Dependencias Python
│
├── frontend/             # Interfaz web — Next.js 15 (React 19)
│   ├── src/              #   Código fuente
│   │   ├── app/          #     App Router (páginas y layouts)
│   │   ├── components/   #     Componentes React
│   │   ├── lib/          #     Utilidades y cliente API
│   │   └── styles/       #     Estilos globales
│   ├── public/           #   Archivos estáticos
│   ├── Dockerfile        #   Imagen Docker del frontend
│   └── package.json      #   Dependencias Node.js
│
├── infra/                # Infraestructura como código
│   ├── k8s/              #   Manifiestos de Kubernetes
│   ├── nginx/            #   Configuración del proxy inverso
│   └── otel/             #   Configuración de OpenTelemetry
│
├── docs/                 # Documentación del proyecto
│   ├── arquitectura/     #   Diagramas y decisiones (ADR)
│   ├── api/              #   Especificación OpenAPI
│   └── manuales/         #   Manuales de usuario y operación
│
├── scripts/              # Scripts de utilidad
│   ├── seed_users.py     #   Crear usuarios iniciales
│   ├── ingest_corpus.py  #   Ingestión de documentos al RAG
│   └── backup_db.sh      #   Respaldo de base de datos
│
├── corpus/               # Corpus normativo para RAG
│   ├── normatividad/     #   Leyes, decretos, resoluciones
│   └── jurisprudencia/   #   Sentencias y conceptos
│
├── desktop-agent/        # Agente de escritorio (Electron)
│
├── apus-renta/           # Módulo APUS de Renta
│
├── .env.example          # Plantilla de variables de entorno
├── .gitignore            # Archivos ignorados por Git
├── docker-compose.yml    # Composición Docker (producción)
├── docker-compose.dev.yml # Composición Docker (desarrollo)
├── CHANGELOG.md          # Registro de cambios
├── LICENSE               # Licencia de propiedad intelectual
└── README.md             # Este archivo
```

---

## Roles del Sistema

CecilIA v2 implementa un sistema de roles con los siguientes perfiles:

| Rol | Descripción | Permisos principales |
|-----|-------------|---------------------|
| **admin** | Administrador del sistema | Gestión completa de usuarios, configuración del sistema, acceso a todos los módulos |
| **auditor_senior** | Auditor fiscal senior | Crear y revisar hallazgos, generar informes, acceso completo al RAG |
| **auditor** | Auditor fiscal | Consultar el RAG, crear borradores de hallazgos, revisar APUS |
| **consultor** | Consultor externo | Acceso de solo lectura al RAG y consultas limitadas |
| **viewer** | Visualizador | Acceso de solo lectura a informes y dashboards |

---

## Credenciales de Prueba

Las siguientes credenciales se crean automáticamente con el script `seed_users`:

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| `admin@cgr.gov.co` | `Admin2026*` | admin |
| `auditor.senior@cgr.gov.co` | `Auditor2026*` | auditor_senior |
| `auditor@cgr.gov.co` | `Auditor2026*` | auditor |
| `consultor@cgr.gov.co` | `Consultor2026*` | consultor |
| `viewer@cgr.gov.co` | `Viewer2026*` | viewer |

> **IMPORTANTE:** Estas credenciales son exclusivamente para desarrollo y pruebas. Deben eliminarse o modificarse antes de cualquier despliegue en producción.

---

## Guía de Desarrollo

### Backend (FastAPI)

```bash
cd backend

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Ejecutar servidor de desarrollo
uvicorn app.main:app --reload --port 8000

# Ejecutar pruebas
pytest -v

# Verificar calidad de código
ruff check app/
mypy app/
```

### Frontend (Next.js)

```bash
cd frontend

# Instalar dependencias
npm install

# Ejecutar servidor de desarrollo
npm run dev

# Ejecutar pruebas
npm test

# Verificar linting
npm run lint

# Compilar para producción
npm run build
```

### Ingestión de Documentos (RAG)

```bash
# Colocar documentos PDF/DOCX en corpus/normatividad/ o corpus/jurisprudencia/
# Ejecutar el script de ingestión
docker compose exec backend python -m scripts.ingest_corpus
```

---

## Aviso Legal

Este software es propiedad exclusiva de la **Contraloría General de la República de Colombia (CGR)**, desarrollado por la **Contraloría Delegada para el Sector TIC (CD-TIC)**.

Queda prohibida su reproducción, distribución, modificación o uso no autorizado sin el consentimiento expreso y por escrito de la CGR.

- **Clasificación:** USO INTERNO — RESERVADO
- **Marco legal:** Constitución Política de Colombia, artículos 267-268; Ley 42 de 1993; Ley 610 de 2000; Decreto 403 de 2020.

---

*CecilIA v2 — Inteligencia Artificial al servicio del Control Fiscal*
*Contraloría General de la República de Colombia*
