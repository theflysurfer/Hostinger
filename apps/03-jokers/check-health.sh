#!/bin/bash

# Script de vérification de santé pour Jokers Hockey
# Usage: ./check-health.sh

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

APP_NAME="jokers-hockey"
URL="https://jokers.xxx.fr"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Health Check: $APP_NAME${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 1. Vérifier PM2
echo -e "${YELLOW}[1/6]${NC} Vérification du processus PM2..."
if pm2 list | grep -q "$APP_NAME"; then
    STATUS=$(pm2 jlist | jq -r ".[] | select(.name==\"$APP_NAME\") | .pm2_env.status")
    if [ "$STATUS" == "online" ]; then
        echo -e "${GREEN}✅ PM2: Application en ligne${NC}"
        UPTIME=$(pm2 jlist | jq -r ".[] | select(.name==\"$APP_NAME\") | .pm2_env.pm_uptime")
        UPTIME_FORMATTED=$(date -d @$((UPTIME/1000)) +"%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "N/A")
        echo -e "   Démarré: $UPTIME_FORMATTED"
    else
        echo -e "${RED}❌ PM2: Application $STATUS${NC}"
    fi
else
    echo -e "${RED}❌ PM2: Application non trouvée${NC}"
fi

# 2. Vérifier le port
echo -e "${YELLOW}[2/6]${NC} Vérification du port 5000..."
if netstat -tulpn 2>/dev/null | grep -q ":5000"; then
    echo -e "${GREEN}✅ Port 5000: En écoute${NC}"
else
    echo -e "${RED}❌ Port 5000: Non disponible${NC}"
fi

# 3. Vérifier Nginx
echo -e "${YELLOW}[3/6]${NC} Vérification de Nginx..."
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ Nginx: Actif${NC}"
else
    echo -e "${RED}❌ Nginx: Inactif${NC}"
fi

# 4. Vérifier le SSL
echo -e "${YELLOW}[4/6]${NC} Vérification du certificat SSL..."
SSL_EXPIRY=$(echo | openssl s_client -servername jokers.xxx.fr -connect jokers.xxx.fr:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null | grep "notAfter" | cut -d= -f2)
if [ -n "$SSL_EXPIRY" ]; then
    echo -e "${GREEN}✅ SSL: Valide jusqu'au $SSL_EXPIRY${NC}"
else
    echo -e "${RED}❌ SSL: Non valide ou non accessible${NC}"
fi

# 5. Vérifier la réponse HTTP
echo -e "${YELLOW}[5/6]${NC} Vérification de la réponse HTTP..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$URL" 2>/dev/null)
if [ "$HTTP_CODE" == "200" ]; then
    echo -e "${GREEN}✅ HTTP: Code $HTTP_CODE (OK)${NC}"
else
    echo -e "${RED}❌ HTTP: Code $HTTP_CODE${NC}"
fi

# 6. Vérifier la base de données
echo -e "${YELLOW}[6/6]${NC} Vérification de la connexion à la base de données..."
if [ -f "/var/www/jokers/.env" ]; then
    source /var/www/jokers/.env
    if [ -n "$DATABASE_URL" ]; then
        if psql "$DATABASE_URL" -c "SELECT 1;" &>/dev/null; then
            echo -e "${GREEN}✅ Database: Connexion OK${NC}"
        else
            echo -e "${RED}❌ Database: Erreur de connexion${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Database: DATABASE_URL non définie${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Database: Fichier .env non trouvé${NC}"
fi

echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Utilisation des ressources:${NC}"
echo -e "${BLUE}================================${NC}"

# CPU et Mémoire
pm2 jlist | jq -r ".[] | select(.name==\"$APP_NAME\") | \"CPU: \(.monit.cpu)% | RAM: \(.monit.memory / 1024 / 1024 | floor)MB\""

echo ""
echo -e "${BLUE}Logs récents:${NC}"
pm2 logs "$APP_NAME" --lines 5 --nostream

echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}Health check terminé!${NC}"
echo -e "${BLUE}================================${NC}"
