#!/bin/bash
# Script pour vérifier le statut des services auto-start et leur utilisation RAM
# Usage: bash check-autostart-status.sh

echo "=== Services Auto-Start - Status & RAM ==="
echo ""
echo "Configuration actuelle:"
echo "- RAGFlow (6.5GB) : 3 min timeout"
echo "- XTTS-API (2.5GB) : 3 min timeout"
echo "- Paperless (1.3GB) : 3 min timeout"
echo "- Nextcloud (130MB) : 3 min timeout"
echo "- MemVid (490MB) : 3 min timeout"
echo "- Jitsi (220MB) : 3 min timeout"
echo "- WordPress sites : 3 min timeout"
echo ""
echo "=== État Actuel ==="
echo ""

# Fonction pour obtenir le statut d'un container
get_container_status() {
    local container=$1
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        uptime=$(docker ps --filter "name=${container}" --format '{{.Status}}' | grep -oP 'Up \K[^(]+' | sed 's/ *$//')
        ram=$(docker stats --no-stream --format '{{.MemUsage}}' "$container" 2>/dev/null | head -1)
        echo "✅ RUNNING | Up $uptime | RAM: $ram"
    else
        status=$(docker ps -a --filter "name=${container}" --format '{{.Status}}' | head -c 40)
        echo "⏸️  STOPPED | $status"
    fi
}

# Services gourmands en RAM
echo "🔴 GROS CONSOMMATEURS (timeout 3 min):"
echo ""

echo "RAGFlow + Elasticsearch (~6.5GB):"
for container in ragflow-server ragflow-es-01 ragflow-mysql ragflow-redis ragflow-minio; do
    echo "  $container: $(get_container_status $container)"
done
echo ""

echo "XTTS-API (2.5GB):"
echo "  xtts-api: $(get_container_status xtts-api)"
echo ""

echo "Paperless-ngx (1.3GB):"
for container in paperless-webserver paperless-db paperless-redis paperless-gotenberg paperless-ai; do
    echo "  $container: $(get_container_status $container)"
done
echo ""

echo "MemVid (490MB):"
echo "  memvid-api: $(get_container_status memvid-api)"
echo ""

echo "Nextcloud (130MB):"
echo "  nextcloud: $(get_container_status nextcloud)"
echo ""

echo "Jitsi Meet (220MB):"
for container in jitsi-web jitsi-prosody jitsi-jicofo jitsi-jvb; do
    echo "  $container: $(get_container_status $container)"
done
echo ""

echo "WordPress sites (400-500MB chacun):"
for site in solidarlink clemence; do
    echo "  wordpress-${site}: $(get_container_status wordpress-${site})"
    echo "  mysql-${site}: $(get_container_status mysql-${site})"
done
echo ""

# Statistiques globales
echo "=== STATISTIQUES GLOBALES ==="
echo ""
RUNNING=$(docker ps -q | wc -l)
TOTAL=$(docker ps -a -q | wc -l)
RAM_STATS=$(free -h | awk 'NR==2{print "Total: "$2" | Used: "$3" | Free: "$7}')
echo "Containers: $RUNNING/$TOTAL running"
echo "RAM: $RAM_STATS"
echo ""

# RAM économisée si services arrêtés
echo "💡 RAM POTENTIELLEMENT LIBÉRABLE (si services s'arrêtent):"
echo "  - RAGFlow + ES : ~6.5 GB"
echo "  - XTTS-API : ~2.5 GB"
echo "  - Paperless : ~1.3 GB"
echo "  - Total : ~10.3 GB sur 16 GB"
echo ""

# Recommandations
echo "=== ACTIONS RECOMMANDÉES ==="
echo ""
echo "1. Tester pendant 10-15 minutes"
echo "2. Vérifier que les services s'arrêtent bien après 3 min"
echo "3. Si OK, passer à 15 min de timeout avec:"
echo "   bash /opt/scripts/set-autostart-timeout.sh 900"
echo ""
