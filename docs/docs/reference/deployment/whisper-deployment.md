# Guide Whisper Services

Documentation pour les deux services de transcription audio déployés sur srv759970.

## Vue d'ensemble

Deux services Whisper sont configurés pour répondre à des besoins différents :

| Service | URL | Caractéristiques | Port | Utilisation |
|---------|-----|------------------|------|-------------|
| **faster-whisper** | whisper.srv759970.hstgr.cloud | Rapide, compatible OpenAI API | 8001 | Transcription simple, haute performance |
| **WhisperX** | whisperx.srv759970.hstgr.cloud | Diarisation speakers, timestamps précis | 8002 | Transcription avec identification locuteurs |

## faster-whisper

### Architecture

```
/opt/whisper-faster/
├── docker-compose.yml
└── (cache HuggingFace)
```

### Configuration

**Image Docker** : `fedirz/faster-whisper-server:latest-cpu`
**Modèle** : `Systran/faster-whisper-small`
**Device** : CPU (int8 quantization)

### docker-compose.yml

```yaml
version: '3.8'

services:
  faster-whisper:
    image: fedirz/faster-whisper-server:latest-cpu
    container_name: faster-whisper
    restart: 'no'  # Auto-start system
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
```

### Endpoints principaux

**POST /v1/audio/transcriptions** (OpenAI-compatible)
```bash
curl -X POST https://whisper.srv759970.hstgr.cloud/v1/audio/transcriptions \
  -H "Authorization: Bearer $API_KEY" \
  -F "file=@audio.mp3" \
  -F "model=Systran/faster-whisper-small" \
  -F "language=fr"
```

**Swagger** : https://whisper.srv759970.hstgr.cloud/docs

### Performance

- **Vitesse** : 10-15x temps réel sur CPU
- **RAM** : ~400MB
- **Formats** : mp3, wav, m4a, flac, ogg
- **Langues** : 99 langues supportées

## WhisperX

### Architecture

```
/opt/whisperx/
├── docker-compose.yml
├── Dockerfile
├── server.py
└── .env (HF_TOKEN)
```

### Configuration

**Image** : Custom build (Python 3.11 + whisperx + FastAPI)
**Modèle** : base (modifiable via API)
**Diarization** : pyannote-audio (nécessite HuggingFace token)

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Python packages
RUN pip install --no-cache-dir \
    whisperx \
    fastapi \
    uvicorn[standard] \
    python-multipart

COPY server.py /app/server.py

EXPOSE 8002

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8002"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  whisperx:
    build: .
    container_name: whisperx
    restart: 'no'
    ports:
      - '8002:8002'
    volumes:
      - /root/.cache/huggingface:/root/.cache/huggingface
    environment:
      - HF_TOKEN=${HF_TOKEN}
      - TZ=Europe/Paris
```

### Configuration HuggingFace Token

Pour activer la diarization, créer `/opt/whisperx/.env` :

```bash
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Obtenir le token :
1. Créer un compte sur https://huggingface.co
2. Aller dans Settings > Access Tokens
3. Créer un nouveau token (read)
4. Accepter les conditions de pyannote/speaker-diarization

### API Endpoints

**POST /transcribe**

```bash
curl -X POST https://whisperx.srv759970.hstgr.cloud/transcribe \
  -F "file=@audio.mp3" \
  -F "model=base" \
  -F "language=fr" \
  -F "diarize=true"
```

**Paramètres** :
- `file` : Fichier audio (required)
- `model` : tiny, base, small, medium, large-v2 (default: base)
- `language` : Code langue ISO 639-1 ou auto-detect (default: None)
- `diarize` : true/false - Active l'identification des speakers (default: false)

**Réponse avec diarization** :
```json
{
  "segments": [
    {
      "start": 0.5,
      "end": 3.2,
      "text": "Bonjour, comment allez-vous ?",
      "speaker": "SPEAKER_00"
    },
    {
      "start": 3.5,
      "end": 5.8,
      "text": "Très bien, merci !",
      "speaker": "SPEAKER_01"
    }
  ],
  "language": "fr"
}
```

**Swagger** : https://whisperx.srv759970.hstgr.cloud/docs

### Performance

- **Vitesse** : 60-70x temps réel (WhisperX optimized)
- **RAM** : ~500MB (sans diarization), ~800MB (avec)
- **Diarization** : Ajoute 2-3s de latence
- **Précision timestamps** : ±50ms

## Déploiement

### Build WhisperX

```bash
ssh root@69.62.108.82
cd /opt/whisperx

# Configurer HF token
nano .env  # Ajouter HF_TOKEN=...

# Build image
docker-compose build

# Démarrer une fois pour test
docker-compose up -d

# Vérifier logs
docker logs -f whisperx

# Arrêter (auto-start prendra le relai)
docker-compose stop
```

### Configuration Nginx

Les deux services partagent la même configuration de base :

```nginx
server {
    listen 443 ssl http2;
    server_name whisper.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/whisper.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/whisper.srv759970.hstgr.cloud/privkey.pem;

    include snippets/basic-auth.conf;

    location / {
        proxy_pass http://127.0.0.1:8890;  # Auto-start proxy
        proxy_set_header Host $host;
        proxy_read_timeout 600;
        client_max_body_size 500M;

        # CORS for Swagger
        add_header 'Access-Control-Allow-Origin' 'https://portal.srv759970.hstgr.cloud' always;
    }
}
```

### Auto-start Configuration

Extrait de `/opt/docker-autostart/config.json` :

