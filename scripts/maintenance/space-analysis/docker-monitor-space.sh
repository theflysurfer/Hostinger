#!/bin/bash
# Script de surveillance de l'espace Docker
# Auteur: Claude Code
# Description: Surveille l'utilisation de l'espace Docker et envoie des alertes

set -e

# Configuration
LOG_DIR="/var/log/docker-monitoring"
LOG_FILE="$LOG_DIR/docker-space.log"
ALERT_THRESHOLD_GB=50  # Alerte si l'espace utilisé dépasse 50 GB
CRITICAL_THRESHOLD_GB=100  # Critique si l'espace utilisé dépasse 100 GB

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Créer le répertoire de logs si nécessaire
mkdir -p "$LOG_DIR"

# Fonction pour obtenir l'utilisation en GB
get_docker_usage_gb() {
    docker system df --format "{{.Size}}" | \
        awk '{
            gsub(/GB/, "", $1)
            gsub(/MB/, "", $1)
            gsub(/KB/, "", $1)

            size=$1
            if ($0 ~ /GB/) total += size
            else if ($0 ~ /MB/) total += size / 1024
            else if ($0 ~ /KB/) total += size / 1024 / 1024
        } END {printf "%.2f", total}'
}

# Fonction pour logger
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Afficher l'en-tête
echo "========================================="
echo "  Surveillance de l'espace Docker"
echo "========================================="
echo ""

# Récupérer les statistiques actuelles
TOTAL_USAGE_GB=$(get_docker_usage_gb)

echo -e "${BLUE}Utilisation actuelle de Docker:${NC}"
docker system df
echo ""

# Statistiques détaillées
IMAGES_COUNT=$(docker images -q | wc -l)
DANGLING_COUNT=$(docker images -f "dangling=true" -q | wc -l)
CONTAINERS_COUNT=$(docker ps -a -q | wc -l)
RUNNING_CONTAINERS=$(docker ps -q | wc -l)
STOPPED_CONTAINERS=$((CONTAINERS_COUNT - RUNNING_CONTAINERS))
VOLUMES_COUNT=$(docker volume ls -q | wc -l)

echo "Statistiques détaillées:"
echo "------------------------"
echo "Images totales: $IMAGES_COUNT"
echo "Images dangling: $DANGLING_COUNT"
echo "Conteneurs totaux: $CONTAINERS_COUNT"
echo "  - En cours d'exécution: $RUNNING_CONTAINERS"
echo "  - Arrêtés: $STOPPED_CONTAINERS"
echo "Volumes: $VOLUMES_COUNT"
echo ""

# Logger les statistiques
log_message "Usage: ${TOTAL_USAGE_GB}GB | Images: $IMAGES_COUNT | Dangling: $DANGLING_COUNT | Containers: $CONTAINERS_COUNT | Volumes: $VOLUMES_COUNT"

# Vérifier les seuils et alerter
echo "Analyse des seuils:"
echo "-------------------"

if (( $(echo "$TOTAL_USAGE_GB >= $CRITICAL_THRESHOLD_GB" | bc -l) )); then
    echo -e "${RED}CRITIQUE: L'utilisation de Docker (${TOTAL_USAGE_GB}GB) dépasse le seuil critique (${CRITICAL_THRESHOLD_GB}GB)${NC}"
    log_message "CRITICAL ALERT: Docker usage ${TOTAL_USAGE_GB}GB exceeds critical threshold ${CRITICAL_THRESHOLD_GB}GB"

    echo ""
    echo "Actions recommandées URGENTES:"
    echo "1. Exécutez: docker-cleanup-images.sh aggressive"
    echo "2. Vérifiez les gros volumes: docker system df -v"
    echo "3. Supprimez les anciennes images manuellement"

elif (( $(echo "$TOTAL_USAGE_GB >= $ALERT_THRESHOLD_GB" | bc -l) )); then
    echo -e "${YELLOW}ALERTE: L'utilisation de Docker (${TOTAL_USAGE_GB}GB) dépasse le seuil d'alerte (${ALERT_THRESHOLD_GB}GB)${NC}"
    log_message "WARNING: Docker usage ${TOTAL_USAGE_GB}GB exceeds warning threshold ${ALERT_THRESHOLD_GB}GB"

    echo ""
    echo "Actions recommandées:"
    echo "1. Exécutez: docker-analyze-images.sh"
    echo "2. Nettoyez les images dangling: docker-cleanup-images.sh safe"
    if [ "$DANGLING_COUNT" -gt 10 ]; then
        echo "3. Vous avez $DANGLING_COUNT images dangling à nettoyer"
    fi

else
    echo -e "${GREEN}OK: L'utilisation de Docker (${TOTAL_USAGE_GB}GB) est sous le seuil d'alerte (${ALERT_THRESHOLD_GB}GB)${NC}"
    log_message "OK: Docker usage ${TOTAL_USAGE_GB}GB is below warning threshold ${ALERT_THRESHOLD_GB}GB"
fi

echo ""

# Afficher l'évolution dans le temps (dernières 10 entrées)
if [ -f "$LOG_FILE" ]; then
    echo "Évolution de l'utilisation (derniers 10 enregistrements):"
    echo "-----------------------------------------------------------"
    tail -10 "$LOG_FILE"
    echo ""
fi

# Recommandations basées sur l'analyse
echo "Recommandations:"
echo "----------------"

if [ "$DANGLING_COUNT" -gt 5 ]; then
    echo -e "${YELLOW}⚠ Vous avez $DANGLING_COUNT images dangling. Exécutez: docker-cleanup-images.sh safe${NC}"
fi

if [ "$STOPPED_CONTAINERS" -gt 10 ]; then
    echo -e "${YELLOW}⚠ Vous avez $STOPPED_CONTAINERS conteneurs arrêtés. Considérez: docker container prune${NC}"
fi

# Vérifier si le cache de build est trop gros
BUILD_CACHE_SIZE=$(docker system df | grep "Build" | awk '{print $4}' | sed 's/GB//')
if (( $(echo "$BUILD_CACHE_SIZE > 10" | bc -l) 2>/dev/null )); then
    echo -e "${YELLOW}⚠ Le cache de build est gros (${BUILD_CACHE_SIZE}GB). Considérez: docker builder prune${NC}"
fi

echo ""
echo "Surveillance terminée le $(date '+%Y-%m-%d %H:%M:%S')"
echo "Log disponible: $LOG_FILE"
