# Telegram Voice Transcription Bot - WhisperX Direct

## 🎯 Objectif

Bot Telegram sécurisé qui transcrit automatiquement les messages vocaux en utilisant WhisperX avec polling asynchrone. Conçu comme première étape d'un pipeline IA de traitement de transcriptions.

---

## 📋 Informations de déploiement

**Répertoire** : `/opt/telegram-bot/`
**Container** : `telegram-voice-bot`
**Réseau** : `telegram-bot_default` + `whisperx_whisperx`
**Bot Telegram** : `@transcripteur_vocal_bot`
**Token** : `7867830645:AAGSgh5xUIeeMPVWJN2ska7qsTN4hcZgHAQ`

---

## 🏗️ Architecture

```
Utilisateur Telegram
    ↓ 🎤 Message vocal (.ogg)
Bot Python (telegram-voice-bot)
    ↓ 📥 Téléchargement audio
    ↓ 📤 POST /transcribe
WhisperX API (job queue Redis)
    ↓ 🆔 job_id + status: "queued"
Bot Python (polling async)
    ↓ 🔄 GET /status/{job_id} toutes les 2s
    ↓ 📊 Status: queued → processing → completed
Bot Python
    ↓ 📝 Formatage résultat
Utilisateur Telegram
    ↓ ✅ Transcription + métadonnées

[FUTUR] → Pipeline IA (LangChain/LlamaIndex)
    ↓ Clarification, grammaire, ponctuation
    ↓ Tagging, catégorisation
    ↓ Enrichissement sémantique
[FUTUR] → Notion API
    ↓ Stockage structuré
```

---

## 🔒 Sécurité implémentée

### Whitelist d'utilisateurs

```env
ALLOWED_USERS=1699768293  # ID Telegram autorisé
ALLOW_ALL_USERS=false     # Mode privé (recommandé)
```

**Comment obtenir un Telegram ID** :
- Méthode 1 : Envoyer un message à `@userinfobot`
- Méthode 2 : Envoyer `/start` au bot (affichera votre ID)

### Rate Limiting

| Limite | Valeur | Configurable |
|--------|--------|--------------|
| Vocaux/minute | 20 | `MAX_REQUESTS_PER_MINUTE` |
| Vocaux/heure | 100 | `MAX_REQUESTS_PER_HOUR` |
| Durée max vocal | 20 min (1200s) | `MAX_VOICE_DURATION` |
| Taille max | 100 MB | `MAX_VOICE_SIZE_MB` |

### Logs et audit

Tous les accès sont loggés avec:
- User ID Telegram
- Timestamp
- Fichier audio (taille, durée)
- Job WhisperX ID
- Statut de transcription

```bash
# Voir les logs en temps réel
docker logs -f telegram-voice-bot

# Exemple de log
2025-10-24 11:45:10 - telegram_bot - INFO - 📨 Message vocal autorisé de Julien (ID: 1699768293, durée: 27s)
2025-10-24 11:45:11 - telegram_bot - INFO - ✅ Job soumis: f9a60a07-068b-4f3b-9b38-2ffa267ae36b (user: 1699768293)
2025-10-24 11:45:18 - telegram_bot - INFO - ✅ Transcription OK: 145 chars (user: 1699768293)
```

---

## 📁 Structure des fichiers

```
/opt/telegram-bot/
├── bot.py                 # Code principal (version sécurisée)
├── Dockerfile             # Image Python 3.11 slim
├── docker-compose.yml     # Orchestration container
├── requirements.txt       # python-telegram-bot==21.3, aiohttp==3.9.5
├── .env                   # Configuration (token, limits, whitelist)
└── .env.example          # Template de configuration
```

---

## 🚀 Déploiement

### Installation initiale

```bash
# 1. Créer le répertoire
ssh root@69.62.108.82
mkdir -p /opt/telegram-bot
cd /opt/telegram-bot

# 2. Créer les fichiers (bot.py, Dockerfile, docker-compose.yml, requirements.txt)
# Voir section "Fichiers de configuration" ci-dessous

# 3. Configuration
cp .env.example .env
nano .env
# Modifier TELEGRAM_BOT_TOKEN et ALLOWED_USERS

# 4. Build et démarrage
docker-compose up --build -d

# 5. Connexion au réseau WhisperX
docker network connect whisperx_whisperx telegram-voice-bot

# 6. Vérifier les logs
docker logs -f telegram-voice-bot
```

