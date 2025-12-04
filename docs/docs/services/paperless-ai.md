# Paperless AI - Intelligent Document Assistant

**URL:** https://paperless-ai.srv759970.hstgr.cloud
**Container:** `paperless-ai`
**Stack:** FastAPI + Ollama + Paperless-ngx API

## Vue d'Ensemble

Paperless AI est un assistant intelligent qui s'intègre avec Paperless-ngx pour fournir des capacités de traitement documentaire avancées basées sur l'IA.

### Fonctionnalités

- **🤖 Analyse sémantique** - Compréhension du contenu des documents
- **🏷️ Auto-tagging intelligent** - Classification par LLM
- **💬 Q&A documentaire** - Posez des questions sur vos documents
- **📊 Extraction de données** - Extraction structurée d'informations (montants, dates, etc.)
- **🔍 Recherche sémantique** - Au-delà de la recherche par mots-clés
- **📝 Résumés automatiques** - Génération de résumés de documents longs

## Architecture

```
┌─────────────────────────────────────────────┐
│           Paperless AI API                  │
│         (FastAPI - Port 8001)               │
└─────────┬───────────────────────┬───────────┘
          │                       │
    ┌─────▼──────────┐    ┌──────▼───────────┐
    │  Paperless-ngx │    │     Ollama       │
    │      API       │    │  (LLM Inference) │
    └────────────────┘    └──────────────────┘
          │
    ┌─────▼──────────┐
    │   PostgreSQL   │
    │   (Documents)  │
    └────────────────┘
```

## Configuration

### Docker Compose

```yaml
services:
  paperless-ai:
    image: paperless-ai:latest
    container_name: paperless-ai
    restart: unless-stopped
    ports:
      - "8001:8000"
    environment:
      - PAPERLESS_API_URL=https://paperless.srv759970.hstgr.cloud/api
      - PAPERLESS_API_TOKEN=${PAPERLESS_TOKEN}
      - OLLAMA_API_URL=http://ollama:11434
      - DEFAULT_MODEL=qwen2.5:7b
      - EMBEDDING_MODEL=nomic-embed-text
    depends_on:
      - ollama
      - paperless-ngx
```

### Variables d'Environnement

```bash
PAPERLESS_API_URL=https://paperless.srv759970.hstgr.cloud/api
PAPERLESS_API_TOKEN=<paperless-token>
OLLAMA_API_URL=http://69.62.108.82:11434
DEFAULT_MODEL=qwen2.5:7b
EMBEDDING_MODEL=nomic-embed-text
MAX_CONTEXT_LENGTH=4096
TEMPERATURE=0.1
```

## API Endpoints

### Documentation Interactive

**Swagger UI:** https://paperless-ai.srv759970.hstgr.cloud/docs
**ReDoc:** https://paperless-ai.srv759970.hstgr.cloud/redoc

### Endpoints Principaux

#### 1. Analyse de Document

```bash
POST /api/v1/analyze
Content-Type: application/json

{
  "document_id": 123,
  "analysis_type": "summary|tags|extract|qa"
}
```

**Exemple:**
```bash
curl -X POST https://paperless-ai.srv759970.hstgr.cloud/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": 123,
    "analysis_type": "summary"
  }'
```

**Réponse:**
```json
{
  "document_id": 123,
  "analysis_type": "summary",
  "result": {
    "summary": "Facture EDF pour la période janvier 2024. Montant total: 156.23€. Consommation: 450 kWh.",
    "confidence": 0.95
  },
  "processing_time": 2.3
}
```

#### 2. Auto-Tagging Intelligent

```bash
POST /api/v1/auto-tag
Content-Type: application/json

{
  "document_id": 123,
  "suggest_only": false
}
```

**Exemple:**
```bash
curl -X POST https://paperless-ai.srv759970.hstgr.cloud/api/v1/auto-tag \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": 123,
    "suggest_only": true
  }'
```

**Réponse:**
```json
{
  "document_id": 123,
  "suggested_tags": [
    {"name": "facture", "confidence": 0.98},
    {"name": "edf", "confidence": 0.95},
    {"name": "energie", "confidence": 0.87}
  ],
  "applied": false
}
```

#### 3. Questions-Réponses

```bash
POST /api/v1/qa
Content-Type: application/json

{
  "document_id": 123,
  "question": "Quel est le montant total?"
}
```

**Exemple:**
```bash
curl -X POST https://paperless-ai.srv759970.hstgr.cloud/api/v1/qa \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": 123,
    "question": "Quel est le montant de cette facture?"
  }'
```

**Réponse:**
```json
{
  "document_id": 123,
  "question": "Quel est le montant de cette facture?",
  "answer": "Le montant total de la facture est de 156,23 euros.",
  "confidence": 0.92,
  "sources": ["page 1"]
}
```

#### 4. Extraction de Données

```bash
POST /api/v1/extract
Content-Type: application/json

{
  "document_id": 123,
  "fields": ["amount", "date", "vendor", "invoice_number"]
}
```

**Exemple:**
```bash
curl -X POST https://paperless-ai.srv759970.hstgr.cloud/api/v1/extract \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": 123,
    "fields": ["amount", "date", "vendor"]
  }'
```

**Réponse:**
```json
{
  "document_id": 123,
  "extracted_data": {
    "amount": {"value": "156.23", "currency": "EUR", "confidence": 0.98},
    "date": {"value": "2024-01-15", "confidence": 0.95},
    "vendor": {"value": "EDF", "confidence": 1.0}
  }
}
```

