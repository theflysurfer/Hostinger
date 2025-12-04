# Guide Faster-Whisper avec Système de Queue

## Vue d'ensemble

Intégration complète de Faster-Whisper avec le système de queues Redis Queue (RQ), permettant le traitement asynchrone de transcriptions audio longues.

## Architecture

```
┌──────────── Redis Partagé (rq-queue-redis:6379) ────────────┐
│                                                               │
│  DB 0: Queue "transcription" (WhisperX)                      │
│  DB 1: Queue "faster-whisper-transcription" (Faster-Whisper)│
│                                                               │
└───────────────────────────────────────────────────────────────┘
         ↓                                 ↓
   whisperx-worker              faster-whisper-worker
         ↓                                 ↓
   WhisperX API (:8002)         Faster-Whisper Queue API (:8003)
```

## Services Déployés

### 1. faster-whisper (Port 8001)
Service de base inchangé, utilisant l'image officielle `fedirz/faster-whisper-server:latest-cpu`.

**API:**
- `GET /health` - Health check
- `POST /v1/audio/transcriptions` - Transcription directe (OpenAI-compatible)

### 2. faster-whisper-queue-api (Port 8003)
Wrapper FastAPI ajoutant les capacités de queuing.

**Endpoints:**
- `GET /` - Informations sur le service
- `GET /health` - Health check (Redis + faster-whisper)
- `POST /transcribe` - Transcription synchrone (passthrough vers faster-whisper)
- `POST /transcribe/async` - Transcription asynchrone via RQ ✨
- `GET /transcribe/status/{job_id}` - Statut du job async
- `GET /queue/stats` - Statistiques de la queue

### 3. faster-whisper-worker
Worker RQ dédié au traitement des transcriptions async.

**Configuration:**
- Queue: `faster-whisper-transcription`
- Redis DB: 1 (isolation avec WhisperX)
- Timeout: 30 minutes par job
- Result TTL: 1 heure

## Installation

### Structure des fichiers

```
/opt/faster-whisper-queue/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── server.py      # API FastAPI avec endpoints async
└── worker.py      # RQ Worker
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  faster-whisper:
    image: fedirz/faster-whisper-server:latest-cpu
    container_name: faster-whisper
    restart: unless-stopped
    ports:
      - '8001:8000'
    volumes:
      - /root/.cache/huggingface:/root/.cache/huggingface
    environment:
      - WHISPER__MODEL=Systran/faster-whisper-small
      - WHISPER__INFERENCE_DEVICE=cpu
      - UVICORN_HOST=0.0.0.0
      - UVICORN_PORT=8000
      - TZ=Europe/Paris
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s
    logging:
      driver: json-file
      options:
        max-size: '10m'
        max-file: '3'
    networks:
      - faster-whisper-net
      - whisperx_whisperx

  faster-whisper-queue-api:
    build: .
    container_name: faster-whisper-queue-api
    restart: unless-stopped
    ports:
      - '8003:8003'
    environment:
      - REDIS_URL=redis://rq-queue-redis:6379/1
      - FASTER_WHISPER_URL=http://faster-whisper:8000
    depends_on:
      - faster-whisper
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
      interval: 10s
      timeout: 5s
      retries: 3
    logging:
      driver: json-file
      options:
        max-size: '10m'
        max-file: '3'
    networks:
      - faster-whisper-net
      - whisperx_whisperx
    volumes:
      - /tmp/faster-whisper-uploads:/tmp/uploads

  faster-whisper-worker:
    build: .
    container_name: faster-whisper-worker
    restart: unless-stopped
    command: python worker.py
    environment:
      - REDIS_URL=redis://rq-queue-redis:6379/1
      - FASTER_WHISPER_URL=http://faster-whisper:8000
    depends_on:
      - faster-whisper
    logging:
      driver: json-file
      options:
        max-size: '10m'
        max-file: '3'
    networks:
      - faster-whisper-net
      - whisperx_whisperx

networks:
  faster-whisper-net:
    driver: bridge
  whisperx_whisperx:
    external: true
```

