# 🤖 RAGFlow & RAG-Anything - Documentation

Installation et configuration de RAGFlow et RAG-Anything sur srv759970.hstgr.cloud

---

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [RAGFlow](#ragflow)
3. [RAG-Anything](#rag-anything)
4. [Configuration](#configuration)
5. [Utilisation](#utilisation)
6. [Maintenance](#maintenance)

---

## 🎯 Vue d'ensemble

### RAGFlow

**RAGFlow** est un moteur RAG (Retrieval-Augmented Generation) open-source de pointe qui fusionne les capacités RAG avec des fonctionnalités d'Agent IA.

**Fonctionnalités clés**:
- Deep document understanding (analyse avancée avec DeepDoc)
- Chunking intelligent basé sur templates
- Citations traçables et réduction des hallucinations
- Support multi-formats (PDF, Word, Excel, images, pages web, etc.)
- Interface web intuitive avec workflow automatisé
- Compatible avec workflows agentiques et MCP

**Accès** : https://ragflow.srv759970.hstgr.cloud

### RAG-Anything

**RAG-Anything** est un framework RAG multimodal all-in-one basé sur LightRAG qui étend les capacités traditionnelles de RAG.

**Fonctionnalités clés**:
- Pipeline multimodal end-to-end (texte, images, tableaux, équations)
- Extraction automatique de knowledge graph multimodal
- Support de parsers avancés (MinerU, Docling)
- Traitement adaptatif avec modes multiples
- API REST FastAPI pour intégration facile

**Accès API** : https://rag-anything.srv759970.hstgr.cloud

---

## 🚀 RAGFlow

### Architecture

Stack Docker complète (5 conteneurs) :

```
ragflow-server     → Application principale (FastAPI)
ragflow-mysql      → Base de données
ragflow-es-01      → Elasticsearch (recherche vectorielle)
ragflow-redis      → Cache et queue
ragflow-minio      → Stockage objet
```

### Emplacement

```
/opt/ragflow/
├── docker/
│   ├── docker-compose-full.yml     # Configuration Docker consolidée
│   ├── .env                         # Variables d'environnement
│   ├── ragflow-logs/                # Logs applicatifs
│   ├── service_conf.yaml.template   # Configuration services
│   └── init.sql                     # Init base de données
```

### Ports

| Service | Port externe | Port interne | Usage |
|---------|-------------|--------------|-------|
| API HTTP | 9500 | 9380 | API principale |
| Admin HTTP | 9501 | 9381 | Interface admin |
| MySQL | 5456 | 3306 | Base de données |
| Elasticsearch | 1220 | 9200 | Moteur de recherche |
| Redis | 6381 | 6379 | Cache |
| MinIO API | 9502 | 9000 | Stockage objet |
| MinIO Console | 9503 | 9001 | Interface MinIO |

### Configuration LLM

Éditer `/opt/ragflow/docker/service_conf.yaml.template` :

```yaml
user_default_llm:
  factory: "OpenAI"              # OpenAI, Anthropic, Ollama, etc.
  api_key: "sk-your-key-here"    # Votre clé API
  base_url: ""                   # URL de base (optionnel)
  model: "gpt-4o-mini"           # Modèle par défaut
```

Après modification:
```bash
cd /opt/ragflow/docker
docker-compose -f docker-compose-full.yml restart ragflow
```

### Commandes essentielles

```bash
# Démarrer
cd /opt/ragflow/docker
docker-compose -f docker-compose-full.yml up -d

# Arrêter
docker-compose -f docker-compose-full.yml down

# Logs
docker logs ragflow-server --tail=50 -f
docker logs ragflow-mysql --tail=50

# Redémarrer
docker restart ragflow-server

# Status complet
docker ps --filter name=ragflow

# Vérifier santé Elasticsearch
curl -u elastic:infini_rag_flow http://localhost:1220/_cluster/health
```

### Systemd

Le service est configuré pour démarrage automatique :

```bash
# Status
systemctl status ragflow.service

# Démarrer/Arrêter/Redémarrer
systemctl start ragflow.service
systemctl stop ragflow.service
systemctl restart ragflow.service

# Logs
journalctl -u ragflow.service -f
```

---

## 🎨 RAG-Anything

### Architecture

API FastAPI personnalisée conteneurisée :

```
rag-anything-api   → Serveur FastAPI avec RAG-Anything intégré
Volumes:
  rag-anything-storage   → Knowledge graph et index
  rag-anything-output    → Documents parsés
```

### Emplacement

```
/opt/rag-anything/
├── Dockerfile              # Image Docker custom
├── docker-compose.yml      # Configuration Docker
├── api_server.py           # Serveur FastAPI
├── .env                    # Variables d'environnement
├── raganything/            # Package Python
├── examples/               # Exemples d'utilisation
└── requirements.txt        # Dépendances Python
```

### Configuration

Fichier `/opt/rag-anything/.env` :

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=

# Model Configuration
LLM_MODEL=gpt-4o-mini
VISION_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIM=3072
MAX_TOKEN_SIZE=8192

# Parser Configuration
PARSER=mineru                # ou docling
PARSE_METHOD=auto            # auto, ocr, ou txt

# HuggingFace Mirror (optionnel)
HF_ENDPOINT=https://hf-mirror.com
```

### API Endpoints

Base URL: `https://rag-anything.srv759970.hstgr.cloud`

#### GET /
Informations sur le service

```bash
curl https://rag-anything.srv759970.hstgr.cloud/
```

#### GET /health
Health check

```bash
curl https://rag-anything.srv759970.hstgr.cloud/health
```

#### POST /upload
Upload et traitement d'un document

```bash
curl -X POST https://rag-anything.srv759970.hstgr.cloud/upload \
  -F "file=@document.pdf" \
  -F "parse_method=auto"
```

**Paramètres**:
- `file`: Document à traiter (PDF, DOCX, PPTX, images, etc.)
- `parse_method`: `auto`, `ocr`, ou `txt`

**Réponse**:
```json
{
  "status": "success",
  "message": "Document document.pdf processed successfully",
  "filename": "document.pdf"
}
```

#### POST /query
Interroger le knowledge base

```bash
curl -X POST https://rag-anything.srv759970.hstgr.cloud/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main findings in the research?",
    "mode": "hybrid",
    "vlm_enhanced": true
  }'
```

**Paramètres**:
- `query` (string): Question à poser
- `mode` (string): Mode de recherche
  - `hybrid`: Combine vectoriel + knowledge graph (recommandé)
  - `local`: Recherche locale uniquement
  - `global`: Recherche globale uniquement
  - `naive`: Recherche vectorielle simple
- `vlm_enhanced` (boolean, optionnel): Utiliser VLM pour analyser les images

**Réponse**:
```json
{
  "answer": "The main findings indicate that...",
  "status": "success"
}
```

#### DELETE /clear
Effacer le stockage RAG

```bash
curl -X DELETE https://rag-anything.srv759970.hstgr.cloud/clear
```

### Commandes Docker

```bash
# Démarrer
cd /opt/rag-anything
docker-compose up -d

# Arrêter
docker-compose down

# Rebuild (après modification du code)
docker-compose build --no-cache
docker-compose up -d --force-recreate

# Logs
docker logs rag-anything-api --tail=50 -f

# Status
docker ps --filter name=rag-anything

# Accéder au conteneur
docker exec -it rag-anything-api bash

# Vérifier les volumes
docker volume ls | grep rag-anything
```

### Systemd

```bash
# Status
systemctl status rag-anything.service

# Démarrer/Arrêter
systemctl start rag-anything.service
systemctl stop rag-anything.service

# Logs
journalctl -u rag-anything.service -f
```

---

## 💡 Utilisation

### Exemple RAGFlow (Interface Web)

1. Accéder à https://ragflow.srv759970.hstgr.cloud
2. Créer un compte (première utilisation)
3. Créer une base de connaissances :
   - Cliquer sur "Knowledge Base"
   - "Create Knowledge Base"
   - Choisir un template de chunking
4. Uploader des documents
5. Créer un assistant ou utiliser l'API

### Exemple RAG-Anything (API Python)

```python
import requests

base_url = "https://rag-anything.srv759970.hstgr.cloud"

# 1. Upload un document
with open("research_paper.pdf", "rb") as f:
    response = requests.post(
        f"{base_url}/upload",
        files={"file": f},
        data={"parse_method": "auto"}
    )
    print(response.json())
    # Output: {"status": "success", "message": "...", "filename": "..."}

# 2. Interroger avec mode hybrid
response = requests.post(
    f"{base_url}/query",
    json={
        "query": "What methodology was used in this research?",
        "mode": "hybrid",
        "vlm_enhanced": True  # Pour analyser les figures avec VLM
    }
)
result = response.json()
print(result["answer"])

# 3. Interroger avec mode global (pour questions générales)
response = requests.post(
    f"{base_url}/query",
    json={
        "query": "Summarize the key contributions",
        "mode": "global"
    }
)
print(response.json()["answer"])
```

### Exemple RAG-Anything (cURL)

```bash
# Upload
curl -X POST https://rag-anything.srv759970.hstgr.cloud/upload \
  -F "file=@presentation.pptx" \
  -F "parse_method=auto"

# Query simple
curl -X POST https://rag-anything.srv759970.hstgr.cloud/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the conclusions?", "mode": "hybrid"}'

# Query avec VLM pour analyser les images
curl -X POST https://rag-anything.srv759970.hstgr.cloud/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain the charts and diagrams",
    "mode": "hybrid",
    "vlm_enhanced": true
  }'
```

---

## 🛠️ Maintenance

### Backup

#### RAGFlow

```bash
# Backup MySQL
docker exec ragflow-mysql mysqldump -u root -pinfini_rag_flow rag_flow > ragflow_backup_$(date +%Y%m%d).sql

# Backup MinIO (stockage documents)
docker exec ragflow-minio mc mirror /data /backup

# Backup volumes complet
docker run --rm \
  -v ragflow-mysql-data:/mysql \
  -v $(pwd):/backup \
  alpine tar czf /backup/ragflow-volumes-backup-$(date +%Y%m%d).tar.gz -C /mysql .
```

#### RAG-Anything

```bash
# Backup storage (knowledge graph)
docker run --rm \
  -v rag-anything-storage:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/rag-anything-storage-$(date +%Y%m%d).tar.gz -C /data .

# Backup output (documents parsés)
docker run --rm \
  -v rag-anything-output:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/rag-anything-output-$(date +%Y%m%d).tar.gz -C /data .
```

### Monitoring

```bash
# Ressources consommées
docker stats --no-stream | grep -E "ragflow|rag-anything"

# Espace disque
docker system df
df -h /var/lib/docker

# Logs d'erreurs
docker logs ragflow-server 2>&1 | grep ERROR | tail -20
docker logs rag-anything-api 2>&1 | grep ERROR | tail -20

# Health checks
curl -f https://ragflow.srv759970.hstgr.cloud/ || echo "RAGFlow DOWN"
curl -f https://rag-anything.srv759970.hstgr.cloud/health || echo "RAG-Anything DOWN"
```

### Mises à jour

#### RAGFlow

```bash
cd /opt/ragflow/docker

# 1. Backup d'abord !
docker exec ragflow-mysql mysqldump -u root -pinfini_rag_flow rag_flow > backup_before_update.sql

# 2. Modifier .env avec nouvelle version
# RAGFLOW_IMAGE=infiniflow/ragflow:v0.22.0-slim

# 3. Pull et redéployer
docker-compose -f docker-compose-full.yml pull
docker-compose -f docker-compose-full.yml up -d --force-recreate

# 4. Vérifier
docker logs ragflow-server --tail=50
```

#### RAG-Anything

```bash
cd /opt/rag-anything

# 1. Pull dernières modifications (si git)
git pull

# 2. Rebuild
docker-compose build --no-cache

# 3. Redéployer
docker-compose up -d --force-recreate

# 4. Vérifier
docker logs rag-anything-api --tail=50
curl https://rag-anything.srv759970.hstgr.cloud/health
```

### Troubleshooting

#### RAGFlow ne démarre pas

```bash
# 1. Vérifier les logs
docker logs ragflow-server

# 2. Vérifier Elasticsearch
curl -u elastic:infini_rag_flow http://localhost:1220/_cluster/health

# 3. Vérifier MySQL
docker exec ragflow-mysql mysql -u root -pinfini_rag_flow -e "SELECT 1"

# 4. Vérifier Redis
docker exec ragflow-redis redis-cli -a infini_rag_flow ping

# 5. Redémarrer tous les services
cd /opt/ragflow/docker
docker-compose -f docker-compose-full.yml restart
```

#### RAG-Anything timeout sur upload

```bash
# 1. Augmenter timeout Nginx
# Éditer /etc/nginx/sites-available/rag-anything
# Ajouter: proxy_read_timeout 600;
systemctl reload nginx

# 2. Vérifier MinerU
docker exec rag-anything-api python -c "import magic_pdf; print('OK')"

# 3. Vérifier clé API
docker exec rag-anything-api env | grep OPENAI_API_KEY
```

#### Problèmes de mémoire

```bash
# RAGFlow consomme beaucoup (surtout Elasticsearch 8GB)
# Réduire MEM_LIMIT dans .env
MEM_LIMIT=4073741824  # 4GB au lieu de 8GB

# Ou désactiver temporairement services non critiques
docker stop ragflow-es-01

# Nettoyer Docker
docker system prune -a --volumes
```

---

## 📚 Ressources

### RAGFlow

- **Documentation** : https://ragflow.io/docs/dev/
- **GitHub** : https://github.com/infiniflow/ragflow
- **Release notes** : https://ragflow.io/docs/dev/release_notes
- **Docker Hub** : https://hub.docker.com/r/infiniflow/ragflow

### RAG-Anything

- **GitHub** : https://github.com/HKUDS/RAG-Anything
- **Paper** : https://arxiv.org/abs/2510.12323
- **PyPI** : https://pypi.org/project/raganything/
- **LightRAG** : https://github.com/HKUDS/LightRAG

---

## 🔐 Sécurité

### Credentials par défaut

**RAGFlow** :
- MySQL root: `infini_rag_flow`
- Elasticsearch elastic: `infini_rag_flow`
- Redis: `infini_rag_flow`
- MinIO: `rag_flow` / `infini_rag_flow`

**Important** : Changez ces mots de passe en production !

### SSL/TLS

- Certificats Let's Encrypt auto-renouvelés
- Domaines: `ragflow.srv759970.hstgr.cloud`, `rag-anything.srv759970.hstgr.cloud`
- Renouvellement automatique via certbot

---

**Dernière mise à jour** : Octobre 2025
