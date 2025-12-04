# WhisperX - Transcription avec Diarization

Service de transcription audio avec diarization (identification des locuteurs).

## Accès

- **URL API**: https://whisperx.srv759970.hstgr.cloud
- **Documentation**: https://whisperx.srv759970.hstgr.cloud/docs
- **Port interne**: 8002
- **Auth**: Basic Auth (julien:DevAccess2025)

## Caractéristiques

- Modèle: `large-v2`
- Diarization: ✅ (qui parle quand)
- Alignment: ✅ (timestamps précis)
- Device: CUDA (GPU)
- Queue: Redis DB 0 ("transcription")

## 🚀 Quick Start - Transcrivez en 5 Minutes

### Exemple curl

```bash
# Transcription asynchrone (recommandé)
curl -X POST "https://whisperx.srv759970.hstgr.cloud/transcribe" \
  -u julien:DevAccess2025 \
  -F "file=@/path/to/audio.mp3" \
  -F "language=fr"

# Réponse
{
  "job_id": "abc123-def456",
  "status": "queued",
  "message": "Job submitted successfully"
}

# Vérifier le statut
curl -X GET "https://whisperx.srv759970.hstgr.cloud/job/abc123-def456" \
  -u julien:DevAccess2025

# Réponse (processing)
{
  "job_id": "abc123-def456",
  "status": "processing",
  "progress": 45
}

# Réponse (completed)
{
  "job_id": "abc123-def456",
  "status": "completed",
  "result": {
    "text": "Bonjour, voici la transcription complète...",
    "segments": [
      {
        "start": 0.0,
        "end": 2.5,
        "text": "Bonjour",
        "speaker": "SPEAKER_00"
      },
      {
        "start": 2.5,
        "end": 5.8,
        "text": "voici la transcription",
        "speaker": "SPEAKER_01"
      }
    ],
    "language": "fr"
  }
}
```

### Exemple Python

```python
import requests
import time

# Configuration
API_URL = "https://whisperx.srv759970.hstgr.cloud"
AUTH = ("julien", "DevAccess2025")

# 1. Soumettre le fichier audio
with open("meeting.mp3", "rb") as audio_file:
    response = requests.post(
        f"{API_URL}/transcribe",
        auth=AUTH,
        files={"file": audio_file},
        data={"language": "fr"}
    )

job_data = response.json()
job_id = job_data["job_id"]
print(f"Job ID: {job_id}")

# 2. Attendre la fin du traitement
while True:
    status_response = requests.get(
        f"{API_URL}/job/{job_id}",
        auth=AUTH
    )
    status_data = status_response.json()

    if status_data["status"] == "completed":
        result = status_data["result"]
        print("\nTranscription complète:")
        print(result["text"])

        print("\nSegments avec speakers:")
        for segment in result["segments"]:
            print(f"[{segment['speaker']}] {segment['text']}")
        break

    elif status_data["status"] == "failed":
        print(f"Erreur: {status_data.get('error')}")
        break

    else:
        print(f"Status: {status_data['status']}")
        time.sleep(5)
```

### Exemple JavaScript (Node.js)

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const API_URL = 'https://whisperx.srv759970.hstgr.cloud';
const AUTH = {
  username: 'julien',
  password: 'DevAccess2025'
};

async function transcribeAudio(filePath) {
  // 1. Soumettre le fichier
  const formData = new FormData();
  formData.append('file', fs.createReadStream(filePath));
  formData.append('language', 'fr');

  const submitResponse = await axios.post(
    `${API_URL}/transcribe`,
    formData,
    {
      auth: AUTH,
      headers: formData.getHeaders()
    }
  );

  const jobId = submitResponse.data.job_id;
  console.log(`Job ID: ${jobId}`);

  // 2. Polling du statut
  while (true) {
    const statusResponse = await axios.get(
      `${API_URL}/job/${jobId}`,
      { auth: AUTH }
    );

    const { status, result, error } = statusResponse.data;

    if (status === 'completed') {
      console.log('\nTranscription:');
      console.log(result.text);

      console.log('\nSegments avec speakers:');
      result.segments.forEach(seg => {
        console.log(`[${seg.speaker}] ${seg.text}`);
      });
      break;
    } else if (status === 'failed') {
      console.error(`Erreur: ${error}`);
      break;
    } else {
      console.log(`Status: ${status}`);
      await new Promise(resolve => setTimeout(resolve, 5000));
    }
  }
}

// Utilisation
transcribeAudio('./meeting.mp3');
```

## Endpoints Principaux

### POST /transcribe
Upload audio file for transcription with diarization.

**Paramètres:**
- `file` (multipart/form-data): Fichier audio
- `language` (optionnel): Code langue (fr, en, es, etc.)

**Retour:** Job ID pour tracking

### GET /job/{job_id}
Check job status and retrieve results.

**Retour:** Status (queued, processing, completed, failed) + résultats si completed

See [API Documentation](https://whisperx.srv759970.hstgr.cloud/docs) for complete reference.

## Limites & Performances

| Limite | Valeur |
|--------|--------|
| **Taille max fichier** | 100MB |
| **Formats supportés** | mp3, wav, m4a, ogg, flac, webm |
| **Durée max audio** | 2 heures |
| **Rate limit** | 10 requêtes/minute |
| **Temps de traitement** | ~1min pour 10min d'audio (avec GPU) |
| **Langues supportées** | 90+ langues (voir doc Swagger) |

**Performance moyenne:**
- Audio 10 min → Transcription en ~1 minute
- Audio 1 heure → Transcription en ~6 minutes
- Diarization ajoute ~20% au temps de traitement

## Dépendances

| Service | Rôle | Impact si down |
|---------|------|----------------|
| **Redis (rq-queue-redis:6379, DB 0)** | Queue de jobs | ❌ Aucune transcription possible |
| **WhisperX Worker** | Processing audio | ❌ Jobs restent en queue |
| **Nginx** | Reverse proxy HTTPS | ❌ API inaccessible |
| **Certbot/SSL** | Certificat HTTPS | ⚠️ Erreur SSL |

**Vérifier dépendances:**
```bash
# Redis
docker exec -it rq-queue-redis redis-cli ping

# Worker
docker ps | grep whisperx-worker

# Queue status
docker exec -it rq-queue-redis redis-cli
SELECT 0
LLEN transcription
```

## Guides Complets

- [Guide Whisper Services](../../guides/services/ai/whisper-deployment.md) - Déploiement et configuration des deux services
- [Faster-Whisper Queue](faster-whisper-queue.md) - Alternative async avec queue RQ
- [Monitoring WhisperX](../../guides/services/monitoring/whisperx-monitoring.md) - Stack Grafana + Prometheus + Loki

## Voir Aussi

- [Docker](../../infrastructure/docker.md) - Gestion des conteneurs
- [Nginx](../../infrastructure/nginx.md) - Reverse proxy configuration