### Démarrage

```bash
cd /opt/faster-whisper-queue
docker-compose up -d

# Vérifier les logs
docker-compose logs -f faster-whisper-worker
```

## Utilisation

### Transcription Synchrone

```bash
curl -X POST http://localhost:8003/transcribe \
  -F "file=@audio.wav" \
  -F "language=fr" \
  -F "task=transcribe"
```

### Transcription Asynchrone

**1. Soumettre le job:**
```bash
curl -X POST http://localhost:8003/transcribe/async \
  -F "file=@long_audio.wav" \
  -F "language=fr" \
  | jq .
```

**Réponse:**
```json
{
  "job_id": "c8b13006-fd93-4ea6-8a26-98c3807165b5",
  "status": "queued",
  "message": "Transcription job queued: long_audio.wav",
  "queue_position": 0,
  "estimated_wait": "0 minutes"
}
```

**2. Vérifier le statut:**
```bash
curl http://localhost:8003/transcribe/status/c8b13006-fd93-4ea6-8a26-98c3807165b5 | jq .
```

**Réponses possibles:**

**Job en attente:**
```json
{
  "job_id": "c8b13006-fd93-4ea6-8a26-98c3807165b5",
  "status": "queued",
  "created_at": "2025-10-20T20:43:19.570894",
  "queue_position": 2,
  "message": "Waiting in queue"
}
```

**Job en cours:**
```json
{
  "job_id": "c8b13006-fd93-4ea6-8a26-98c3807165b5",
  "status": "started",
  "created_at": "2025-10-20T20:43:19.570894",
  "started_at": "2025-10-20T20:43:25.591326",
  "message": "Transcription in progress"
}
```

**Job terminé:**
```json
{
  "job_id": "c8b13006-fd93-4ea6-8a26-98c3807165b5",
  "status": "finished",
  "created_at": "2025-10-20T20:43:19.570894",
  "started_at": "2025-10-20T20:43:25.591326",
  "ended_at": "2025-10-20T20:45:10.578469",
  "result": {
    "text": "Bonjour, ceci est une transcription...",
    "segments": [...],
    "metadata": {
      "filename": "long_audio.wav",
      "processing_time": 105.5,
      "language": "fr",
      "task": "transcribe",
      "service": "faster-whisper"
    }
  },
  "message": "Transcription completed"
}
```

**Job échoué:**
```json
{
  "job_id": "c8b13006-fd93-4ea6-8a26-98c3807165b5",
  "status": "failed",
  "created_at": "2025-10-20T20:43:19.570894",
  "started_at": "2025-10-20T20:43:25.591326",
  "ended_at": "2025-10-20T20:43:30.578469",
  "error": "Faster-whisper API error: 500 Server Error...",
  "message": "Transcription failed"
}
```

### Statistiques de la Queue

```bash
curl http://localhost:8003/queue/stats | jq .
```

**Réponse:**
```json
{
  "queue_name": "faster-whisper-transcription",
  "queued": 3,
  "workers": 1,
  "failed": 2,
  "finished": 15,
  "started": 1
}
```

## Monitoring

### Grafana/Loki

**Logs collectés:**
- `faster-whisper` - Service de base
- `faster-whisper-queue-api` - API wrapper
- `faster-whisper-worker` - Worker RQ

**Queries utiles:**
```logql
# Logs du worker
{container="faster-whisper-worker"}

# Jobs démarrés
{container="faster-whisper-worker"} |= "Starting transcription"

# Erreurs
{container="faster-whisper-worker"} |= "ERROR"

# Tous les services faster-whisper
{container=~"faster-whisper.*"}
```

### RQ Dashboard

URL: https://whisperx-dashboard.srv759970.hstgr.cloud

Affiche les queues de **WhisperX** et **Faster-Whisper** dans un seul dashboard.

## Comparaison WhisperX vs Faster-Whisper

