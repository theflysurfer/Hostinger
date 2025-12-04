# n8n - Workflow Automation & Integration

**Type:** Workflow Automation Platform
**URL:** https://n8n.srv759970.hstgr.cloud
**Port interne:** 5678
**Authentification:** Basic Auth (cf. `/etc/nginx/.htpasswd`)

## Vue d'Ensemble

n8n est une plateforme d'automatisation de workflows puissante et extensible qui permet de connecter différents services et APIs ensemble. Alternative open-source à Zapier et Integromat (Make), n8n offre une interface visuelle pour créer des automatisations complexes.

### Caractéristiques Principales

- **Interface visuelle** - Éditeur de workflows par glisser-déposer
- **400+ intégrations** - Connecteurs pré-construits pour les services populaires
- **Webhooks** - Déclenchement via HTTP/HTTPS
- **Cron Jobs** - Exécution programmée
- **JavaScript** - Code personnalisé dans les workflows
- **Self-hosted** - Contrôle total des données
- **API REST** - Gestion programmatique des workflows
- **Exécution asynchrone** - Support des tâches longues

## Accès

### Interface Web

**URL principale:** https://n8n.srv759970.hstgr.cloud

**Authentification:**
- Méthode: HTTP Basic Auth (nginx)
- Fichier: `/etc/nginx/.htpasswd`
- Utilisateurs configurés: voir avec l'administrateur

### API REST

**Base URL:** https://n8n.srv759970.hstgr.cloud/api/v1

**Exemple - Lister les workflows:**
```bash
curl -u username:password https://n8n.srv759970.hstgr.cloud/api/v1/workflows
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Internet                          │
└────────────────────┬────────────────────────────────┘
                     │ HTTPS (443)
                     ▼
┌─────────────────────────────────────────────────────┐
│         Nginx Reverse Proxy + Basic Auth           │
│         /etc/nginx/sites-available/n8n             │
│                                                     │
│  • SSL: Let's Encrypt                              │
│  • Basic Auth: .htpasswd                           │
│  • Headers: WebSocket support                      │
└────────────────────┬────────────────────────────────┘
                     │ HTTP
                     ▼
┌─────────────────────────────────────────────────────┐
│            n8n Container (Port 5678)                │
│            /opt/n8n/docker-compose.yml              │
│                                                     │
│  • Image: n8nio/n8n:latest                         │
│  • Data: /opt/n8n/data                             │
│  • Files: /opt/n8n/files                           │
│  • Execution Mode: main                            │
└─────────────────────────────────────────────────────┘
```

## Déploiement

### Docker Compose

**Emplacement:** `/opt/n8n/docker-compose.yml`

```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    ports:
      - '127.0.0.1:5678:5678'
    environment:
      - N8N_HOST=n8n.srv759970.hstgr.cloud
      - N8N_PROTOCOL=https
      - N8N_PORT=5678
      - WEBHOOK_URL=https://n8n.srv759970.hstgr.cloud/
      - GENERIC_TIMEZONE=Europe/Paris
      - N8N_LOG_LEVEL=info
    volumes:
      - /opt/n8n/data:/home/node/.n8n
      - /opt/n8n/files:/files
    user: "1000:1000"
```

### Commandes Docker

**Démarrage:**
```bash
cd /opt/n8n
docker-compose up -d
```

**Arrêt:**
```bash
cd /opt/n8n
docker-compose down
```

**Redémarrage:**
```bash
cd /opt/n8n
docker-compose restart
```

**Logs:**
```bash
# Logs en temps réel
docker logs -f n8n

# Dernières 100 lignes
docker logs n8n --tail 100
```

**Rebuild (après mise à jour):**
```bash
cd /opt/n8n
docker-compose pull
docker-compose up -d
```

## Configuration Nginx

**Fichier:** `/etc/nginx/sites-available/n8n`

### Configuration HTTPS

```nginx
# HTTPS - n8n Workflow Automation
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name n8n.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/n8n.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/n8n.srv759970.hstgr.cloud/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    access_log /var/log/nginx/n8n-access.log;
    error_log /var/log/nginx/n8n-error.log;

    # Basic Auth protection
    include snippets/basic-auth.conf;

    location / {
        proxy_pass http://127.0.0.1:5678;
        proxy_http_version 1.1;

        # Headers pour WebSockets
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Headers standards
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts pour workflows longs
        proxy_read_timeout 600s;
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
    }
}

# HTTP -> HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name n8n.srv759970.hstgr.cloud;
    return 301 https://$host$request_uri;
}
```

