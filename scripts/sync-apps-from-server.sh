#!/bin/bash
# Script de synchronisation des applications depuis le serveur
# Usage: ./sync-apps-from-server.sh [app-name|all]

set -e

SERVER="root@69.62.108.82"
REMOTE_BASE="/opt"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_BASE="$SCRIPT_DIR/../apps"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Mapping apps prioritaires: nom_serveur:catégorie_locale:nom_local
declare -A APPS=(
    ["downto40"]="11-dashboards:energie-40eur-dashboard"
    ["dashy"]="12-monitoring:dashy"
    ["faster-whisper-queue"]="02-ai-transcription:whisperx"
    ["wordpress-clemence"]="01-wordpress:clemence"
    ["nextcloud"]="08-collaboration:nextcloud"
    ["ragflow"]="04-ai-rag:ragflow"
    ["paperless-ngx"]="09-documents:paperless-ngx"
    ["n8n"]="10-automation:n8n"
    ["monitoring"]="12-monitoring:monitoring-stack"
    ["databases-shared"]="13-infrastructure:databases-shared"
)

sync_app() {
    local remote_name=$1
    local mapping=${APPS[$remote_name]}

    if [ -z "$mapping" ]; then
        log_error "App '$remote_name' not found in priority list"
        return 1
    fi

    IFS=':' read -r category local_name <<< "$mapping"

    local remote_path="$REMOTE_BASE/$remote_name"
    local local_path="$LOCAL_BASE/$category/$local_name"

    log_info "Syncing $remote_name → $local_path"

    # Vérifier que l'app existe sur le serveur
    if ! ssh $SERVER "[ -d $remote_path ]"; then
        log_error "Remote directory $remote_path does not exist"
        return 1
    fi

    # Créer le dossier local s'il n'existe pas
    mkdir -p "$local_path/config"
    mkdir -p "$local_path/scripts"
    mkdir -p "$local_path/docs"

    # Copier docker-compose.yml
    if ssh $SERVER "[ -f $remote_path/docker-compose.yml ]"; then
        log_info "  → Copying docker-compose.yml"
        scp $SERVER:$remote_path/docker-compose.yml "$local_path/"
    else
        log_warn "  → No docker-compose.yml found"
    fi

    # Copier .env si existe (masquer les secrets)
    if ssh $SERVER "[ -f $remote_path/.env ]"; then
        log_info "  → Copying .env (secrets masked)"
        scp $SERVER:$remote_path/.env "$local_path/config/.env.example"
        # Masquer les valeurs sensibles
        sed -i 's/=.*/=YOUR_VALUE_HERE/g' "$local_path/config/.env.example"
    fi

    # Copier Dockerfile si existe
    if ssh $SERVER "[ -f $remote_path/Dockerfile ]"; then
        log_info "  → Copying Dockerfile"
        scp $SERVER:$remote_path/Dockerfile "$local_path/"
    fi

    # Copier README si existe
    if ssh $SERVER "[ -f $remote_path/README.md ]"; then
        log_info "  → Copying README.md"
        scp $SERVER:$remote_path/README.md "$local_path/docs/"
    fi

    # Copier scripts de démarrage
    if ssh $SERVER "[ -d $remote_path/scripts ]"; then
        log_info "  → Copying scripts/"
        scp -r $SERVER:$remote_path/scripts/* "$local_path/scripts/" 2>/dev/null || true
    fi

    # Créer un README local avec métadonnées
    cat > "$local_path/README.md" << EOF
# $local_name

**Catégorie**: $category
**Serveur source**: \`$remote_path\`
**Dernière sync**: $(date +"%Y-%m-%d %H:%M")

## Fichiers synchronisés

- \`docker-compose.yml\`: Configuration Docker
- \`config/.env.example\`: Variables d'environnement (secrets masqués)
- \`scripts/\`: Scripts de démarrage et maintenance
- \`docs/\`: Documentation originale du serveur

## Commandes rapides

\`\`\`bash
# Démarrer l'application
cd $local_path
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter l'application
docker-compose down
\`\`\`

## Sync depuis serveur

\`\`\`bash
# Re-synchroniser cette app
./scripts/sync-apps-from-server.sh $remote_name
\`\`\`

---
*Synchronisé automatiquement depuis srv759970.hstgr.cloud*
EOF

    log_info "  ✓ Sync completed for $remote_name"
}

# Main
if [ $# -eq 0 ]; then
    echo "Usage: $0 [app-name|all]"
    echo ""
    echo "Available apps:"
    for app in "${!APPS[@]}"; do
        echo "  - $app"
    done
    exit 1
fi

if [ "$1" == "all" ]; then
    log_info "Syncing all priority apps..."
    for app in "${!APPS[@]}"; do
        sync_app "$app"
        echo ""
    done
    log_info "All apps synced successfully!"
else
    sync_app "$1"
fi
