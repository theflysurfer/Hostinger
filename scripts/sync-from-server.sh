#!/bin/bash
#
# sync-from-server.sh
# Script pour synchroniser TOUTES les configurations du serveur srv759970 vers le repo local
#
# Usage: ./scripts/sync-from-server.sh
#

set -e

SERVER="automation@69.62.108.82"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVER_CONFIGS="$REPO_ROOT/server-configs"

echo "🔄 Synchronisation des configurations depuis srv759970.hstgr.cloud..."
echo "📂 Destination: $SERVER_CONFIGS"
echo ""

# Créer structure si elle n'existe pas
mkdir -p "$SERVER_CONFIGS"/{docker-compose,nginx/sites-available,nginx/snippets,dashy,systemd,scripts,certbot,env}

# ============================================================================
# 1. DOCKER COMPOSE FILES
# ============================================================================
echo "📦 [1/9] Synchronisation Docker Compose files..."

# Liste des services Docker avec docker-compose
SERVICES=(
    "dashy"
    "whisperx"
    "faster-whisper-queue"
    "monitoring"
    "ragflow"
    "neutts-air"
    "memvid"
    "videorag"
    "mkdocs"
)

for service in "${SERVICES[@]}"; do
    if ssh $SERVER "test -f /opt/$service/docker-compose.yml"; then
        echo "  ✓ Copying /opt/$service/docker-compose.yml → docker-compose/${service}.yml"
        scp $SERVER:/opt/$service/docker-compose.yml "$SERVER_CONFIGS/docker-compose/${service}.yml" 2>/dev/null || echo "  ⚠ Skipped $service (not found)"
    else
        echo "  ⚠ Skipped $service (not found)"
    fi
done

# Cas spéciaux avec des noms différents
if ssh $SERVER "test -f /opt/clemence/docker-compose.yml"; then
    echo "  ✓ Copying /opt/clemence/docker-compose.yml → docker-compose/clemence-wordpress.yml"
    scp $SERVER:/opt/clemence/docker-compose.yml "$SERVER_CONFIGS/docker-compose/clemence-wordpress.yml" 2>/dev/null
fi

echo ""

# ============================================================================
# 2. NGINX CONFIGURATIONS
# ============================================================================
echo "🌐 [2/9] Synchronisation Nginx configurations..."

# Sites disponibles
echo "  → Sites disponibles..."
ssh $SERVER "ls /etc/nginx/sites-available/" | while read -r site; do
    if [[ "$site" != "default" ]]; then
        echo "    ✓ $site"
        scp $SERVER:/etc/nginx/sites-available/$site "$SERVER_CONFIGS/nginx/sites-available/" 2>/dev/null
    fi
done

# Snippets réutilisables
echo "  → Snippets réutilisables..."
SNIPPETS=("basic-auth.conf" "proxy-headers.conf" "ssl-config.conf")
for snippet in "${SNIPPETS[@]}"; do
    if ssh $SERVER "test -f /etc/nginx/snippets/$snippet"; then
        echo "    ✓ $snippet"
        scp $SERVER:/etc/nginx/snippets/$snippet "$SERVER_CONFIGS/nginx/snippets/" 2>/dev/null
    fi
done

# nginx.conf global
echo "  → nginx.conf global..."
scp $SERVER:/etc/nginx/nginx.conf "$SERVER_CONFIGS/nginx/nginx.conf" 2>/dev/null

echo ""

# ============================================================================
# 3. DASHY CONFIGURATION
# ============================================================================
echo "📊 [3/9] Synchronisation Dashy configuration..."
scp $SERVER:/opt/dashy/conf.yml "$SERVER_CONFIGS/dashy/conf.yml" 2>/dev/null
echo "  ✓ conf.yml"
echo ""

# ============================================================================
# 4. SYSTEMD SERVICES
# ============================================================================
echo "⚙️  [4/9] Synchronisation Systemd services..."

# Services custom importants
SYSTEMD_SERVICES=("ollama" "docker")
for service in "${SYSTEMD_SERVICES[@]}"; do
    if ssh $SERVER "systemctl list-unit-files | grep -q $service.service"; then
        echo "  ✓ $service.service"
        scp $SERVER:/etc/systemd/system/$service.service "$SERVER_CONFIGS/systemd/" 2>/dev/null || \
        scp $SERVER:/lib/systemd/system/$service.service "$SERVER_CONFIGS/systemd/" 2>/dev/null || \
        echo "    ⚠ Could not copy $service.service"
    fi
done

# Liste tous les services enabled
echo "  → Liste des services enabled..."
ssh $SERVER "systemctl list-unit-files --state=enabled --no-pager" > "$SERVER_CONFIGS/systemd/enabled-services.txt"

echo ""

# ============================================================================
# 5. CERTBOT / SSL CERTIFICATES INFO
# ============================================================================
echo "🔒 [5/9] Synchronisation Certbot / SSL info..."
ssh $SERVER "certbot certificates 2>/dev/null" > "$SERVER_CONFIGS/certbot/certificates-list.txt" || echo "  ⚠ Certbot not available"
echo "  ✓ certificates-list.txt"
echo ""

# ============================================================================
# 6. DOCKER STATE
# ============================================================================
echo "🐳 [6/9] Export Docker state..."

# Conteneurs en cours d'exécution
ssh $SERVER "docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'" > "$SERVER_CONFIGS/docker-running.txt"
echo "  ✓ docker-running.txt ($(ssh $SERVER 'docker ps -q | wc -l') conteneurs)"

# Tous les conteneurs
ssh $SERVER "docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'" > "$SERVER_CONFIGS/docker-all.txt"
echo "  ✓ docker-all.txt"

