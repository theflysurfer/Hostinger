# NeuTTS - Neural Text-to-Speech & Voice Cloning

**API URL:** https://neutts-api.srv759970.hstgr.cloud
**UI URL:** https://neutts-ui.srv759970.hstgr.cloud
**Container:** `neutts-api`, `neutts-ui`
**Stack:** FastAPI + Streamlit + Coqui TTS

## Vue d'Ensemble

NeuTTS est une solution de synthèse vocale neuronale avec capacités de clonage de voix, basée sur la technologie Coqui TTS.

### Fonctionnalités Principales

- **🎙️ Voice Cloning** - Clonage de voix à partir de quelques secondes d'audio
- **🗣️ Multi-speakers** - Voix pré-entraînées en plusieurs langues
- **⚡ Synthèse rapide** - Génération TTS optimisée
- **🎵 Contrôle prosodique** - Ajustement de l'intonation et du rythme
- **📊 API REST** - Intégration facile dans vos applications
- **🖥️ Interface Web** - UI Streamlit pour tests et démos

## Architecture

```
┌─────────────────────────────────────────────┐
│           NeuTTS UI (Streamlit)             │
│         Port 8501 - Interface Web           │
└─────────────────┬───────────────────────────┘
                  │
    ┌─────────────┴──────────────┐
    │                            │
┌───▼────────────┐      ┌────────▼─────────┐
│  NeuTTS API    │      │  Voice Samples   │
│  (FastAPI)     │      │     Storage      │
│  Port 5002     │      │                  │
└────────────────┘      └──────────────────┘
         │
    ┌────┴────┐
    │         │
┌───▼────┐  ┌─▼──────┐
│ Coqui  │  │ XTTS-v2│
│  TTS   │  │ Models │
└────────┘  └────────┘
```

## Installation & Configuration

### Docker Compose

```yaml
version: '3.8'

services:
  neutts-api:
    image: ghcr.io/neutts/neutts-api:latest
    container_name: neutts-api
    restart: unless-stopped
    ports:
      - "5002:5002"
    volumes:
      - /opt/neutts/models:/models
      - /opt/neutts/voices:/voices
      - /opt/neutts/output:/output
    environment:
      - MODEL_PATH=/models/tts_models
      - VOICE_SAMPLES_PATH=/voices
      - OUTPUT_PATH=/output
      - MAX_TEXT_LENGTH=1000
      - CACHE_ENABLED=true
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  neutts-ui:
    image: ghcr.io/neutts/neutts-ui:latest
    container_name: neutts-ui
    restart: unless-stopped
    ports:
      - "8501:8501"
    environment:
      - NEUTTS_API_URL=http://neutts-api:5002
    depends_on:
      - neutts-api
```

### Configuration

```yaml
# /opt/neutts/config.yml
models:
  default: "tts_models/multilingual/multi-dataset/xtts_v2"
  available:
    - "tts_models/fr/mai/tacotron2-DDC"
    - "tts_models/en/ljspeech/tacotron2-DDC"

voice_cloning:
  min_audio_length: 6  # secondes
  max_audio_length: 30
  sample_rate: 22050
  supported_formats: ["wav", "mp3", "ogg", "flac"]

output:
  format: "wav"
  sample_rate: 22050
  bitrate: 192

cache:
  enabled: true
  ttl: 3600  # 1 heure
  max_size: 1000  # entrées
```

## Utilisation

### Interface Web (Streamlit)

**URL:** https://neutts-ui.srv759970.hstgr.cloud

#### Onglet "Text-to-Speech"

1. Saisir le texte à synthétiser
2. Sélectionner la voix (pré-entraînée ou clonée)
3. Ajuster les paramètres (vitesse, pitch)
4. Cliquer sur "Generate"
5. Écouter et télécharger le résultat

#### Onglet "Voice Cloning"

1. Uploader un échantillon audio (6-30 secondes)
2. Saisir le texte de l'échantillon (transcription)
3. Donner un nom à la voix
4. Cliquer sur "Clone Voice"
5. Utiliser la voix clonée dans l'onglet TTS

#### Onglet "Batch Processing"

