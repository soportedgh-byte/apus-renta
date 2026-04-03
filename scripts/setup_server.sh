#!/usr/bin/env bash
# ============================================================================
# CecilIA v2 — Sistema de IA para Control Fiscal
# Contraloría General de la República de Colombia
#
# Archivo : setup_server.sh
# Propósito: Preparación inicial del servidor — Docker, firewall, SSL e inicialización de BD
# Sprint  : 0
# Autor   : Equipo Técnico CecilIA — CD-TIC-CGR
# Fecha   : Abril 2026
# ============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Variables de configuración
# ---------------------------------------------------------------------------
APP_DOMAIN="${APP_DOMAIN:-cecilia.contraloria.gov.co}"
CERTBOT_EMAIL="${CERTBOT_EMAIL:-sistemas@contraloria.gov.co}"
POSTGRES_VERSION="${POSTGRES_VERSION:-16}"
DB_NAME="${DB_NAME:-cecilia}"
DB_USER="${DB_USER:-cecilia_app}"
ALLOWED_SSH_PORT="${ALLOWED_SSH_PORT:-22}"

# ---------------------------------------------------------------------------
# Colores
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC}  $(date '+%H:%M:%S') $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $(date '+%H:%M:%S') $*"; }
error() { echo -e "${RED}[ERROR]${NC} $(date '+%H:%M:%S') $*"; }

# ---------------------------------------------------------------------------
# Verificar que se ejecuta como root
# ---------------------------------------------------------------------------
if [ "$(id -u)" -ne 0 ]; then
    error "Este script debe ejecutarse como root (sudo)."
    exit 1
fi

info "============================================="
info "Configuración inicial del servidor CecilIA v2"
info "  Dominio : $APP_DOMAIN"
info "  BD      : $DB_NAME"
info "============================================="

# ---------------------------------------------------------------------------
# 1. Actualizar el sistema
# ---------------------------------------------------------------------------
info "Actualizando paquetes del sistema …"
apt-get update -y
apt-get upgrade -y
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    ufw \
    fail2ban \
    unzip \
    git \
    htop

# ---------------------------------------------------------------------------
# 2. Instalar Docker
# ---------------------------------------------------------------------------
if command -v docker &>/dev/null; then
    info "Docker ya está instalado: $(docker --version)"
else
    info "Instalando Docker …"
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
        | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
        https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
        | tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io
    systemctl enable docker
    systemctl start docker
    info "Docker instalado: $(docker --version)"
fi

# ---------------------------------------------------------------------------
# 3. Instalar Docker Compose
# ---------------------------------------------------------------------------
if command -v docker-compose &>/dev/null; then
    info "Docker Compose ya está instalado: $(docker-compose --version)"
else
    info "Instalando Docker Compose …"
    COMPOSE_VERSION="2.27.0"
    curl -fsSL "https://github.com/docker/compose/releases/download/v${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    info "Docker Compose instalado: $(docker-compose --version)"
fi

# ---------------------------------------------------------------------------
# 4. Configurar firewall (UFW)
# ---------------------------------------------------------------------------
info "Configurando firewall (UFW) …"
ufw default deny incoming
ufw default allow outgoing

# SSH
ufw allow "$ALLOWED_SSH_PORT"/tcp comment "SSH"

# HTTP / HTTPS
ufw allow 80/tcp comment "HTTP"
ufw allow 443/tcp comment "HTTPS"

# Habilitar sin preguntar
echo "y" | ufw enable
ufw status verbose
info "Firewall configurado."

# ---------------------------------------------------------------------------
# 5. Configurar Fail2Ban
# ---------------------------------------------------------------------------
info "Configurando Fail2Ban …"
cat > /etc/fail2ban/jail.local <<'JAIL'
[DEFAULT]
bantime  = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port    = ssh
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true
port    = http,https
logpath = /var/log/nginx/error.log
JAIL

systemctl enable fail2ban
systemctl restart fail2ban
info "Fail2Ban configurado."

# ---------------------------------------------------------------------------
# 6. Configurar certificados SSL con Let's Encrypt
# ---------------------------------------------------------------------------
info "Instalando Certbot para SSL …"
apt-get install -y certbot

if [ -d "/etc/letsencrypt/live/$APP_DOMAIN" ]; then
    info "Certificado SSL ya existe para $APP_DOMAIN."
else
    info "Solicitando certificado SSL para $APP_DOMAIN …"
    certbot certonly \
        --standalone \
        --non-interactive \
        --agree-tos \
        --email "$CERTBOT_EMAIL" \
        -d "$APP_DOMAIN" || {
        warn "No se pudo obtener el certificado SSL automáticamente."
        warn "Puede ejecutar manualmente: certbot certonly -d $APP_DOMAIN"
    }
