# Guide Monitoring WhisperX avec Grafana + Prometheus + Loki

## Vue d'ensemble

Stack de monitoring complète pour WhisperX avec métriques temps réel et logs centralisés.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Grafana Dashboard                        │
│              https://monitoring.srv759970.hstgr.cloud        │
│  ┌──────────────────────────┬──────────────────────────┐   │
│  │   Prometheus Datasource  │   Loki Datasource        │   │
│  │   (Métriques RQ)         │   (Logs Docker)          │   │
│  └──────────────────────────┴──────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │                                │
         ▼                                ▼
┌──────────────────┐            ┌──────────────────┐
│   Prometheus     │            │      Loki        │
│   :9090          │            │      :3100       │
└──────────────────┘            └──────────────────┘
         │                                │
         ▼                                ▼
┌──────────────────┐            ┌──────────────────┐
│  RQ Exporter     │            │    Promtail      │
│  :9726           │            │                  │
└──────────────────┘            └──────────────────┘
         │                                │
         ▼                                ▼
┌──────────────────┐            ┌──────────────────┐
│  Redis Queue     │            │  Docker Logs     │
│  (WhisperX)      │            │  (whisperx-*)    │
└──────────────────┘            └──────────────────┘
```

## Composants

### 1. Prometheus (Métriques)
- **Port** : 9090
- **Fonction** : Collecte et stocke les métriques time-series
- **Rétention** : 30 jours
- **Scrape interval** : 15 secondes

### 2. RQ Exporter (Exporteur Redis Queue)
- **Port** : 9726
- **Image** : `mdawar/rq-exporter:latest`
- **Fonction** : Exporte les métriques RQ vers Prometheus
- **Métriques exposées** :
  - `rq_workers` : Nombre de workers actifs
  - `rq_jobs{status="queued|started|finished|failed"}` : Compteurs de jobs par statut
  - `rq_queue_length` : Longueur des queues
  - `rq_workers_success_total` : Total des succès
  - `rq_workers_failed_total` : Total des échecs

### 3. Loki (Logs)
- **Port** : 3100
- **Fonction** : Agrégation et stockage de logs
- **Rétention** : 7 jours (168h)
- **Storage** : Filesystem local

### 4. Promtail (Collecteur de logs)
- **Fonction** : Collecte logs Docker et envoie à Loki
- **Cibles** :
  - `whisperx-worker` : Logs du worker RQ
  - `whisperx` : Logs de l'API FastAPI

### 5. Grafana (Visualisation)
- **Port** : 3001 (mappé sur 3000 interne)
- **URL** : https://monitoring.srv759970.hstgr.cloud
- **Version** : 12.2.0
- **Credentials** :
  - User : `admin`
  - Password : `YourSecurePassword2025!`

## Installation

### Structure des fichiers

```
/opt/monitoring/
├── docker-compose.yml
├── prometheus/
│   └── prometheus.yml
├── loki/
│   └── loki-config.yml
├── promtail/
│   └── promtail-config.yml
└── grafana/
    └── provisioning/
        ├── datasources/
        │   └── datasources.yml
        └── dashboards/
            └── dashboards.yml
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
    ports:
      - '9090:9090'
    networks:
      - monitoring

  rq-exporter:
    image: mdawar/rq-exporter:latest
    container_name: rq-exporter
    restart: unless-stopped
    environment:
      - RQ_REDIS_HOST=whisperx-redis
      - RQ_REDIS_PORT=6379
      - RQ_REDIS_DB=0
    ports:
      - '9726:9726'
    networks:
      - monitoring
      - whisperx_default

  loki:
    image: grafana/loki:latest
    container_name: loki
    restart: unless-stopped
    ports:
      - '3100:3100'
    volumes:
      - ./loki/loki-config.yml:/etc/loki/local-config.yaml
      - loki-data:/loki
    command: -config.file=/etc/loki/local-config.yaml
    networks:
      - monitoring

  promtail:
    image: grafana/promtail:latest
    container_name: promtail
    restart: unless-stopped
    volumes:
      - ./promtail/promtail-config.yml:/etc/promtail/config.yml
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock
    command: -config.file=/etc/promtail/config.yml
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    ports:
      - '3001:3000'
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=YourSecurePassword2025!
      - GF_INSTALL_PLUGINS=redis-datasource
      - GF_SERVER_ROOT_URL=https://monitoring.srv759970.hstgr.cloud
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    networks:
      - monitoring

