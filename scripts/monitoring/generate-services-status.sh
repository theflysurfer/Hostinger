#!/bin/bash
#######################################
# Live Services Status Generator
# Generates docs/SERVICES_STATUS.md with real-time Docker container status
# Usage: ./generate-services-status.sh
#######################################

set -eo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
OUTPUT_FILE="$REPO_ROOT/docs/docs/99-dynamic/services-status.md"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %Z')

# ANSI colors for console output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 Generating live services status...${NC}"

# Service categories mapping (container name prefix -> category)
declare -A CATEGORY_MAP=(
    ["nextcloud"]="Collaboration"
    ["rocketchat"]="Collaboration"
    ["onlyoffice"]="Collaboration"
    ["jitsi"]="Collaboration"
    ["whisperx"]="Speech-to-Text & TTS"
    ["faster-whisper"]="Speech-to-Text & TTS"
    ["whisper"]="Speech-to-Text & TTS"
    ["xtts"]="Speech-to-Text & TTS"
    ["neutts"]="Speech-to-Text & TTS"
    ["ollama"]="AI & Machine Learning"
    ["ragflow"]="RAG & Semantic Search"
    ["rag-anything"]="RAG & Semantic Search"
    ["raganything"]="RAG & Semantic Search"
    ["memvid"]="RAG & Semantic Search"
    ["videorag"]="RAG & Semantic Search"
    ["paperless"]="Document Management"
    ["tika"]="Document Management"
    ["wordpress"]="Web Applications & CMS"
    ["clemence"]="Web Applications & CMS"
    ["solidarlink"]="Web Applications & CMS"
    ["cristina"]="Web Applications & CMS"
    ["strapi"]="Web Applications & CMS"
    ["impro"]="Web Applications & CMS"
    ["mysql"]="Databases"
    ["mariadb"]="Databases"
    ["postgres"]="Databases"
    ["mongodb"]="Databases"
    ["mongo"]="Databases"
    ["redis"]="Databases"
    ["elasticsearch"]="Databases"
    ["grafana"]="Monitoring & Infrastructure"
    ["prometheus"]="Monitoring & Infrastructure"
    ["loki"]="Monitoring & Infrastructure"
    ["promtail"]="Monitoring & Infrastructure"
    ["dozzle"]="Monitoring & Infrastructure"
    ["portainer"]="Monitoring & Infrastructure"
    ["glances"]="Monitoring & Infrastructure"
    ["netdata"]="Monitoring & Infrastructure"
    ["dashy"]="Monitoring & Infrastructure"
    ["nginx"]="Infrastructure"
    ["traefik"]="Infrastructure"
    ["caddy"]="Infrastructure"
)

# Get container category
get_category() {
    local container_name="$1"
    local name_lower=$(echo "$container_name" | tr '[:upper:]' '[:lower:]')

    for prefix in "${!CATEGORY_MAP[@]}"; do
        if [[ "$name_lower" == *"$prefix"* ]]; then
            echo "${CATEGORY_MAP[$prefix]}"
            return
        fi
    done

    echo "Other Services"
}

# Get container URL if available
get_container_url() {
    local container_name="$1"
    local name_lower=$(echo "$container_name" | tr '[:upper:]' '[:lower:]')

    # Map known containers to their URLs
    case "$name_lower" in
        *"nextcloud"*)
            echo "https://nextcloud.srv759970.hstgr.cloud"
            ;;
        *"rocketchat"* | *"chat"*)
            echo "https://chat.srv759970.hstgr.cloud"
            ;;
        *"jitsi"* | *"meet"*)
            echo "https://meet.srv759970.hstgr.cloud"
            ;;
        *"whisperx"*)
            echo "https://whisperx.srv759970.hstgr.cloud/docs"
            ;;
        *"faster-whisper"*)
            echo "https://faster-whisper.srv759970.hstgr.cloud/docs"
            ;;
        *"neutts-api"*)
            echo "https://neutts-api.srv759970.hstgr.cloud/docs"
            ;;
        *"neutts-ui"* | *"neutts"*)
            echo "https://neutts-ui.srv759970.hstgr.cloud"
            ;;
        *"ollama"*)
            echo "http://69.62.108.82:11434"
            ;;
        *"ragflow"*)
            echo "https://ragflow.srv759970.hstgr.cloud"
            ;;
        *"rag-anything"* | *"raganything"*)
            echo "https://rag-anything.srv759970.hstgr.cloud"
            ;;
        *"memvid"*)
            echo "https://memvid.srv759970.hstgr.cloud"
            ;;
        *"paperless"*"ngx"* | *"paperless"*)
            echo "https://paperless.srv759970.hstgr.cloud"
            ;;
        *"paperless"*"ai"*)
            echo "https://paperless-ai.srv759970.hstgr.cloud"
            ;;
        *"tika"*)
            echo "http://69.62.108.82:9998"
            ;;
        *"clemence"*)
            echo "https://clemence.srv759970.hstgr.cloud"
            ;;
        *"solidarlink"*)
            echo "https://solidarlink.srv759970.hstgr.cloud"
            ;;
        *"cristina"*"frontend"* | *"cristina"*"web"*)
            echo "https://cristina.srv759970.hstgr.cloud"
            ;;
        *"strapi"* | *"cristina"*"admin"*)
            echo "https://admin.cristina.srv759970.hstgr.cloud/admin"
            ;;
        *"impro"*)
            echo "https://impro.srv759970.hstgr.cloud"
            ;;
        *"grafana"*)
            echo "https://monitoring.srv759970.hstgr.cloud"
            ;;
        *"prometheus"*)
            echo "http://69.62.108.82:9090"
            ;;
        *"dozzle"*)
            echo "https://dozzle.srv759970.hstgr.cloud"
            ;;
        *"portainer"*)
            echo "http://69.62.108.82:9000"
            ;;
        *"glances"*)
            echo "https://glances.srv759970.hstgr.cloud"
            ;;
        *"netdata"*)
            echo "http://69.62.108.82:19999"
            ;;
        *"dashy"*)
            echo "https://dashy.srv759970.hstgr.cloud"
            ;;
        *)
            echo ""
            ;;
    esac
}

