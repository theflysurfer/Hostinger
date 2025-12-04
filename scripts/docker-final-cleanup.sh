#!/bin/bash
# Script de nettoyage final des images Docker
# À exécuter sur le serveur

set -e

echo "========================================="
echo "  Nettoyage Final des Images Docker"
echo "========================================="
echo ""

# 1. Vérifier si Minio est utilisé
echo "[1/3] Vérification de Minio..."
MINIO_CONTAINERS=$(docker ps -a --filter ancestor=quay.io/minio/minio:RELEASE.2025-06-13T11-33-47Z --format "{{.Names}}" | wc -l)

if [ "$MINIO_CONTAINERS" -eq 0 ]; then
    echo "   ℹ️  Aucun conteneur Minio trouvé"

    # Chercher dans les volumes et configs
    if docker volume ls | grep -q minio; then
        echo "   ⚠️  Volumes Minio détectés - IMAGE À CONSERVER"
        KEEP_MINIO=true
    else
        echo "   ✅ Pas de volumes Minio - IMAGE PEUT ÊTRE SUPPRIMÉE"
        KEEP_MINIO=false
    fi
else
    echo "   ⚠️  $MINIO_CONTAINERS conteneur(s) Minio trouvé(s) - IMAGE À CONSERVER"
    KEEP_MINIO=true
fi
echo ""

# 2. Supprimer les images inutilisées validées
echo "[2/3] Suppression des images inutilisées..."

# Images à supprimer
IMAGES_TO_REMOVE=(
    "5e7abcdd2021"           # nginx:<none> - 52.8 MB
    "d9fecb37a0a8"           # <none>:<none> - 427 MB
    "valkey/valkey:8"        # 120 MB - Doublon avec Redis
    "python:3.10-slim"       # 122 MB - Remplacé par 3.11
    "caddy:2-alpine"         # 53.5 MB - Non utilisé
)

for img in "${IMAGES_TO_REMOVE[@]}"; do
    if docker images --format "{{.Repository}}:{{.Tag}} {{.ID}}" | grep -q "$img"; then
        echo "   🗑️  Suppression de $img..."
        docker rmi "$img" -f 2>/dev/null || echo "      ⚠️  Échec (peut avoir des dépendances)"
    else
        echo "   ℹ️  $img déjà supprimée"
    fi
done
echo ""

# 3. Supprimer Minio si non utilisé
if [ "$KEEP_MINIO" = false ]; then
    echo "[3/3] Suppression de Minio (non utilisé)..."
    docker rmi quay.io/minio/minio:RELEASE.2025-06-13T11-33-47Z -f 2>/dev/null || echo "   ⚠️  Échec de suppression"
else
    echo "[3/3] Conservation de Minio (en utilisation)"
fi
echo ""

# 4. Nettoyer les images dangling restantes
echo "Nettoyage final des images dangling..."
docker image prune -f
echo ""

# 5. Afficher le résultat
echo "========================================="
echo "  RÉSULTAT FINAL"
echo "========================================="
docker system df
echo ""

echo "✅ Nettoyage terminé le $(date '+%Y-%m-%d %H:%M:%S')"
