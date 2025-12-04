#!/bin/bash
#
# backup-server-state.sh
# Script de backup automatique de l'état du serveur srv759970
# À déployer sur le serveur dans /root/scripts/
#
# Usage: ./backup-server-state.sh
# Cron: 0 3 * * * /root/scripts/backup-server-state.sh >> /var/log/backup-cron.log 2>&1
#

set -e

BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="server-state-$DATE"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

# Retention: nombre de jours à garder
RETENTION_DAYS=30

echo "============================================================================"
echo "🔄 Backup Server State - $(date)"
echo "============================================================================"
echo ""

# Créer répertoire de backup
mkdir -p "$BACKUP_PATH"/{configs,docker,volumes,databases}

echo "📂 Backup directory: $BACKUP_PATH"
echo ""

# ============================================================================
# 1. CONFIGURATIONS
# ============================================================================
echo "[1/6] 📋 Backup configurations..."

# Docker Compose files
echo "  → Docker Compose files..."
find /opt -name "docker-compose.yml" -exec cp --parents {} "$BACKUP_PATH/configs/" \; 2>/dev/null
COMPOSE_COUNT=$(find "$BACKUP_PATH/configs" -name "docker-compose.yml" | wc -l)
echo "    ✓ $COMPOSE_COUNT fichiers"

# Nginx configs
echo "  → Nginx configurations..."
cp -r /etc/nginx/sites-available "$BACKUP_PATH/configs/nginx-sites/" 2>/dev/null
cp -r /etc/nginx/snippets "$BACKUP_PATH/configs/nginx-snippets/" 2>/dev/null
cp /etc/nginx/nginx.conf "$BACKUP_PATH/configs/" 2>/dev/null
echo "    ✓ Nginx sauvegardé"

# Dashy config
echo "  → Dashy configuration..."
if [ -f /opt/dashy/conf.yml ]; then
    cp /opt/dashy/conf.yml "$BACKUP_PATH/configs/dashy-conf.yml"
    echo "    ✓ Dashy conf.yml"
fi

# .env files (ATTENTION: contient des secrets!)
echo "  → .env files..."
find /opt -name ".env" -exec cp --parents {} "$BACKUP_PATH/configs/" \; 2>/dev/null
ENV_COUNT=$(find "$BACKUP_PATH/configs" -name ".env" | wc -l)
echo "    ✓ $ENV_COUNT fichiers .env"

echo ""

# ============================================================================
# 2. DOCKER STATE
# ============================================================================
echo "[2/6] 🐳 Export Docker state..."

# Conteneurs running
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' > "$BACKUP_PATH/docker/containers-running.txt"
echo "  ✓ Conteneurs running: $(docker ps -q | wc -l)"

# Tous les conteneurs
docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}' > "$BACKUP_PATH/docker/containers-all.txt"
echo "  ✓ Conteneurs total: $(docker ps -aq | wc -l)"

# Images
docker images --format 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}' > "$BACKUP_PATH/docker/images.txt"
echo "  ✓ Images: $(docker images -q | wc -l)"

# Volumes
docker volume ls --format 'table {{.Name}}\t{{.Driver}}' > "$BACKUP_PATH/docker/volumes.txt"
echo "  ✓ Volumes: $(docker volume ls -q | wc -l)"

# Networks
docker network ls --format 'table {{.Name}}\t{{.Driver}}\t{{.Scope}}' > "$BACKUP_PATH/docker/networks.txt"
echo "  ✓ Networks"

echo ""

# ============================================================================
# 3. DOCKER VOLUMES CRITIQUES
# ============================================================================
echo "[3/6] 💾 Backup Docker volumes critiques..."

# Liste des volumes à backup
CRITICAL_VOLUMES=(
    "dashy_icons"
    "grafana_data"
    "prometheus_data"
    "loki_data"
)

for volume in "${CRITICAL_VOLUMES[@]}"; do
    if docker volume ls -q | grep -q "^${volume}$"; then
        echo "  → $volume..."
        docker run --rm \
            -v ${volume}:/volume \
            -v $BACKUP_PATH/volumes:/backup \
            alpine tar czf /backup/${volume}.tar.gz -C /volume . 2>/dev/null || echo "    ⚠ Erreur backup $volume"

        if [ -f "$BACKUP_PATH/volumes/${volume}.tar.gz" ]; then
            SIZE=$(du -h "$BACKUP_PATH/volumes/${volume}.tar.gz" | cut -f1)
            echo "    ✓ $SIZE"
        fi
    else
        echo "  ⚠ Volume $volume non trouvé, skip"
    fi
done

echo ""

# ============================================================================
# 4. BASES DE DONNÉES
# ============================================================================
echo "[4/6] 🗄️  Backup bases de données..."

# MySQL/MariaDB (Clemence WordPress)
if docker ps --format '{{.Names}}' | grep -q "mysql-clemence"; then
    echo "  → MySQL (Clemence WordPress)..."
    docker exec mysql-clemence mysqldump -u clemence_user -pClemenceDB2025 clemence_db \
        > "$BACKUP_PATH/databases/clemence_db.sql" 2>/dev/null || echo "    ⚠ Erreur dump MySQL"
    if [ -f "$BACKUP_PATH/databases/clemence_db.sql" ]; then
        SIZE=$(du -h "$BACKUP_PATH/databases/clemence_db.sql" | cut -f1)
        echo "    ✓ $SIZE"
    fi