# Get status emoji
get_status_emoji() {
    local status="$1"
    case "$status" in
        "running")
            echo "🟢"
            ;;
        "restarting")
            echo "🟡"
            ;;
        "paused")
            echo "🟡"
            ;;
        "exited")
            echo "🔴"
            ;;
        "dead")
            echo "⚫"
            ;;
        "created")
            echo "⚪"
            ;;
        *)
            echo "❓"
            ;;
    esac
}

# Get health status
get_health_status() {
    local health="$1"
    if [[ -z "$health" || "$health" == "<none>" ]]; then
        echo ""
    else
        case "$health" in
            "healthy")
                echo "✅"
                ;;
            "unhealthy")
                echo "❌"
                ;;
            "starting")
                echo "⏳"
                ;;
            *)
                echo ""
                ;;
        esac
    fi
}

# Parse uptime to human-readable format
parse_uptime() {
    local uptime="$1"

    if [[ "$uptime" =~ ([0-9]+)\ weeks? ]]; then
        echo "${BASH_REMATCH[1]}w"
    elif [[ "$uptime" =~ ([0-9]+)\ days? ]]; then
        echo "${BASH_REMATCH[1]}d"
    elif [[ "$uptime" =~ ([0-9]+)\ hours? ]]; then
        echo "${BASH_REMATCH[1]}h"
    elif [[ "$uptime" =~ ([0-9]+)\ minutes? ]]; then
        echo "${BASH_REMATCH[1]}m"
    elif [[ "$uptime" =~ ([0-9]+)\ seconds? ]]; then
        echo "${BASH_REMATCH[1]}s"
    else
        echo "$uptime"
    fi
}

# Collect container information
echo -e "${YELLOW}📦 Collecting container information...${NC}"

# Get all containers (running and stopped)
containers_json=$(docker ps -a --format '{{json .}}')

# Parse containers and group by category
declare -A categories
declare -A container_data

while IFS= read -r line; do
    if [[ -z "$line" ]]; then
        continue
    fi

    name=$(echo "$line" | jq -r '.Names')
    status=$(echo "$line" | jq -r '.Status' | awk '{print tolower($1)}')
    uptime=$(echo "$line" | jq -r '.Status')
    image=$(echo "$line" | jq -r '.Image')
    ports=$(echo "$line" | jq -r '.Ports')

    # Get health status if available
    health=$(docker inspect --format='{{.State.Health.Status}}' "$name" 2>/dev/null || echo "")

    category=$(get_category "$name")
    url=$(get_container_url "$name")

    # Add to category
    if [[ -z "${categories[$category]}" ]]; then
        categories[$category]=""
    fi
    categories[$category]+="$name|"

    # Store container data
    container_data["$name"]="$status|$uptime|$image|$ports|$health|$url"

done <<< "$containers_json"

# Generate markdown file
echo -e "${YELLOW}📝 Generating markdown file...${NC}"

cat > "$OUTPUT_FILE" << 'HEADER'
# 🚀 Services Status - Live

!!! info "Auto-Generated Page"
    Cette page est générée automatiquement toutes les 5 minutes via le script `scripts/generate-services-status.sh`.

HEADER

echo "**Dernière mise à jour:** $TIMESTAMP" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Count statistics
total_containers=$(echo "$containers_json" | wc -l)
running_containers=$(docker ps --filter "status=running" --format '{{.Names}}' | wc -l)
stopped_containers=$((total_containers - running_containers))

cat >> "$OUTPUT_FILE" << STATS

## 📊 Statistiques Globales

| Métrique | Valeur |
|----------|--------|
| **Total containers** | $total_containers |
| **🟢 En cours d'exécution** | $running_containers |
| **🔴 Arrêtés** | $stopped_containers |
| **Serveur** | srv759970.hstgr.cloud |

---

STATS

# Generate sections by category
echo "" >> "$OUTPUT_FILE"
echo "## 📦 Services par Catégorie" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Sort categories
sorted_categories=($(for cat in "${!categories[@]}"; do echo "$cat"; done | sort))

