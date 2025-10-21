# MemVid RAG API - Déploiement Docker

Service RAG (Retrieval-Augmented Generation) basé sur MemVid, utilisant des vidéos MP4 pour stocker et rechercher de la mémoire sémantique.

## Architecture

- **FastAPI** : API REST pour l'indexation et la recherche
- **MemVid** : Encode les chunks de texte en QR codes dans des vidéos
- **Ollama** : LLM local pour le chat avec contexte RAG
- **Docker** : Containerisation complète

## Déploiement

### 1. Transférer sur le serveur

```bash
scp -r memvid-deploy/ root@69.62.108.82:/opt/memvid
```

### 2. Build et démarrer

```bash
ssh root@69.62.108.82
cd /opt/memvid
docker-compose build
docker-compose up -d
```

### 3. Vérifier les logs

```bash
docker-compose logs -f memvid-api
```

## API Endpoints

### Status
```bash
GET /status
GET /health
```

### Indexation
```bash
POST /index/text
  Body: {"text": "...", "metadata": {...}}

POST /index/upload
  Form-data: file=document.pdf
```

### Recherche
```bash
POST /search
  Body: {"query": "...", "top_k": 5}
```

### Chat
```bash
POST /chat
  Body: {
    "query": "...",
    "top_k": 3,
    "model": "ollama",
    "ollama_model": "qwen2.5:14b"
  }
```

### Reset
```bash
DELETE /reset
```

## Nginx Configuration

```nginx
server {
    listen 80;
    server_name memvid.srv759970.hstgr.cloud;

    location / {
        proxy_pass http://localhost:8503;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
}
```

## SSL avec Let's Encrypt

```bash
certbot --nginx -d memvid.srv759970.hstgr.cloud
```

## Intégration Auto-Start

Ajouter à `/opt/docker-autostart/config.json` :

```json
{
  "memvid.srv759970.hstgr.cloud": {
    "port": 8503,
    "compose_path": "/opt/memvid",
    "services": ["memvid-api"],
    "theme": "matrix",
    "mode": "blocking"
  }
}
```

## Utilisation

### Exemple 1 : Indexer du texte

```bash
curl -X POST https://memvid.srv759970.hstgr.cloud/index/text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "MemVid est une bibliothèque qui encode du texte en vidéo MP4...",
    "metadata": {"source": "docs"}
  }'
```

### Exemple 2 : Upload PDF

```bash
curl -X POST https://memvid.srv759970.hstgr.cloud/index/upload \
  -F "file=@document.pdf"
```

### Exemple 3 : Recherche

```bash
curl -X POST https://memvid.srv759970.hstgr.cloud/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Comment fonctionne MemVid?",
    "top_k": 5
  }'
```

### Exemple 4 : Chat

```bash
curl -X POST https://memvid.srv759970.hstgr.cloud/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explique moi MemVid en français",
    "top_k": 3
  }'
```

## Performance

- **Stockage** : 100MB texte → 1-2MB vidéo (ratio 50-100×)
- **Recherche** : <100ms pour 1M chunks
- **RAM** : ~500MB constant
- **Indexation** : ~10K chunks/s

## Logs

- **Application** : `/opt/memvid/logs/memvid-api.log`
- **Docker** : `docker-compose logs -f`
