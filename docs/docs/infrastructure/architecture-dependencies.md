# Architecture et Dépendances - Serveur srv759970.hstgr.cloud

**Date**: 27 octobre 2025
**Serveur**: srv759970.hstgr.cloud
**OS**: MSYS_NT-10.0-22635 (Ubuntu-based)
**Ressources**: 15 GB RAM, 193 GB disque, 4 CPU cores

---

## 📊 Vue d'ensemble

**État actuel**:
- 🟢 **Actifs**: 14 stacks / 36 conteneurs
- 🔴 **Arrêtés**: 13 conteneurs (optimisation RAM)
- 💾 **Disque**: 77 GB / 193 GB (40%)
- 🧠 **RAM**: 9 GB disponibles / 15 GB

---

## 🎯 Stacks de Services

### 1. 🤖 RAGFlow (IA / RAG) - **STACK PRINCIPAL ACTIF**

**Statut**: 🟢 Actif (depuis optimisation)
**Réseau**: `docker_ragflow`
**RAM totale**: ~3.4 GB

#### Conteneurs

| Conteneur | Image | RAM | Rôle | Dépendances |
|-----------|-------|-----|------|-------------|
| `ragflow-server` | infiniflow/ragflow:v0.21.0-slim | 2.1 GB | API Backend + Frontend nginx | ✅ ragflow-mysql<br>✅ ragflow-redis<br>✅ ragflow-minio<br>✅ ragflow-es-01 |
| `ragflow-es-01` | elasticsearch:8.11.3 | 913 MB | Vector database (Elasticsearch) | ✅ ragflow-server |
| `ragflow-mysql` | mysql:8.0.39 | 386 MB | Database (metadata) | ✅ ragflow-server |
| `ragflow-minio` | minio:2025.06.13 | 261 MB | Object storage (documents) | ✅ ragflow-server |
| `ragflow-redis` | valkey/valkey:8 | 4.8 MB | Cache & queue | ✅ ragflow-server |

#### Volumes
- `docker_esdata01` - Elasticsearch data (32.5 MB)
- `docker_mysql_data` - MySQL database (257 MB)
- `docker_minio_data` - MinIO object storage (16 KB)
- `docker_redis_data` - Redis cache (2.4 KB)

#### Ports exposés
- `9500` → 9380 (Backend API)
- `9501` → 9381 (Admin API)
- `9504` → 80 (Frontend nginx)
- `1220` → 9200 (Elasticsearch)

#### Dépendances critiques
```
ragflow-server
├── ragflow-mysql (base de données)
├── ragflow-redis (cache)
├── ragflow-minio (stockage fichiers)
└── ragflow-es-01 (vectorisation documents)
```

**⚠️ Si un composant tombe** : Le système complet est inutilisable

---

### 2. ⚡ Energie Dashboard - **PROJET DOWNTO40 PRINCIPAL**

**Statut**: 🟢 Actif
**Réseau**: `energie-dashboard_default`
**RAM totale**: ~123 MB

#### Conteneurs

| Conteneur | Image | RAM | Rôle | Dépendances |
|-----------|-------|-----|------|-------------|
| `energie-40eur-dashboard` | energie-dashboard_app | 123 MB | Streamlit dashboard prix électricité | Aucune (standalone) |

#### Volumes
- Aucun (données locales ou API externes)

#### Ports exposés
- `8501` → 8501 (Streamlit HTTP)

#### URL
- https://energie.srv759970.hstgr.cloud

**✅ Indépendant** : Peut fonctionner seul

---

### 3. 🔗 LangChain Service - **API IA**

**Statut**: 🟢 Actif
**Réseau**: `langchain-service_langchain-network`
**RAM totale**: ~74 MB

#### Conteneurs

| Conteneur | Image | RAM | Rôle | Dépendances |
|-----------|-------|-----|------|-------------|
| `langchain-service` | langchain-service:latest | 74 MB | API LangChain orchestration | ⚠️ telegram-voice-bot<br>⚠️ redis-shared (optionnel) |

#### Limite mémoire
- Max: 1 GB (défini dans docker-compose)

#### Ports exposés
- `8503` → 8503 (Uvicorn HTTP)

**⚠️ Connecté à** : telegram-voice-bot, whisperx

---

### 4. 💬 Telegram Voice Bot

**Statut**: 🟢 Actif (Healthy)
**Réseaux**:
- `telegram-bot_default`
- `langchain-service_langchain-network`
- `whisperx_whisperx`

**RAM totale**: ~35 MB

#### Conteneurs

