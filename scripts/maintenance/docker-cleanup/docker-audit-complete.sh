#!/bin/bash
# ==================================================
# DOCKER COMPLETE AUDIT SCRIPT
# ==================================================
# Inventaire complet de TOUTES les images Docker
# Génère un rapport JSON + Markdown
# ==================================================

set -euo pipefail

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurations
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="/opt/scripts/docker-audit-reports"
JSON_REPORT="${REPORT_DIR}/audit_${TIMESTAMP}.json"
MD_REPORT="${REPORT_DIR}/audit_${TIMESTAMP}.md"
LATEST_LINK="${REPORT_DIR}/latest.md"

# Créer le dossier de rapports
mkdir -p "${REPORT_DIR}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🐳 DOCKER COMPLETE AUDIT${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# ==================================================
# FONCTION: Get container count by image
# ==================================================
get_container_count() {
    local image="$1"
    docker ps -a --filter "ancestor=${image}" --format "{{.ID}}" 2>/dev/null | wc -l
}

# ==================================================
# FONCTION: Get running container count by image
# ==================================================
get_running_count() {
    local image="$1"
    docker ps --filter "ancestor=${image}" --format "{{.ID}}" 2>/dev/null | wc -l
}

# ==================================================
# FONCTION: Check if image has active containers
# ==================================================
has_active_containers() {
    local image="$1"
    local running=$(get_running_count "$image")
    [ "$running" -gt 0 ] && echo "true" || echo "false"
}

# ==================================================
# COLLECTE DES DONNÉES
# ==================================================

echo -e "${YELLOW}📊 Collecte des informations Docker...${NC}"

# Images
TOTAL_IMAGES=$(docker images --format "{{.ID}}" | wc -l)
DANGLING_IMAGES=$(docker images -f "dangling=true" --format "{{.ID}}" | wc -l)

# Conteneurs
TOTAL_CONTAINERS=$(docker ps -a --format "{{.ID}}" | wc -l)
RUNNING_CONTAINERS=$(docker ps --format "{{.ID}}" | wc -l)
STOPPED_CONTAINERS=$((TOTAL_CONTAINERS - RUNNING_CONTAINERS))

# Volumes
TOTAL_VOLUMES=$(docker volume ls --format "{{.Name}}" | wc -l)
UNUSED_VOLUMES=$(docker volume ls -f "dangling=true" --format "{{.Name}}" | wc -l)

# Disk usage
DISK_USAGE=$(docker system df --format "table {{.Type}}\t{{.TotalCount}}\t{{.Size}}\t{{.Reclaimable}}" | tail -n +2)

echo -e "${GREEN}✓ Informations collectées${NC}"
echo ""

# ==================================================
# GÉNÉRATION DU RAPPORT JSON
# ==================================================

echo -e "${YELLOW}📝 Génération du rapport JSON...${NC}"

