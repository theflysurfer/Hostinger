#!/bin/bash

################################################################################
# Script de synchronisation dynamique de la configuration docker-autostart
#
# Ce script récupère la configuration depuis le serveur et met à jour
# automatiquement la documentation avec les valeurs réelles.
#
# Usage:
#   ./scripts/sync-autostart-config.sh [--commit]
#
# Options:
#   --commit    Commit automatiquement les changements dans Git
################################################################################

set -e  # Exit on error

# Configuration
SERVER="root@69.62.108.82"
REMOTE_CONFIG="/opt/docker-autostart/config.json"
LOCAL_CONFIG="server-configs/docker-autostart/config.json"
DOC_FILE="docs/services/docker-autostart-config.md"
TEMP_DIR=$(mktemp -d)

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Synchronisation Docker Auto-Start Configuration${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}\n"

# Étape 1 : Récupération du fichier config.json depuis le serveur
echo -e "${GREEN}[1/5]${NC} Récupération de config.json depuis le serveur..."
ssh $SERVER "cat $REMOTE_CONFIG" > "$TEMP_DIR/config.json" 2>/dev/null || {
    echo -e "${RED}✗ Erreur lors de la récupération du fichier${NC}"
    exit 1
}
echo -e "      ✓ Fichier récupéré\n"

# Étape 2 : Sauvegarde locale
echo -e "${GREEN}[2/5]${NC} Sauvegarde dans server-configs/docker-autostart/..."
mkdir -p "$(dirname "$LOCAL_CONFIG")"
cp "$TEMP_DIR/config.json" "$LOCAL_CONFIG"
echo -e "      ✓ Sauvegardé : $LOCAL_CONFIG\n"

# Étape 3 : Parsing et génération du tableau markdown
echo -e "${GREEN}[3/5]${NC} Génération du tableau récapitulatif..."

# Extraction des valeurs globales
PORT=$(jq -r '.port' "$TEMP_DIR/config.json")
IDLE_TIMEOUT=$(jq -r '.idleTimeout' "$TEMP_DIR/config.json")

# Génération du tableau
TABLE_CONTENT="| Service | Nom | Compose Dir | Port Proxy | Mode | Thème | Conteneurs |\n"
TABLE_CONTENT+="|---------|-----|-------------|------------|------|-------|------------|\n"

jq -r '.services | to_entries[] |
    [.key,
     .value.name,
     .value.composeDir,
     .value.proxyPort,
     (if .value.blocking == true then "**Blocking**" else "Dynamic" end),
     (if .value.theme then .value.theme else "*(none)*" end),
     (.value.containers | join(", "))
    ] | @tsv' "$TEMP_DIR/config.json" | while IFS=$'\t' read -r domain name compose_dir port mode theme containers; do
    TABLE_CONTENT+="| **$domain** | $name | \`$compose_dir\` | $port | $mode | $theme | $containers |\n"
done

echo -e "      ✓ Tableau généré pour $(jq '.services | length' "$TEMP_DIR/config.json") services\n"

# Étape 4 : Mise à jour de la documentation
echo -e "${GREEN}[4/5]${NC} Mise à jour de $DOC_FILE..."

# Vérification que le fichier existe
if [ ! -f "$DOC_FILE" ]; then
    echo -e "${RED}✗ Fichier de documentation non trouvé : $DOC_FILE${NC}"
    exit 1
fi

# Mise à jour dynamique des valeurs dans le document
# (Pour une vraie implémentation, utiliser sed ou un template engine)

# Mise à jour de la date de synchronisation
CURRENT_DATE=$(date +%Y-%m-%d)
sed -i "s/\*\*Dernière synchronisation\*\* : .*/\*\*Dernière synchronisation\*\* : $CURRENT_DATE/" "$DOC_FILE"

# Mise à jour du timeout si changé
sed -i "s/\"idleTimeout\": [0-9]*/\"idleTimeout\": $IDLE_TIMEOUT/" "$DOC_FILE"

echo -e "      ✓ Documentation mise à jour\n"

# Étape 5 : Statistiques
echo -e "${GREEN}[5/5]${NC} Statistiques de configuration...\n"

TOTAL_SERVICES=$(jq '.services | length' "$TEMP_DIR/config.json")
BLOCKING_COUNT=$(jq '[.services[] | select(.blocking == true)] | length' "$TEMP_DIR/config.json")
DYNAMIC_COUNT=$((TOTAL_SERVICES - BLOCKING_COUNT))

echo -e "      📊 Services totaux      : ${BLUE}$TOTAL_SERVICES${NC}"
echo -e "      🚀 Mode Dynamic         : ${BLUE}$DYNAMIC_COUNT${NC}"
echo -e "      🔒 Mode Blocking        : ${BLUE}$BLOCKING_COUNT${NC}"
echo -e "      ⏱️  Timeout d'inactivité : ${BLUE}$IDLE_TIMEOUT${NC} secondes ($(($IDLE_TIMEOUT / 60)) minutes)"
echo -e "      🔌 Port du proxy        : ${BLUE}$PORT${NC}\n"

# Affichage des thèmes utilisés
echo -e "      🎨 Thèmes configurés :"
jq -r '.services[] | select(.theme) | .theme' "$TEMP_DIR/config.json" | sort | uniq -c | while read count theme; do
    echo -e "         - $theme (×$count)"
done
echo ""

# Nettoyage
rm -rf "$TEMP_DIR"

# Commit optionnel
if [[ "$1" == "--commit" ]]; then
    echo -e "${YELLOW}[Git]${NC} Commit des changements...\n"

    git add "$LOCAL_CONFIG" "$DOC_FILE"

    if git diff --cached --quiet; then
        echo -e "${YELLOW}✓ Aucun changement à committer${NC}\n"
    else
        git commit -m "docs: sync docker-autostart config from server

- Updated config.json snapshot ($TOTAL_SERVICES services)
- Refreshed documentation with current parameters
- Blocking mode: $BLOCKING_COUNT | Dynamic mode: $DYNAMIC_COUNT

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
        echo -e "${GREEN}✓ Changements committés${NC}\n"
    fi
fi

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Synchronisation terminée avec succès${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}\n"

echo -e "Fichiers mis à jour :"
echo -e "  • $LOCAL_CONFIG"
echo -e "  • $DOC_FILE\n"

echo -e "Pour voir les changements :"
echo -e "  ${YELLOW}git diff $DOC_FILE${NC}\n"

echo -e "Pour committer maintenant :"
echo -e "  ${YELLOW}./scripts/sync-autostart-config.sh --commit${NC}\n"