| Conteneur | Image | RAM | Rôle | Dépendances |
|-----------|-------|-----|------|-------------|
| `telegram-voice-bot` | telegram-bot:latest | 35 MB | Bot Telegram vocal | ✅ langchain-service<br>⚠️ whisperx (redis) |

#### Limite mémoire
- Max: 512 MB

**🔗 Multi-réseau** : Communique avec 3 stacks différentes

---

### 5. 💬 Discord Voice Bot

**Statut**: 🟢 Actif (Unhealthy - à vérifier)
**Réseau**: `discord-bot_discord-network`
**RAM totale**: ~34 MB

#### Conteneurs

| Conteneur | Image | RAM | Rôle | Dépendances |
|-----------|-------|-----|------|-------------|
| `discord-voice-bot` | discord-bot:latest | 34 MB | Bot Discord vocal | ⚠️ À vérifier (unhealthy) |

#### Limite mémoire
- Max: 512 MB

**⚠️ Status unhealthy** : Nécessite investigation

---

### 6. 🤝 Human Chain - **Interface Humain/IA**

**Statut**: 🟢 Actif (Backend unhealthy)
**Réseau**: `human-chain_human-chain-net`
**RAM totale**: ~62 MB

#### Conteneurs

| Conteneur | Image | RAM | Rôle | Dépendances |
|-----------|-------|-----|------|-------------|
| `human-chain-frontend` | human-chain_frontend | 5.9 MB | Interface web (React/Vue) | ✅ human-chain-backend |
| `human-chain-backend` | human-chain_backend | 56.9 MB | API backend | ⚠️ À vérifier (unhealthy) |

**⚠️ Backend unhealthy** : Frontend dépend du backend

---

### 7. 🎬 MemVid - **Vidéo + Transcription**

**Statut**: 🔴 Arrêté (optimisation RAM)
**Réseaux**:
- `memvid_memvid-network`
- `monitoring_monitoring`
- `whisperx_whisperx`

**RAM totale quand actif**: ~962 MB

#### Conteneurs

| Conteneur | Image | RAM | Rôle | Dépendances |
|-----------|-------|-----|------|-------------|
| `memvid-api` | memvid_memvid-api | 871 MB | API FastAPI uploads vidéos | ✅ redis-shared<br>✅ postgresql-shared<br>⚠️ whisperx |
| `memvid-ui` | memvid_memvid-ui | 45 MB | Interface Streamlit | ✅ memvid-api |
| `memvid-worker` | memvid_memvid-worker | (stopped) | Worker traitement vidéos | ✅ redis-shared<br>✅ memvid-api |

#### Volumes
- Aucun volume dédié

**🔗 Multi-réseau** : Communique avec monitoring + whisperx

---

### 8. 🎙️ WhisperX - **Transcription Audio**

**Statut**: 🟢 Actif (worker uniquement)
**Réseau**: `faster-whisper-queue_faster-whisper-net` + `whisperx_whisperx`
**RAM totale**: ~24 MB

#### Conteneurs

| Conteneur | Image | RAM | Rôle | Dépendances |
|-----------|-------|-----|------|-------------|
| `faster-whisper-worker` | faster-whisper-worker | 24 MB | Worker transcription Whisper | ✅ redis-shared |
| `rq-exporter-faster-whisper` | mdawar/rq-exporter | 23 MB | Metrics RQ queue | ✅ redis-shared |
| `rq-exporter-whisperx` | mdawar/rq-exporter | 25 MB | Metrics RQ queue | ✅ redis-shared |

#### Volumes
- `whisperx_rq-queue-redis-data` (4.8 MB)
- `whisperx_whisperx-redis-data` (236 KB)
- `whisperx_whisperx-uploads` (34 MB)

**✅ Partagé** : Utilisé par telegram-bot, memvid, discord-bot

---

### 9. 🗄️ Bases de Données Partagées - **INFRASTRUCTURE CRITIQUE**

**Statut**: 🟢 Actif
**Réseau**: `databases-shared`
**RAM totale**: ~535 MB

#### Conteneurs

| Conteneur | Image | RAM | Rôle | Services utilisant |
|-----------|-------|-----|------|---------------------|
| `postgresql-shared` | postgres:17-alpine | 31 MB | PostgreSQL partagé | ✅ memvid-api<br>⚠️ nextcloud (si actif) |
| `redis-shared` | redis:7-alpine | 7 MB | Redis partagé | ✅ memvid<br>✅ whisperx<br>✅ telegram-bot |
| `mongodb-shared` | mongo:7 | 101 MB | MongoDB partagé | 🔴 Arrêté (aucun service actif) |
| `postgres-exporter` | postgres-exporter | 11 MB | Metrics PostgreSQL | ✅ prometheus (monitoring) |