**Activer la configuration:**
```bash
ln -sf /etc/nginx/sites-available/n8n /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

## Variables d'Environnement

### Variables Essentielles

| Variable | Valeur | Description |
|----------|--------|-------------|
| `N8N_HOST` | n8n.srv759970.hstgr.cloud | Hostname du serveur |
| `N8N_PROTOCOL` | https | Protocole d'accès |
| `N8N_PORT` | 5678 | Port interne |
| `WEBHOOK_URL` | https://n8n.srv759970.hstgr.cloud/ | URL des webhooks |
| `GENERIC_TIMEZONE` | Europe/Paris | Timezone pour les cron jobs |
| `N8N_LOG_LEVEL` | info | Niveau de logs |

### Variables Optionnelles

**Authentification (si besoin d'un second niveau):**
```yaml
- N8N_BASIC_AUTH_ACTIVE=true
- N8N_BASIC_AUTH_USER=admin
- N8N_BASIC_AUTH_PASSWORD=secure_password
```

**Base de données externe (PostgreSQL):**
```yaml
- DB_TYPE=postgresdb
- DB_POSTGRESDB_HOST=postgresql-shared
- DB_POSTGRESDB_PORT=5432
- DB_POSTGRESDB_DATABASE=n8n
- DB_POSTGRESDB_USER=n8n_user
- DB_POSTGRESDB_PASSWORD=password
```

**Exécution en mode queue:**
```yaml
- EXECUTIONS_MODE=queue
- QUEUE_BULL_REDIS_HOST=redis-shared
- QUEUE_BULL_REDIS_PORT=6379
```

## Utilisation

### Créer un Workflow Simple

1. **Accéder à n8n:** https://n8n.srv759970.hstgr.cloud
2. **Créer un nouveau workflow** - Cliquer sur "+ New workflow"
3. **Ajouter un trigger** - Ex: "Webhook", "Cron", "Manual"
4. **Ajouter des nodes** - Ex: "HTTP Request", "Set", "IF"
5. **Connecter les nodes** - Glisser-déposer entre les points de connexion
6. **Configurer chaque node** - Paramètres et données
7. **Tester** - Bouton "Execute Workflow"
8. **Activer** - Toggle "Active" en haut à droite

### Exemples de Workflows

#### 1. Webhook vers Discord

```
Webhook (Trigger)
  → Set (Formatter les données)
  → HTTP Request (POST vers Discord webhook)
```

**Configuration Webhook:**
- Method: POST
- Path: /webhook/discord-notification

**Configuration HTTP Request:**
- Method: POST
- URL: https://discord.com/api/webhooks/YOUR_WEBHOOK_ID
- Body: JSON avec le message

#### 2. Transcription Automatique

```
Webhook (Receive audio file URL)
  → HTTP Request (Download audio)
  → HTTP Request (POST to WhisperX)
  → Set (Format transcript)
  → HTTP Request (Send results)
```

#### 3. Surveillance de Services

```
Cron (Every 5 minutes)
  → HTTP Request (Check service health)
  → IF (Status != 200)
    → HTTP Request (Send alert to Rocket.Chat)
```

### Intégrations Disponibles

**Services IA:**
- Ollama (LLM local)
- OpenAI
- Anthropic Claude
- Hugging Face

**Transcription:**
- WhisperX API (local)
- Faster-Whisper Queue
- Whisper.cpp

**Communication:**
- Rocket.Chat
- Discord
- Slack
- Telegram
- Email (SMTP/SendGrid)

**Stockage:**
- Nextcloud
- Paperless-ngx (webhooks)
- S3 compatible
- Local filesystem

**Bases de données:**
- PostgreSQL (local)
- MongoDB (local)
- Redis (local)
- MySQL

**Outils:**
- HTTP Request (universel)
- Code (JavaScript/Python)
- Webhook
- Cron

## Webhooks

### URL des Webhooks

**Format:** `https://n8n.srv759970.hstgr.cloud/webhook/<webhook-path>`

**Exemple:**
```bash
curl -X POST https://n8n.srv759970.hstgr.cloud/webhook/my-workflow \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from external system"}'
```

### Webhooks de Test vs Production

- **Test:** `/webhook-test/<path>` - Exécution unique pour debug
- **Production:** `/webhook/<path>` - Workflow activé en permanence

### Authentification des Webhooks

**Option 1 - Header Authorization:**
```javascript
// Dans le node Webhook, activer "Authentication"
headers: {
  "Authorization": "Bearer your-secret-token"
}
```

**Option 2 - Query parameter:**
```bash
curl https://n8n.srv759970.hstgr.cloud/webhook/secure?token=SECRET
```

## Intégrations avec les Services srv759970

### 1. Transcription avec WhisperX

**Workflow:** Upload audio → Transcription → Stockage

```yaml
Nodes:
  1. Webhook (Receive audio URL)
  2. HTTP Request (POST to https://whisperx.srv759970.hstgr.cloud/transcribe)
     - Headers: {"Content-Type": "multipart/form-data"}
     - Body: File from previous node
  3. Set (Extract transcript)
  4. HTTP Request (Save to Paperless-ngx or Nextcloud)
```