volumes:
  prometheus-data:
  grafana-data:
  loki-data:

networks:
  monitoring:
    driver: bridge
  whisperx_default:
    external: true
```

### Démarrage

```bash
cd /opt/monitoring
docker-compose up -d
```

### Vérification

```bash
# Status des conteneurs
docker-compose ps

# Health check complet
docker ps --filter name='prometheus|loki|promtail|rq-exporter|grafana'

# Métriques RQ disponibles
curl http://localhost:9726/metrics | grep rq_

# Prometheus targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job, health}'
```

## Configuration Nginx

### Certificat SSL

```bash
certbot certonly --nginx \
  -d monitoring.srv759970.hstgr.cloud \
  --non-interactive \
  --agree-tos \
  -m julien@julienfernandez.xyz
```

### /etc/nginx/sites-available/monitoring

```nginx
# HTTPS - Grafana Monitoring
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name monitoring.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/monitoring.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/monitoring.srv759970.hstgr.cloud/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        include snippets/basic-auth.conf;

        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_read_timeout 300;
    }
}

# HTTP -> HTTPS
server {
    listen 80;
    server_name monitoring.srv759970.hstgr.cloud;
    return 301 https://$host$request_uri;
}
```

Activation :

```bash
ln -sf /etc/nginx/sites-available/monitoring /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

## Utilisation de Grafana

### Connexion

1. Accéder à https://monitoring.srv759970.hstgr.cloud
2. Entrer les credentials basic auth (serveur)
3. Login Grafana : `admin` / `YourSecurePassword2025!`

### Datasources pré-configurées

Les datasources sont automatiquement provisionnées au démarrage :

1. **Prometheus** (défaut)
   - URL : `http://prometheus:9090`
   - Métriques RQ disponibles

2. **Loki**
   - URL : `http://loki:3100`
   - Logs des conteneurs WhisperX

### Importer le dashboard RQ

1. Menu → Dashboards → Import
2. Entrer l'ID : **12196**
3. Sélectionner datasource Prometheus
4. Import

Le dashboard affiche :
- Nombre de workers actifs/idle
- Jobs par statut (queued, started, finished, failed)
- Longueur des queues
- Taux de succès/échec
- Temps d'exécution moyen

### Créer un panel de logs

1. Create → Dashboard → Add visualization
2. Datasource : Loki
3. Query :
   ```logql
   {container="whisperx-worker"}
   ```
4. Options :
   - Show time : Oui
   - Wrap lines : Oui
   - Prettify JSON : Oui

### Requêtes utiles

#### Prometheus (Métriques)

```promql
# Nombre total de jobs terminés
rq_jobs{queue="transcription",status="finished"}

# Nombre de jobs en cours
rq_jobs{queue="transcription",status="started"}

# Taux d'échec (%)
(rq_jobs{status="failed"} / (rq_jobs{status="finished"} + rq_jobs{status="failed"})) * 100

# Workers actifs
rq_workers{queue="transcription"}
```

#### Loki (Logs)

```logql
# Logs du worker WhisperX
{container="whisperx-worker"}

# Logs avec erreur
{container="whisperx-worker"} |= "ERROR"

# Logs de transcription
{container="whisperx-worker"} |= "Transcribing"

# Logs de l'API
{container="whisperx"} | json
```

## Monitoring des jobs WhisperX

### Via RQ Dashboard (original)

URL : https://whisperx-dashboard.srv759970.hstgr.cloud

Affiche :
- Queues actives
- Jobs en temps réel
- Workers

### Via Grafana (nouveau)

URL : https://monitoring.srv759970.hstgr.cloud

**Avantages** :
- Historique des métriques (graphiques)
- Logs centralisés en temps réel
- Alertes configurables
- Dashboards personnalisables
- Corrélation métriques + logs

### Exemples de panels