#### Volumes
- `databases-shared_postgres-data` (0 B - vide actuellement)
- `databases-shared_redis-data` (0 B)
- `databases-shared_mongo-data` (0 B)

**🚨 INFRASTRUCTURE CRITIQUE** : Utilisé par 5+ stacks

---

### 10. 📊 Monitoring Stack - **Grafana + Prometheus + Loki**

**Statut**: 🔴 Arrêté (optimisation RAM)
**Réseau**: `monitoring_monitoring`
**RAM totale quand actif**: ~262 MB

#### Conteneurs

| Conteneur | Image | RAM | Rôle | Dépendances |
|-----------|-------|-----|------|-------------|
| `grafana` | grafana/grafana | 118 MB | Dashboards métriques | ✅ prometheus<br>✅ loki |
| `prometheus` | prom/prometheus | 51 MB | Time-series database | ✅ postgres-exporter<br>✅ rq-exporters |
| `loki` | grafana/loki | 92 MB | Log aggregation | ⚠️ promtail |
| `promtail` | grafana/promtail | 42 MB | Log collector | ✅ loki |

#### Volumes
- `monitoring_grafana-data` (139.9 MB)
- `monitoring_prometheus-data` (66.5 MB)
- `monitoring_loki-data` (6.1 MB)

#### Ports exposés (quand actif)
- `3000` → 3000 (Grafana UI)
- `9090` → 9090 (Prometheus API)
- `3100` → 3100 (Loki API)

**🔗 Multi-réseau** : Connecté à databases-shared, langchain, memvid

---

### 11. 📁 Nextcloud - **Cloud Storage**

**Statut**: 🔴 Arrêté (optimisation RAM)
**Réseaux**:
- `databases-shared`
- `nextcloud`

**RAM totale quand actif**: ~125 MB

#### Conteneurs

| Conteneur | Image | RAM | Rôle | Dépendances |
|-----------|-------|-----|------|-------------|
| `nextcloud` | nextcloud:29-apache | 111 MB | Application Nextcloud | ✅ postgresql-shared<br>✅ redis-shared |
| `nextcloud-cron` | nextcloud:29-apache | 14 MB | Tâches planifiées | ✅ nextcloud |

#### Volumes
- `nextcloud_nextcloud-data` (0 B - vide)
- `nextcloud_onlyoffice-data` (2 KB)
- `nextcloud_onlyoffice-log` (36 KB)

**🔗 Multi-réseau** : Utilise databases-shared

---

### 12. 📝 WordPress Clemence

**Statut**: 🔴 Arrêté (optimisation RAM)
**Réseau**: `wordpress-clemence_clemence-network`
**RAM totale quand actif**: ~840 MB

#### Conteneurs

| Conteneur | Image | RAM | Rôle | Dépendances |
|-----------|-------|-----|------|-------------|
| `wordpress-clemence` | wordpress:php8.3-fpm | 69 MB | WordPress PHP-FPM | ✅ mysql-clemence |
| `mysql-clemence` | mysql:8.0 | 383 MB | Base de données MySQL | ✅ wordpress-clemence |
| `nginx-clemence` | nginx:alpine | 5 MB | Serveur web nginx | ✅ wordpress-clemence |
| `wp-cli-clemence` | wordpress:cli-php8.3 | 0.3 MB | WP-CLI pour admin | ✅ wordpress-clemence |

#### Volumes
- `wordpress-clemence_mysql-data` (247.5 MB)
- `wordpress-clemence_wordpress-data` (116.5 MB)

#### Dépendances strictes
```
nginx-clemence
└── wordpress-clemence (PHP-FPM via FastCGI)
    └── mysql-clemence (database)
```

**⚠️ Stack complet** : Les 4 conteneurs doivent être actifs ensemble

---

### 13. 🖼️ Photos Chantier

**Statut**: 🟢 Actif
**Réseau**: `photos-chantier_photos-network`
**RAM totale**: ~46 MB

#### Conteneurs

| Conteneur | Image | RAM | Rôle | Dépendances |
|-----------|-------|-----|------|-------------|
| `photos-chantier` | photos-chantier | 46 MB | Application photos | Aucune (standalone) |

**✅ Indépendant** : Peut fonctionner seul

---

### 14. 📚 MkDocs - **Documentation**

**Statut**: 🟢 Actif
**Réseau**: `mkdocs_default`
**RAM totale**: ~52 MB

#### Conteneurs

