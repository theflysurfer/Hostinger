#!/bin/bash

#######################################
# Sync Calibre Library from OneDrive to VPS
#
# Ce script synchronise la bibliothèque Calibre depuis OneDrive
# vers le VPS pour être utilisée par Kavita
#######################################

set -e

# Configuration
ONEDRIVE_REMOTE="onedrive"
ONEDRIVE_PATH="Calibre/Calibre Library"
LOCAL_PATH="/home/automation/calibre-library"
LOG_FILE="/home/automation/logs/calibre-sync.log"
LOCK_FILE="/tmp/calibre-sync.lock"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Vérifier le lock file (éviter sync simultanés)
if [ -f "$LOCK_FILE" ]; then
    error "Sync already running (lock file exists)"
    exit 1
fi

# Créer lock file
touch "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

# Créer le dossier de destination si nécessaire
mkdir -p "$LOCAL_PATH"
mkdir -p "$(dirname "$LOG_FILE")"

log "=== Starting Calibre Library Sync ==="

# Vérifier que rclone est installé
if ! command -v rclone &> /dev/null; then
    error "rclone is not installed"
    exit 1
fi

# Vérifier que le remote OneDrive existe
if ! rclone listremotes | grep -q "^${ONEDRIVE_REMOTE}:"; then
    error "OneDrive remote '$ONEDRIVE_REMOTE' not configured"
    exit 1
fi

# Afficher l'espace disque avant
log "Disk space before sync:"
df -h "$LOCAL_PATH" | tee -a "$LOG_FILE"

# Synchronisation avec rclone
log "Starting rclone sync..."

rclone sync \
    "${ONEDRIVE_REMOTE}:${ONEDRIVE_PATH}" \
    "$LOCAL_PATH" \
    --progress \
    --log-file="$LOG_FILE" \
    --log-level=INFO \
    --transfers=4 \
    --checkers=8 \
    --stats=1m \
    --exclude=".caltrash/**" \
    --exclude="*.tmp" \
    --exclude="*.part" \
    --filter="+ *.epub" \
    --filter="+ *.pdf" \
    --filter="+ *.mobi" \
    --filter="+ *.azw3" \
    --filter="+ *.cbz" \
    --filter="+ *.cbr" \
    --filter="+ metadata.db" \
    --filter="+ metadata_db_prefs_backup.json" \
    --filter="- *.log"

SYNC_EXIT_CODE=$?

if [ $SYNC_EXIT_CODE -eq 0 ]; then
    success "Rclone sync completed successfully"
else
    error "Rclone sync failed with exit code $SYNC_EXIT_CODE"
    exit $SYNC_EXIT_CODE
fi

# Afficher l'espace disque après
log "Disk space after sync:"
df -h "$LOCAL_PATH" | tee -a "$LOG_FILE"

# Compter les fichiers
EPUB_COUNT=$(find "$LOCAL_PATH" -type f -name "*.epub" | wc -l)
PDF_COUNT=$(find "$LOCAL_PATH" -type f -name "*.pdf" | wc -l)
TOTAL_SIZE=$(du -sh "$LOCAL_PATH" | cut -f1)

log "Library stats:"
log "  - EPUB files: $EPUB_COUNT"
log "  - PDF files: $PDF_COUNT"
log "  - Total size: $TOTAL_SIZE"

# Vérifier les permissions
log "Fixing permissions..."
chown -R 1000:1000 "$LOCAL_PATH" 2>&1 | tee -a "$LOG_FILE"
chmod -R 755 "$LOCAL_PATH" 2>&1 | tee -a "$LOG_FILE"

# Notifier Kavita de rescanner (si running)
if docker ps | grep -q kavita; then
    log "Triggering Kavita library scan..."
    # Kavita scanne automatiquement, mais on peut forcer via API si besoin
    success "Kavita will auto-detect changes"
else
    warning "Kavita container not running"
fi

success "=== Sync completed ==="
log ""