### 2. Document OCR avec Paperless

**Workflow:** Upload PDF → Paperless → Webhook callback

```yaml
Nodes:
  1. Webhook (Receive document)
  2. HTTP Request (POST to Paperless-ngx API)
  3. Wait (Wait for OCR completion)
  4. HTTP Request (Get processed document)
  5. Notification (Rocket.Chat or Email)
```

### 3. Monitoring avec Grafana

**Workflow:** Cron → Check services → Alert si down

```yaml
Nodes:
  1. Cron (Every 5 minutes)
  2. HTTP Request (Check /health endpoints)
  3. IF (Status != healthy)
  4. HTTP Request (Create Grafana annotation)
  5. HTTP Request (Send alert to Rocket.Chat)
```

### 4. Synthèse Vocale avec XTTS

**Workflow:** Texte → TTS → Audio file

```yaml
Nodes:
  1. Webhook (Receive text)
  2. HTTP Request (POST to https://xtts-api.srv759970.hstgr.cloud/tts)
  3. Binary Data (Save audio)
  4. HTTP Request (Upload to Nextcloud)
  5. Response (Return download URL)
```

## Monitoring & Logs

### Logs Docker

**Voir les logs en temps réel:**
```bash
docker logs -f n8n
```

**Filtrer par niveau:**
```bash
docker logs n8n 2>&1 | grep ERROR
docker logs n8n 2>&1 | grep WARN
```

### Logs Nginx

**Access logs:**
```bash
tail -f /var/log/nginx/n8n-access.log
```

**Error logs:**
```bash
tail -f /var/log/nginx/n8n-error.log
```

### Métriques d'Exécution

**Dans l'interface n8n:**
- **Executions** - Liste toutes les exécutions
- **Workflows** - Statut actif/inactif
- **Credentials** - Connexions configurées

**Via logs Docker:**
```bash
# Compter les exécutions réussies
docker logs n8n 2>&1 | grep "Workflow execution finished" | wc -l

# Compter les erreurs
docker logs n8n 2>&1 | grep "Workflow execution error" | wc -l
```

## Backup & Restauration

### Backup des Données

**Répertoires à sauvegarder:**
```bash
/opt/n8n/data/          # Base de données SQLite et configurations
/opt/n8n/files/         # Fichiers uploadés dans les workflows
```

**Script de backup:**
```bash
#!/bin/bash
BACKUP_DIR="/backup/n8n/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Arrêter n8n temporairement
cd /opt/n8n && docker-compose stop

# Copier les données
cp -r /opt/n8n/data "$BACKUP_DIR/"
cp -r /opt/n8n/files "$BACKUP_DIR/"
cp /opt/n8n/docker-compose.yml "$BACKUP_DIR/"

# Redémarrer n8n
cd /opt/n8n && docker-compose start

echo "Backup saved to $BACKUP_DIR"
```

### Restauration

```bash
# Arrêter n8n
cd /opt/n8n && docker-compose down

# Restaurer depuis backup
BACKUP_PATH="/backup/n8n/20251023_120000"
rm -rf /opt/n8n/data /opt/n8n/files
cp -r "$BACKUP_PATH/data" /opt/n8n/
cp -r "$BACKUP_PATH/files" /opt/n8n/

# Vérifier les permissions
chown -R 1000:1000 /opt/n8n/data /opt/n8n/files

# Redémarrer
cd /opt/n8n && docker-compose up -d
```

### Export/Import de Workflows

**Export d'un workflow:**
1. Ouvrir le workflow dans n8n
2. Menu "..." → "Download"
3. Fichier JSON téléchargé

**Import d'un workflow:**
1. Page d'accueil n8n
2. "Import from File"
3. Sélectionner le fichier JSON

**Export via CLI:**
```bash
# Copier la base de données
docker cp n8n:/home/node/.n8n/database.sqlite /tmp/n8n-backup.sqlite
```

## Mise à Jour

### Update de l'Image Docker

```bash
cd /opt/n8n

# Pull la dernière version
docker-compose pull

# Redémarrer avec la nouvelle image
docker-compose up -d

# Vérifier les logs
docker logs n8n --tail 50
```

### Versions Spécifiques

**Modifier docker-compose.yml:**
```yaml
services:
  n8n:
    image: n8nio/n8n:1.58.0  # Version spécifique au lieu de :latest
```

**Appliquer:**
```bash
cd /opt/n8n
docker-compose up -d
```

## Sécurité

### Protection par Basic Auth (Nginx)

**Déjà configurée** via `include snippets/basic-auth.conf`

**Ajouter/modifier des utilisateurs:**
```bash
# Ajouter un utilisateur
htpasswd /etc/nginx/.htpasswd newuser

# Modifier un mot de passe
htpasswd /etc/nginx/.htpasswd existinguser

# Supprimer un utilisateur
htpasswd -D /etc/nginx/.htpasswd olduser

# Recharger nginx
systemctl reload nginx
```