| Conteneur | Image | RAM | Rôle | Dépendances |
|-----------|-------|-----|------|-------------|
| `mkdocs` | mkdocs:latest | 52 MB | Documentation site | Aucune (standalone) |

**✅ Indépendant** : Peut fonctionner seul

---

### 15. 📊 Dashy - **Dashboard Liens**

**Statut**: 🟢 Actif (Healthy)
**Réseau**: `dashy_default`
**RAM totale**: ~116 MB

#### Conteneurs

| Conteneur | Image | RAM | Rôle | Dépendances |
|-----------|-------|-----|------|-------------|
| `dashy` | lissy93/dashy | 116 MB | Dashboard liens/apps | Aucune (standalone) |

**✅ Indépendant** : Peut fonctionner seul

---

### 16. 🖥️ Portainer - **Docker Management**

**Statut**: 🟢 Actif
**Réseau**: `bridge` (default)
**RAM totale**: ~21 MB

#### Conteneurs

| Conteneur | Image | RAM | Rôle | Dépendances |
|-----------|-------|-----|------|-------------|
| `portainer` | portainer/portainer-ce | 21 MB | Docker web UI | Aucune (accès Docker socket) |

#### Volumes
- `portainer_data` (1 MB)

**✅ Indépendant** : Management interface

---

### 17. 📈 Glances - **System Monitoring**

**Statut**: 🟢 Actif
**Réseau**: `bridge` (default)
**RAM totale**: ~68 MB

#### Conteneurs

| Conteneur | Image | RAM | Rôle | Dépendances |
|-----------|-------|-----|------|-------------|
| `glances` | nicolargo/glances | 68 MB | Monitoring système temps réel | Aucune (lecture host) |

#### Limite mémoire
- Max: 256 MB

**✅ Indépendant** : Monitoring local

---

### 18. 🖥️ RustDesk - **Remote Desktop**

**Statut**: 🟢 Actif
**Réseau**: `rustdesk_rustdesk-net`
**RAM totale**: ~0.8 MB

#### Conteneurs

| Conteneur | Image | RAM | Rôle | Dépendances |
|-----------|-------|-----|------|-------------|
| `hbbr` | rustdesk/rustdesk-server | 0.8 MB | RustDesk relay broker | Aucune (P2P relay) |

**✅ Indépendant** : Service P2P

---

## 🔗 Graphe de Dépendances Global

```
INFRASTRUCTURE PARTAGÉE
└── databases-shared
    ├── postgresql-shared ────┬──> memvid-api
    │                          ├──> nextcloud (stopped)
    │                          └──> postgres-exporter
    ├── redis-shared ─────────┬──> memvid (api + worker)
    │                          ├──> whisperx (workers)
    │                          ├──> telegram-voice-bot
    │                          └──> nextcloud (stopped)
    └── mongodb-shared ────────> (AUCUN SERVICE ACTIF)

STACKS INDÉPENDANTES
├── ragflow ──────────────────> ragflow-server + es-01 + mysql + minio + redis
├── energie-dashboard ────────> energie-40eur-dashboard
├── photos-chantier ──────────> photos-chantier
├── mkdocs ───────────────────> mkdocs
├── dashy ────────────────────> dashy
├── portainer ────────────────> portainer
├── glances ──────────────────> glances
└── rustdesk ─────────────────> hbbr

STACKS AVEC DÉPENDANCES INTERNES
├── human-chain
│   ├── human-chain-frontend ─> human-chain-backend
│   └── human-chain-backend
├── wordpress-clemence
│   ├── nginx-clemence ───────> wordpress-clemence ──> mysql-clemence
│   └── wp-cli-clemence ──────> wordpress-clemence
└── langchain-service
    └── langchain-service ────> telegram-voice-bot

STACKS MULTI-RÉSEAU (Complexes)
├── memvid
│   ├── memvid-api ───────────> postgresql-shared, redis-shared, whisperx
│   ├── memvid-ui ────────────> memvid-api
│   └── memvid-worker ────────> memvid-api, redis-shared
├── telegram-voice-bot ───────> langchain-service, whisperx (redis)
├── whisperx
│   ├── faster-whisper-worker > redis-shared
│   └── rq-exporters ─────────> redis-shared, prometheus
└── monitoring (STOPPED)
    ├── prometheus ───────────> postgres-exporter, rq-exporters, langchain
    ├── grafana ──────────────> prometheus, loki
    ├── loki ─────────────────> promtail
    └── promtail ─────────────> (logs host)
```

---

## ⚠️ Points Critiques

### 🚨 Services avec dépendances multiples