fi

# Configurar renovación automática
info "Configurando renovación automática de certificados …"
cat > /etc/cron.d/certbot-renew <<'CRON'
# Renovación automática de certificados SSL — CecilIA v2
0 3 * * * root certbot renew --quiet --post-hook "docker-compose -f /opt/cecilia-v2/docker-compose.yml restart nginx"
CRON
info "Renovación SSL automática configurada."

# ---------------------------------------------------------------------------
# 7. Crear directorio de la aplicación
# ---------------------------------------------------------------------------
APP_DIR="/opt/cecilia-v2"
info "Creando directorio de la aplicación en $APP_DIR …"
mkdir -p "$APP_DIR"
mkdir -p /var/log/cecilia-v2

# ---------------------------------------------------------------------------
# 8. Inicializar base de datos PostgreSQL (vía Docker)
# ---------------------------------------------------------------------------
info "Inicializando base de datos PostgreSQL …"

# Generar contraseña aleatoria si no existe
DB_PASSWORD_FILE="$APP_DIR/.db_password"
if [ ! -f "$DB_PASSWORD_FILE" ]; then
    DB_PASSWORD=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32)
    echo "$DB_PASSWORD" > "$DB_PASSWORD_FILE"
    chmod 600 "$DB_PASSWORD_FILE"
    info "Contraseña de BD generada y almacenada en $DB_PASSWORD_FILE"
else
    DB_PASSWORD=$(cat "$DB_PASSWORD_FILE")
    info "Usando contraseña de BD existente."
fi

# Crear red Docker si no existe
docker network create cecilia-net 2>/dev/null || true

# Levantar PostgreSQL con pgvector
docker run -d \
    --name cecilia-postgres \
    --network cecilia-net \
    --restart unless-stopped \
    -e POSTGRES_DB="$DB_NAME" \
    -e POSTGRES_USER="$DB_USER" \
    -e POSTGRES_PASSWORD="$DB_PASSWORD" \
    -v cecilia-pgdata:/var/lib/postgresql/data \
    -p 127.0.0.1:5432:5432 \
    pgvector/pgvector:pg${POSTGRES_VERSION} 2>/dev/null || {
    warn "El contenedor cecilia-postgres ya existe. Se omite la creación."
}

info "Esperando a que PostgreSQL esté listo …"
for i in $(seq 1 15); do
    if docker exec cecilia-postgres pg_isready -U "$DB_USER" &>/dev/null; then
        info "PostgreSQL listo."
        break
    fi
    sleep 2
done

# Habilitar extensión pgvector
docker exec cecilia-postgres \
    psql -U "$DB_USER" -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null || true

info "Base de datos inicializada con extensión pgvector."

# ---------------------------------------------------------------------------
# 9. Generar archivo .env de referencia
# ---------------------------------------------------------------------------
ENV_FILE="$APP_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    info "Generando archivo .env …"
    cat > "$ENV_FILE" <<ENVFILE
# CecilIA v2 — Variables de entorno
# Generado automáticamente el $(date '+%Y-%m-%d %H:%M:%S')

# Base de datos
DATABASE_URL=postgresql+psycopg2://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}

# JWT
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=480

# LLM
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
EMBEDDING_MODEL=text-embedding-3-small

# Aplicación
APP_ENV=production
APP_DOMAIN=${APP_DOMAIN}
LOG_LEVEL=INFO
ENVFILE
    chmod 600 "$ENV_FILE"
    info "Archivo .env generado en $ENV_FILE"
else
    info "Archivo .env ya existe. No se sobrescribe."
fi

# ---------------------------------------------------------------------------
# Resumen
# ---------------------------------------------------------------------------
info "============================================="
info "CONFIGURACIÓN DEL SERVIDOR COMPLETADA"
info ""
info "  Docker         : $(docker --version)"
info "  Docker Compose : $(docker-compose --version)"
info "  Firewall       : UFW activo (puertos $ALLOWED_SSH_PORT, 80, 443)"
info "  SSL            : Certbot instalado para $APP_DOMAIN"
info "  Base de datos  : PostgreSQL $POSTGRES_VERSION + pgvector"
info "  Directorio app : $APP_DIR"
info "  .env           : $ENV_FILE"
info ""
info "Próximos pasos:"
info "  1. Copiar el código fuente a $APP_DIR"
info "  2. Verificar las variables en $ENV_FILE"
info "  3. Ejecutar: ./scripts/deploy.sh"
info "============================================="