### Mise à jour du code

```bash
cd /opt/telegram-bot
nano bot.py  # Modifier le code
docker-compose up --build -d  # Rebuild et redémarrage
```

---

## ⚙️ Configuration (.env)

```env
# Token Telegram (obligatoire)
TELEGRAM_BOT_TOKEN=7867830645:AAGSgh5xUIeeMPVWJN2ska7qsTN4hcZgHAQ

# URL WhisperX
WHISPERX_URL=http://whisperx:8002

# Sécurité: Liste des IDs autorisés (séparés par virgule)
# Exemple: ALLOWED_USERS=1699768293,987654321
ALLOWED_USERS=1699768293
ALLOW_ALL_USERS=false

# Limites de sécurité (adaptées usage intensif)
MAX_VOICE_DURATION=1200       # 20 minutes
MAX_VOICE_SIZE_MB=100         # 100 MB
MAX_REQUESTS_PER_MINUTE=20    # 20 vocaux/minute
MAX_REQUESTS_PER_HOUR=100     # 100 vocaux/heure
```

---

## 📱 Utilisation

### Commandes disponibles

| Commande | Description |
|----------|-------------|
| `/start` | Affiche votre ID et statut d'accès |
| `/help` | Aide et limites de sécurité |
| `/status` | État de WhisperX et du système |
| `/stats` | Voir votre quota restant |

### Workflow utilisateur

1. **Ouvrir Telegram** → Chercher `@transcripteur_vocal_bot`
2. **Envoyer un vocal** 🎤 (appuyer sur le micro, enregistrer, envoyer)
3. **Attendre 10-30s** (selon durée du vocal)
4. **Recevoir la transcription** avec:
   - ✅ Texte complet
   - 🗣️ Langue détectée
   - ⏱️ Durée
   - 📏 Nombre de segments

### Format de réponse

```
✅ Transcription terminée

🗣️ Langue: fr
⏱️ Durée: 27.5s
📏 Segments: 4

📝 Texte:
Bonjour, je teste le bot de transcription vocale.
Il fonctionne parfaitement et la qualité est excellente.
```

---

## 🔧 Maintenance

### Commandes courantes

```bash
# Logs en temps réel
docker logs -f telegram-voice-bot

# Redémarrer
cd /opt/telegram-bot && docker-compose restart

# Arrêter
docker-compose stop

# Rebuild complet
docker-compose down
docker-compose up --build -d
docker network connect whisperx_whisperx telegram-voice-bot

# Vérifier la connexion WhisperX
docker exec telegram-voice-bot python3 -c "import urllib.request; print(urllib.request.urlopen('http://whisperx:8002/').read().decode())"
```

### Ajouter un utilisateur à la whitelist

```bash
# 1. Demander à l'utilisateur d'envoyer /start au bot
# Il recevra : "Votre Telegram ID: 123456789"

# 2. Modifier .env
cd /opt/telegram-bot
nano .env
# Ajouter l'ID: ALLOWED_USERS=1699768293,123456789

# 3. Redémarrer
docker-compose restart
```

### Problèmes courants

**Bot ne répond pas** :
```bash
docker logs telegram-voice-bot --tail 50
# Vérifier les erreurs de token ou connexion
```

**Erreur "Cannot connect to host whisperx:8002"** :
```bash
# Vérifier la connexion réseau
docker network connect whisperx_whisperx telegram-voice-bot
```

**Rate limit trop restrictif** :
```bash
nano .env
# Modifier MAX_REQUESTS_PER_MINUTE et MAX_REQUESTS_PER_HOUR
docker-compose restart
```

---

## 🔮 Évolution future : Pipeline IA

### Architecture prévue

```
Telegram Voice
    ↓
Bot Python (transcription)
    ↓
Webhook n8n
    ↓
[Noeud 1] LangChain - Clarification
    ↓ Nettoie la transcription, ajoute ponctuation
[Noeud 2] LlamaIndex - Enrichissement
    ↓ Extrait concepts, tags, catégories
[Noeud 3] Ollama/LLM - Analyse sémantique
    ↓ Génère résumé, action items, sentiment
[Noeud 4] Formatage structuré
    ↓ JSON avec métadonnées enrichies
Notion API
    ↓ Stockage dans base de données Notion
```