### Credentials dans n8n

**Bonnes pratiques:**
- Ne jamais hardcoder les credentials dans les workflows
- Utiliser le système de "Credentials" de n8n
- Stocker les secrets dans des variables d'environnement

**Exemple - Configurer une API key:**
1. Settings → Credentials → Add Credential
2. Choisir le type (HTTP Header Auth, OAuth2, etc.)
3. Nom: "Ollama API"
4. Configuration selon le type
5. Save

### Webhooks Sécurisés

**Méthode 1 - Token dans l'URL:**
```javascript
// Dans le workflow, vérifier le token
{{ $json.query.token === 'SECRET_TOKEN' }}
```

**Méthode 2 - Header Authorization:**
```javascript
// Node Webhook → Authentication → Header Auth
{{ $json.headers.authorization === 'Bearer SECRET_TOKEN' }}
```

## Troubleshooting

### n8n ne démarre pas

**Vérifier les logs:**
```bash
docker logs n8n
```

**Erreurs courantes:**

**1. Permission denied:**
```bash
# Fix: Vérifier les permissions
ls -la /opt/n8n/data
chown -R 1000:1000 /opt/n8n/data /opt/n8n/files
```

**2. Port déjà utilisé:**
```bash
# Vérifier qui utilise le port 5678
ss -tlnp | grep 5678

# Modifier le port dans docker-compose.yml si nécessaire
```

**3. Erreur de base de données:**
```bash
# Supprimer la base corrompue (⚠️ perte de données!)
rm /opt/n8n/data/database.sqlite
docker-compose restart
```

### Workflows ne s'exécutent pas

**Vérifier:**
1. Le workflow est-il activé? (Toggle "Active")
2. Les credentials sont-elles valides?
3. Les URLs des APIs sont-elles correctes?
4. Les logs d'exécution (page "Executions")

**Debug mode:**
```bash
# Ajouter dans docker-compose.yml
environment:
  - N8N_LOG_LEVEL=debug

# Redémarrer
docker-compose up -d
```

### Webhooks ne fonctionnent pas

**Test du webhook:**
```bash
# Test direct sur le container
curl -X POST http://localhost:5678/webhook/test \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# Test via nginx
curl -X POST https://n8n.srv759970.hstgr.cloud/webhook/test \
  -u username:password \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

**Vérifier nginx:**
```bash
# Logs d'accès
tail -f /var/log/nginx/n8n-access.log

# Logs d'erreur
tail -f /var/log/nginx/n8n-error.log

# Test de config
nginx -t
```

### Performance lente

**Causes possibles:**
1. Workflows trop complexes
2. Trop d'exécutions concurrentes
3. Base de données SQLite limitée

**Solutions:**

**1. Activer le mode Queue (Redis):**
```yaml
environment:
  - EXECUTIONS_MODE=queue
  - QUEUE_BULL_REDIS_HOST=redis-shared
  - QUEUE_BULL_REDIS_PORT=6379
```

**2. Utiliser PostgreSQL:**
```yaml
environment:
  - DB_TYPE=postgresdb
  - DB_POSTGRESDB_HOST=postgresql-shared
  - DB_POSTGRESDB_DATABASE=n8n
```

**3. Limiter les exécutions:**
```yaml
environment:
  - N8N_PAYLOAD_SIZE_MAX=16
  - EXECUTIONS_TIMEOUT=300
```

## Ressources

### Documentation Officielle

- **Site officiel:** https://n8n.io
- **Documentation:** https://docs.n8n.io
- **Community:** https://community.n8n.io
- **GitHub:** https://github.com/n8n-io/n8n

### Tutoriels & Templates

- **Templates:** https://n8n.io/workflows
- **YouTube:** Channel officiel n8n
- **Blog:** https://blog.n8n.io

### Support srv759970

- **Logs:** `/var/log/nginx/n8n-*.log`
- **Config:** `/opt/n8n/docker-compose.yml`
- **Données:** `/opt/n8n/data`
- **Dashy:** https://dashy.srv759970.hstgr.cloud
- **Docs:** https://docs.srv759970.hstgr.cloud

## Voir Aussi

- [WhisperX](../ai/whisperx.md) - Transcription audio
- [Paperless-ngx](../documents/paperless-ngx.md) - Gestion documentaire
- [Ollama](../ai/ollama.md) - LLM local
- [Rocket.Chat](../collaboration/rocketchat.md) - Messagerie d'équipe
- [Nextcloud](../collaboration/nextcloud.md) - Cloud storage

---

**Dernière mise à jour:** 2025-10-23
**Status:** ✅ Production
**Maintenance:** Automatique (Docker restart policy)
