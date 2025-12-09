# XTTS-v2 - Synthèse Vocale avec Clonage de Voix

## Vue d'ensemble

XTTS-v2 (eXtended Text-to-Speech) est un système de synthèse vocale avancé avec capacité de clonage de voix développé par Coqui AI. Il permet de générer de la parole dans **17 langues** à partir de seulement **6 secondes d'audio de référence**.

### Caractéristiques principales

- **Clonage vocal ultra-rapide** : 6-30 secondes d'audio suffisent
- **Support multilingue** : 17 langues dont français, anglais, espagnol, allemand, italien, arabe, chinois, japonais
- **Qualité audio** : 24kHz mono WAV
- **Clonage cross-langue** : Utilisez une voix en français pour parler en anglais
- **API REST** : FastAPI avec endpoints `/synthesize` et `/stream`
- **Interface web** : Streamlit avec enregistrement vocal intégré

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Nginx (Reverse Proxy)                     │
│  xtts-api.srv759970.hstgr.cloud + xtts.srv759970.hstgr.cloud│
│                     SSL/TLS (Let's Encrypt)                  │
└────────────────┬──────────────────────┬──────────────────────┘
                 │                      │
                 │                      │
        ┌────────▼────────┐    ┌───────▼────────┐
        │   xtts-api      │    │ xtts-streamlit  │
        │   Port: 8004    │    │  Port: 8501     │
        │   FastAPI       │    │  Streamlit UI   │
        └────────┬────────┘    └─────────────────┘
                 │
                 │
        ┌────────▼────────────────────────────┐
        │  Prometheus Metrics (/metrics)      │
        │  - Synthesis requests counter       │
        │  - Duration histogram               │
        │  - Audio size histogram             │
        │  - Model loaded gauge               │
        └─────────────────────────────────────┘
                 │
                 │
        ┌────────▼────────────────────────────┐
        │  Loki Logs (via Promtail)          │
        │  - Container logs                   │
        │  - API requests/errors              │
        └─────────────────────────────────────┘
```

## Endpoints API

### GET /

Informations générales sur l'API

**Réponse :**
```json
{
  "name": "XTTS-v2 API",
  "version": "1.0.0",
  "supported_languages": ["fr", "en", "es", ...],
  "model_loaded": true,
  "device": "cpu"
}
```

### GET /health

Vérification de l'état de santé de l'API

**Réponse :**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cpu"
}
```

### GET /languages

Liste complète des langues supportées

**Réponse :**
```json
{
  "supported_languages": ["fr", "en", "es", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh", "hu", "ko", "ja", "hi"],
  "count": 17,
  "languages_details": {
    "fr": "Français",
    "en": "English",
    ...
  }
}
```

### POST /synthesize

Synthèse vocale standard avec clonage de voix

**Paramètres (multipart/form-data) :**
- `text` (string, requis) : Texte à synthétiser
- `language` (string, défaut: "fr") : Code langue (fr, en, es, etc.)
- `reference_audio` (file, requis) : Fichier audio de référence (WAV, MP3, FLAC)

**Exemple cURL :**
```bash
curl -X POST https://xtts-api.srv759970.hstgr.cloud/synthesize \
  -F "text=Bonjour, ceci est un test de synthèse vocale" \
  -F "language=fr" \
  -F "reference_audio=@ma_voix.wav" \
  -o resultat.wav
```

**Réponse :** Fichier audio WAV 24kHz mono

### POST /stream

Synthèse vocale en mode streaming (optimisé pour textes longs)

**Paramètres :**
- `text` (string, requis)
- `language` (string, défaut: "fr")
- `reference_audio` (file, requis)
- `enable_text_splitting` (bool, défaut: true)

**Exemple cURL :**
```bash
curl -X POST https://xtts-api.srv759970.hstgr.cloud/stream \
  -F "text=Texte très long à synthétiser..." \
  -F "language=fr" \
  -F "reference_audio=@ma_voix.wav" \
  -F "enable_text_splitting=true" \
  -o resultat_stream.wav
```

### GET /metrics

Métriques Prometheus pour le monitoring

**Métriques disponibles :**
- `xtts_synthesis_requests_total` : Nombre total de requêtes (labels: language, endpoint, status)
- `xtts_synthesis_duration_seconds` : Durée des synthèses (histogram)
- `xtts_audio_output_bytes` : Taille des fichiers générés (histogram)
- `xtts_model_loaded` : État du modèle (1=chargé, 0=non chargé)

## Interface Web Streamlit

L'interface Streamlit est accessible à : **https://xtts.srv759970.hstgr.cloud**

### Onglets disponibles

#### 🎙️ Synthèse Rapide
- Upload d'audio de référence
- Sélection de langue
- Saisie de texte
- Choix du mode (Standard / Streaming)
- Génération et téléchargement

#### 🎤 Enregistrer ma Voix
- **Enregistrement vocal direct depuis le navigateur**
- Utilise `st.audio_input()` (Streamlit 1.50.0+)
- Aperçu et téléchargement de l'enregistrement
- Test de clonage immédiat
- Sauvegarde en session pour réutilisation

#### 📢 Lecture de Texte
- **Faire lire n'importe quel texte**
- Deux sources de voix :
  - Voix enregistrée (depuis l'onglet précédent)
  - Upload de fichier
- Textes pré-définis (conte, actualités, poésie)
- Lecture et téléchargement du résultat

#### 📊 Test de Langues
- Test multi-langues simultané
- Même audio de référence pour toutes les langues
- Textes de test pré-configurés par langue

#### ⚙️ Paramètres Avancés
- Informations API
- Liste des langues
- Documentation endpoints
- Exemples cURL

## Déploiement

### Pré-requis

- Docker et Docker Compose
- Nginx avec SSL (Let's Encrypt)
- Prometheus, Grafana, Loki (monitoring)
- Minimum 4 GB RAM (8 GB recommandé)
- ~2 GB d'espace disque pour le modèle XTTS-v2

### Structure des fichiers

```
/opt/coqui-tts/deploy/
├── api.py                  # FastAPI server
├── streamlit_app.py        # Interface Streamlit
├── Dockerfile              # Image Docker pour l'API
├── docker-compose.yml      # Orchestration des services
├── samples/                # Fichiers audio de test
├── outputs/                # Fichiers générés
└── nginx-xtts.conf        # Configuration Nginx
```

### Installation

1. **Cloner le dépôt local vers le serveur**

```bash
# Sur le serveur
mkdir -p /opt/coqui-tts/deploy
cd /opt/coqui-tts/deploy

# Copier les fichiers depuis votre machine locale
scp api.py streamlit_app.py Dockerfile docker-compose.yml root@srv759970:/opt/coqui-tts/deploy/
```

2. **Créer les répertoires**

```bash
mkdir -p samples outputs
```

3. **Démarrer les services**

```bash
docker-compose up -d
```

Le premier démarrage télécharge le modèle XTTS-v2 (1.87 GB) depuis Hugging Face. Cela prend **3-5 minutes**.

4. **Configurer SSL avec Certbot**

```bash
# Certificat pour l'API
certbot certonly --nginx -d xtts-api.srv759970.hstgr.cloud

# Certificat pour l'interface (utilise le même certificat)
certbot certonly --nginx -d xtts.srv759970.hstgr.cloud \
  --cert-name xtts-api.srv759970.hstgr.cloud
```

5. **Configurer Nginx**

```bash
# Copier la configuration
cp nginx-xtts.conf /etc/nginx/sites-available/xtts
ln -s /etc/nginx/sites-available/xtts /etc/nginx/sites-enabled/

# Tester et recharger
nginx -t
systemctl reload nginx
```

### Vérification du déploiement

```bash
# Vérifier les conteneurs
docker ps --filter name=xtts

# Vérifier les logs
docker logs xtts-api --tail 50
docker logs xtts-streamlit --tail 50

# Tester l'API
curl -s https://xtts-api.srv759970.hstgr.cloud/health | jq .

# Tester l'interface
curl -I https://xtts.srv759970.hstgr.cloud
```

## Configuration Docker

### docker-compose.yml

```yaml
version: '3.8'

services:
  xtts-api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: xtts-api
    restart: unless-stopped
    ports:
      - "8004:8004"
    volumes:
      - ./samples:/app/samples
      - ./outputs:/app/outputs
      - xtts-models:/app/models
      - /root/.cache/huggingface:/root/.cache/huggingface
    environment:
      - PYTHONUNBUFFERED=1
      - COQUI_TOS_AGREED=1
      - HF_HOME=/root/.cache/huggingface
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8004/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 360s  # 6 minutes pour le chargement du modèle
    networks:
      - xtts-network
      - monitoring_monitoring
    labels:
      - "prometheus.scrape=true"
      - "prometheus.port=8004"
      - "prometheus.path=/metrics"

  xtts-streamlit:
    image: python:3.10-slim
    container_name: xtts-streamlit
    restart: unless-stopped
    ports:
      - "8501:8501"
    volumes:
      - ./streamlit_app.py:/app/streamlit_app.py
      - ./samples:/app/samples
    working_dir: /app
    environment:
      - XTTS_API_URL=http://xtts-api:8004
    command: >
      sh -c "pip install --no-cache-dir streamlit requests &&
             streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.maxUploadSize 200"
    depends_on:
      - xtts-api
    networks:
      - xtts-network

volumes:
  xtts-models:
    driver: local

networks:
  xtts-network:
    name: xtts-network
  monitoring_monitoring:
    external: true
```

### Points importants

- **start_period: 360s** : Le modèle XTTS-v2 prend 3-5 minutes à charger. Le healthcheck attend 6 minutes avant de commencer les vérifications.
- **HF_HOME** : Cache Hugging Face pour éviter de re-télécharger le modèle
- **monitoring_monitoring** : Réseau externe pour Prometheus/Loki
- **maxUploadSize: 200** : Permet l'upload de fichiers audio jusqu'à 200 MB

## Sécurité

### SSL/TLS

- **Certificats Let's Encrypt** via Certbot
- **Renouvellement automatique** : `certbot renew --dry-run`
- **Protocoles** : TLS 1.2, TLS 1.3
- **Ciphers** : Configuration Mozilla Modern

Configuration Nginx :
```nginx
ssl_certificate /etc/letsencrypt/live/xtts-api.srv759970.hstgr.cloud/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/xtts-api.srv759970.hstgr.cloud/privkey.pem;
include /etc/letsencrypt/options-ssl-nginx.conf;
ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
```

### Nginx (Reverse Proxy)

```nginx
# API XTTS-v2
server {
    listen 443 ssl http2;
    server_name xtts-api.srv759970.hstgr.cloud;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/xtts-api.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/xtts-api.srv759970.hstgr.cloud/privkey.pem;

    access_log /var/log/nginx/xtts-api-access.log;
    error_log /var/log/nginx/xtts-api-error.log;

    location / {
        proxy_pass http://127.0.0.1:8004;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts pour synthèse longue
        proxy_read_timeout 600;
        proxy_connect_timeout 600;
        proxy_send_timeout 600;

        # Upload de fichiers audio
        client_max_body_size 200M;
    }
}

# Interface Streamlit
server {
    listen 443 ssl http2;
    server_name xtts.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/xtts-api.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/xtts-api.srv759970.hstgr.cloud/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Host $host;

        # WebSocket support for Streamlit
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_read_timeout 86400;
        client_max_body_size 200M;
    }

    location /_stcore/stream {
        proxy_pass http://127.0.0.1:8501/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### Basic Auth (optionnel)

Pour protéger l'interface Streamlit avec Basic Auth :

```nginx
location / {
    auth_basic "XTTS-v2 Interface";
    auth_basic_user_file /etc/nginx/.htpasswd;

    proxy_pass http://127.0.0.1:8501;
    # ... reste de la config
}
```

Créer le fichier .htpasswd :
```bash
htpasswd -c /etc/nginx/.htpasswd username
```

## Monitoring

### Prometheus

Le service XTTS-v2 expose des métriques Prometheus sur `http://xtts-api:8004/metrics`.

**Configuration Prometheus** (`/opt/monitoring/prometheus/prometheus.yml`) :

```yaml
scrape_configs:
  - job_name: 'xtts-api'
    static_configs:
      - targets: ['xtts-api:8004']
        labels:
          service: 'xtts'
          env: 'production'
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'xtts-api'
```

### Grafana

Dashboards recommandés :

**1. XTTS-v2 Performance**
- Nombre de requêtes par langue
- Durée moyenne de synthèse
- Taille moyenne des audios générés
- Taux d'erreur par endpoint

**Exemples de requêtes PromQL :**

```promql
# Nombre de requêtes par minute
rate(xtts_synthesis_requests_total[5m])

# Durée moyenne de synthèse par langue
histogram_quantile(0.95,
  rate(xtts_synthesis_duration_seconds_bucket[5m])
) by (language)

# Taux d'erreur
sum(rate(xtts_synthesis_requests_total{status="error"}[5m]))
/
sum(rate(xtts_synthesis_requests_total[5m]))

# Taille moyenne des fichiers audio
avg(rate(xtts_audio_output_bytes_sum[5m]))
```

**2. XTTS-v2 Health**
- État du modèle (chargé/non chargé)
- Statut des conteneurs
- Utilisation CPU/RAM
- Logs d'erreur

### Loki

Les logs des conteneurs sont collectés via Promtail et envoyés à Loki.

**Configuration Promtail** (`/opt/monitoring/loki/promtail-config.yml`) :

```yaml
scrape_configs:
  - job_name: xtts
    static_configs:
      - targets:
          - localhost
        labels:
          job: xtts-logs
          __path__: /var/lib/docker/containers/*-xtts-*/*.log
    pipeline_stages:
      - json:
          expressions:
            output: log
            stream: stream
            attrs: attrs
      - labels:
          stream:
```

**Requêtes LogQL utiles :**

```logql
# Erreurs dans les logs XTTS
{job="xtts-logs"} |= "ERROR"

# Requêtes de synthèse
{job="xtts-logs"} |= "Synthesizing text"

# Temps de chargement du modèle
{job="xtts-logs"} |= "Model loaded successfully"

# Erreurs HTTP 500
{job="xtts-logs"} |= "status_code=500"
```

## Performance

### Benchmarks

Sur un serveur CPU (sans GPU) :

| Durée texte | Temps synthèse | Ratio temps réel |
|-------------|----------------|------------------|
| 10s         | ~30-60s        | 3-6x             |
| 30s         | ~90-180s       | 3-6x             |
| 60s         | ~180-360s      | 3-6x             |

Sur un serveur GPU (NVIDIA) :

| Durée texte | Temps synthèse | Ratio temps réel |
|-------------|----------------|------------------|
| 10s         | ~3-10s         | 0.3-1x           |
| 30s         | ~9-30s         | 0.3-1x           |
| 60s         | ~18-60s        | 0.3-1x           |

### Optimisations

1. **GPU** : Pour des performances optimales, décommenter la section GPU dans `docker-compose.yml` :

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

2. **Cache modèle** : Le modèle est mis en cache dans `/root/.cache/huggingface` pour éviter les re-téléchargements

3. **Streaming** : Pour les textes longs (>200 mots), utilisez `/stream` au lieu de `/synthesize`

## Dépannage

### Le modèle ne se charge pas

**Symptôme** : `model_loaded: false` dans `/health`

**Solution** :
```bash
# Vérifier les logs
docker logs xtts-api --tail 100

# Redémarrer le conteneur
docker-compose restart xtts-api

# Vérifier l'espace disque
df -h
```

### Container restart loop

**Symptôme** : Le conteneur redémarre en boucle

**Cause** : Healthcheck démarre trop tôt (avant le chargement du modèle)

**Solution** : Augmenter `start_period` dans `docker-compose.yml` :
```yaml
healthcheck:
  start_period: 480s  # 8 minutes au lieu de 6
```

### Erreur "Model download failed"

**Cause** : Problème de connexion à Hugging Face

**Solution** :
```bash
# Tester la connexion
curl -I https://huggingface.co

# Vérifier le cache
ls -lh /root/.cache/huggingface/

# Nettoyer et retélécharger
rm -rf /root/.cache/huggingface/hub/models--coqui--XTTS-v2
docker-compose restart xtts-api
```

### Synthèse très lente (CPU)

**Cause** : Pas de GPU disponible

**Solutions** :
- Ajouter un GPU NVIDIA
- Utiliser un serveur avec GPU (recommandé pour production)
- Accepter le temps de traitement (~3-6x le temps réel sur CPU)

### Erreur "Audio file too large"

**Cause** : `client_max_body_size` trop petit dans Nginx

**Solution** :
```nginx
location / {
    client_max_body_size 200M;  # Augmenter si besoin
    # ...
}
```

Puis recharger Nginx :
```bash
nginx -t && systemctl reload nginx
```

## Maintenance

### Mise à jour du modèle

```bash
# Supprimer le cache
rm -rf /root/.cache/huggingface/hub/models--coqui--XTTS-v2

# Redémarrer (re-télécharge automatiquement)
docker-compose restart xtts-api
```

### Sauvegarde

**Fichiers à sauvegarder** :
- `/opt/coqui-tts/deploy/` : Configuration et code
- `/opt/coqui-tts/deploy/samples/` : Fichiers audio de référence
- Configuration Nginx : `/etc/nginx/sites-available/xtts`

**Pas besoin de sauvegarder** :
- `/root/.cache/huggingface/` : Peut être re-téléchargé
- `/opt/coqui-tts/deploy/outputs/` : Fichiers temporaires

### Restauration

```bash
# Restaurer les fichiers
rsync -av backup/coqui-tts/ /opt/coqui-tts/

# Restaurer Nginx
cp backup/nginx/xtts /etc/nginx/sites-available/
ln -sf /etc/nginx/sites-available/xtts /etc/nginx/sites-enabled/

# Redémarrer
docker-compose up -d
nginx -t && systemctl reload nginx
```

## Licence et Limitations

### Coqui Public Model License (CPML)

XTTS-v2 utilise la licence **Coqui Public Model License** qui impose des restrictions :

- ✅ **Autorisé** : Usage personnel, recherche, éducation, prototypage
- ❌ **Non autorisé** : Usage commercial sans licence commerciale
- ⚠️ **Restriction** : Pas d'utilisation pour générer des revenus sans accord explicite

**Pour un usage commercial**, contacter Idiap Research Institute qui maintient le fork PyPI.

### Alternatives commerciales

Si vous avez besoin d'une licence commerciale :

1. **ElevenLabs** : TTS cloud avec clonage vocal (API payante)
2. **PlayHT** : Service cloud similaire
3. **Coqui Studio** : Version commerciale (si disponible)

## Ressources

### Documentation officielle

- **Coqui TTS (archived)** : https://github.com/coqui-ai/TTS
- **Idiap Fork (maintained)** : https://github.com/idiap/coqui-ai-TTS
- **PyPI Package** : https://pypi.org/project/coqui-tts/
- **Hugging Face Model** : https://huggingface.co/coqui/XTTS-v2

### Exemples et Tutoriels

- **Google Colab Demo** : https://colab.research.google.com/github/coqui-ai/TTS/blob/dev/notebooks/XTTS_v2_demo.ipynb
- **Paper XTTS** : https://arxiv.org/abs/2406.04904

### Support

Pour des questions sur le déploiement sur srv759970 :
- Consulter les logs : `docker logs xtts-api`
- Vérifier Grafana : https://grafana.srv759970.hstgr.cloud
- Consulter la documentation : https://docs.srv759970.hstgr.cloud

## Changelog

### v1.0.0 (2025-10-21)

- Déploiement initial XTTS-v2
- FastAPI avec endpoints `/synthesize` et `/stream`
- Interface Streamlit avec 5 onglets
- **Enregistrement vocal direct** depuis le navigateur
- **Lecture de texte** avec voix uploadée ou enregistrée
- Support de 17 langues
- Intégration Prometheus/Grafana/Loki
- SSL/TLS avec Let's Encrypt
- Nginx reverse proxy
- Healthcheck avec `start_period: 360s`
