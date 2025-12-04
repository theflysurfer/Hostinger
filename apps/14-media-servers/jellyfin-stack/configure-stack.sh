#!/bin/bash

#######################################
# Configuration automatique de la stack Jellyfin
# Configure tous les services et les connecte entre eux
#######################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Configuration automatique Stack Jellyfin${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Real-Debrid API Key (déjà configuré)
RD_API_KEY="VWVR6CQXUN47NANPDSBIIUW234ST3KOXMGQSC6JSSLK6ZD6EQPAQ"

# Attendre que tous les services soient prêts
echo -e "${YELLOW}→${NC} Attente du démarrage de tous les services..."
sleep 30

# ===========================
# 1. Récupérer les API Keys
# ===========================
echo -e "${BLUE}1. Récupération des API Keys...${NC}"

# Prowlarr API Key
PROWLARR_API_KEY=$(docker exec prowlarr cat /config/config.xml 2>/dev/null | grep -oP '(?<=<ApiKey>)[^<]+' || echo "")
if [ -z "$PROWLARR_API_KEY" ]; then
    echo -e "${YELLOW}→${NC} Prowlarr API Key non trouvé, création..."
    PROWLARR_API_KEY=$(uuidgen | tr -d '-' | cut -c1-32)
fi
echo -e "${GREEN}✓${NC} Prowlarr API Key: $PROWLARR_API_KEY"

# Radarr API Key
RADARR_API_KEY=$(docker exec radarr cat /config/config.xml 2>/dev/null | grep -oP '(?<=<ApiKey>)[^<]+' || echo "")
if [ -z "$RADARR_API_KEY" ]; then
    echo -e "${YELLOW}→${NC} Radarr API Key non trouvé, création..."
    RADARR_API_KEY=$(uuidgen | tr -d '-' | cut -c1-32)
fi
echo -e "${GREEN}✓${NC} Radarr API Key: $RADARR_API_KEY"

# Sonarr API Key
SONARR_API_KEY=$(docker exec sonarr cat /config/config.xml 2>/dev/null | grep -oP '(?<=<ApiKey>)[^<]+' || echo "")
if [ -z "$SONARR_API_KEY" ]; then
    echo -e "${YELLOW}→${NC} Sonarr API Key non trouvé, création..."
    SONARR_API_KEY=$(uuidgen | tr -d '-' | cut -c1-32)
fi
echo -e "${GREEN}✓${NC} Sonarr API Key: $SONARR_API_KEY"

# Bazarr API Key
BAZARR_API_KEY=$(docker exec bazarr cat /config/config/config.yaml 2>/dev/null | grep -oP '(?<=apikey: )[^\s]+' || echo "")
if [ -z "$BAZARR_API_KEY" ]; then
    echo -e "${YELLOW}→${NC} Bazarr API Key non trouvé"
    BAZARR_API_KEY=$(uuidgen | tr -d '-' | cut -c1-32)
fi
echo -e "${GREEN}✓${NC} Bazarr API Key: $BAZARR_API_KEY"

echo ""

# ===========================
# 2. Configurer Prowlarr
# ===========================
echo -e "${BLUE}2. Configuration de Prowlarr (indexers)...${NC}"

# Ajouter YTS
curl -s -X POST "http://localhost:9696/api/v1/indexer" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $PROWLARR_API_KEY" \
  -d '{
    "enableRss": true,
    "enableAutomaticSearch": true,
    "enableInteractiveSearch": true,
    "supportsRss": true,
    "supportsSearch": true,
    "protocol": "torrent",
    "priority": 25,
    "name": "YTS",
    "fields": [],
    "implementationName": "YTS",
    "implementation": "YTS",
    "configContract": "YTSSettings",
    "tags": []
  }' > /dev/null 2>&1 && echo -e "${GREEN}✓${NC} YTS ajouté" || echo -e "${YELLOW}→${NC} YTS déjà configuré"

# Ajouter 1337x
curl -s -X POST "http://localhost:9696/api/v1/indexer" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $PROWLARR_API_KEY" \
  -d '{
    "enableRss": true,
    "enableAutomaticSearch": true,
    "enableInteractiveSearch": true,
    "supportsRss": true,
    "supportsSearch": true,
    "protocol": "torrent",
    "priority": 25,
    "name": "1337x",
    "fields": [],
    "implementationName": "1337x",
    "implementation": "1337x",
    "configContract": "1337xSettings",
    "tags": []
  }' > /dev/null 2>&1 && echo -e "${GREEN}✓${NC} 1337x ajouté" || echo -e "${YELLOW}→${NC} 1337x déjà configuré"

echo ""

# ===========================
# 3. Connecter Radarr
# ===========================
echo -e "${BLUE}3. Configuration de Radarr...${NC}"

