#!/bin/bash

# Script de déploiement pour Jokers Hockey
# Usage: ./deploy.sh [branch]
# Exemple: ./deploy.sh main

set -e  # Arrêter en cas d'erreur

# Couleurs pour les messages
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="jokers-hockey"
APP_DIR="/var/www/jokers"
BRANCH="${1:-main}"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Déploiement de $APP_NAME${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Vérifier qu'on est dans le bon répertoire
cd "$APP_DIR" || exit 1

echo -e "${YELLOW}[1/8]${NC} Vérification du statut Git..."
git status

echo -e "${YELLOW}[2/8]${NC} Pull des dernières modifications (branche: $BRANCH)..."
git pull origin "$BRANCH"

echo -e "${YELLOW}[3/8]${NC} Installation des dépendances..."
npm install --production=false

echo -e "${YELLOW}[4/8]${NC} Vérification TypeScript..."
npm run check || {
    echo -e "${RED}❌ Erreur TypeScript détectée!${NC}"
    echo -e "${YELLOW}Voulez-vous continuer quand même? (y/N)${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo -e "${RED}Déploiement annulé.${NC}"
        exit 1
    fi
}

echo -e "${YELLOW}[5/8]${NC} Build du projet..."
npm run build

echo -e "${YELLOW}[6/8]${NC} Push du schéma de base de données..."
npm run db:push || {
    echo -e "${RED}❌ Erreur lors du push du schéma BDD!${NC}"
    echo -e "${YELLOW}Voulez-vous continuer quand même? (y/N)${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo -e "${RED}Déploiement annulé.${NC}"
        exit 1
    fi
}

echo -e "${YELLOW}[7/8]${NC} Redémarrage de l'application avec PM2..."
pm2 restart "$APP_NAME"

echo -e "${YELLOW}[8/8]${NC} Vérification de l'état de l'application..."
sleep 2
pm2 status "$APP_NAME"

echo ""
echo -e "${GREEN}✅ Déploiement terminé avec succès!${NC}"
echo ""
echo -e "${BLUE}Commandes utiles:${NC}"
echo -e "  Logs:      ${YELLOW}pm2 logs $APP_NAME${NC}"
echo -e "  Status:    ${YELLOW}pm2 status${NC}"
echo -e "  Monitor:   ${YELLOW}pm2 monit${NC}"
echo -e "  Site web:  ${YELLOW}https://jokers.xxx.fr${NC}"
echo ""