1. Uploader un fichier CSV (text, output_filename)
2. Sélectionner la voix
3. Lancer le traitement
4. Télécharger l'archive ZIP

### API REST

**Documentation:** https://neutts-api.srv759970.hstgr.cloud/docs

#### Endpoints Principaux

```bash
# TTS Simple
POST /api/v1/tts
Content-Type: application/json
{
  "text": "Bonjour, comment allez-vous ?",
  "speaker": "default",
  "language": "fr",
  "speed": 1.0
}

# TTS avec voix clonée
POST /api/v1/tts/clone
Content-Type: multipart/form-data
{
  "text": "Texte à synthétiser",
  "reference_audio": <file>,
  "reference_text": "Transcription de l'audio"
}

# Lister les voix disponibles
GET /api/v1/voices

# Upload voix clonée
POST /api/v1/voices/upload
Content-Type: multipart/form-data
{
  "name": "my_voice",
  "audio_file": <file>,
  "transcript": "Texte de l'échantillon"
}
```

#### Exemples

**Python:**
```python
import requests

API_URL = "https://neutts-api.srv759970.hstgr.cloud/api/v1"

# Synthèse simple
response = requests.post(
    f"{API_URL}/tts",
    json={
        "text": "Bonjour le monde !",
        "speaker": "default",
        "language": "fr"
    }
)

# Sauvegarder l'audio
with open("output.wav", "wb") as f:
    f.write(response.content)

# Voice cloning
with open("voice_sample.wav", "rb") as audio:
    response = requests.post(
        f"{API_URL}/tts/clone",
        files={"reference_audio": audio},
        data={
            "text": "Texte à synthétiser avec voix clonée",
            "reference_text": "Transcription de l'échantillon audio"
        }
    )

with open("cloned_output.wav", "wb") as f:
    f.write(response.content)
```

**cURL:**
```bash
# TTS simple
curl -X POST https://neutts-api.srv759970.hstgr.cloud/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Bonjour", "speaker": "default", "language": "fr"}' \
  --output output.wav

# Lister les voix
curl https://neutts-api.srv759970.hstgr.cloud/api/v1/voices

# Voice cloning
curl -X POST https://neutts-api.srv759970.hstgr.cloud/api/v1/tts/clone \
  -F "reference_audio=@voice_sample.wav" \
  -F "reference_text=Bonjour comment allez-vous" \
  -F "text=Texte à synthétiser" \
  --output cloned.wav
```

**JavaScript:**
```javascript
// TTS avec Fetch API
async function synthesizeSpeech(text, speaker = 'default') {
  const response = await fetch('https://neutts-api.srv759970.hstgr.cloud/api/v1/tts', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: text,
      speaker: speaker,
      language: 'fr'
    })
  });

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);

  // Jouer l'audio
  const audio = new Audio(url);
  audio.play();
}

synthesizeSpeech("Bonjour le monde !");
```

## Modèles Disponibles

### XTTS-v2 (Recommandé)

**Caractéristiques:**
- Multi-lingue (17 langues)
- Voice cloning avec 6 secondes d'audio
- Qualité studio
- Latence: ~2-3 secondes

**Langues supportées:**
- Français, Anglais, Espagnol, Allemand, Italien
- Portugais, Polonais, Turc, Russe, Néerlandais
- Tchèque, Arabe, Chinois, Japonais, Hongrois, Coréen, Hindi

### Tacotron2-DDC

**Caractéristiques:**
- Haute qualité
- Latence plus faible (~1 seconde)
- Pas de voice cloning
- Nécessite voix pré-entraînée

## Intégrations

### WhisperX + NeuTTS (Boucle STT→TTS)

```python
# Transcription → Traduction → TTS
import requests

# 1. Transcription avec WhisperX
audio_file = open("recording.mp3", "rb")
transcription = requests.post(
    "https://whisperx.srv759970.hstgr.cloud/transcribe",
    files={"file": audio_file}
).json()

# 2. Synthèse avec NeuTTS
synthesized = requests.post(
    "https://neutts-api.srv759970.hstgr.cloud/api/v1/tts",
    json={
        "text": transcription["text"],
        "speaker": "default",
        "language": "fr"
    }
)

with open("synthesized.wav", "wb") as f:
    f.write(synthesized.content)
```