cat > "${JSON_REPORT}" << 'EOF_JSON_START'
{
  "audit_date": "TIMESTAMP_PLACEHOLDER",
  "summary": {
    "total_images": TOTAL_IMAGES_PLACEHOLDER,
    "dangling_images": DANGLING_IMAGES_PLACEHOLDER,
    "total_containers": TOTAL_CONTAINERS_PLACEHOLDER,
    "running_containers": RUNNING_CONTAINERS_PLACEHOLDER,
    "stopped_containers": STOPPED_CONTAINERS_PLACEHOLDER,
    "total_volumes": TOTAL_VOLUMES_PLACEHOLDER,
    "unused_volumes": UNUSED_VOLUMES_PLACEHOLDER
  },
  "images": [
EOF_JSON_START

# Collecter toutes les images avec détails
FIRST_IMAGE=true
docker images --format "{{.Repository}}|{{.Tag}}|{{.ID}}|{{.Size}}|{{.CreatedAt}}" | while IFS='|' read -r repo tag id size created; do
    # Skip header
    if [ "$repo" = "REPOSITORY" ]; then
        continue
    fi

    # Construire le nom complet de l'image
    if [ "$repo" = "<none>" ]; then
        image_name="<none>:<none>"
        full_name="$id"
    else
        image_name="${repo}:${tag}"
        full_name="${repo}:${tag}"
    fi

    # Compter les conteneurs
    total_containers=$(get_container_count "$full_name" 2>/dev/null || echo "0")
    running_containers=$(get_running_count "$full_name" 2>/dev/null || echo "0")
    is_active=$(has_active_containers "$full_name" 2>/dev/null || echo "false")

    # Échapper les guillemets dans les strings JSON
    repo_escaped=$(echo "$repo" | sed 's/"/\\"/g')
    tag_escaped=$(echo "$tag" | sed 's/"/\\"/g')
    created_escaped=$(echo "$created" | sed 's/"/\\"/g')

    # Ajouter une virgule si ce n'est pas le premier élément
    if [ "$FIRST_IMAGE" = false ]; then
        echo "," >> "${JSON_REPORT}"
    fi
    FIRST_IMAGE=false

    # Ajouter l'image au JSON
    cat >> "${JSON_REPORT}" << EOF
    {
      "repository": "${repo_escaped}",
      "tag": "${tag_escaped}",
      "image_id": "${id}",
      "size": "${size}",
      "created_at": "${created_escaped}",
      "total_containers": ${total_containers},
      "running_containers": ${running_containers},
      "is_active": ${is_active}
    }
EOF
done

# Fermer le JSON
cat >> "${JSON_REPORT}" << 'EOF_JSON_END'
  ],
  "containers": [
EOF_JSON_END

# Collecter tous les conteneurs
FIRST_CONTAINER=true
docker ps -a --format "{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}|{{.Size}}|{{.CreatedAt}}" | while IFS='|' read -r name image status ports size created; do
    # Échapper les caractères spéciaux
    name_escaped=$(echo "$name" | sed 's/"/\\"/g')
    image_escaped=$(echo "$image" | sed 's/"/\\"/g')
    status_escaped=$(echo "$status" | sed 's/"/\\"/g')
    ports_escaped=$(echo "$ports" | sed 's/"/\\"/g')
    size_escaped=$(echo "$size" | sed 's/"/\\"/g')
    created_escaped=$(echo "$created" | sed 's/"/\\"/g')

    # Déterminer le statut
    if echo "$status" | grep -q "Up"; then
        is_running="true"
        if echo "$status" | grep -q "healthy"; then
            health="healthy"
        elif echo "$status" | grep -q "unhealthy"; then
            health="unhealthy"
        else
            health="unknown"
        fi
    else
        is_running="false"
        health="stopped"
    fi

    # Ajouter une virgule si ce n'est pas le premier élément
    if [ "$FIRST_CONTAINER" = false ]; then
        echo "," >> "${JSON_REPORT}"
    fi
    FIRST_CONTAINER=false

    # Ajouter le conteneur au JSON
    cat >> "${JSON_REPORT}" << EOF
    {
      "name": "${name_escaped}",
      "image": "${image_escaped}",
      "status": "${status_escaped}",
      "ports": "${ports_escaped}",
      "size": "${size_escaped}",
      "created_at": "${created_escaped}",
      "is_running": ${is_running},
      "health": "${health}"
    }
EOF
done

# Fermer le JSON des conteneurs et ajouter volumes
cat >> "${JSON_REPORT}" << 'EOF_JSON_VOLUMES'
  ],
  "volumes": [
EOF_JSON_VOLUMES

# Collecter les volumes
FIRST_VOLUME=true
docker volume ls --format "{{.Name}}|{{.Driver}}|{{.Scope}}" | while IFS='|' read -r name driver scope; do
    # Skip header
    if [ "$name" = "VOLUME" ]; then
        continue
    fi

    # Vérifier si le volume est utilisé
    is_used=$(docker ps -a --filter "volume=${name}" --format "{{.ID}}" | wc -l)
    if [ "$is_used" -gt 0 ]; then
        in_use="true"
    else
        in_use="false"
    fi

    # Ajouter une virgule si ce n'est pas le premier élément
    if [ "$FIRST_VOLUME" = false ]; then
        echo "," >> "${JSON_REPORT}"
    fi
    FIRST_VOLUME=false

    # Ajouter le volume au JSON
    cat >> "${JSON_REPORT}" << EOF
    {
      "name": "${name}",
      "driver": "${driver}",
      "scope": "${scope}",
      "in_use": ${in_use}
    }
EOF
done

# Fermer le JSON
cat >> "${JSON_REPORT}" << 'EOF_JSON_FINAL'
  ],
  "disk_usage": {}
}
EOF_JSON_FINAL