# Images
ssh $SERVER "docker images --format 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}'" > "$SERVER_CONFIGS/docker-images.txt"
echo "  ✓ docker-images.txt"

# Volumes
ssh $SERVER "docker volume ls --format 'table {{.Name}}\t{{.Driver}}'" > "$SERVER_CONFIGS/docker-volumes.txt"
echo "  ✓ docker-volumes.txt"

# Networks
ssh $SERVER "docker network ls --format 'table {{.Name}}\t{{.Driver}}\t{{.Scope}}'" > "$SERVER_CONFIGS/docker-networks.txt"
echo "  ✓ docker-networks.txt"

echo ""

# ============================================================================
# 7. SCRIPTS SERVEUR
# ============================================================================
echo "📜 [7/9] Synchronisation scripts serveur..."

# Backup script si existe
if ssh $SERVER "test -f /root/scripts/backup-server-state.sh"; then
    scp $SERVER:/root/scripts/backup-server-state.sh "$SERVER_CONFIGS/scripts/" 2>/dev/null
    echo "  ✓ backup-server-state.sh"
fi

if ssh $SERVER "test -f /root/scripts/sync-configs-to-git.sh"; then
    scp $SERVER:/root/scripts/sync-configs-to-git.sh "$SERVER_CONFIGS/scripts/" 2>/dev/null
    echo "  ✓ sync-configs-to-git.sh"
fi

echo ""

# ============================================================================
# 8. VARIABLES D'ENVIRONNEMENT (SANS SECRETS)
# ============================================================================
echo "🔐 [8/9] Export variables d'environnement (masquées)..."

# .env files (sans les secrets)
ssh $SERVER "find /opt -name '.env' -type f 2>/dev/null" | while read -r env_file; do
    service_name=$(echo $env_file | cut -d'/' -f3)
    echo "  → $service_name/.env"
    # Copier en masquant les valeurs sensibles
    ssh $SERVER "cat $env_file | sed 's/=.*/=***MASKED***/g'" > "$SERVER_CONFIGS/env/${service_name}.env.template"
done

echo ""

# ============================================================================
# 9. METADATA & INVENTORY
# ============================================================================
echo "📋 [9/9] Export metadata & inventory..."

# Informations système
cat > "$SERVER_CONFIGS/server-info.txt" << EOF
# Server Information - $(date)
# Generated by sync-from-server.sh

## Hostname
$(ssh $SERVER "hostname")

## OS Version
$(ssh $SERVER "cat /etc/os-release | grep PRETTY_NAME")

## Uptime
$(ssh $SERVER "uptime")

## Docker Version
$(ssh $SERVER "docker --version")

## Docker Compose Version
$(ssh $SERVER "docker-compose --version")

## Nginx Version
$(ssh $SERVER "nginx -v 2>&1")

## Disk Usage
$(ssh $SERVER "df -h /")

## Memory
$(ssh $SERVER "free -h")

## Services Count
- Docker containers running: $(ssh $SERVER 'docker ps -q | wc -l')
- Docker containers total: $(ssh $SERVER 'docker ps -aq | wc -l')
- Nginx sites enabled: $(ssh $SERVER 'ls /etc/nginx/sites-enabled | wc -l')
- Systemd services enabled: $(ssh $SERVER 'systemctl list-unit-files --state=enabled | wc -l')
EOF

echo "  ✓ server-info.txt"

# Générer un inventaire complet
cat > "$SERVER_CONFIGS/INVENTORY.md" << EOF
# srv759970.hstgr.cloud - Inventory

**Last Updated:** $(date)
**Server:** srv759970.hstgr.cloud (69.62.108.82)

## Docker Compose Services

$(find "$SERVER_CONFIGS/docker-compose" -name "*.yml" -exec basename {} .yml \; | sort | awk '{print "- " $0}')

## Nginx Sites

$(find "$SERVER_CONFIGS/nginx/sites-available" -type f -exec basename {} \; | sort | awk '{print "- " $0}')

## Systemd Services

$(cat "$SERVER_CONFIGS/systemd/enabled-services.txt" | grep enabled | awk '{print "- " $1}' | head -20)

## SSL Certificates

\`\`\`
$(cat "$SERVER_CONFIGS/certbot/certificates-list.txt" 2>/dev/null || echo "N/A")
\`\`\`

## Docker State

**Running Containers:** $(ssh $SERVER 'docker ps -q | wc -l')

\`\`\`
$(cat "$SERVER_CONFIGS/docker-running.txt")
\`\`\`
EOF

echo "  ✓ INVENTORY.md"

echo ""
echo "============================================================================"
echo "✅ Synchronisation terminée!"
echo "============================================================================"
echo ""
echo "📊 Résumé:"
echo "  - Docker Compose: $(find "$SERVER_CONFIGS/docker-compose" -name "*.yml" 2>/dev/null | wc -l) fichiers"
echo "  - Nginx Sites: $(find "$SERVER_CONFIGS/nginx/sites-available" -type f 2>/dev/null | wc -l) sites"
echo "  - Nginx Snippets: $(find "$SERVER_CONFIGS/nginx/snippets" -type f 2>/dev/null | wc -l) snippets"
echo "  - Systemd Services: $(find "$SERVER_CONFIGS/systemd" -name "*.service" 2>/dev/null | wc -l) fichiers"
echo ""
echo "📂 Tous les fichiers sont dans: $SERVER_CONFIGS"
echo ""
echo "Prochaines étapes:"
echo "  1. Vérifier les fichiers: ls -la $SERVER_CONFIGS"
echo "  2. Commit dans Git: git add server-configs/ && git commit -m 'feat: sync server configs'"
echo "  3. Lire la doc: cat docs/infrastructure/backup-restore.md"
echo ""
