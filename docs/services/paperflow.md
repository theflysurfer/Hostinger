# Paperflow - Document Processing System

**Status:** Production
**Type:** Shared Service / Document Processing
**Containers:** 3 (API, Worker, Flower)
**Total Size:** ~6.65 GB
**Health:** ⚠️ Worker & Flower unhealthy
**Uptime:** 3+ weeks

---

## Overview

Paperflow est un système de traitement de documents basé sur Celery avec 3 composants:
1. **API** - Interface REST pour soumettre des documents
2. **Worker** - Traitement asynchrone des documents (Celery)
3. **Flower** - Monitoring des workers Celery

---

## Architecture

```
Client
  ↓
Paperflow API (port 9520)
  ↓
Redis/RabbitMQ (message broker)
  ↓
Paperflow Worker (Celery)
  ↓
Results Storage
  ↑
Flower Monitoring (port 9522)
```

---

## Components

### 1. Paperflow API

**Container:** `paperflow-api`
**Image:** `d39037f5b4df` (shared with worker)
**Port:** 9520:8000
**URL:** http://69.62.108.82:9520
**Status:** ✅ Healthy (3 weeks uptime)

#### Endpoints

```bash
# Health check
GET http://69.62.108.82:9520/health

# Submit document
POST http://69.62.108.82:9520/api/documents

# Get document status
GET http://69.62.108.82:9520/api/documents/{id}

# List documents
GET http://69.62.108.82:9520/api/documents
```

#### Start/Stop

```bash
# Start
docker start paperflow-api

# Stop
docker stop paperflow-api

# Logs
docker logs -f paperflow-api
```

---

### 2. Paperflow Worker

**Container:** `paperflow-worker`
**Image:** `paperflow_paperflow-worker:latest` (6.65 GB) ⚠️
**Port:** 8000/tcp (internal)
**Status:** ⚠️ Unhealthy (restarted 34 min ago)

#### Worker Configuration

```yaml
Container: paperflow-worker
Celery Workers: Auto (based on CPU)
Queue: paperflow
Broker: Redis or RabbitMQ
Backend: Redis
```

#### Commands

```bash
# Start worker
docker start paperflow-worker

# Stop worker
docker stop paperflow-worker

# Restart worker
docker restart paperflow-worker

# View logs
docker logs -f paperflow-worker

# Check Celery status
docker exec paperflow-worker celery -A paperflow inspect active
```

---

### 3. Paperflow Flower

**Container:** `paperflow-flower`
**Image:** `d39037f5b4df` (shared with API)
**Port:** 9522:5555
**URL:** http://69.62.108.82:9522
**Status:** ⚠️ Unhealthy (35 hours uptime)

#### Flower Dashboard

Access monitoring at: http://69.62.108.82:9522

**Features:**
- Real-time worker monitoring
- Task history
- Task queue status
- Worker resource usage
- Task execution graphs

#### Start/Stop

```bash
# Start
docker start paperflow-flower

# Stop
docker stop paperflow-flower

# Logs
docker logs -f paperflow-flower
```

---

## Deployment

### Docker Compose

Location: `/opt/paperflow/` (to be confirmed)

```yaml
version: '3.8'
services:
  redis:
    image: redis:alpine
    container_name: paperflow-redis
    restart: unless-stopped
    volumes:
      - redis-data:/data

  paperflow-api:
    image: paperflow:latest
    container_name: paperflow-api
    restart: unless-stopped
    ports:
      - "9520:8000"
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    depends_on:
      - redis
    command: uvicorn main:app --host 0.0.0.0 --port 8000

  paperflow-worker:
    image: paperflow_paperflow-worker:latest
    container_name: paperflow-worker
    restart: unless-stopped
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    depends_on:
      - redis
    command: celery -A paperflow worker --loglevel=info

  paperflow-flower:
    image: paperflow:latest
    container_name: paperflow-flower
    restart: unless-stopped
    ports:
      - "9522:5555"
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - redis
    command: celery -A paperflow flower --port=5555

volumes:
  redis-data:
```

---

## Usage Examples

### Submit Document

```bash
# Upload document for processing
curl -X POST http://69.62.108.82:9520/api/documents \
  -F "file=@document.pdf" \
  -F "operation=extract"
```

```python
import requests

url = "http://69.62.108.82:9520/api/documents"
files = {"file": open("document.pdf", "rb")}
data = {"operation": "extract"}

response = requests.post(url, files=files, data=data)
task_id = response.json()["task_id"]
print(f"Task ID: {task_id}")
```

### Check Status

```bash
# Check task status
curl http://69.62.108.82:9520/api/documents/TASK_ID
```

### Get Results

```python
import requests
import time

def wait_for_result(task_id):
    url = f"http://69.62.108.82:9520/api/documents/{task_id}"

    while True:
        response = requests.get(url)
        status = response.json()["status"]

        if status == "completed":
            return response.json()["result"]
        elif status == "failed":
            raise Exception(response.json()["error"])

        time.sleep(2)
```

---

## Document Processing Capabilities

### Supported Formats

