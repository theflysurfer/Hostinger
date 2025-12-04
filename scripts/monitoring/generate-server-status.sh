#!/bin/bash
# Script de génération du statut serveur en temps réel
# À exécuter sur le serveur : bash generate-server-status.sh

OUTPUT_FILE="/opt/mkdocs/docs/SERVER_STATUS.md"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S UTC")

# Récupérer les stats Docker
TOTAL_CONTAINERS=$(docker ps -a --format '{{.Names}}' | wc -l)
RUNNING_CONTAINERS=$(docker ps --format '{{.Names}}' | wc -l)
STOPPED_CONTAINERS=$((TOTAL_CONTAINERS - RUNNING_CONTAINERS))

# Récupérer les stats RAM
RAM_STATS=$(free -h | awk 'NR==2{print $2";"$3";"$7}')
RAM_TOTAL=$(echo $RAM_STATS | cut -d';' -f1)
RAM_USED=$(echo $RAM_STATS | cut -d';' -f2)
RAM_AVAILABLE=$(echo $RAM_STATS | cut -d';' -f3)

# Récupérer les stats Disque
DISK_STATS=$(df -h / | awk 'NR==2{print $2";"$3";"$4";"$5}')
DISK_TOTAL=$(echo $DISK_STATS | cut -d';' -f1)
DISK_USED=$(echo $DISK_STATS | cut -d';' -f2)
DISK_FREE=$(echo $DISK_STATS | cut -d';' -f3)
DISK_PERCENT=$(echo $DISK_STATS | cut -d';' -f4)

# Début du fichier Markdown
cat > "$OUTPUT_FILE" << 'EOF'
# 📊 État du Serveur en Temps Réel

> ⚠️ **Note** : Cette page est générée automatiquement.
EOF

echo "**Dernière mise à jour** : $TIMESTAMP" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

---

## Conteneurs Docker

### Statistiques Globales

- **Total conteneurs** : $TOTAL_CONTAINERS
- **Running** : $RUNNING_CONTAINERS ✅
- **Stopped** : $STOPPED_CONTAINERS ⏸️

### Liste Complète

| Nom | Statut | Uptime | RAM |
|-----|--------|--------|-----|
EOF

# Générer la liste des conteneurs avec leurs stats
docker ps -a --format '{{.Names}}\t{{.Status}}' | while IFS=$'\t' read -r name status; do
    # Récupérer l'utilisation RAM du conteneur s'il tourne
    if docker ps --format '{{.Names}}' | grep -q "^${name}$"; then
        RAM_USAGE=$(docker stats --no-stream --format '{{.MemUsage}}' "$name" 2>/dev/null | head -1)
        STATUS_ICON="✅"
        # Extraire juste "Up X hours" du status
        UPTIME=$(echo "$status" | grep -oP 'Up \K[^(]+' | sed 's/ *$//')
        [ -z "$UPTIME" ] && UPTIME=$(echo "$status" | head -c 40)
    else
        RAM_USAGE="-"
        STATUS_ICON="⏸️"
        # Extraire "Exited (X) Y ago"
        UPTIME=$(echo "$status" | head -c 40)
    fi
    echo "| $name | $STATUS_ICON $UPTIME | $RAM_USAGE |" >> "$OUTPUT_FILE"
done

cat >> "$OUTPUT_FILE" << EOF

---

## Utilisation Ressources

### 💾 RAM

| Métrique | Valeur |
|----------|--------|
| **Total** | $RAM_TOTAL |
| **Utilisé** | $RAM_USED |
| **Disponible** | $RAM_AVAILABLE |

### 💿 Disque (/)

| Métrique | Valeur |
|----------|--------|
| **Total** | $DISK_TOTAL |
| **Utilisé** | $DISK_USED ($DISK_PERCENT) |
| **Libre** | $DISK_FREE |

---

## Services avec Auto-Start/Stop 🔄

Ces services démarrent automatiquement à la demande et s'arrêtent après 30 minutes d'inactivité :

EOF

# Lister les services configurés dans docker-autostart
if [ -f /opt/docker-autostart/config.json ]; then
    echo "### Services gérés par Docker Auto-Start" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"

    # Extraire les noms des services du config.json
    grep '"name":' /opt/docker-autostart/config.json | sed 's/.*"name": "\(.*\)".*/- \1/' | sort >> "$OUTPUT_FILE"
else
    cat >> "$OUTPUT_FILE" << 'EOF'
- Dashy Portal
- MkDocs Documentation
- Nextcloud
- WhisperX (+ workers + redis)
- Faster-Whisper
- Tika
- MemVid (UI + worker)
- RAGFlow (+ ES + MySQL + Redis + MinIO)
- RAG-Anything
- ONLYOFFICE
- Rocket.Chat
- Jitsi Meet
- WordPress sites (SolidarLink, Clémence, etc.)
EOF
fi

cat >> "$OUTPUT_FILE" << 'EOF'

---

## Top 10 Consommateurs RAM

| Conteneur | RAM Utilisée |
|-----------|--------------|
EOF

# Générer le top 10 RAM
docker stats --no-stream --format 'table {{.Name}}\t{{.MemUsage}}' | tail -n +2 | sort -k2 -h -r | head -10 | while read line; do
    echo "| $line |" | sed 's/\t/ | /g' >> "$OUTPUT_FILE"
done

cat >> "$OUTPUT_FILE" << 'EOF'

---

## 🔄 Rafraîchir ces données

Pour mettre à jour cette page :

```bash
ssh root@69.62.108.82
bash /opt/scripts/generate-server-status.sh
```

Ou automatiser avec un cron job (toutes les 5 minutes) :

```bash
*/5 * * * * /opt/scripts/generate-server-status.sh
```

---

*Généré automatiquement par `/opt/scripts/generate-server-status.sh`*
EOF

echo "✅ Fichier généré : $OUTPUT_FILE"
