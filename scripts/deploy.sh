#!/usr/bin/env bash
# ============================================================================
# CecilIA v2 — Sistema de IA para Control Fiscal
# Contraloría General de la República de Colombia
#
# Archivo : deploy.sh
# Propósito: Script de despliegue — pull, build, migraciones, reinicio y health-check
# Sprint  : 0
# Autor   : Equipo Técnico CecilIA — CD-TIC-CGR
# Fecha   : Abril 2026
# ============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Variables de configuración
# ---------------------------------------------------------------------------
APP_NAME="cecilia-v2"
BRANCH="${DEPLOY_BRANCH:-main}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
HEALTH_URL="${HEALTH_URL:-http://localhost:8000/api/v1/health}"
HEALTH_RETRIES=15
HEALTH_INTERVAL=4    # segundos entre reintentos
LOG_FILE="/var/log/${APP_NAME}/deploy_$(date +%Y%m%d_%H%M%S).log"

# ---------------------------------------------------------------------------
# Colores para salida
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------
info()  { echo -e "${GREEN}[INFO]${NC}  $(date '+%H:%M:%S') $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $(date '+%H:%M:%S') $*"; }
error() { echo -e "${RED}[ERROR]${NC} $(date '+%H:%M:%S') $*"; }

check_dependency() {
    if ! command -v "$1" &>/dev/null; then
        error "Dependencia requerida no encontrada: $1"
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# Verificar dependencias
# ---------------------------------------------------------------------------
info "Verificando dependencias …"
for dep in git docker docker-compose curl; do
    check_dependency "$dep"
done

# ---------------------------------------------------------------------------
# Crear directorio de logs
# ---------------------------------------------------------------------------
mkdir -p "$(dirname "$LOG_FILE")"

# ---------------------------------------------------------------------------
# 1. Obtener código más reciente
# ---------------------------------------------------------------------------
info "Obteniendo código más reciente de la rama '$BRANCH' …"
git fetch origin "$BRANCH" 2>&1 | tee -a "$LOG_FILE"
git checkout "$BRANCH" 2>&1 | tee -a "$LOG_FILE"
git pull origin "$BRANCH" 2>&1 | tee -a "$LOG_FILE"
COMMIT=$(git rev-parse --short HEAD)
info "Código actualizado al commit: $COMMIT"

# ---------------------------------------------------------------------------
# 2. Construir imágenes Docker
# ---------------------------------------------------------------------------
info "Construyendo imágenes Docker …"
docker-compose -f "$COMPOSE_FILE" build --parallel 2>&1 | tee -a "$LOG_FILE"
info "Imágenes construidas exitosamente."

# ---------------------------------------------------------------------------
# 3. Ejecutar migraciones de base de datos
# ---------------------------------------------------------------------------
info "Ejecutando migraciones de base de datos …"
docker-compose -f "$COMPOSE_FILE" run --rm backend \
    alembic upgrade head 2>&1 | tee -a "$LOG_FILE"
info "Migraciones aplicadas."

# ---------------------------------------------------------------------------
# 4. Reiniciar servicios
# ---------------------------------------------------------------------------
info "Reiniciando servicios …"
docker-compose -f "$COMPOSE_FILE" down --timeout 30 2>&1 | tee -a "$LOG_FILE"
docker-compose -f "$COMPOSE_FILE" up -d 2>&1 | tee -a "$LOG_FILE"
info "Servicios reiniciados."

# ---------------------------------------------------------------------------
# 5. Health-check
# ---------------------------------------------------------------------------
info "Esperando a que el servicio esté disponible ($HEALTH_URL) …"
HEALTHY=false
for i in $(seq 1 "$HEALTH_RETRIES"); do
    if curl -sf "$HEALTH_URL" > /dev/null 2>&1; then
        HEALTHY=true
        break
    fi
    warn "  Intento $i/$HEALTH_RETRIES — servicio no disponible, reintentando en ${HEALTH_INTERVAL}s …"
    sleep "$HEALTH_INTERVAL"
done

if [ "$HEALTHY" = true ]; then
    info "=========================================="
    info "DESPLIEGUE EXITOSO"
    info "  Rama   : $BRANCH"
    info "  Commit : $COMMIT"
    info "  Fecha  : $(date '+%Y-%m-%d %H:%M:%S')"
    info "  Log    : $LOG_FILE"
    info "=========================================="
    exit 0
else
    error "=========================================="
    error "DESPLIEGUE FALLIDO — El servicio no responde"
    error "  Revise los logs: docker-compose -f $COMPOSE_FILE logs"
    error "  Log de despliegue: $LOG_FILE"
    error "=========================================="

    # Intentar rollback
    warn "Intentando rollback al estado anterior …"
    docker-compose -f "$COMPOSE_FILE" down --timeout 10 2>&1 | tee -a "$LOG_FILE"
    git checkout HEAD~1 2>&1 | tee -a "$LOG_FILE"
    docker-compose -f "$COMPOSE_FILE" up -d 2>&1 | tee -a "$LOG_FILE"
    warn "Rollback ejecutado. Verifique el estado del sistema."

    exit 1
fi