for category in "${sorted_categories[@]}"; do
    echo "" >> "$OUTPUT_FILE"
    echo "### $category" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "| Service | Status | Health | Uptime | URL |" >> "$OUTPUT_FILE"
    echo "|---------|--------|--------|--------|-----|" >> "$OUTPUT_FILE"

    # Get containers in this category
    IFS='|' read -ra containers <<< "${categories[$category]}"

    # Sort containers
    sorted_containers=($(printf '%s\n' "${containers[@]}" | grep -v '^$' | sort))

    for container in "${sorted_containers[@]}"; do
        if [[ -z "$container" ]]; then
            continue
        fi

        IFS='|' read -r status uptime image ports health url <<< "${container_data[$container]}"

        status_emoji=$(get_status_emoji "$status")
        health_emoji=$(get_health_status "$health")
        uptime_short=$(parse_uptime "$uptime")

        # Format status text
        status_text="$status_emoji **$status**"
        if [[ -n "$health_emoji" ]]; then
            status_text="$status_emoji $status"
        fi

        # Format URL
        url_text="-"
        if [[ -n "$url" ]]; then
            url_text="[🔗 Accès]($url)"
        fi

        echo "| \`$container\` | $status_text | $health_emoji | $uptime_short | $url_text |" >> "$OUTPUT_FILE"
    done
done

# Add system resources section
echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "## 💻 Ressources Système" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Get system stats
cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
mem_info=$(free -h | grep "Mem:")
mem_total=$(echo "$mem_info" | awk '{print $2}')
mem_used=$(echo "$mem_info" | awk '{print $3}')
mem_percent=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')

disk_info=$(df -h / | tail -1)
disk_total=$(echo "$disk_info" | awk '{print $2}')
disk_used=$(echo "$disk_info" | awk '{print $3}')
disk_percent=$(echo "$disk_info" | awk '{print $5}')

cat >> "$OUTPUT_FILE" << RESOURCES

| Ressource | Utilisation | Total |
|-----------|-------------|-------|
| **CPU** | ${cpu_usage}% | - |
| **RAM** | ${mem_used} (${mem_percent}%) | ${mem_total} |
| **Disque** | ${disk_used} (${disk_percent}) | ${disk_total} |

RESOURCES

# Add Docker stats for top consumers
echo "" >> "$OUTPUT_FILE"
echo "### 🔥 Top Consommateurs (RAM)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "| Container | RAM | CPU |" >> "$OUTPUT_FILE"
echo "|-----------|-----|-----|" >> "$OUTPUT_FILE"

docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.CPUPerc}}" | \
    tail -n +2 | \
    sort -k2 -hr | \
    head -10 | \
    awk '{printf "| `%s` | %s | %s |\n", $1, $2, $3}' >> "$OUTPUT_FILE"

# Add legend
cat >> "$OUTPUT_FILE" << 'LEGEND'

---

## 📖 Légende

### Status
- 🟢 **running** - Container en cours d'exécution
- 🟡 **restarting** - Container en cours de redémarrage
- 🟡 **paused** - Container en pause
- 🔴 **exited** - Container arrêté
- ⚫ **dead** - Container mort
- ⚪ **created** - Container créé mais pas démarré

### Health Check
- ✅ **healthy** - Health check OK
- ❌ **unhealthy** - Health check échoué
- ⏳ **starting** - Health check en cours

---

## 🔄 Mise à Jour Automatique

Cette page est mise à jour automatiquement via cron:

```bash
# Mise à jour toutes les 5 minutes
*/5 * * * * cd /root/hostinger && ./scripts/generate-services-status.sh >> /var/log/services-status.log 2>&1
```

Pour forcer une mise à jour manuelle:

```bash
cd /root/hostinger
./scripts/generate-services-status.sh
```

## 🔗 Voir Aussi

- [Dashy Portal](https://dashy.srv759970.hstgr.cloud) - Dashboard visuel interactif
- [Portainer](http://69.62.108.82:9000) - Gestion Docker GUI
- [Dozzle](https://dozzle.srv759970.hstgr.cloud) - Logs en temps réel
- [Grafana](https://monitoring.srv759970.hstgr.cloud) - Métriques et monitoring

LEGEND

echo "" >> "$OUTPUT_FILE"
echo "*Généré automatiquement le $TIMESTAMP par \`generate-services-status.sh\`*" >> "$OUTPUT_FILE"

echo -e "${GREEN}✅ Services status page generated: $OUTPUT_FILE${NC}"
echo -e "${BLUE}📈 Total containers: $total_containers (🟢 $running_containers running, 🔴 $stopped_containers stopped)${NC}"

# Git commit if in repo
if git -C "$REPO_ROOT" rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${YELLOW}📝 Committing changes to git...${NC}"
    cd "$REPO_ROOT"
    git add "$OUTPUT_FILE"
    if git diff --staged --quiet; then
        echo -e "${BLUE}ℹ️  No changes to commit${NC}"
    else
        git commit -m "docs: auto-update services status - $TIMESTAMP" --no-verify || true
        echo -e "${GREEN}✅ Changes committed${NC}"
    fi
fi

echo -e "${GREEN}🎉 Done!${NC}"
