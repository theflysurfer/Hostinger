#!/bin/bash
# Script pour changer les timeouts des gros consommateurs RAM
# Usage: bash set-autostart-timeout.sh <timeout_seconds>
# Exemples:
#   bash set-autostart-timeout.sh 180   # 3 minutes (test)
#   bash set-autostart-timeout.sh 900   # 15 minutes (prod)
#   bash set-autostart-timeout.sh 1800  # 30 minutes (par défaut)

TIMEOUT=$1
CONFIG_FILE="/opt/docker-autostart/config.json"

if [ -z "$TIMEOUT" ]; then
    echo "❌ Usage: $0 <timeout_seconds>"
    echo ""
    echo "Exemples:"
    echo "  $0 180   # 3 minutes"
    echo "  $0 900   # 15 minutes"
    echo "  $0 1800  # 30 minutes"
    exit 1
fi

# Vérifier que c'est un nombre
if ! [[ "$TIMEOUT" =~ ^[0-9]+$ ]]; then
    echo "❌ Erreur: Le timeout doit être un nombre"
    exit 1
fi

# Convertir en minutes pour affichage
MINUTES=$((TIMEOUT / 60))

echo "🔧 Configuration des timeouts..."
echo "   Timeout: ${TIMEOUT}s (${MINUTES} minutes)"
echo ""

# Backup de la config actuelle
BACKUP_FILE="${CONFIG_FILE}.backup-$(date +%Y%m%d-%H%M%S)"
cp "$CONFIG_FILE" "$BACKUP_FILE"
echo "✅ Backup créé: $BACKUP_FILE"

# Services à modifier (gros consommateurs RAM)
SERVICES=(
    "ragflow.srv759970.hstgr.cloud"
    "xtts.srv759970.hstgr.cloud"
    "paperless.srv759970.hstgr.cloud"
    "memvid.srv759970.hstgr.cloud"
    "nextcloud.srv759970.hstgr.cloud"
    "meet.srv759970.hstgr.cloud"
    "solidarlink.srv759970.hstgr.cloud"
    "clemence.srv759970.hstgr.cloud"
    "jesuishyperphagique.srv759970.hstgr.cloud"
    "panneauxsolidaires.srv759970.hstgr.cloud"
)

# Créer un fichier temporaire avec jq
TMP_FILE=$(mktemp)
cp "$CONFIG_FILE" "$TMP_FILE"

# Modifier chaque service
for service in "${SERVICES[@]}"; do
    echo "   Updating: $service"
    jq --arg service "$service" --argjson timeout "$TIMEOUT" \
        '.services[$service].idleTimeout = $timeout' \
        "$TMP_FILE" > "${TMP_FILE}.new" && mv "${TMP_FILE}.new" "$TMP_FILE"
done

# Copier la nouvelle config
mv "$TMP_FILE" "$CONFIG_FILE"

echo ""
echo "✅ Configuration mise à jour"
echo ""
echo "Services modifiés (timeout = ${MINUTES}min):"
for service in "${SERVICES[@]}"; do
    name=$(jq -r --arg service "$service" '.services[$service].name' "$CONFIG_FILE")
    echo "  - $name"
done

echo ""
echo "🔄 Redémarrage de docker-autostart..."
systemctl restart docker-autostart

sleep 2

if systemctl is-active --quiet docker-autostart; then
    echo "✅ Docker-autostart redémarré avec succès"
    echo ""
    echo "📊 Statut:"
    systemctl status docker-autostart --no-pager | head -15
else
    echo "❌ Erreur: docker-autostart n'a pas démarré"
    echo "   Restauration du backup..."
    cp "$BACKUP_FILE" "$CONFIG_FILE"
    systemctl restart docker-autostart
    exit 1
fi

echo ""
echo "✅ Configuration terminée!"
echo ""
echo "Pour vérifier le statut des services:"
echo "  bash /opt/scripts/check-autostart-status.sh"
echo ""
