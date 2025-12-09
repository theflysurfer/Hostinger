#!/bin/bash
# Script d'analyse des images Docker
# Auteur: Claude Code
# Description: Analyse détaillée des images Docker pour identifier les images inutilisées et l'espace gaspillé

set -e

echo "========================================="
echo "  Analyse des Images Docker"
echo "========================================="
echo ""

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Résumé général de l'utilisation de Docker
echo -e "${BLUE}[1/6] Résumé de l'utilisation de l'espace Docker${NC}"
echo "========================================="
docker system df
echo ""

# 2. Lister toutes les images dangling (sans tag)
echo -e "${YELLOW}[2/6] Images dangling (sans tag - <none>:<none>)${NC}"
echo "========================================="
DANGLING_COUNT=$(docker images -f "dangling=true" -q | wc -l)
echo "Nombre d'images dangling: $DANGLING_COUNT"

if [ "$DANGLING_COUNT" -gt 0 ]; then
    echo ""
    echo "ID          | Taille    | Date de création"
    echo "------------|-----------|------------------"
    docker images -f "dangling=true" --format "{{.ID}} | {{.Size}} | {{.CreatedAt}}" | head -20

    if [ "$DANGLING_COUNT" -gt 20 ]; then
        echo "... et $((DANGLING_COUNT - 20)) autres images"
    fi

    # Calculer l'espace total des images dangling
    DANGLING_SIZE=$(docker images -f "dangling=true" --format "{{.Size}}" | \
        awk '{
            size=$1
            unit=substr($1, length($1))
            value=substr($1, 1, length($1)-2)

            if (unit == "GB") total += value * 1024
            else if (unit == "MB") total += value
            else if (unit == "KB") total += value / 1024

        } END {printf "%.2f MB\n", total}')

    echo ""
    echo -e "${RED}Espace total occupé par les images dangling: $DANGLING_SIZE${NC}"
else
    echo -e "${GREEN}Aucune image dangling trouvée !${NC}"
fi
echo ""

# 3. Lister les images inutilisées (pas de conteneur associé)
echo -e "${YELLOW}[3/6] Images inutilisées (aucun conteneur)${NC}"
echo "========================================="

# Récupérer toutes les images utilisées par des conteneurs
USED_IMAGES=$(docker ps -a --format "{{.Image}}" | sort -u)

# Lister toutes les images
ALL_IMAGES=$(docker images --format "{{.Repository}}:{{.Tag}}")

# Trouver les images non utilisées
UNUSED_IMAGES=""
UNUSED_COUNT=0

while IFS= read -r image; do
    if ! echo "$USED_IMAGES" | grep -q "$image"; then
        UNUSED_COUNT=$((UNUSED_COUNT + 1))
        UNUSED_IMAGES="${UNUSED_IMAGES}${image}\n"
    fi
done <<< "$ALL_IMAGES"

echo "Nombre d'images inutilisées: $UNUSED_COUNT"
if [ "$UNUSED_COUNT" -gt 0 ]; then
    echo ""
    echo "Images inutilisées:"
    echo -e "$UNUSED_IMAGES" | head -20

    if [ "$UNUSED_COUNT" -gt 20 ]; then
        echo "... et $((UNUSED_COUNT - 20)) autres images"
    fi
else
    echo -e "${GREEN}Toutes les images sont utilisées !${NC}"
fi
echo ""

# 4. Grouper les images par projet/application
echo -e "${BLUE}[4/6] Images groupées par projet${NC}"
echo "========================================="
docker images --format "{{.Repository}}" | grep -v "<none>" | cut -d'/' -f1 | cut -d'_' -f1 | sort | uniq -c | sort -rn
echo ""

# 5. Top 10 des plus grosses images
echo -e "${BLUE}[5/6] Top 10 des plus grosses images${NC}"
echo "========================================="
echo "Repository:Tag                                    | Taille    | Date de création"
echo "--------------------------------------------------|-----------|------------------"
docker images --format "{{.Repository}}:{{.Tag}}|{{.Size}}|{{.CreatedAt}}" | \
    awk -F'|' '{print $0, $2}' | \
    sort -t'|' -k4 -hr | \
    head -10 | \
    awk -F'|' '{printf "%-50s| %-10s| %s\n", $1, $2, $3}'
echo ""

# 6. Statistiques détaillées sur le cache de build
echo -e "${BLUE}[6/6] Statistiques du cache de build${NC}"
echo "========================================="
BUILD_CACHE_SIZE=$(docker system df -v | grep "Build cache usage" | awk '{print $4}')
echo -e "Taille du cache de build: ${YELLOW}$BUILD_CACHE_SIZE${NC}"
echo ""

# Résumé final avec recommandations
echo "========================================="
echo -e "${GREEN}  RÉSUMÉ ET RECOMMANDATIONS${NC}"
echo "========================================="
echo ""
echo "Images dangling: $DANGLING_COUNT"
echo "Images inutilisées: $UNUSED_COUNT"
echo ""

if [ "$DANGLING_COUNT" -gt 0 ] || [ "$UNUSED_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}Recommandations:${NC}"
    echo "1. Exécutez 'docker-cleanup-images.sh' pour nettoyer les images dangling"
    echo "2. Vérifiez les images inutilisées avant de les supprimer"
    echo "3. Exécutez 'docker system prune -a' pour un nettoyage complet (ATTENTION: supprime toutes les images inutilisées)"
else
    echo -e "${GREEN}Votre système Docker est propre !${NC}"
fi
echo ""

echo "Analyse terminée le $(date '+%Y-%m-%d %H:%M:%S')"