**Panel 1 : Jobs par statut (Time series)**
```promql
rq_jobs{queue="transcription"}
```

**Panel 2 : Logs worker (Logs)**
```logql
{container="whisperx-worker"} |~ "Job|Transcription|Loading"
```

**Panel 3 : Taux de succès (Stat)**
```promql
rq_jobs{queue="transcription",status="finished"}
```

## Alertes

### Exemple : Job failed

Dans Grafana → Alerting → Alert rules :

```yaml
- alert: WhisperXJobsFailed
  expr: rate(rq_jobs{status="failed"}[5m]) > 0.1
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Taux élevé d'échecs jobs WhisperX"
    description: "{{ $value }} jobs/min échouent"
```

## Maintenance

### Logs

```bash
# Logs Grafana
docker logs -f grafana

# Logs Prometheus
docker logs -f prometheus

# Logs Loki
docker logs -f loki

# Logs Promtail
docker logs -f promtail

# Logs RQ Exporter
docker logs -f rq-exporter
```

### Backup

```bash
# Backup volumes Grafana
docker run --rm -v monitoring_grafana-data:/data -v $(pwd):/backup alpine tar czf /backup/grafana-backup.tar.gz -C /data .

# Backup volumes Prometheus
docker run --rm -v monitoring_prometheus-data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus-backup.tar.gz -C /data .
```

### Restart

```bash
cd /opt/monitoring
docker-compose restart
```

### Update

```bash
cd /opt/monitoring
docker-compose pull
docker-compose up -d
```

## Troubleshooting

### Grafana n'affiche pas les métriques

1. Vérifier Prometheus targets :
   ```bash
   curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.health != "up")'
   ```

2. Vérifier RQ exporter :
   ```bash
   curl http://localhost:9726/metrics | head -20
   ```

3. Vérifier réseau Docker :
   ```bash
   docker network inspect monitoring_monitoring
   docker network inspect whisperx_default
   ```

### Loki ne reçoit pas les logs

1. Vérifier Promtail :
   ```bash
   docker logs promtail | grep ERROR
   ```

2. Vérifier permissions Docker socket :
   ```bash
   ls -la /var/run/docker.sock
   ```

3. Tester manuellement :
   ```bash
   curl -X POST http://localhost:3100/loki/api/v1/push \
     -H "Content-Type: application/json" \
     -d '{"streams":[{"stream":{"job":"test"},"values":[["'$(date +%s)000000000'","test message"]]}]}'
   ```

### Certificat SSL expiré

```bash
# Vérifier expiration
certbot certificates | grep monitoring

# Renouveler manuellement
certbot renew --cert-name monitoring.srv759970.hstgr.cloud

# Recharger Nginx
systemctl reload nginx
```

## URLs de référence

- **Grafana** : https://monitoring.srv759970.hstgr.cloud
- **Prometheus** : http://srv759970.hstgr.cloud:9090
- **RQ Exporter** : http://srv759970.hstgr.cloud:9726/metrics
- **Loki** : http://srv759970.hstgr.cloud:3100
- **RQ Dashboard (legacy)** : https://whisperx-dashboard.srv759970.hstgr.cloud

## Dashboard RQ officiel

ID Grafana Labs : **12196**

Lien direct : https://grafana.com/grafana/dashboards/12196-rq-dashboard/

## Ressources

- [Prometheus](https://prometheus.io/docs/)
- [Grafana](https://grafana.com/docs/grafana/latest/)
- [Loki](https://grafana.com/docs/loki/latest/)
- [RQ Exporter](https://github.com/mdawar/rq-exporter)
- [Promtail](https://grafana.com/docs/loki/latest/send-data/promtail/)

## Voir Aussi

- [Faster-Whisper Queue](../services/faster-whisper-queue.md) - Service à monitorer
- [WhisperX Service](../services/whisperx.md) - Service WhisperX
- [Guide Whisper Services](GUIDE_WHISPER_SERVICES.md) - Déploiement des services
- [Nginx](../infrastructure/nginx.md) - Configuration reverse proxy
- [Docker](../infrastructure/docker.md) - Gestion des conteneurs