1. **redis-shared** (SPOF)
   - Utilisé par: memvid, whisperx, telegram-bot, nextcloud
   - Impact si down: 4+ services affectés

2. **postgresql-shared** (SPOF)
   - Utilisé par: memvid-api, nextcloud
   - Impact si down: 2 services affectés

3. **langchain-service**
   - Utilisé par: telegram-voice-bot
   - Impact si down: telegram bot non fonctionnel

### 🔴 Services avec status unhealthy

1. **human-chain-backend** - Backend non fonctionnel
2. **discord-voice-bot** - Bot Discord non fonctionnel

### 📦 Volumes orphelins (à nettoyer)

Les volumes suivants n'ont **aucun conteneur actif** :

```bash
# Volumes de services supprimés
- invidious_invidious-db-data (52.75 MB)
- paperless-ai_paperless-ai-data (258.9 KB)
- paperless-ngx_* (4 volumes)
- rag-anything_* (2 volumes)
- open-webui (1.08 GB) ⚠️ GROS
- deploy_xtts-models (0 B)

# Volumes WordPress orphelins
- wordpress-jesuishyperphagique_* (274 MB)
- wordpress-panneauxsolidaires_* (274 MB)
- wordpress-solidarlink_* (474 MB)
- wordpress-shared-db_* (221 MB)
```

**Total récupérable**: ~2.5 GB

---

## 🎯 Recommandations

### Pour redémarrer un service arrêté

#### WordPress Clemence (Stack complète)
```bash
docker start mysql-clemence && sleep 5
docker start wordpress-clemence
docker start nginx-clemence
docker start wp-cli-clemence
```

#### Monitoring Stack
```bash
docker start loki promtail
docker start prometheus
docker start grafana
```

#### Nextcloud
```bash
docker start nextcloud
docker start nextcloud-cron
```

#### MemVid
```bash
docker start memvid-api
docker start memvid-ui
# memvid-worker si besoin de traitement
docker start memvid-worker
```

### Pour nettoyer les volumes orphelins

```bash
# ATTENTION: Supprimer définitivement les données !
docker volume rm \
  invidious_invidious-db-data \
  open-webui \
  paperless-ai_paperless-ai-data \
  paperless-ngx_paperless-data \
  paperless-ngx_paperless-db-data \
  paperless-ngx_paperless-media \
  paperless-ngx_paperless-redis-data \
  rag-anything_rag-anything-output \
  rag-anything_rag-anything-storage \
  deploy_xtts-models \
  wordpress-jesuishyperphagique_mysql-jesuishyperphagique-data \
  wordpress-jesuishyperphagique_wordpress-jesuishyperphagique-data \
  wordpress-panneauxsolidaires_mysql-panneauxsolidaires-data \
  wordpress-panneauxsolidaires_wordpress-panneauxsolidaires-data \
  wordpress-solidarlink_mysql-data \
  wordpress-solidarlink_mysql-solidarlink-data \
  wordpress-solidarlink_wordpress-data \
  wordpress-solidarlink_wordpress-solidarlink-data \
  wordpress-shared-db_mysql-wordpress-shared-data
```

### Pour identifier un service utilisateur de `redis-shared`

```bash
# Voir les connexions actives
docker exec redis-shared redis-cli CLIENT LIST

# Voir les clés utilisées
docker exec redis-shared redis-cli KEYS '*'
```

### Pour identifier un service utilisateur de `postgresql-shared`

```bash
# Lister les bases de données
docker exec postgresql-shared psql -U postgres -c '\l'

# Lister les connexions actives
docker exec postgresql-shared psql -U postgres -c "SELECT datname, usename, client_addr FROM pg_stat_activity WHERE state = 'active';"
```

---

## 📝 Notes de Maintenance

**Dernière optimisation**: 27 octobre 2025
- Elasticsearch heap: 8GB → 1GB (-3.5 GB RAM)
- Services arrêtés: 13 conteneurs (-1.5 GB RAM)
- Docker images nettoyées: -84.5 GB disque
- Logs nettoyés: -1.6 GB disque

**Services critiques actifs**:
- ✅ RAGFlow (complet)
- ✅ energie-40eur-dashboard (DownTo40 projet)
- ✅ databases-shared (infrastructure)
- ✅ langchain + telegram/discord bots
- ✅ whisperx workers

**À investiguer**:
- ⚠️ human-chain-backend (unhealthy)
- ⚠️ discord-voice-bot (unhealthy)
- ⚠️ mongodb-shared (aucun service actif, peut être supprimé)

---

**Dernière mise à jour**: 27 octobre 2025 - 16h15