# Ajouter Prowlarr à Radarr
curl -s -X POST "http://localhost:7878/api/v3/indexer" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $RADARR_API_KEY" \
  -d "{
    \"enableRss\": true,
    \"enableAutomaticSearch\": true,
    \"enableInteractiveSearch\": true,
    \"supportsRss\": true,
    \"supportsSearch\": true,
    \"protocol\": \"torrent\",
    \"priority\": 25,
    \"name\": \"Prowlarr\",
    \"fields\": [
      {\"name\": \"baseUrl\", \"value\": \"http://prowlarr:9696\"},
      {\"name\": \"apiKey\", \"value\": \"$PROWLARR_API_KEY\"}
    ],
    \"implementationName\": \"Prowlarr\",
    \"implementation\": \"Prowlarr\",
    \"configContract\": \"ProwlarrSettings\",
    \"tags\": []
  }" > /dev/null 2>&1 && echo -e "${GREEN}✓${NC} Prowlarr connecté à Radarr" || echo -e "${YELLOW}→${NC} Déjà configuré"

# Ajouter RDTClient comme download client
curl -s -X POST "http://localhost:7878/api/v3/downloadclient" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $RADARR_API_KEY" \
  -d '{
    "enable": true,
    "protocol": "torrent",
    "priority": 1,
    "removeCompletedDownloads": false,
    "removeFailedDownloads": true,
    "name": "RDTClient",
    "fields": [
      {"name": "host", "value": "rdtclient"},
      {"name": "port", "value": 6500},
      {"name": "category", "value": "radarr"}
    ],
    "implementationName": "qBittorrent",
    "implementation": "QBittorrent",
    "configContract": "QBittorrentSettings",
    "tags": []
  }' > /dev/null 2>&1 && echo -e "${GREEN}✓${NC} RDTClient connecté à Radarr" || echo -e "${YELLOW}→${NC} Déjà configuré"

# Ajouter root folder
curl -s -X POST "http://localhost:7878/api/v3/rootfolder" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $RADARR_API_KEY" \
  -d '{"path": "/data/movies"}' > /dev/null 2>&1 && echo -e "${GREEN}✓${NC} Root folder movies ajouté" || echo -e "${YELLOW}→${NC} Déjà configuré"

echo ""

# ===========================
# 4. Connecter Sonarr
# ===========================
echo -e "${BLUE}4. Configuration de Sonarr...${NC}"

# Ajouter Prowlarr à Sonarr
curl -s -X POST "http://localhost:8989/api/v3/indexer" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $SONARR_API_KEY" \
  -d "{
    \"enableRss\": true,
    \"enableAutomaticSearch\": true,
    \"enableInteractiveSearch\": true,
    \"supportsRss\": true,
    \"supportsSearch\": true,
    \"protocol\": \"torrent\",
    \"priority\": 25,
    \"name\": \"Prowlarr\",
    \"fields\": [
      {\"name\": \"baseUrl\", \"value\": \"http://prowlarr:9696\"},
      {\"name\": \"apiKey\", \"value\": \"$PROWLARR_API_KEY\"}
    ],
    \"implementationName\": \"Prowlarr\",
    \"implementation\": \"Prowlarr\",
    \"configContract\": \"ProwlarrSettings\",
    \"tags\": []
  }" > /dev/null 2>&1 && echo -e "${GREEN}✓${NC} Prowlarr connecté à Sonarr" || echo -e "${YELLOW}→${NC} Déjà configuré"

# Ajouter RDTClient
curl -s -X POST "http://localhost:8989/api/v3/downloadclient" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $SONARR_API_KEY" \
  -d '{
    "enable": true,
    "protocol": "torrent",
    "priority": 1,
    "removeCompletedDownloads": false,
    "removeFailedDownloads": true,
    "name": "RDTClient",
    "fields": [
      {"name": "host", "value": "rdtclient"},
      {"name": "port", "value": 6500},
      {"name": "category", "value": "sonarr"}
    ],
    "implementationName": "qBittorrent",
    "implementation": "QBittorrent",
    "configContract": "QBittorrentSettings",
    "tags": []
  }' > /dev/null 2>&1 && echo -e "${GREEN}✓${NC} RDTClient connecté à Sonarr" || echo -e "${YELLOW}→${NC} Déjà configuré"

# Ajouter root folder
curl -s -X POST "http://localhost:8989/api/v3/rootfolder" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $SONARR_API_KEY" \
  -d '{"path": "/data/tvshows"}' > /dev/null 2>&1 && echo -e "${GREEN}✓${NC} Root folder tvshows ajouté" || echo -e "${YELLOW}→${NC} Déjà configuré"

echo ""

# ===========================
# 5. Résumé
# ===========================
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  Configuration terminée !${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${BLUE}API Keys:${NC}"
echo "  Prowlarr: $PROWLARR_API_KEY"
echo "  Radarr:   $RADARR_API_KEY"
echo "  Sonarr:   $SONARR_API_KEY"
echo "  Bazarr:   $BAZARR_API_KEY"
echo ""
echo -e "${BLUE}Prochaines étapes manuelles:${NC}"
echo "  1. Jellyfin (http://VPS_IP:8096) : Créer compte admin et bibliothèques"
echo "  2. Bazarr (http://VPS_IP:6767) : Ajouter providers de sous-titres"
echo "  3. Jellyseerr (http://VPS_IP:5055) : Connecter à Jellyfin"
echo ""
echo -e "${GREEN}✓${NC} Tu peux maintenant utiliser Jellyseerr pour demander des films/séries !"
echo ""
