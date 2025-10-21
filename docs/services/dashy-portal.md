# Dashy - Portail Centralisé de Services

**URL:** https://dashy.srv759970.hstgr.cloud
**Version:** Dashy v3.1.1
**Container:** `dashy`
**Configuration:** `/opt/dashy/conf.yml`
**Docker Compose:** `/opt/dashy/docker-compose.yml`

## Vue d'Ensemble

Dashy est un dashboard de navigation centralisé offrant un accès rapide à **tous les services** déployés sur srv759970.hstgr.cloud.

### Statistiques

- **30+ services** organisés en 13 catégories
- **8+ APIs** avec documentation Swagger/OpenAPI
- **40+ conteneurs** Docker monitorés
- **13 services** protégés par Basic Auth
- **Status checks** temps réel (interval: 5 minutes)

## Catégories de Services

### 🎤 APIs de Transcription (Speech-to-Text)

| Service | URL | Description |
|---------|-----|-------------|
| **WhisperX API** | [/docs](https://whisperx.srv759970.hstgr.cloud/docs) | Transcription avec diarization (pyannote-audio) |
| **Faster-Whisper Queue** | [/docs](https://faster-whisper.srv759970.hstgr.cloud/docs) | Transcription async avec RQ |
| **Faster-Whisper Direct** | [/docs](https://whisper.srv759970.hstgr.cloud/docs) | Transcription rapide OpenAI-compatible |

### 🤖 APIs AI & Machine Learning

| Service | URL | Description |
|---------|-----|-------------|
| **Ollama LLM** | [API](https://ollama.srv759970.hstgr.cloud) | Inférence LLM locale (qwen2.5, mistral, llama) |
| **NeuTTS-Air API** | [/docs](https://neutts-api.srv759970.hstgr.cloud/docs) | TTS avec voice cloning |
| **NeuTTS-Air UI** | [App](https://neutts.srv759970.hstgr.cloud) | Interface Streamlit pour TTS |

### 📚 APIs RAG & Semantic Search

| Service | URL | Description |
|---------|-----|-------------|
| **RAGFlow** | [App](https://ragflow.srv759970.hstgr.cloud) | RAG avancé (ES, MySQL, Redis, MinIO) |
| **RAG-Anything** | [/docs](https://rag-anything.srv759970.hstgr.cloud/docs) | Multimodal RAG avec knowledge graph |
| **MemVid RAG** | [/docs](https://memvid.srv759970.hstgr.cloud/docs) | RAG sémantique avec encodage vidéo |

### 🔧 APIs Utilitaires

| Service | URL | Description |
|---------|-----|-------------|
| **Apache Tika** | [API](https://tika.srv759970.hstgr.cloud) | Parsing 1000+ formats documents |
| **Portail Swagger Unifié** | [UI](https://portal.srv759970.hstgr.cloud/api) | Swagger UI centralisé |

### 📊 Monitoring & Observabilité

| Service | URL | Description |
|---------|-----|-------------|
| **Grafana** | [Dashboard](https://monitoring.srv759970.hstgr.cloud) | Prometheus + Loki |
| **Prometheus** | [Metrics](http://srv759970.hstgr.cloud:9090) | Time-series metrics |
| **RQ Dashboard** | [Jobs](https://whisperx-dashboard.srv759970.hstgr.cloud) | Redis Queue monitoring |
| **Dozzle** | [Logs](https://dozzle.srv759970.hstgr.cloud) | Docker logs temps réel |
| **Netdata** | [System](http://srv759970.hstgr.cloud:19999) | Métriques système |
| **Portainer** | [Admin](http://srv759970.hstgr.cloud:9000) | Gestion Docker GUI |

### 🌐 Applications Web & Dashboards

| Service | URL | Description |
|---------|-----|-------------|
| **Support Dashboard** | [App](https://dashboard.srv759970.hstgr.cloud) | IT Support (Streamlit) |
| **SharePoint Dashboards** | [App](https://sharepoint.srv759970.hstgr.cloud) | Analytics SharePoint |
| **API & Admin Portal** | [Portal](https://portal.srv759970.hstgr.cloud) | Documentation centralisée |

### 🏢 Sites Web & CMS

| Service | URL | Description |
|---------|-----|-------------|
| **Cristina Site** | [Site](https://cristina.srv759970.hstgr.cloud) | Site Astro SSG |
| **Cristina Admin (Strapi)** | [Admin](https://admin.cristina.srv759970.hstgr.cloud/admin) | CMS Strapi 5 |
| **Clémence Site** | [Site](https://clemence.srv759970.hstgr.cloud) | WordPress Docker |
| **SolidarLink** | [Site](https://solidarlink.srv759970.hstgr.cloud) | WordPress natif |

### 📖 Documentation & Portails

| Service | URL | Description |
|---------|-----|-------------|
| **MkDocs Documentation** | [Docs](https://docs.srv759970.hstgr.cloud) | Documentation technique (60+ guides) |
| **Dashy Dashboard** | [Portal](https://dashy.srv759970.hstgr.cloud) | Ce portail |

### 🔗 Liens Rapides - Swagger/OpenAPI

Section dédiée avec tous les endpoints de documentation interactive:

- **WhisperX:** [Swagger UI](https://whisperx.srv759970.hstgr.cloud/docs) | [ReDoc](https://whisperx.srv759970.hstgr.cloud/redoc)
- **Faster-Whisper Queue:** [Swagger UI](https://faster-whisper.srv759970.hstgr.cloud/docs) | [ReDoc](https://faster-whisper.srv759970.hstgr.cloud/redoc)
- **Faster-Whisper Direct:** [Swagger UI](https://whisper.srv759970.hstgr.cloud/docs)
- **NeuTTS-Air:** [Swagger UI](https://neutts-api.srv759970.hstgr.cloud/docs)
- **MemVid RAG:** [Swagger UI](https://memvid.srv759970.hstgr.cloud/docs)
- **RAG-Anything:** [Swagger UI](https://rag-anything.srv759970.hstgr.cloud/docs)
- **Portail Unifié:** [Multi-API Swagger](https://portal.srv759970.hstgr.cloud/api)

## Configuration

### Structure du Fichier conf.yml

```yaml
pageInfo:
  title: srv759970 Services Portal
  description: Portail Centralisé - APIs, Applications & Infrastructure
  navLinks:
    - title: GitHub
      path: https://github.com/julienfernandez
    - title: Documentation Technique
      path: https://docs.srv759970.hstgr.cloud
    - title: Analyse Auth Strategy
      path: https://docs.srv759970.hstgr.cloud/analysis/auth-strategy-oauth-vs-basic/

appConfig:
  theme: colorful
  layout: auto
  iconSize: medium
  language: fr
  statusCheck: true
  statusCheckInterval: 300  # 5 minutes
  defaultOpeningMethod: newtab
```

### Sections Principales

1. **APIs de Transcription** (3 services)
2. **APIs AI & ML** (3 services)
3. **APIs RAG & Search** (3 services)
4. **APIs Utilitaires** (2 services)
5. **Monitoring** (6 services)
6. **Applications Web** (3 services)
7. **Sites Web & CMS** (4 services)
8. **Documentation** (2 services)
9. **Infrastructure** (6 composants)
10. **Sécurité** (3 composants)
11. **Services RAG** (5 composants)
12. **Liens Swagger** (9 endpoints)
13. **Informations Serveur** (3 infos)

## Status Checks

Dashy vérifie automatiquement l'état de tous les services toutes les **5 minutes**.

### Health Check Endpoints

```yaml
# Exemple WhisperX
statusCheck: true
statusCheckUrl: https://whisperx.srv759970.hstgr.cloud/

# Exemple Prometheus
statusCheck: true
statusCheckUrl: http://srv759970.hstgr.cloud:9090/-/healthy
```

### Indicateurs d'État

- 🟢 **Vert:** Service accessible et opérationnel
- 🔴 **Rouge:** Service inaccessible ou erreur
- ⚪ **Gris:** Status check désactivé

## Déploiement

### Docker Compose

```yaml
# /opt/dashy/docker-compose.yml
version: '3.8'

services:
  dashy:
    image: lissy93/dashy:latest
    container_name: dashy
    restart: unless-stopped
    ports:
      - "4000:80"
    volumes:
      - ./conf.yml:/app/public/conf.yml
      - dashy-icons:/app/public/item-icons
    environment:
      - NODE_ENV=production
    healthcheck:
      test: ["CMD", "node", "/app/services/healthcheck"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  dashy-icons:
```

### Commandes de Gestion

```bash
# Démarrer Dashy
cd /opt/dashy
docker-compose up -d

# Redémarrer après modification config
docker-compose restart

# Voir les logs
docker-compose logs -f

# Vérifier le status
docker-compose ps

# Rebuild complet
docker-compose down
docker-compose up -d --build
```

## Nginx Configuration

```nginx
# /etc/nginx/sites-available/dashy
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name dashy.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/faster-whisper.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/faster-whisper.srv759970.hstgr.cloud/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Basic Auth
    include snippets/basic-auth.conf;

    location / {
        proxy_pass http://127.0.0.1:4000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;

        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTP -> HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name dashy.srv759970.hstgr.cloud;
    return 301 https://$host$request_uri;
}
```

## Personnalisation

### Ajouter un Nouveau Service

1. Éditer `/opt/dashy/conf.yml`
2. Ajouter l'item dans la section appropriée:

```yaml
- title: Mon Nouveau Service
  description: Description du service
  icon: fas fa-rocket  # Font Awesome icon
  url: https://service.srv759970.hstgr.cloud
  target: newtab
  statusCheck: true
  statusCheckUrl: https://service.srv759970.hstgr.cloud/health
  tags: [API, Custom, HTTPS]
```

3. Redémarrer Dashy:

```bash
cd /opt/dashy
docker-compose restart
```

### Icons Disponibles

- **Font Awesome:** `fas fa-icon-name`
- **Homelab Icons:** `hl-service-name` (ex: `hl-docker`, `hl-grafana`)
- **Material Design Icons:** `mdi-icon-name`
- **Custom Images:** Placer dans `/app/public/item-icons/`

### Thèmes Disponibles

```yaml
theme: colorful      # (Actuel)
# Alternatives:
# theme: default
# theme: material-dark
# theme: material-light
# theme: nord
# theme: nord-frost
# theme: dracula
# theme: high-contrast-dark
# theme: high-contrast-light
```

## Widgets

### Clock Widget (Infrastructure Section)

```yaml
widgets:
  - type: clock
    options:
      timeZone: Europe/Paris
      format: fr-FR
      hideDate: false
```

### Autres Widgets Disponibles

- **Weather:** Météo locale
- **RSS Feed:** Flux RSS
- **iFrame:** Embed sites externes
- **System Info:** Infos système
- **Image:** Affichage d'images

## Maintenance

### Mise à Jour Dashy

```bash
cd /opt/dashy
docker-compose pull
docker-compose up -d
```

### Backup Configuration

```bash
# Backup conf.yml
cp /opt/dashy/conf.yml /opt/dashy/conf.yml.backup-$(date +%Y%m%d)

# Backup complet
tar -czf /root/backups/dashy-$(date +%Y%m%d).tar.gz /opt/dashy/
```

### Validation Configuration

```bash
# Vérifier la syntaxe YAML
docker run --rm -v /opt/dashy/conf.yml:/conf.yml mikefarah/yq eval /conf.yml

# Voir les logs de build
docker logs dashy --tail 50
```

## Troubleshooting

### Build Errors

**Symptôme:** Build échoue avec erreur OpenSSL

**Solution:** Utiliser Node.js legacy OpenSSL (déjà configuré)

```yaml
environment:
  - NODE_OPTIONS=--openssl-legacy-provider
```

### Status Checks Timeout

**Symptôme:** Services marqués comme "down" alors qu'ils fonctionnent

**Solution:** Augmenter l'intervalle de check

```yaml
appConfig:
  statusCheckInterval: 600  # 10 minutes au lieu de 5
```

### Services Inaccessibles

**Symptôme:** 401 Unauthorized sur certains services

**Solution:** Vérifier Basic Auth dans Nginx

```bash
# Test sans auth
curl -I https://whisperx.srv759970.hstgr.cloud

# Test avec auth
curl -I -u julien:DevAccess2025 https://whisperx.srv759970.hstgr.cloud
```

## Sécurité

### Basic Auth Protection

Dashy est protégé par HTTP Basic Authentication:

- **Username:** `julien`
- **Password:** `DevAccess2025`
- **Fichier:** `/etc/nginx/.htpasswd`

### HTTPS/TLS

- **Certificat:** Let's Encrypt
- **Expiration:** 2026-01-18
- **Auto-renewal:** Activé via Certbot

### Recommandations

1. ✅ **Garder Basic Auth** pour accès sécurisé
2. ✅ **Envisager Tailscale VPN** pour accès network-level (voir [Analyse Auth Strategy](../analysis/auth-strategy-oauth-vs-basic.md))
3. ⚠️ **Ne pas exposer** Dashy sans authentification

## Statistiques

### Métriques de Configuration Actuelle

- **Total Items:** 60+ services et composants
- **Sections:** 13 catégories
- **Swagger Endpoints:** 9 APIs documentées
- **Status Checks:** 35+ endpoints monitorés
- **Taille Config:** ~400 lignes YAML

### Performance

- **Build Time:** ~30-40 secondes
- **Page Load:** < 2 secondes
- **Status Check Interval:** 5 minutes
- **Bundle Size:** ~13MB (prod build)

## Voir Aussi

- [Infrastructure > Nginx](../infrastructure/nginx.md) - Configuration reverse proxy
- [Infrastructure > Security](../infrastructure/security.md) - Basic Auth setup
- [Analysis > Auth Strategy](../analysis/auth-strategy-oauth-vs-basic.md) - OAuth vs Basic Auth
- [MkDocs Documentation](https://docs.srv759970.hstgr.cloud) - Documentation complète

## Liens Externes

- **Dashy Official Docs:** https://dashy.to/docs
- **GitHub Repository:** https://github.com/Lissy93/dashy
- **Icon Sets:** https://dashy.to/docs/icons

---

**Dernière mise à jour:** 2025-01-21
**Prochaine révision:** Après ajout de nouveaux services