- PDF
- DOCX
- TXT
- Images (OCR)
- HTML

### Operations

- Text extraction
- OCR (Optical Character Recognition)
- Metadata extraction
- Format conversion
- Document splitting
- Content analysis

---

## Monitoring & Health

### Health Checks

```bash
# API health
curl http://69.62.108.82:9520/health

# Worker status (via Flower)
open http://69.62.108.82:9522

# Celery inspect
docker exec paperflow-worker celery -A paperflow inspect active
docker exec paperflow-worker celery -A paperflow inspect stats
```

### Current Issues ⚠️

**1. Worker Unhealthy**
- Status: Unhealthy
- Last restart: 34 minutes ago
- Action needed: Investigate logs

**2. Flower Unhealthy**
- Status: Unhealthy
- Uptime: 35 hours
- Action needed: Check health check configuration

### Troubleshooting

```bash
# View worker logs
docker logs --tail 200 paperflow-worker

# View API logs
docker logs --tail 200 paperflow-api

# View Flower logs
docker logs --tail 200 paperflow-flower

# Check Redis connection
docker exec paperflow-worker python -c "import redis; r = redis.Redis(host='redis'); print(r.ping())"

# Inspect running tasks
docker exec paperflow-worker celery -A paperflow inspect active
```

---

## Performance & Optimization

### Current Image Size: 6.65 GB ⚠️

**Analysis:** L'image worker est très lourde (6.65 GB)

**Optimizations possibles:**

1. **Multi-stage build**
   ```dockerfile
   # Build stage
   FROM python:3.11 as builder
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --user --no-cache-dir -r requirements.txt

   # Runtime stage
   FROM python:3.11-slim
   WORKDIR /app
   COPY --from=builder /root/.local /root/.local
   COPY . .
   ENV PATH=/root/.local/bin:$PATH
   CMD ["celery", "-A", "paperflow", "worker"]
   ```
   **Gain estimé:** 1-1.5 GB

2. **Supprimer dépendances de build**
   - gcc, build-essential non nécessaires en runtime
   - Nettoyer pip cache
   - Utiliser slim/alpine base image

3. **Optimiser venv**
   - Ne copier que les packages nécessaires
   - Exclure tests et documentation

### Resource Usage

```bash
# Monitor resources
docker stats paperflow-worker paperflow-api paperflow-flower

# Memory limits
docker update --memory 2g --memory-swap 2g paperflow-worker
```

---

## Configuration

### Environment Variables

```bash
# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=json

# Worker
CELERY_WORKER_CONCURRENCY=4
CELERY_WORKER_MAX_TASKS_PER_CHILD=1000

# API
API_PORT=8000
LOG_LEVEL=info

# Processing
MAX_FILE_SIZE=50MB
ALLOWED_FORMATS=pdf,docx,txt
```

---

## Security

### Best Practices

- Validate file uploads
- Scan for malware
- Limit file sizes
- Sanitize file names
- Implement rate limiting

### Authentication

```python
# Add API key authentication
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

---

## Maintenance

### Regular Tasks

- **Daily:** Monitor task queue length
- **Weekly:** Clear old task results
- **Monthly:** Update dependencies

### Celery Maintenance

```bash
# Purge completed tasks
docker exec paperflow-worker celery -A paperflow purge

# Restart workers gracefully
docker exec paperflow-worker celery -A paperflow control shutdown
docker restart paperflow-worker

# Inspect worker pools
docker exec paperflow-worker celery -A paperflow inspect stats
```

---

## Scaling

### Horizontal Scaling

```bash
# Add more workers
docker-compose up -d --scale paperflow-worker=3
```

### Queue Prioritization

```python
# High priority queue
celery.send_task('paperflow.tasks.process_document',
                 args=[doc_id],
                 queue='high_priority')

# Low priority queue
celery.send_task('paperflow.tasks.process_document',
                 args=[doc_id],
                 queue='low_priority')
```

---

## Dependencies

### Python Packages

- celery
- redis
- fastapi / flask
- flower
- PyPDF2 / pdfplumber
- python-docx
- pillow (OCR)
- tesseract (OCR)

### External Services

- Redis (message broker & result backend)
- Optionally: RabbitMQ, PostgreSQL

---

## Related Documentation

- [Paperless-NGX](paperless-ngx.md) - Document Management
- [Tika](tika.md) - Document Parsing
- [LangChain Service](langchain-service.md) - AI Processing
- [Registry](../applications/registry.yml)

---

## Action Items

- [x] Document architecture
- [x] Document API endpoints
- [ ] Investigate worker unhealthy status
- [ ] Investigate Flower unhealthy status
- [ ] Optimize Docker image (6.65 GB → ~5 GB)
- [ ] Add to registry.yml
- [ ] Configure nginx reverse proxy
- [ ] Add domain (paperflow.srv759970.hstgr.cloud)
- [ ] Implement API authentication
- [ ] Set up monitoring alerts

---

**Last Updated:** 2025-12-04
**Maintainer:** DevOps Team
**API Version:** 1.0
**Celery Version:** 5.x