| Caractéristique | WhisperX | Faster-Whisper |
|----------------|----------|----------------|
| **Port API** | 8002 | 8003 |
| **Queue Redis DB** | 0 | 1 |
| **Queue Name** | `transcription` | `faster-whisper-transcription` |
| **Modèle** | whisper-large-v2 | faster-whisper-small |
| **Device** | CPU | CPU |
| **Diarization** | ✅ Oui | ❌ Non |
| **Alignement** | ✅ Oui | ❌ Non |
| **Vitesse** | Moyen | Rapide |
| **Qualité** | Excellente | Bonne |

## URLs de Production

- **Faster-Whisper (direct)**: http://srv759970.hstgr.cloud:8001
- **Faster-Whisper Queue API**: http://srv759970.hstgr.cloud:8003
- **WhisperX API**: http://srv759970.hstgr.cloud:8002
- **RQ Dashboard**: https://whisperx-dashboard.srv759970.hstgr.cloud
- **Grafana Monitoring**: https://monitoring.srv759970.hstgr.cloud

## Troubleshooting

### Worker en boucle de redémarrage

```bash
docker logs faster-whisper-worker --tail 50
```

**Causes communes:**
- Redis non accessible → Vérifier le network `whisperx_whisperx`
- faster-whisper service down → `docker ps | grep faster-whisper`

### Jobs bloqués en "queued"

```bash
# Vérifier que le worker tourne
docker ps | grep faster-whisper-worker

# Logs du worker
docker logs faster-whisper-worker --tail 30

# Nombre de workers actifs
curl http://localhost:8003/queue/stats | jq '.workers'
```

### Erreurs "Connection refused"

Vérifier que tous les services sont sur le bon network:

```bash
docker network inspect whisperx_whisperx | grep -E "faster-whisper|rq-queue-redis"
```

## Performance

### Benchmarks

Tests avec fichier audio de 5 minutes (français):

| Service | Temps de traitement | Qualité WER |
|---------|-------------------|-------------|
| WhisperX (large-v2) | ~180s | 5.2% |
| Faster-Whisper (small) | ~45s | 8.7% |

### Recommandations

**Utiliser WhisperX si:**
- Besoin de diarization (qui parle quand)
- Besoin d'alignement précis des timestamps
- Qualité de transcription critique
- Fichiers < 30 minutes

**Utiliser Faster-Whisper si:**
- Vitesse prioritaire
- Pas besoin de diarization
- Fichiers longs (> 30 minutes)
- Volume élevé de fichiers courts

## Maintenance

### Logs

```bash
# Tous les services
cd /opt/faster-whisper-queue && docker-compose logs -f

# Worker uniquement
docker logs -f faster-whisper-worker
```

### Restart

```bash
cd /opt/faster-whisper-queue
docker-compose restart
```

### Update

```bash
cd /opt/faster-whisper-queue
docker-compose pull faster-whisper
docker-compose build --no-cache
docker-compose up -d
```

### Nettoyage des jobs

Les résultats sont automatiquement supprimés après 1 heure (TTL).

Pour forcer un nettoyage:
```bash
docker exec rq-queue-redis redis-cli -n 1 FLUSHDB
```

## Ressources

- [Faster-Whisper Server](https://github.com/fedirz/faster-whisper-server)
- [RQ Documentation](https://python-rq.org/)
- [Guide WhisperX](./whisperx.md)
- [Guide Monitoring](../infrastructure/monitoring.md)

## Voir Aussi

- [Guide Whisper Services](../../guides/services/ai/whisper-deployment.md) - Comparaison et choix entre services
- [WhisperX Service](whisperx.md) - Service avec diarization
- [Monitoring WhisperX](../../guides/services/monitoring/whisperx-monitoring.md) - Stack Grafana + Prometheus + Loki
- [Docker](../../infrastructure/docker.md) - Gestion des conteneurs
- [Reference Docker Commands](../../reference/docker/commands.md) - Commandes Docker courantes
