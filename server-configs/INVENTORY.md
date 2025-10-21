# srv759970.hstgr.cloud - Server Inventory

**Last Updated:** 2025-01-21 12:30 (Complet)
**Server:** srv759970.hstgr.cloud (69.62.108.82)
**OS:** Ubuntu 24.04.2 LTS
**Uptime:** 195+ days
**Docker Containers:** 36 running

---

## 📦 Docker Compose Services (19)

| Service | Path | Containers | Status |
|---------|------|------------|--------|
| **api-portal** | /opt/api-portal | swagger-ui | ✅ Running |
| **cristina-backend** | /opt/cristina-backend | strapi (Strapi 5 + Node 22) | ✅ Deployed |
| **dashy** | /opt/dashy | dashy | ✅ Running |
| **faster-whisper-queue** | /opt/faster-whisper-queue | faster-whisper-queue-api, faster-whisper-worker | ✅ Running |
| **impro-manager** | /opt/impro-manager | impro-app | 🟡 Deployed |
| **memvid** | /opt/memvid | memvid-api, memvid-worker, memvid-ui | ✅ Running |
| **mkdocs** | /opt/mkdocs | mkdocs | ✅ Running |
| **monitoring** | /opt/monitoring | grafana, prometheus, loki, promtail, rq-exporter (x2) | ✅ Running |
| **neutts-air** | /opt/neutts-air | neutts-api, neutts-streamlit | ✅ Running |
| **rag-anything** | /opt/rag-anything | rag-anything-api | ✅ Running |
| **rustdesk** | /opt/rustdesk | hbbs, hbbr | ✅ Running |
| **sharepoint-dashboards** | /opt/sharepoint-dashboards | sharepoint-dashboards | 🟡 Auto-start |
| **support-dashboard** | /opt/support-dashboard | support-dashboard | 🟡 Auto-start |
| **tika-server** | /opt/tika-server | tika-server | 🟡 Deployed |
| **whisper-faster** | /opt/whisper-faster | faster-whisper | ✅ Running |
| **whisperx** | /opt/whisperx | whisperx, whisperx-worker, whisperx-dashboard, rq-queue-redis | ✅ Running |
| **wordpress-clemence** | /opt/wordpress-clemence | wordpress-clemence, nginx-clemence, mysql-clemence, wp-cli-clemence | ✅ Running |
| **wordpress-jesuishyperphagique** | /opt/wordpress-jesuishyperphagique | wordpress-jesuishyperphagique, nginx-jesuishyperphagique | ✅ Running |
| **wordpress-panneauxsolidaires** | /opt/wordpress-panneauxsolidaires | wordpress-panneauxsolidaires, nginx-panneauxsolidaires | ✅ Running |

**Excluded:** wordpress-shared-db (MySQL partagé - partie de wordpress-jesuishyperphagique/panneauxsolidaires)
**Removed:** sablier (obsolète - remplacé par /opt/docker-autostart custom)

---

## 🐳 Docker Containers (36 total)

### 🎤 Transcription & STT (6)
- `whisperx` - Transcription avec diarization (WhisperX API)
- `whisperx-worker` - RQ worker pour WhisperX
- `whisperx-dashboard` - RQ Dashboard pour monitoring queue
- `faster-whisper` - Transcription rapide OpenAI-compatible
- `faster-whisper-worker` - RQ worker pour Faster-Whisper Queue
- `faster-whisper-queue-api` - API async avec queue

### 🤖 AI/ML & RAG (4)
- `rag-anything-api` - Multimodal RAG avec LightRAG
- `neutts-api` - Text-to-speech avec voice cloning
- `neutts-streamlit` - UI Streamlit pour NeuTTS
- `memvid-api` - RAG sémantique avec encodage vidéo
- `memvid-worker` - Worker pour MemVid
- `memvid-ui` - Interface MemVid

### 📊 Monitoring & Observability (8)
- `grafana` - Dashboard metrics + logs
- `prometheus` - Time-series metrics
- `loki` - Log aggregation
- `promtail` - Log shipper
- `rq-exporter-whisperx` - Prometheus exporter (Redis Queue DB 0)
- `rq-exporter-faster-whisper` - Prometheus exporter (Redis Queue DB 1)
- `dozzle` - Docker logs viewer temps réel
- `portainer` - Docker management GUI
- `netdata` - System monitoring (CPU, RAM, disk)

### 🔧 Infrastructure (4)
- `rq-queue-redis` - Redis partagé (DB 0: WhisperX, DB 1: Faster-Whisper)
- `swagger-ui` - Portail API centralisé
- `mkdocs` - Documentation technique
- `dashy` - Service portal dashboard

### 🌐 WordPress Sites (8)
- `wordpress-clemence` + `nginx-clemence` + `mysql-clemence` + `wp-cli-clemence`
- `wordpress-jesuishyperphagique` + `nginx-jesuishyperphagique`
- `wordpress-panneauxsolidaires` + `nginx-panneauxsolidaires`
- `mysql-wordpress-shared` - MySQL partagé pour jesuishyperphagique + panneauxsolidaires