#### 5. Recherche Sémantique

```bash
POST /api/v1/semantic-search
Content-Type: application/json

{
  "query": "factures d'électricité de janvier",
  "top_k": 5
}
```

**Réponse:**
```json
{
  "query": "factures d'électricité de janvier",
  "results": [
    {
      "document_id": 123,
      "title": "Facture EDF Janvier 2024",
      "similarity": 0.94,
      "snippet": "Facture pour la période du 01/01/2024 au 31/01/2024..."
    }
  ]
}
```

## Intégrations

### Paperless-ngx

Paperless AI se connecte à Paperless-ngx via son API pour:
- Récupérer le contenu des documents
- Appliquer automatiquement les tags suggérés
- Mettre à jour les métadonnées

### Ollama

Utilise les modèles LLM locaux pour:
- Analyse sémantique (qwen2.5:7b)
- Génération d'embeddings (nomic-embed-text)
- Classification et extraction

**Modèles recommandés:**
- `qwen2.5:7b` - Analyse générale et Q&A
- `mistral:7b` - Alternative performante
- `nomic-embed-text` - Embeddings pour recherche sémantique

## Workflows Automatisés

### Auto-Processing Pipeline

```yaml
1. Nouveau document détecté dans Paperless
   ↓
2. Paperless AI analyse le contenu
   ↓
3. Extraction automatique (montant, date, vendeur)
   ↓
4. Génération de tags intelligents
   ↓
5. Classification par type de document
   ↓
6. Application des tags et métadonnées
   ↓
7. Indexation pour recherche sémantique
```

### Configuration du Webhook

Dans Paperless-ngx, configurez un webhook pour déclencher l'analyse automatique:

```bash
# Webhook URL
POST https://paperless-ai.srv759970.hstgr.cloud/api/v1/webhook/document-added

# Payload
{
  "document_id": 123,
  "event": "document_added"
}
```

## Cas d'Usage

### 1. Traitement de Factures

```python
import requests

# Analyser une facture
response = requests.post(
    "https://paperless-ai.srv759970.hstgr.cloud/api/v1/extract",
    json={
        "document_id": 123,
        "fields": ["amount", "due_date", "vendor", "invoice_number"]
    }
)

data = response.json()
print(f"Montant: {data['extracted_data']['amount']['value']} EUR")
print(f"Vendeur: {data['extracted_data']['vendor']['value']}")
```

### 2. Q&A sur Documents Juridiques

```python
# Poser une question
response = requests.post(
    "https://paperless-ai.srv759970.hstgr.cloud/api/v1/qa",
    json={
        "document_id": 456,
        "question": "Quelles sont les clauses de résiliation?"
    }
)

answer = response.json()
print(f"Réponse: {answer['answer']}")
```

### 3. Recherche Sémantique

```python
# Rechercher des documents similaires
response = requests.post(
    "https://paperless-ai.srv759970.hstgr.cloud/api/v1/semantic-search",
    json={
        "query": "documents relatifs au bail commercial",
        "top_k": 10
    }
)

results = response.json()
for doc in results['results']:
    print(f"{doc['title']} - Similarité: {doc['similarity']}")
```

## Performance

### Temps de Traitement Moyens

- **Analyse/Résumé:** 2-5 secondes
- **Auto-tagging:** 1-3 secondes
- **Extraction de données:** 3-7 secondes
- **Q&A:** 2-4 secondes
- **Recherche sémantique:** < 1 seconde

### Optimisations

```yaml
# Utiliser un modèle plus léger pour production
DEFAULT_MODEL=qwen2.5:3b  # Plus rapide

# Augmenter le cache
CACHE_SIZE=1000

# Batch processing
BATCH_SIZE=10
```

## Monitoring

### Métriques

```bash
GET /api/v1/metrics
```

**Réponse:**
```json
{
  "total_analyses": 1234,
  "avg_processing_time": 3.2,
  "cache_hit_rate": 0.65,
  "active_connections": 5,
  "model_status": "healthy"
}
```

### Logs

```bash
# Logs en temps réel
docker logs -f paperless-ai

# Filtrer par niveau
docker logs paperless-ai | grep ERROR
```

## Troubleshooting

### Le Modèle est Lent

**Solution:** Utiliser un modèle plus léger
```bash
# Changer le modèle par défaut
docker exec paperless-ai \
  sed -i 's/qwen2.5:7b/qwen2.5:3b/g' /app/.env
docker restart paperless-ai
```

### Erreur de Connexion à Paperless

**Vérifier le token:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  https://paperless.srv759970.hstgr.cloud/api/documents/
```

### Ollama Inaccessible

**Vérifier le service:**
```bash
curl http://69.62.108.82:11434/api/tags
```

## Sécurité

- ✅ **HTTPS** - Connexions chiffrées
- ✅ **API Token** - Authentification requise
- ✅ **Rate Limiting** - Protection contre abus
- ✅ **Validation des entrées** - Prévention injection

## Voir Aussi

- [Paperless-ngx](paperless-ngx.md) - Système de GED principal
- [Ollama](../ai/ollama.md) - Service d'inférence LLM
- [Monitoring](../infrastructure/monitoring.md) - Stack de monitoring

## Liens Externes

- **Documentation FastAPI:** https://fastapi.tiangolo.com/
- **Ollama Models:** https://ollama.com/library

---

**Dernière mise à jour:** 2025-10-23
**Prochaine révision:** Après ajout de nouveaux modèles
