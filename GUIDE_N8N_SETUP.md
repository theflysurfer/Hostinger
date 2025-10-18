# Guide n8n - Automatisation et SMS vers Whisper

## 🎯 Objectif

n8n est une plateforme d'automatisation open-source qui permet de créer des workflows sans code. Ce guide explique comment connecter les SMS à l'API Whisper pour la transcription audio.

---

## 📋 Installation

### n8n déployé via Docker

**URL** : https://n8n.srv759970.hstgr.cloud
**Port interne** : 5678
**Container** : `n8n`

**Authentification** :
- Basic Auth : `julien` / `DevAccess2025`
- n8n : Créer un compte lors de la première connexion

---

## 🚀 Accès à n8n

1. Ouvrir https://n8n.srv759970.hstgr.cloud
2. Entrer Basic Auth : `julien` / `DevAccess2025`
3. Créer un compte n8n (email + mot de passe)

---

## 📱 Connecter SMS à Whisper API

### Workflow : SMS Audio → Whisper Transcription

**Objectif** : Recevoir un SMS contenant un lien audio → Télécharger l'audio → Envoyer à Whisper → Retourner la transcription

### Étape 1 : Créer un nouveau workflow

1. Dans n8n, cliquer **+ New Workflow**
2. Nommer : `SMS to Whisper Transcription`

### Étape 2 : Ajouter un trigger Webhook

1. Ajouter le node **Webhook**
2. Configuration :
   - **HTTP Method** : `POST`
   - **Path** : `sms-whisper`
   - **Respond** : `Last Node`
3. Copier l'URL du webhook (exemple : `https://n8n.srv759970.hstgr.cloud/webhook/sms-whisper`)

### Étape 3 : Extraire l'URL audio du SMS

1. Ajouter le node **Code**
2. Code JavaScript :
```javascript
// Extraire l'URL audio depuis le body du webhook
const smsBody = $input.item.json.body;
const audioUrl = smsBody.MediaUrl0 || smsBody.audio_url || smsBody.url;

return {
  json: {
    audioUrl: audioUrl,
    from: $input.item.json.From || $input.item.json.from,
    timestamp: new Date().toISOString()
  }
};
```

### Étape 4 : Télécharger le fichier audio

1. Ajouter le node **HTTP Request**
2. Configuration :
   - **Method** : `GET`
   - **URL** : `{{ $json.audioUrl }}`
   - **Response Format** : `File`
   - **Binary Property** : `audio`

### Étape 5 : Envoyer à Whisper API

1. Ajouter le node **HTTP Request**
2. Configuration :
   - **Method** : `POST`
   - **URL** : `https://whisper.srv759970.hstgr.cloud/v1/audio/transcriptions`
   - **Authentication** : `Generic Credential Type` → `Basic Auth`
     - Username : `julien`
     - Password : `DevAccess2025`
   - **Send Body** : `Yes` → `Form-Data Multipart`
   - **Body Parameters** :
     - **Key** : `file` → **Value** : `{{ $binary.audio }}`
     - **Key** : `model` → **Value** : `base`
     - **Key** : `response_format` → **Value** : `json`

### Étape 6 : Formater et retourner la réponse

1. Ajouter le node **Code**
2. Code JavaScript :
```javascript
const transcription = $input.item.json.text;
const from = $('Code').item.json.from;

return {
  json: {
    status: "success",
    transcription: transcription,
    from: from,
    timestamp: new Date().toISOString()
  }
};
```

### Étape 7 : Répondre au webhook

1. Ajouter le node **Respond to Webhook**
2. Configuration :
   - **Respond With** : `JSON`
   - **Response Body** : `{{ $json }}`

### Étape 8 : Activer le workflow

1. Cliquer sur **Save** en haut à droite
2. Activer le workflow avec le toggle en haut

---

## 🧪 Test du workflow

### Via cURL

```bash
curl -u julien:DevAccess2025 \
  -X POST https://n8n.srv759970.hstgr.cloud/webhook/sms-whisper \
  -H "Content-Type: application/json" \
  -d '{
    "From": "+33612345678",
    "audio_url": "https://example.com/audio.mp3"
  }'
```

### Via Twilio (si intégration SMS réelle)

1. Configurer un compte Twilio
2. Dans Twilio Console → Phone Numbers → Configure
3. **Messaging Configuration** :
   - **A MESSAGE COMES IN** : `Webhook`
   - **URL** : `https://n8n.srv759970.hstgr.cloud/webhook/sms-whisper`
   - **HTTP Method** : `POST`

---

## 📊 Exemples de workflows n8n utiles

### 1. Email vers Whisper
- Trigger : **Email Trigger** (IMAP)
- Action : Extraire pièce jointe audio → Whisper → Envoyer transcription par email

### 2. Google Drive Audio → Whisper
- Trigger : **Google Drive Trigger** (nouveau fichier dans dossier)
- Action : Télécharger fichier → Whisper → Ajouter transcription dans Google Sheets

### 3. Slack Audio → Whisper
- Trigger : **Slack Trigger** (message avec fichier)
- Action : Télécharger audio → Whisper → Répondre dans le thread

---

## 🔧 Configuration Docker de n8n

```bash
docker run -d \
  --name n8n \
  --restart unless-stopped \
  -p 5678:5678 \
  -e N8N_HOST=n8n.srv759970.hstgr.cloud \
  -e N8N_PORT=5678 \
  -e N8N_PROTOCOL=https \
  -e WEBHOOK_URL=https://n8n.srv759970.hstgr.cloud/ \
  -e GENERIC_TIMEZONE=Europe/Paris \
  -v /var/www/n8n:/home/node/.n8n \
  docker.n8n.io/n8nio/n8n
```

---

## 🔒 Sécurité

- **Basic Auth Nginx** : Protège l'accès à n8n (julien/DevAccess2025)
- **Webhook URLs** : Utiliser des chemins complexes pour éviter les accès non autorisés
- **Whisper API Auth** : Protégé par Basic Auth
- **Données** : Stockées dans `/var/www/n8n` sur le serveur

---

## 🛠️ Commandes utiles

### Redémarrer n8n
```bash
ssh root@69.62.108.82
docker restart n8n
```

### Voir les logs
```bash
docker logs -f n8n
```

### Mettre à jour n8n
```bash
docker stop n8n
docker rm n8n
docker pull docker.n8n.io/n8nio/n8n
# Relancer la commande docker run ci-dessus
```

### Backup des workflows
```bash
ssh root@69.62.108.82
tar -czf n8n-backup-$(date +%Y%m%d).tar.gz /var/www/n8n
```

---

## 📚 Ressources

- **n8n Documentation** : https://docs.n8n.io/
- **Webhook Node** : https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/
- **HTTP Request Node** : https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/
- **Whisper API Docs** : https://platform.openai.com/docs/api-reference/audio

---

**Créé le** : 2025-10-16
**URL n8n** : https://n8n.srv759970.hstgr.cloud
