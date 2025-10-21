# Intégration RQ/Redis et Loki - Instructions

## Fichiers créés

1. **app/jobs.py** - Jobs RQ asynchrones (index_text_job, index_folder_job, chat_job)
2. **app/queue.py** - Configuration RQ et gestion des jobs
3. **app/loki_handler.py** - Handler Loki pour logging centralisé
4. **app/async_endpoints.py** - Endpoints API asynchrones (à intégrer dans api_v2.py)
5. **worker.py** - Worker RQ standalone
6. **docker-compose.v3.yml** - Docker Compose mis à jour avec worker + Redis + Loki

## Modifications à faire dans app/api_v2.py

### 1. Ajouter imports (lignes 11-13, après les imports existants)

```python
from .queue import enqueue_indexing, enqueue_chat, get_job_status
from .jobs import index_text_job, index_folder_job, chat_job
from .loki_handler import configure_loki_logging, loguru_loki_sink
```

### 2. Configurer Loki logging (après ligne 18, après la configuration logger)

```python
# Configure Loki logging
import os
loki_url = os.getenv("LOKI_URL")
if loki_url:
    logger.add(loguru_loki_sink, serialize=True)
    logger.info(f"Loki logging configured: {loki_url}")
```

### 3. Copier les endpoints async depuis async_endpoints.py

Ajouter après les endpoints existants (après la section INDEXING ENDPOINTS), avant la section SEARCH & RAG ENDPOINTS :

```python
# ===========================================================================
# ASYNC JOB ENDPOINTS
# ===========================================================================

@app.post("/projects/{project_id}/index/text/async")
async def index_text_async(project_id: str, request: IndexTextRequest):
    # ... copier le contenu depuis async_endpoints.py ...

@app.post("/projects/{project_id}/index/folder/async")
async def index_folder_async(project_id: str, request: IndexFolderRequest):
    # ... copier le contenu depuis async_endpoints.py ...

@app.post("/projects/{project_id}/chat/async")
async def chat_async(project_id: str, request: ChatRequest):
    # ... copier le contenu depuis async_endpoints.py ...

@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    # ... copier le contenu depuis async_endpoints.py ...

@app.get("/jobs")
async def list_jobs(status: Optional[str] = None, limit: int = 50):
    # ... copier le contenu depuis async_endpoints.py ...
```

### 4. Extraire la logique chat dans une fonction interne

Dans api_v2.py, créer une fonction `perform_chat_internal` pour la logique de chat réutilisable :

```python
def perform_chat_internal(project_id: str, query: str, top_k: int, model: str, **kwargs):
    """Internal chat function (reusable for sync and async)"""
    # Extraire le code existant du endpoint /chat
    # ... (code actuel du endpoint chat)
    return {
        "answer": answer,
        "context_chunks": len(results),
        "sources": sources
    }
```

Puis modifier le endpoint `/projects/{project_id}/chat` pour utiliser cette fonction.

## Déploiement

1. **Upload des fichiers** :
```bash
# Depuis le répertoire memvid-deploy/
scp app/jobs.py root@69.62.108.82:/opt/memvid/app/
scp app/queue.py root@69.62.108.82:/opt/memvid/app/
scp app/loki_handler.py root@69.62.108.82:/opt/memvid/app/
scp worker.py root@69.62.108.82:/opt/memvid/
scp docker-compose.v3.yml root@69.62.108.82:/opt/memvid/docker-compose.yml
```

2. **Modifier api_v2.py sur le serveur** selon les instructions ci-dessus

3. **Rebuild et redémarrage** :
```bash
ssh root@69.62.108.82 "cd /opt/memvid && docker-compose down && docker-compose build --no-cache && docker-compose up -d"
```

4. **Vérifier les services** :
```bash
ssh root@69.62.108.82 "docker-compose -f /opt/memvid/docker-compose.yml ps"
ssh root@69.62.108.82 "docker logs memvid-worker"
```

## Nouveaux endpoints disponibles

### Jobs asynchrones :
- `POST /projects/{id}/index/text/async` - Indexation de texte async
- `POST /projects/{id}/index/folder/async` - Indexation de dossier async
- `POST /projects/{id}/chat/async` - Chat RAG async

### Gestion des jobs :
- `GET /jobs/{job_id}` - Statut et résultat d'un job
- `GET /jobs?status=<status>&limit=<N>` - Liste des jobs

## Monitoring

### RQ Dashboard (WhisperX)
- URL : https://whisperx-dashboard.srv759970.hstgr.cloud
- Auth : julien / DevAccess2025
- Queues : memvid-chat, memvid-indexing, memvid-default

### Loki (via Grafana)
- URL : https://monitoring.srv759970.hstgr.cloud
- Auth : admin / AdminPass2025!
- Label filters : `{app="memvid-api", service="rag"}`

### Prometheus/Grafana
- Dashboard : https://monitoring.srv759970.hstgr.cloud/d/memvid-rag-api/memvid-rag-api
- Métriques incluent maintenant les jobs RQ

## Test

```bash
# Créer un projet
PROJECT_ID=$(curl -s -X POST https://memvid.srv759970.hstgr.cloud/projects \
  -u julien:DevAccess2025 \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Async","description":"Test async jobs"}' | jq -r '.id')

# Indexer en async
JOB_ID=$(curl -s -X POST https://memvid.srv759970.hstgr.cloud/projects/$PROJECT_ID/index/text/async \
  -u julien:DevAccess2025 \
  -H "Content-Type: application/json" \
  -d '{"text":"MemVid is awesome for async processing"}' | jq -r '.job_id')

# Vérifier le statut
curl -s https://memvid.srv759970.hstgr.cloud/jobs/$JOB_ID \
  -u julien:DevAccess2025 | jq

# Lister les jobs
curl -s https://memvid.srv759970.hstgr.cloud/jobs \
  -u julien:DevAccess2025 | jq
```
