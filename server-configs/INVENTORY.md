# srv759970.hstgr.cloud - Server Inventory

**Last Updated:** 2025-01-21
**Server:** srv759970.hstgr.cloud (69.62.108.82)
**OS:** Ubuntu 24.04.2 LTS
**Uptime:** 195+ days

## 📦 Docker Compose Services

- clemence-wordpress
- dashy
- faster-whisper-queue
- memvid
- mkdocs
- monitoring
- neutts-air
- whisperx

## 🐳 Docker Containers Running (36 total)

### Transcription Services
- whisperx
- whisperx-worker
- whisperx-dashboard
- faster-whisper
- faster-whisper-worker
- faster-whisper-queue-api

### AI/ML Services
- rag-anything-api
- neutts-api
- neutts-streamlit
- memvid-api
- memvid-worker
- memvid-ui

### Monitoring Stack
- grafana
- prometheus
- loki
- promtail
- rq-exporter-whisperx
- rq-exporter-faster-whisper
- dozzle
- portainer
- netdata

### Infrastructure
- rq-queue-redis
- swagger-ui
- sablier (auto-start/stop)
- mkdocs

### WordPress Sites
- nginx-clemence
- wordpress-clemence
- mysql-clemence
- wp-cli-clemence
- nginx-jesuishyperphagique
- wordpress-jesuishyperphagique
- nginx-panneauxsolidaires
- wordpress-panneauxsolidaires
- mysql-wordpress-shared

### Remote Desktop
- hbbs (RustDesk server)
- hbbr (RustDesk relay)

## 🌐 Nginx Sites

### Production Sites
- dashy.srv759970.hstgr.cloud
- whisperx.srv759970.hstgr.cloud
- faster-whisper.srv759970.hstgr.cloud
- whisper.srv759970.hstgr.cloud
- monitoring.srv759970.hstgr.cloud
- docs.srv759970.hstgr.cloud
- dashboard.srv759970.hstgr.cloud
- sharepoint.srv759970.hstgr.cloud
- portal.srv759970.hstgr.cloud

### Client Sites
- clemence.srv759970.hstgr.cloud
- cristina.srv759970.hstgr.cloud
- admin.cristina.srv759970.hstgr.cloud
- solidarlink.srv759970.hstgr.cloud

### AI/ML APIs
- neutts.srv759970.hstgr.cloud
- neutts-api.srv759970.hstgr.cloud
- memvid.srv759970.hstgr.cloud
- tika.srv759970.hstgr.cloud
- ollama.srv759970.hstgr.cloud
- ragflow.srv759970.hstgr.cloud
- rag-anything.srv759970.hstgr.cloud

### Monitoring Tools
- dozzle.srv759970.hstgr.cloud
- whisperx-dashboard.srv759970.hstgr.cloud

## 🔒 SSL Certificates (Let's Encrypt)

Active certificates managed by Certbot for all HTTPS domains.

**Auto-renewal:** Enabled

## ⚙️ Systemd Services

### Custom Services
- ollama.service (LLM inference)
- docker.service
- nginx.service
- postfix.service (SMTP)
- opendkim.service (Email DKIM)

## 📊 Statistics

- **Docker Containers:** 36 running
- **Docker Compose Stacks:** 8
- **Nginx Sites:** 20+
- **SSL Domains:** 20+
- **Basic Auth Protected:** 13 services
- **Swagger/OpenAPI Endpoints:** 8+

## 🔄 Last Sync

This inventory was generated on **2025-01-21** via `sync-from-server.sh`.

For live status, run:
```bash
ssh root@69.62.108.82 "docker ps"
```
