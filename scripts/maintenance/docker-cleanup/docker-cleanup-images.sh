#!/bin/bash
# Script de nettoyage des images Docker
# Auteur: Claude Code
# Description: Nettoyage sécurisé des images Docker inutilisées avec confirmation

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================="
echo "  Nettoyage des Images Docker"
echo "========================================="
echo ""

# Mode d'utilisation
CLEANUP_MODE=${1:-"safe"}

show_help() {
    echo "Usage: $0 [mode]"
    echo ""
    echo "Modes disponibles:"
    echo "  safe       - Nettoie uniquement les images dangling (par défaut)"
    echo "  unused     - Nettoie toutes les images inutilisées"
    echo "  aggressive - Nettoie images, conteneurs arrêtés, volumes et cache"
    echo "  dry-run    - Affiche ce qui serait supprimé sans rien supprimer"
    echo ""
    echo "Exemples:"
    echo "  $0              # Nettoyage sûr (dangling uniquement)"
    echo "  $0 safe         # Nettoyage sûr (dangling uniquement)"
    echo "  $0 unused       # Nettoie toutes les images inutilisées"
    echo "  $0 aggressive   # Nettoyage complet"
    echo "  $0 dry-run      # Simulation"
    exit 0
}

if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    show_help
fi

# Fonction pour confirmer l'action
confirm() {
    read -p "$1 (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Opération annulée."
        exit 0
    fi
}

# Afficher l'état actuel
echo -e "${BLUE}État actuel de Docker:${NC}"
docker system df
echo ""

case "$CLEANUP_MODE" in
    "safe")
        echo -e "${YELLOW}Mode: SAFE - Nettoyage des images dangling uniquement${NC}"
        echo "========================================="

        DANGLING_COUNT=$(docker images -f "dangling=true" -q | wc -l)

        if [ "$DANGLING_COUNT" -eq 0 ]; then
            echo -e "${GREEN}Aucune image dangling à nettoyer !${NC}"
            exit 0
        fi

        echo "Images dangling à supprimer: $DANGLING_COUNT"
        echo ""
        docker images -f "dangling=true" --format "{{.ID}} | {{.Size}} | {{.CreatedAt}}" | head -10

        if [ "$DANGLING_COUNT" -gt 10 ]; then
            echo "... et $((DANGLING_COUNT - 10)) autres images"
        fi

        echo ""
        confirm "Voulez-vous supprimer ces images dangling ?"

        echo -e "${BLUE}Suppression des images dangling...${NC}"
        docker image prune -f

        echo ""
        echo -e "${GREEN}Nettoyage terminé !${NC}"
        docker system df
        ;;

    "unused")
        echo -e "${YELLOW}Mode: UNUSED - Nettoyage de toutes les images inutilisées${NC}"
        echo "========================================="
        echo -e "${RED}ATTENTION: Ce mode supprime toutes les images non utilisées par des conteneurs${NC}"
        echo ""

        # Afficher les images qui seraient supprimées
        echo "Images qui seront supprimées:"
        docker images --format "{{.Repository}}:{{.Tag}} | {{.Size}}" | head -20
        echo ""

        confirm "Êtes-vous sûr de vouloir continuer ?"

        echo -e "${BLUE}Suppression des images inutilisées...${NC}"
        docker image prune -a -f

        echo ""
        echo -e "${GREEN}Nettoyage terminé !${NC}"
        docker system df
        ;;

    "aggressive")
        echo -e "${RED}Mode: AGGRESSIVE - Nettoyage complet du système Docker${NC}"
        echo "========================================="
        echo -e "${RED}ATTENTION: Ce mode supprime:${NC}"
        echo "  - Toutes les images inutilisées"
        echo "  - Tous les conteneurs arrêtés"
        echo "  - Tous les volumes inutilisés"
        echo "  - Tout le cache de build"
        echo ""

        docker system df -v
        echo ""

        confirm "Êtes-vous ABSOLUMENT sûr de vouloir continuer ?"

        echo -e "${BLUE}Nettoyage complet en cours...${NC}"

        echo "1. Suppression des conteneurs arrêtés..."
        docker container prune -f

        echo "2. Suppression des images inutilisées..."
        docker image prune -a -f

        echo "3. Suppression des volumes inutilisés..."
        docker volume prune -f

        echo "4. Suppression du cache de build..."
        docker builder prune -a -f

        echo ""
        echo -e "${GREEN}Nettoyage complet terminé !${NC}"
        docker system df
        ;;

    "dry-run")
        echo -e "${BLUE}Mode: DRY-RUN - Simulation sans suppression${NC}"
        echo "========================================="

        echo ""
        echo -e "${YELLOW}Images dangling qui seraient supprimées:${NC}"
        DANGLING_COUNT=$(docker images -f "dangling=true" -q | wc -l)
        echo "Nombre: $DANGLING_COUNT"
        docker images -f "dangling=true" --format "{{.ID}} | {{.Size}} | {{.CreatedAt}}" | head -10

        echo ""
        echo -e "${YELLOW}Espace qui serait libéré (estimation):${NC}"
        docker system df -v | grep -E "Images|Build|Containers|Local Volumes"

        echo ""
        echo -e "${GREEN}Aucune suppression effectuée (mode simulation)${NC}"
        echo "Pour effectuer le nettoyage, utilisez:"
        echo "  $0 safe       # Nettoyer les images dangling"
        echo "  $0 unused     # Nettoyer toutes les images inutilisées"
        ;;

    *)
        echo -e "${RED}Mode inconnu: $CLEANUP_MODE${NC}"
        echo ""
        show_help
        ;;
esac

echo ""
echo "Nettoyage terminé le $(date '+%Y-%m-%d %H:%M:%S')"