fi

# PostgreSQL (Strapi)
if docker ps --format '{{.Names}}' | grep -q "postgres"; then
    echo "  → PostgreSQL (Strapi)..."
    # Adapter selon tes configs Strapi
    echo "    ⚠ À implémenter selon config Strapi"
fi

echo ""

# ============================================================================
# 5. SYSTEMD & SERVICES
# ============================================================================
echo "[5/6] ⚙️  Export systemd services..."

# Services enabled
systemctl list-unit-files --state=enabled --no-pager > "$BACKUP_PATH/configs/systemd-enabled.txt"
echo "  ✓ Services enabled: $(systemctl list-unit-files --state=enabled | wc -l)"

# Copier les .service files custom
mkdir -p "$BACKUP_PATH/configs/systemd/"
cp /etc/systemd/system/*.service "$BACKUP_PATH/configs/systemd/" 2>/dev/null || true

# Ollama service si existe
if systemctl list-unit-files | grep -q ollama.service; then
    cp /etc/systemd/system/ollama.service "$BACKUP_PATH/configs/systemd/" 2>/dev/null || \
    cp /lib/systemd/system/ollama.service "$BACKUP_PATH/configs/systemd/" 2>/dev/null || true
    echo "  ✓ ollama.service"
fi

echo ""

# ============================================================================
# 6. METADATA
# ============================================================================
echo "[6/6] 📊 Export metadata..."

# Server info
cat > "$BACKUP_PATH/server-info.txt" << EOF
# Backup Metadata
Date: $(date)
Hostname: $(hostname)
OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)
Kernel: $(uname -r)
Uptime: $(uptime -p)

# Docker
Docker Version: $(docker --version)
Docker Compose Version: $(docker-compose --version)

# Nginx
Nginx Version: $(nginx -v 2>&1)

# System
Disk Usage:
$(df -h /)

Memory:
$(free -h)

# Containers Running
$(docker ps --format '{{.Names}}' | wc -l) conteneurs

# Services
$(systemctl list-units --type=service --state=running --no-pager | wc -l) services systemd running
EOF

echo "  ✓ server-info.txt"

# Certbot certificates
certbot certificates > "$BACKUP_PATH/configs/certbot-certificates.txt" 2>/dev/null || \
    echo "Certbot not available" > "$BACKUP_PATH/configs/certbot-certificates.txt"
echo "  ✓ certbot-certificates.txt"

echo ""

# ============================================================================
# COMPRESSION
# ============================================================================
echo "📦 Compression du backup..."

cd "$BACKUP_DIR"
tar czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME/" 2>/dev/null

if [ -f "${BACKUP_NAME}.tar.gz" ]; then
    BACKUP_SIZE=$(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)
    echo "  ✓ ${BACKUP_NAME}.tar.gz ($BACKUP_SIZE)"

    # Supprimer le dossier non compressé
    rm -rf "$BACKUP_NAME"
else
    echo "  ❌ Erreur de compression"
    exit 1
fi

echo ""

# ============================================================================
# CLEANUP OLD BACKUPS
# ============================================================================
echo "🗑️  Nettoyage des anciens backups (>$RETENTION_DAYS jours)..."

DELETED_COUNT=$(find "$BACKUP_DIR" -name "server-state-*.tar.gz" -mtime +$RETENTION_DAYS -delete -print | wc -l)
if [ $DELETED_COUNT -gt 0 ]; then
    echo "  ✓ $DELETED_COUNT backup(s) supprimé(s)"
else
    echo "  ℹ️  Aucun ancien backup à supprimer"
fi

echo ""

# ============================================================================
# SUMMARY
# ============================================================================
echo "============================================================================"
echo "✅ Backup terminé avec succès!"
echo "============================================================================"
echo ""
echo "📊 Résumé:"
echo "  • Fichier: ${BACKUP_NAME}.tar.gz"
echo "  • Taille: $BACKUP_SIZE"
echo "  • Emplacement: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
echo ""
echo "📋 Contenu:"
echo "  • Docker Compose: $COMPOSE_COUNT fichiers"
echo "  • .env files: $ENV_COUNT fichiers"
echo "  • Conteneurs: $(docker ps -q | wc -l) running / $(docker ps -aq | wc -l) total"
echo "  • Volumes backupés: ${#CRITICAL_VOLUMES[@]} volumes"
echo "  • Nginx configs: ✓"
echo "  • Systemd services: ✓"
echo ""
echo "💾 Backups disponibles:"
ls -lh "$BACKUP_DIR"/server-state-*.tar.gz | tail -5
echo ""
echo "Pour restaurer:"
echo "  tar xzf $BACKUP_DIR/${BACKUP_NAME}.tar.gz -C /tmp/"
echo "  # Puis copier manuellement les fichiers nécessaires"
echo ""