```json
{
  "services": {
    "whisper.srv759970.hstgr.cloud": {
      "name": "Whisper API (faster-whisper)",
      "composeDir": "/opt/whisper-faster",
      "proxyPort": 8001,
      "blocking": true,
      "containers": ["faster-whisper"]
    },
    "whisperx.srv759970.hstgr.cloud": {
      "name": "WhisperX API (with diarization)",
      "composeDir": "/opt/whisperx",
      "proxyPort": 8002,
      "blocking": true,
      "containers": ["whisperx"]
    }
  }
}
```

## Choix du service

### Utiliser faster-whisper si :
- ✅ Transcription simple sans besoin de speakers
- ✅ Performance maximale requise
- ✅ Compatibilité OpenAI API nécessaire
- ✅ Pas de token HuggingFace disponible

### Utiliser WhisperX si :
- ✅ Besoin d'identifier les speakers (réunions, interviews)
- ✅ Timestamps précis requis (±50ms)
- ✅ Audio multi-locuteurs
- ✅ Post-traitement avancé souhaité

## Exemples d'utilisation

### faster-whisper : Transcription simple

```python
import openai

client = openai.OpenAI(
    base_url="https://whisper.srv759970.hstgr.cloud/v1",
    api_key="dummy"  # Not used but required
)

with open("meeting.mp3", "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        model="Systran/faster-whisper-small",
        file=audio_file,
        language="fr"
    )

print(transcript.text)
```

### WhisperX : Transcription avec diarization

```python
import requests

url = "https://whisperx.srv759970.hstgr.cloud/transcribe"

with open("meeting.mp3", "rb") as f:
    files = {"file": f}
    data = {
        "model": "base",
        "language": "fr",
        "diarize": "true"
    }

    response = requests.post(url, files=files, data=data)
    result = response.json()

for segment in result["segments"]:
    print(f"[{segment['speaker']}] {segment['text']}")
```

## Monitoring

### Logs

```bash
# faster-whisper
docker logs -f faster-whisper

# WhisperX
docker logs -f whisperx

# Auto-start system
journalctl -u docker-autostart -f | grep whisper
```

### Métriques

```bash
# RAM usage
docker stats faster-whisper whisperx

# Uptime
docker ps | grep whisper
```

## Troubleshooting

### faster-whisper ne démarre pas

```bash
# Vérifier image
docker images | grep faster-whisper

# Pull si manquante
docker pull fedirz/faster-whisper-server:latest-cpu

# Restart manual
cd /opt/whisper-faster
docker-compose up -d
docker logs -f faster-whisper
```

### WhisperX : Erreur diarization

**Symptôme** : `401 Unauthorized` ou `403 Forbidden` lors de diarization

**Cause** : HF_TOKEN invalide ou modèles pyannote non acceptés

**Solution** :
```bash
# Vérifier token
cat /opt/whisperx/.env

# Accepter les conditions des modèles
# 1. https://huggingface.co/pyannote/speaker-diarization
# 2. https://huggingface.co/pyannote/segmentation
# Cliquer "Agree and access repository"

# Rebuild
cd /opt/whisperx
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 502 Bad Gateway

**Cause** : Container pas encore prêt après auto-start

**Solution** : Le proxy attend 30s en mode Blocking. Si toujours 502 :
```bash
# Augmenter timeout dans /opt/docker-autostart/server.js
# Ligne ~120 : const MAX_WAIT_TIME = 60000; // 60s au lieu de 30s

systemctl restart docker-autostart
```

### Audio upload fails (413 Payload Too Large)

**Cause** : Fichier > 500MB

**Solution** : Augmenter `client_max_body_size` dans Nginx
```bash
nano /etc/nginx/sites-available/whisperx
# Changer : client_max_body_size 1G;

nginx -t && systemctl reload nginx
```

## Sécurité

### Basic Auth

Tous les accès sont protégés par basic auth Nginx :
```bash
# Credentials
cat /etc/nginx/.htpasswd
```

### SSL/TLS

Certificats Let's Encrypt avec renouvellement automatique :
```bash
certbot renew --dry-run
```

### Exposition

- Port 8001 (faster-whisper) : **localhost only**
- Port 8002 (WhisperX) : **localhost only**
- Port 8890 (auto-start proxy) : **localhost only**
- Port 443 (Nginx) : **public** (avec basic auth)

## Limitations

### faster-whisper
- ❌ Pas de diarization
- ❌ Timestamps moins précis (~1s)
- ✅ Mais plus rapide et léger

### WhisperX
- ❌ Nécessite HuggingFace token pour diarization
- ❌ Plus lourd en RAM avec diarization
- ❌ Build custom requis
- ✅ Mais identification speakers + timestamps précis

## Liens utiles

- **faster-whisper repo** : https://github.com/fedirz/faster-whisper-server
- **WhisperX repo** : https://github.com/m-bain/whisperX
- **OpenAI Whisper** : https://github.com/openai/whisper
- **pyannote-audio** : https://github.com/pyannote/pyannote-audio
- **Swagger UI Portal** : https://portal.srv759970.hstgr.cloud/api

## Voir Aussi

- [Faster-Whisper Queue](../../../services/ai/faster-whisper-queue.md) - Documentation complète du système async avec RQ
- [WhisperX Service](../../../services/ai/whisperx.md) - Accès rapide WhisperX
- [Monitoring WhisperX](../monitoring/whisperx-monitoring.md) - Stack de monitoring complète
- [Docker Autostart](../../deployment/docker-autostart-setup.md) - Configuration auto-start
- [Nginx](../../infrastructure/nginx.md) - Reverse proxy configuration