# Remplacer les placeholders
sed -i "s/TIMESTAMP_PLACEHOLDER/$(date -Iseconds)/" "${JSON_REPORT}"
sed -i "s/TOTAL_IMAGES_PLACEHOLDER/${TOTAL_IMAGES}/" "${JSON_REPORT}"
sed -i "s/DANGLING_IMAGES_PLACEHOLDER/${DANGLING_IMAGES}/" "${JSON_REPORT}"
sed -i "s/TOTAL_CONTAINERS_PLACEHOLDER/${TOTAL_CONTAINERS}/" "${JSON_REPORT}"
sed -i "s/RUNNING_CONTAINERS_PLACEHOLDER/${RUNNING_CONTAINERS}/" "${JSON_REPORT}"
sed -i "s/STOPPED_CONTAINERS_PLACEHOLDER/${STOPPED_CONTAINERS}/" "${JSON_REPORT}"
sed -i "s/TOTAL_VOLUMES_PLACEHOLDER/${TOTAL_VOLUMES}/" "${JSON_REPORT}"
sed -i "s/UNUSED_VOLUMES_PLACEHOLDER/${UNUSED_VOLUMES}/" "${JSON_REPORT}"

echo -e "${GREEN}✓ Rapport JSON généré: ${JSON_REPORT}${NC}"

# ==================================================
# GÉNÉRATION DU RAPPORT MARKDOWN
# ==================================================

echo -e "${YELLOW}📝 Génération du rapport Markdown...${NC}"

cat > "${MD_REPORT}" << EOF
# 🐳 Docker Complete Audit Report

**Date**: $(date '+%Y-%m-%d %H:%M:%S')
**Serveur**: $(hostname)

---

## 📊 Résumé

| Métrique | Total | Actifs | Inactifs/Dangling |
|----------|-------|--------|-------------------|
| **Images** | ${TOTAL_IMAGES} | $((TOTAL_IMAGES - DANGLING_IMAGES)) | ${DANGLING_IMAGES} |
| **Conteneurs** | ${TOTAL_CONTAINERS} | ${RUNNING_CONTAINERS} | ${STOPPED_CONTAINERS} |
| **Volumes** | ${TOTAL_VOLUMES} | $((TOTAL_VOLUMES - UNUSED_VOLUMES)) | ${UNUSED_VOLUMES} |

---

## 💾 Utilisation Disque

