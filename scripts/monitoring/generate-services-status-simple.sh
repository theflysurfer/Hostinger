#!/bin/bash
#######################################
# Live Services Status Generator (Simplified)
# Generates docs/SERVICES_STATUS.md with real-time Docker container status
#######################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
OUTPUT_FILE="$REPO_ROOT/docs/SERVICES_STATUS.md"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %Z')

echo "🔄 Generating live services status..."

# Start generating markdown
cat > "$OUTPUT_FILE" << 'HEADER'
# 🚀 Services Status - Live

!!! info "Auto-Generated Page"
    Cette page est générée automatiquement toutes les 5 minutes via le script `scripts/generate-services-status.sh`.

HEADER

echo "**Dernière mise à jour:** $TIMESTAMP" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Get statistics
total_containers=$(docker ps -a --format '{{.Names}}' | wc -l)
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

# Add services table
echo "" >> "$OUTPUT_FILE"
echo "## 📦 Tous les Services" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "| Container | Status | Uptime | Ports |" >> "$OUTPUT_FILE"
echo "|-----------|--------|--------|-------|" >> "$OUTPUT_FILE"

# Get all containers with details
docker ps -a --format '{{.Names}}|{{.Status}}|{{.Ports}}' | sort | while IFS='|' read -r name status ports; do
    # Determine status emoji
    if echo "$status" | grep -q "Up"; then
        status_icon="🟢"
    elif echo "$status" | grep -q "Exited"; then
        status_icon="🔴"
    elif echo "$status" | grep -q "Restarting"; then
        status_icon="🟡"
    else
        status_icon="⚪"
    fi

    # Clean up ports display
    ports_display="-"
    if [[ -n "$ports" && "$ports" != "" ]]; then
        ports_display=$(echo "$ports" | head -c 50)
    fi

    # Extract uptime
    uptime_display=$(echo "$status" | sed 's/Up //' | sed 's/Exited.*/stopped/')

    echo "| \`$name\` | $status_icon $uptime_display | $ports_display |" >> "$OUTPUT_FILE"
done

# Add system resources
echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "## 💻 Ressources Système" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Get mem info
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
| **RAM** | ${mem_used} (${mem_percent}%) | ${mem_total} |
| **Disque** | ${disk_used} (${disk_percent}) | ${disk_total} |

RESOURCES

# Add top consumers
echo "" >> "$OUTPUT_FILE"
echo "### 🔥 Top 10 Consommateurs (RAM)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "\`\`\`" >> "$OUTPUT_FILE"
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.CPUPerc}}" | head -11 >> "$OUTPUT_FILE"
echo "\`\`\`" >> "$OUTPUT_FILE"

# Add legend and footer
cat >> "$OUTPUT_FILE" << 'FOOTER'

---

## 📖 Légende

- 🟢 **Running** - Container actif
- 🔴 **Stopped** - Container arrêté
- 🟡 **Restarting** - Container en redémarrage
- ⚪ **Other** - Autre statut

## 🔄 Mise à Jour

Pour mettre à jour manuellement:

```bash
cd /root/hostinger
./scripts/generate-services-status.sh
```

## 🔗 Liens Rapides

- [Dashy Portal](https://dashy.srv759970.hstgr.cloud) - Dashboard visuel
- [Portainer](http://69.62.108.82:9000) - Gestion Docker
- [Dozzle](https://dozzle.srv759970.hstgr.cloud) - Logs temps réel
- [Grafana](https://monitoring.srv759970.hstgr.cloud) - Monitoring

FOOTER

echo "" >> "$OUTPUT_FILE"
echo "*Généré le $TIMESTAMP*" >> "$OUTPUT_FILE"

echo "✅ Services status page generated: $OUTPUT_FILE"
echo "📈 Total: $total_containers containers ($running_containers running, $stopped_containers stopped)"

# Copy to MkDocs docs directory
cp "$OUTPUT_FILE" /opt/mkdocs/docs/SERVICES_STATUS.md 2>/dev/null || true

# Trigger MkDocs reload
touch /opt/mkdocs/mkdocs.yml 2>/dev/null || true