### 🖥️ Remote Desktop (2)
- `hbbs` - RustDesk server
- `hbbr` - RustDesk relay

---

## 🌐 Nginx Sites (30 total)

### Production Services
| Site | URL | Backend | Auth |
|------|-----|---------|------|
| **dashy** | https://dashy.srv759970.hstgr.cloud | localhost:4000 | Basic Auth |
| **docs** | https://docs.srv759970.hstgr.cloud | localhost:8000 | Public |
| **monitoring** | https://monitoring.srv759970.hstgr.cloud | localhost:3001 | Basic Auth (double avec Grafana) |
| **whisperx-api** | https://whisperx.srv759970.hstgr.cloud | localhost:8002 | Basic Auth |
| **faster-whisper-queue** | https://faster-whisper.srv759970.hstgr.cloud | localhost:8003 | Basic Auth |
| **whisper-faster** | https://whisper.srv759970.hstgr.cloud | localhost:8001 | Basic Auth |
| **whisperx-dashboard** | https://whisperx-dashboard.srv759970.hstgr.cloud | localhost:9181 | Basic Auth |
| **dozzle** | https://dozzle.srv759970.hstgr.cloud | localhost:8888 | Basic Auth |
| **prometheus** | https://prometheus.srv759970.hstgr.cloud | localhost:9090 | Basic Auth |

### AI/ML APIs
| Site | URL | Backend | Auth |
|------|-----|---------|------|
| **neutts-air** | https://neutts-api.srv759970.hstgr.cloud | localhost:8004 | Basic Auth |
| **neutts** | https://neutts.srv759970.hstgr.cloud | localhost:8501 (Streamlit) | Basic Auth |
| **memvid** | https://memvid.srv759970.hstgr.cloud | localhost:8503 | Basic Auth |
| **memvid-ui** | https://memvid-ui.srv759970.hstgr.cloud | localhost:8504 | Basic Auth |
| **rag-anything** | https://rag-anything.srv759970.hstgr.cloud | localhost:9510 | Basic Auth |
| **ragflow** | https://ragflow.srv759970.hstgr.cloud | localhost:9500 | Basic Auth |
| **ollama-api** | https://ollama.srv759970.hstgr.cloud | localhost:11434 | Basic Auth |
| **ollama-https** | (alias) | localhost:11434 | Basic Auth |
| **tika** | https://tika.srv759970.hstgr.cloud | localhost:9998 | Basic Auth |

### Dashboards & Portals
| Site | URL | Backend | Auth |
|------|-----|---------|------|
| **dashboard** | https://dashboard.srv759970.hstgr.cloud | localhost:8501 (Streamlit) | Basic Auth |
| **sharepoint** | https://sharepoint.srv759970.hstgr.cloud | localhost:8502 (Streamlit) | Basic Auth |
| **portal** | https://portal.srv759970.hstgr.cloud | localhost:8503 (Static + Swagger) | Basic Auth |

### Client Sites - WordPress
| Site | URL | Backend | Auth |
|------|-----|---------|------|
| **clemence** | https://clemence.srv759970.hstgr.cloud | localhost:9002 | Basic Auth (staging) |
| **jesuishyperphagique** | https://jesuishyperphagique.srv759970.hstgr.cloud | nginx-jesuishyperphagique:80 | Public |
| **panneauxsolidaires** | https://panneauxsolidaires.srv759970.hstgr.cloud | nginx-panneauxsolidaires:80 | Public |
| **solidarlink** | https://solidarlink.srv759970.hstgr.cloud | localhost:8080 | Basic Auth (staging) |
| **wordpress** | https://wordpress.srv759970.hstgr.cloud | (generic) | Basic Auth |

### Client Sites - Autres
| Site | URL | Backend | Auth |
|------|-----|---------|------|
| **cristina** | https://cristina.srv759970.hstgr.cloud | Static Astro SSG | Public |
| **strapi** | https://admin.cristina.srv759970.hstgr.cloud/admin | localhost:1337 | Strapi Auth |

### Tools & Services
| Site | URL | Backend | Auth |
|------|-----|---------|------|
| **rustdesk** | https://rustdesk.srv759970.hstgr.cloud | hbbs:21116 | Public |
| **n8n** | https://n8n.srv759970.hstgr.cloud | localhost:5678 | N8N Auth |
| **mcp** | https://mcp.srv759970.hstgr.cloud | localhost:3000 | Basic Auth |

---

## 🔒 SSL Certificates (Let's Encrypt)

**Provider:** Let's Encrypt (Certbot)
**Auto-renewal:** Enabled (systemd timer)
**Domains protégés:** 30+ domaines avec certificats actifs

**Certificats principaux:**
- `*.srv759970.hstgr.cloud` (wildcard non utilisé - certificats individuels)
- Expiration moyenne: 60-90 jours
- Dernière génération: Octobre 2025