\`\`\`
${DISK_USAGE}
\`\`\`

---

## 📦 Images Docker (Toutes)

EOF

# Ajouter le tableau des images
echo "| Repository | Tag | Size | Conteneurs (Running/Total) | Créé | Statut |" >> "${MD_REPORT}"
echo "|------------|-----|------|---------------------------|------|--------|" >> "${MD_REPORT}"

docker images --format "{{.Repository}}|{{.Tag}}|{{.ID}}|{{.Size}}|{{.CreatedAt}}" | while IFS='|' read -r repo tag id size created; do
    # Skip header
    if [ "$repo" = "REPOSITORY" ]; then
        continue
    fi

    if [ "$repo" = "<none>" ]; then
        full_name="$id"
        display_name="<dangling>"
        tag_display="<none>"
    else
        full_name="${repo}:${tag}"
        display_name="$repo"
        tag_display="$tag"
    fi

    total_containers=$(get_container_count "$full_name" 2>/dev/null || echo "0")
    running_containers=$(get_running_count "$full_name" 2>/dev/null || echo "0")

    if [ "$running_containers" -gt 0 ]; then
        status="✅ Active"
    elif [ "$total_containers" -gt 0 ]; then
        status="⚠️ Stopped"
    else
        status="❌ Unused"
    fi

    # Formater la date (prendre seulement la date, pas l'heure complète)
    created_short=$(echo "$created" | cut -d' ' -f1-3)

    echo "| ${display_name} | ${tag_display} | ${size} | ${running_containers}/${total_containers} | ${created_short} | ${status} |" >> "${MD_REPORT}"
done

# Ajouter la section conteneurs
cat >> "${MD_REPORT}" << EOF

---

## 🚢 Conteneurs Docker (Tous)

| Nom | Image | Statut | Ports | Taille |
|-----|-------|--------|-------|--------|
EOF

docker ps -a --format "{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}|{{.Size}}" | while IFS='|' read -r name image status ports size; do
    # Déterminer l'icône de statut
    if echo "$status" | grep -q "Up"; then
        if echo "$status" | grep -q "healthy"; then
            status_icon="✅"
        elif echo "$status" | grep -q "unhealthy"; then
            status_icon="⚠️"
        else
            status_icon="🟢"
        fi
    else
        status_icon="❌"
    fi

    # Truncate ports si trop long
    ports_display=$(echo "$ports" | cut -c1-50)
    if [ ${#ports} -gt 50 ]; then
        ports_display="${ports_display}..."
    fi

    echo "| ${name} | ${image} | ${status_icon} ${status} | ${ports_display} | ${size} |" >> "${MD_REPORT}"
done

# Ajouter la section volumes
cat >> "${MD_REPORT}" << EOF

---

## 📁 Volumes Docker

| Nom | Driver | En Utilisation | Conteneurs Attachés |
|-----|--------|----------------|---------------------|
EOF

docker volume ls --format "{{.Name}}|{{.Driver}}" | while IFS='|' read -r name driver; do
    # Skip header
    if [ "$name" = "VOLUME" ]; then
        continue
    fi

    # Compter les conteneurs qui utilisent ce volume
    container_count=$(docker ps -a --filter "volume=${name}" --format "{{.ID}}" | wc -l)

    if [ "$container_count" -gt 0 ]; then
        in_use="✅ Oui"
        containers="${container_count} conteneur(s)"
    else
        in_use="❌ Non"
        containers="Aucun"
    fi

    echo "| ${name} | ${driver} | ${in_use} | ${containers} |" >> "${MD_REPORT}"
done

# Ajouter les recommandations
cat >> "${MD_REPORT}" << EOF

---

## 🎯 Recommandations

### Nettoyage Immédiat

EOF

if [ "$DANGLING_IMAGES" -gt 0 ]; then
    cat >> "${MD_REPORT}" << EOF
- ⚠️ **${DANGLING_IMAGES} images dangling** à supprimer:
  \`\`\`bash
  docker image prune -f
  \`\`\`

EOF
fi

if [ "$STOPPED_CONTAINERS" -gt 0 ]; then
    cat >> "${MD_REPORT}" << EOF
- ⚠️ **${STOPPED_CONTAINERS} conteneurs arrêtés** à nettoyer:
  \`\`\`bash
  docker container prune -f
  \`\`\`

EOF
fi

if [ "$UNUSED_VOLUMES" -gt 0 ]; then
    cat >> "${MD_REPORT}" << EOF
- ⚠️ **${UNUSED_VOLUMES} volumes inutilisés** à supprimer:
  \`\`\`bash
  docker volume prune -f
  \`\`\`

EOF
fi

# Trouver les images inutilisées
UNUSED_IMAGES=$(docker images --format "{{.Repository}}:{{.Tag}}|{{.ID}}|{{.Size}}" | while IFS='|' read -r name id size; do
    if [ "$name" = "<none>:<none>" ]; then
        continue
    fi
    total=$(get_container_count "$name" 2>/dev/null || echo "0")
    if [ "$total" -eq 0 ]; then
        echo "- ${name} (${size})"
    fi
done)

if [ -n "$UNUSED_IMAGES" ]; then
    cat >> "${MD_REPORT}" << EOF

### Images Sans Conteneurs

Les images suivantes n'ont aucun conteneur associé:

${UNUSED_IMAGES}

EOF
fi

# Footer
cat >> "${MD_REPORT}" << EOF

---

**Rapport généré par**: docker-audit-complete.sh
**Fichier JSON**: ${JSON_REPORT}
**Fichier MD**: ${MD_REPORT}
EOF

# Créer un lien symbolique vers le dernier rapport
ln -sf "${MD_REPORT}" "${LATEST_LINK}"

echo -e "${GREEN}✓ Rapport Markdown généré: ${MD_REPORT}${NC}"
echo -e "${GREEN}✓ Lien symbolique créé: ${LATEST_LINK}${NC}"

# ==================================================
# RÉSUMÉ
# ==================================================

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}📊 RÉSUMÉ DE L'AUDIT${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}Images:${NC}        ${TOTAL_IMAGES} total (${DANGLING_IMAGES} dangling)"
echo -e "${YELLOW}Conteneurs:${NC}    ${RUNNING_CONTAINERS} running, ${STOPPED_CONTAINERS} stopped"
echo -e "${YELLOW}Volumes:${NC}       ${TOTAL_VOLUMES} total (${UNUSED_VOLUMES} unused)"
echo ""
echo -e "${GREEN}✓ Rapports générés avec succès!${NC}"
echo -e "${BLUE}  JSON: ${JSON_REPORT}${NC}"
echo -e "${BLUE}  MD:   ${MD_REPORT}${NC}"
echo -e "${BLUE}  Latest: ${LATEST_LINK}${NC}"
echo ""
