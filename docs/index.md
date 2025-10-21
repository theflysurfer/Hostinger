# Documentation srv759970.hstgr.cloud

Bienvenue sur la documentation technique complète du serveur **srv759970.hstgr.cloud**.

## 🚀 Services Principaux

### APIs de Transcription Audio

- **[WhisperX](services/whisperx.md)** - Transcription avancée avec diarization (qui parle quand)
- **[Faster-Whisper Queue](services/faster-whisper-queue.md)** - Transcription async avec gestion de queues RQ
- **[Monitoring WhisperX](services/monitoring.md)** - Stack Grafana + Prometheus + Loki

### Autres Services

- **[Tika](services/tika.md)** - Parsing de documents (PDF, Office, images OCR)
- **[Ollama](services/ollama.md)** - Inférence LLM locale

## 🏗️ Infrastructure

- **[Docker](infrastructure/docker.md)** - Gestion des conteneurs et réseaux
- **[Nginx](infrastructure/nginx.md)** - Reverse proxy et configuration SSL
- **[Sécurité](infrastructure/security.md)** - Basic auth, SSL, firewall

## 📚 Guides

- **[Déploiement VPS](guides/deployment.md)** - Configuration initiale du serveur
- **[Email](guides/email.md)** - Configuration SMTP et alertes
- **[WordPress](guides/wordpress.md)** - Déploiement sites WordPress avec Docker

## 📊 Portails

- **Services Portal**: [https://portal.srv759970.hstgr.cloud](https://portal.srv759970.hstgr.cloud)
- **Dashy Dashboard**: [https://dashy.srv759970.hstgr.cloud](https://dashy.srv759970.hstgr.cloud)
- **Grafana Monitoring**: [https://monitoring.srv759970.hstgr.cloud](https://monitoring.srv759970.hstgr.cloud)
- **RQ Dashboard**: [https://whisperx-dashboard.srv759970.hstgr.cloud](https://whisperx-dashboard.srv759970.hstgr.cloud)
- **Dozzle (Logs)**: [https://dozzle.srv759970.hstgr.cloud](https://dozzle.srv759970.hstgr.cloud)

## 🔧 APIs Disponibles

| Service | URL | Documentation | Status |
|---------|-----|---------------|--------|
| WhisperX | https://whisperx.srv759970.hstgr.cloud | [Swagger](https://whisperx.srv759970.hstgr.cloud/docs) | ✅ |
| Faster-Whisper Queue | https://faster-whisper.srv759970.hstgr.cloud | [Swagger](https://faster-whisper.srv759970.hstgr.cloud/docs) | ✅ |
| Faster-Whisper (direct) | http://srv759970.hstgr.cloud:8001 | [Swagger](http://srv759970.hstgr.cloud:8001/docs) | ✅ |
| Tika | http://srv759970.hstgr.cloud:9998 | API REST | ✅ |
| Ollama | http://srv759970.hstgr.cloud:11434 | API REST | ✅ |

## 🏗️ Architecture

### Services de Transcription

```
┌──────────── Redis Partagé (rq-queue-redis:6379) ────────────┐
│                                                               │
│  DB 0: Queue "transcription" (WhisperX)                      │
│  DB 1: Queue "faster-whisper-transcription"                  │
│                                                               │
└───────────────────────────────────────────────────────────────┘
         ↓                                 ↓
   whisperx-worker              faster-whisper-worker
         ↓                                 ↓
   WhisperX API (:8002)         Faster-Whisper Queue API (:8003)
```

### Stack Monitoring

```
Grafana (:3001) → Prometheus (:9090) + Loki (:3100)
                       ↓                    ↓
                  RQ Exporters         Promtail
                       ↓                    ↓
                   Redis Queue         Docker Logs
```

## 🔗 Liens Rapides

- **Dashboards**:
  - [Dashy](https://dashy.srv759970.hstgr.cloud) - Vue d'ensemble des services
  - [Dozzle](https://dozzle.srv759970.hstgr.cloud) - Logs Docker temps réel
  - [Grafana](https://monitoring.srv759970.hstgr.cloud) - Métriques et logs

- **Monitoring**:
  - [Prometheus](http://srv759970.hstgr.cloud:9090) - Métriques time-series
  - [RQ Dashboard](https://whisperx-dashboard.srv759970.hstgr.cloud) - Queues Redis

## 📝 Dernières Mises à Jour

- **2025-10-21**: Configuration HTTPS pour Dozzle, WhisperX, Dashy
- **2025-10-21**: Upload complet de la documentation MkDocs
- **2025-10-20**: Ajout Faster-Whisper Queue API avec système RQ
- **2025-10-20**: Déploiement stack Grafana + Prometheus + Loki
- **2025-10-20**: Déploiement Dashy dashboard + MkDocs documentation

---

*Documentation générée avec MkDocs Material - [https://docs.srv759970.hstgr.cloud](https://docs.srv759970.hstgr.cloud)*