### Technologies envisagées

| Composant | Technologie | Raison |
|-----------|-------------|--------|
| **Orchestration** | n8n | Workflows visuels, déjà déployé |
| **LLM Framework** | LangChain | Chaînes de traitement, prompt templates |
| **Vector DB** | LlamaIndex | Indexation sémantique, RAG |
| **LLM** | Ollama (llama3.2) | Déjà déployé, local, gratuit |
| **Stockage** | Notion API | Interface utilisateur, flexible |

### Workflow n8n prévu

**Trigger** : Webhook POST depuis bot Telegram

**Noeud 1 - Code: Préparation**
```javascript
// Extraire texte transcription
const text = $input.item.json.transcription;
return {
  json: {
    raw_text: text,
    metadata: {
      user_id: $input.item.json.user_id,
      duration: $input.item.json.duration,
      language: $input.item.json.language
    }
  }
};
```

**Noeud 2 - HTTP Request: LangChain Clarification**
```
POST https://ollama.srv759970.hstgr.cloud/api/generate
Body:
{
  "model": "llama3.2",
  "prompt": "Corrige la ponctuation et la grammaire de ce texte transcrit : {{ $json.raw_text }}",
  "stream": false
}
```

**Noeud 3 - HTTP Request: Extraction de tags**
```
POST https://ollama.srv759970.hstgr.cloud/api/generate
Body:
{
  "model": "llama3.2",
  "prompt": "Extrais les tags, catégories et concepts clés : {{ $json.clarified_text }}",
  "format": "json"
}
```

**Noeud 4 - HTTP Request: Notion Create Page**
```
POST https://api.notion.com/v1/pages
Headers:
  Authorization: Bearer {NOTION_TOKEN}
  Notion-Version: 2022-06-28
Body:
{
  "parent": { "database_id": "{DATABASE_ID}" },
  "properties": {
    "Titre": { "title": [{ "text": { "content": "{{ $json.summary }}" }}] },
    "Transcription": { "rich_text": [{ "text": { "content": "{{ $json.clarified_text }}" }}] },
    "Tags": { "multi_select": {{ $json.tags }} },
    "Durée": { "number": {{ $json.metadata.duration }} },
    "Date": { "date": { "start": "{{ $now }}" } }
  }
}
```

**Noeud 5 - Respond to Webhook**
```javascript
return {
  json: {
    status: "success",
    notion_url: $json.url,
    processed_at: new Date().toISOString()
  }
};
```

### Points d'extension

1. **Diarization** : Identifier les locuteurs différents
2. **Résumé** : Générer un résumé court automatique
3. **Action Items** : Extraire les tâches à faire
4. **Sentiment Analysis** : Analyser le ton (positif/négatif)
5. **Relations** : Lier aux notes Notion existantes
6. **Notifications** : Envoyer email/Slack si action critique

---

## 📊 Métriques et monitoring

**À implémenter** (voir `GUIDE_MONITORING_WHISPERX.md`) :

- Nombre de transcriptions/jour
- Temps moyen de traitement
- Taux d'erreur WhisperX
- Usage CPU/RAM du bot
- Quotas utilisateurs

---

## 🔗 Liens connexes

- **WhisperX API** : `/opt/whisperx/` - [docs/services/ai/whisperx.md](./whisperx.md)
- **n8n Automation** : https://n8n.srv759970.hstgr.cloud - [docs/services/apps/n8n.md](../apps/n8n.md)
- **Ollama LLM** : https://ollama.srv759970.hstgr.cloud - [docs/services/ai/ollama.md](./ollama.md)

---

## 📝 Changelog

**2025-10-24** : Déploiement initial version sécurisée
- Bot Telegram avec whitelist ID
- Polling asynchrone WhisperX
- Rate limiting (20/min, 100/h)
- Limites fichiers (20 min, 100 MB)
- Commandes: /start, /help, /status, /stats
- Documentation complète

---

**Prêt pour évolution vers pipeline IA complet avec n8n + LangChain + Notion**