### n8n Workflow

```json
{
  "nodes": [
    {
      "name": "HTTP Request",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://neutts-api.srv759970.hstgr.cloud/api/v1/tts",
        "method": "POST",
        "jsonParameters": true,
        "options": {
          "response": {
            "responseFormat": "file"
          }
        },
        "bodyParameters": {
          "parameters": [
            {
              "name": "text",
              "value": "={{$json[\"text\"]}}"
            },
            {
              "name": "speaker",
              "value": "default"
            }
          ]
        }
      }
    }
  ]
}
```

## Performance

### Benchmarks

| Modèle | Latence | Qualité | RAM | GPU |
|--------|---------|---------|-----|-----|
| XTTS-v2 | 2-3s | ⭐⭐⭐⭐⭐ | 4GB | Recommandé |
| Tacotron2 | 1s | ⭐⭐⭐⭐ | 2GB | Optionnel |

### Optimisations

**1. GPU Acceleration:**
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          capabilities: [gpu]
```

**2. Cache:**
```yaml
environment:
  - CACHE_ENABLED=true
  - CACHE_TTL=3600
```

**3. Batch Processing:**
```python
# Générer plusieurs audios en parallèle
texts = ["Texte 1", "Texte 2", "Texte 3"]
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(tts, text) for text in texts]
```

## Monitoring

### Health Check

```bash
curl https://neutts-api.srv759970.hstgr.cloud/health
```

### Logs

```bash
# API logs
docker logs -f neutts-api

# UI logs
docker logs -f neutts-ui
```

### Métriques

```yaml
# Prometheus metrics sur /metrics
- neutts_requests_total
- neutts_generation_time_seconds
- neutts_cache_hits_total
- neutts_model_load_time_seconds
```

## Troubleshooting

### Synthèse Lente

**Activer GPU:**
```bash
# Vérifier GPU disponible
docker exec neutts-api nvidia-smi

# Si pas de GPU, optimiser CPU
environment:
  - NUM_THREADS=4
  - USE_GPU=false
```

### Voice Cloning de Mauvaise Qualité

**Améliorer l'échantillon:**
- Utiliser 10-15 secondes d'audio
- Enregistrement propre (pas de bruit de fond)
- Voix expressive et claire
- Format WAV 22050 Hz recommandé

### Erreurs de Mémoire

**Réduire la longueur du texte:**
```yaml
environment:
  - MAX_TEXT_LENGTH=500
  - BATCH_SIZE=1
```

## Sécurité

### Protection

- ✅ **HTTPS** - Let's Encrypt SSL/TLS
- ✅ **Rate Limiting** - 100 req/min par IP
- ✅ **File Upload Limits** - Max 30MB
- ✅ **Content-Type Validation** - Audio formats uniquement

### Recommandations

1. ✅ Limiter la longueur du texte (< 1000 caractères)
2. ✅ Valider les formats audio uploadés
3. ✅ Nettoyer les fichiers temporaires régulièrement
4. ⚠️ Considérer authentification pour API publique

## Cas d'Usage

### 1. Audiobooks
```python
# Convertir livre en audio
chapters = load_book_chapters()
for i, chapter in enumerate(chapters):
    audio = synthesize(chapter, speaker="narrator")
    save_audio(f"chapter_{i}.wav", audio)
```

### 2. Assistants Vocaux
```python
# Réponse vocale chatbot
user_query = "Quelle est la météo ?"
response = chatbot.answer(user_query)
audio = neutts_synthesize(response)
play_audio(audio)
```

### 3. Accessibilité
```python
# Lecture de contenu web
webpage_text = extract_text(url)
audio = neutts_synthesize(webpage_text)
return audio_stream
```

## Voir Aussi

- [WhisperX](whisperx.md) - Transcription (STT)
- [XTTS-v2](xtts-v2.md) - Alternative TTS
- [Ollama](ollama.md) - LLM pour génération de texte

## Liens Externes

- **Coqui TTS:** https://github.com/coqui-ai/TTS
- **XTTS-v2 Paper:** https://arxiv.org/abs/2311.18271

---

**Dernière mise à jour:** 2025-10-23
**Status:** 🟢 Production