---

## ⚙️ Systemd Services

### Services Personnalisés
- `ollama.service` - LLM inference service (localhost:11434)
- `docker.service` - Docker Engine
- `nginx.service` - Nginx web server
- `postfix.service` - SMTP email server
- `opendkim.service` - Email DKIM signing

### Services Enabled (20+)
```
docker.service
nginx.service
postfix.service
opendkim.service
ollama.service
ssh.service
ufw.service
systemd-resolved.service
systemd-timesyncd.service
cron.service
rsyslog.service
```

---

## 🔐 Authentification

### Basic Auth Protected (13 services)
Services protégés par HTTP Basic Auth (Nginx):
1. dashy
2. monitoring (Grafana)
3. whisperx
4. faster-whisper-queue
5. whisper (faster-whisper direct)
6. whisperx-dashboard
7. dozzle
8. prometheus
9. ollama
10. tika
11. neutts-air + neutts
12. memvid + memvid-ui
13. rag-anything

**Credentials actuels:** `julien:DevAccess2025`
**Fichier:** `/etc/nginx/.htpasswd`
**Snippet:** `/etc/nginx/snippets/basic-auth.conf`

### Application Native Auth
- Grafana: `admin:YourSecurePassword2025!`
- Strapi: Admin panel avec login dédié
- WordPress (x4): Accès WP admin natif
- N8N: Authentification N8N

---

## 🤖 Automation

### Auto-Start/Stop System
**Path:** `/opt/docker-autostart/`
**Type:** Custom Node.js proxy
**Port:** 8890
**Système:** Remplace Sablier (obsolète, supprimé)

**Services avec auto-start:**
- Support Dashboard (Streamlit) - Theme: Matrix
- SharePoint Dashboards (Streamlit) - Theme: Shuffle
- Cristina Backend (Strapi) - Theme: Ghost
- Clémence Site (WordPress) - Theme: Ghost
- SolidarLink (WordPress) - Theme: Hacker Terminal
- Whisper API - Mode: Blocking (API)
- WhisperX API - Mode: Blocking (API)
- Tika API - Mode: Blocking (API)

**Documentation:** `docs/guides/GUIDE_DOCKER_AUTOSTART.md`

---

## 📊 Statistiques

- **Total Services:** 30+ actifs
- **Docker Containers:** 36 running
- **Docker Compose Stacks:** 19
- **Nginx Sites:** 30
- **SSL Domains:** 30+
- **Basic Auth Protected:** 13
- **Swagger/OpenAPI Endpoints:** 8+
- **WordPress Sites:** 4
- **Streamlit Apps:** 3
- **FastAPI Apps:** 6+

---

## 💾 Backup Strategy

### Infrastructure as Code
- **Git Repository:** All configs versioned
- **Script:** `scripts/sync-from-server.sh`
- **Frequency:** Manual or automated (cron)
- **Retention:** Git history

### Server Backups
- **Script:** `/root/scripts/backup-server-state.sh`
- **Frequency:** Daily (3 AM via cron)
- **Location:** `/root/backups/`
- **Retention:** 30 days
- **Content:** Configs + Docker volumes + Databases

**Documentation:** `docs/infrastructure/backup-restore.md`

---

## 🔄 Last Sync

**Date:** 2025-01-21 12:30
**Method:** `scripts/sync-from-server.sh`
**Files Synced:** 19 docker-compose.yml
**Docker State:** 36 containers running
**Nginx Sites:** 30 configured

**Changes depuis dernier sync:**
- ✅ Sablier supprimé (obsolète)
- ✅ 12 nouveaux docker-compose ajoutés
- ✅ Services manquants documentés

---

## 📝 Notes

- **Sablier:** Ancien système auto-start/stop, **supprimé** le 2025-01-21 (remplacé par `/opt/docker-autostart/`)
- **wordpress-shared-db:** MySQL partagé, pas de docker-compose dédié (géré via jesuishyperphagique/panneauxsolidaires)
- **Auto-start:** 8 services configurés avec auto-start/stop dynamique
- **RAM Optimization:** Services peu utilisés arrêtés automatiquement (idle 30min)

---

## 🆘 Quick Commands

```bash
# Lister conteneurs running
ssh root@69.62.108.82 "docker ps"

# Vérifier Nginx
ssh root@69.62.108.82 "nginx -t && systemctl status nginx"

# Voir logs service
ssh root@69.62.108.82 "docker logs <container_name> --tail 50"

# Restart service
ssh root@69.62.108.82 "cd /opt/<service> && docker-compose restart"

# Backup manuel
ssh root@69.62.108.82 "/root/scripts/backup-server-state.sh"

# Sync configs vers local
bash scripts/sync-from-server.sh
```

---

**Pour informations à jour en temps réel, exécutez:**
```bash
ssh root@69.62.108.82 "docker ps --format 'table {{.Names}}\t{{.Status}}'"
```
