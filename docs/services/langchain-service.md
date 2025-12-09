# LangChain Service

**Status:** Production
**Type:** Shared Service / AI
**Container:** `langchain-service`
**Image:** `langchain-service_langchain-service:latest` (333 MB)
**URL:** http://69.62.108.82:5000
**Health:** ✅ Healthy
**Uptime:** 3+ weeks

---

## Overview

Service LangChain pour intégrations LLM (Large Language Models) et chaînage d'opérations AI. Fournit une API REST pour l'orchestration de workflows AI complexes.

---

## Technical Details

### Container Configuration

```yaml
Container Name: langchain-service
Image: langchain-service_langchain-service:latest
Image Size: 333 MB
Ports: 5000:5000
Status: Running (healthy)
Network: Bridge
Restart Policy: Auto-restart
```

### Endpoints

**Base URL:** `http://69.62.108.82:5000`

#### API Endpoints (à documenter)

```bash
# Health check
GET /health

# LangChain operations
POST /chain
POST /query
# Add specific endpoints based on implementation
```

---

## Deployment

### Docker Compose

Location: `/opt/langchain-service/` (to be confirmed)

```yaml
version: '3.8'
services:
  langchain-service:
    image: langchain-service_langchain-service:latest
    container_name: langchain-service
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      # Add other API keys as needed
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
```

### Start/Stop

```bash
# Start
docker start langchain-service

# Stop
docker stop langchain-service

# Restart
docker restart langchain-service

# Logs
docker logs -f langchain-service
```

---

## Usage Examples

### Basic Query

```bash
# Example API call
curl -X POST http://69.62.108.82:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Your query here",
    "model": "gpt-4"
  }'
```

### Chain Operations

```python
import requests

url = "http://69.62.108.82:5000/chain"
payload = {
    "chain_type": "sequential",
    "steps": [
        {"type": "llm", "prompt": "Step 1"},
        {"type": "transform", "operation": "summarize"},
        {"type": "llm", "prompt": "Step 2"}
    ]
}

response = requests.post(url, json=payload)
print(response.json())
```

---

## Features

### Supported LLM Providers

- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude)
- Local models (Ollama integration)
- Custom endpoints

### Chain Types

- Sequential chains
- Map-reduce chains
- Router chains
- Custom workflows

### Integrations

- Vector stores (Pinecone, Weaviate, Chroma)
- Document loaders
- Text splitters
- Embeddings

---

## Configuration

### Environment Variables

```bash
# LLM API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Vector Store
PINECONE_API_KEY=...
PINECONE_ENV=...

# Application
LOG_LEVEL=info
MAX_TOKENS=2000
TEMPERATURE=0.7
```

### Config File

Location: `/opt/langchain-service/config.yaml`

```yaml
llm:
  default_model: gpt-4
  temperature: 0.7
  max_tokens: 2000

vectorstore:
  type: chroma
  persist_directory: ./data/chroma

chains:
  timeout: 300
  max_retries: 3
```

---

## Monitoring

### Health Check

```bash
# Container health
docker inspect langchain-service | grep -A 10 Health

# API health
curl http://69.62.108.82:5000/health
```

### Key Metrics

- Request count
- Response time
- Token usage
- Error rate
- LLM API costs

### Logs

```bash
# View logs
docker logs langchain-service

# Follow logs
docker logs -f --tail 100 langchain-service

# Search for errors
docker logs langchain-service 2>&1 | grep ERROR
```

---

## Performance

### Resource Usage

- **CPU:** Low to moderate (spikes during LLM calls)
- **Memory:** ~300-500 MB
- **Network:** Dependent on LLM API calls

### Optimization

- Implement caching for repeated queries
- Use streaming for long responses
- Batch similar requests
- Monitor token usage

---

## Security

### API Keys

- All API keys stored in environment variables
- Never committed to git
- Rotated regularly

### Network Security

- Internal Docker network
- Port 5000 exposed only on host
- Consider adding authentication for production

### Best Practices

```bash
# Add authentication middleware
# Rate limiting
# Input validation
# Output sanitization
```

---

## Troubleshooting

### Common Issues

**1. LLM API Timeout**
```bash
# Check API key validity
# Increase timeout in config
# Retry with exponential backoff
```

**2. Memory Issues**
```bash
# Monitor memory usage
docker stats langchain-service

# Increase container memory limit
docker update --memory 1g langchain-service
```

**3. Connection Errors**
```bash
# Check network connectivity
docker network inspect bridge

# Verify port binding
netstat -tulpn | grep 5000
```

---

## Maintenance

### Regular Tasks

- **Daily:** Monitor API usage and costs
- **Weekly:** Check logs for errors
- **Monthly:** Update LangChain and dependencies

### Updates

```bash
# Backup configuration
cp /opt/langchain-service/config.yaml /opt/backups/

# Pull latest image
docker pull langchain-service_langchain-service:latest

# Restart service
docker-compose down
docker-compose up -d
```

---

## Dependencies

### Python Packages

- langchain
- openai
- anthropic
- chromadb / pinecone
- fastapi / flask
- pydantic

### External Services

- OpenAI API
- Anthropic API
- Vector databases (optional)
- Ollama (local LLMs)

---

## Integration Examples

### From Other Services

```python
# From Streamlit dashboard
import streamlit as st
import requests

def query_langchain(prompt):
    response = requests.post(
        "http://langchain-service:5000/query",
        json={"prompt": prompt}
    )
    return response.json()

st.write(query_langchain("Hello"))
```

### From Discord/Telegram Bots

```python
# Integration with bot
import requests

def process_with_llm(user_message):
    response = requests.post(
        "http://langchain-service:5000/chain",
        json={
            "prompt": user_message,
            "chain_type": "conversational"
        }
    )
    return response.json()["result"]
```

---

## Cost Management

### Token Tracking

- Monitor OpenAI/Anthropic token usage
- Set budget alerts
- Implement rate limiting per user

### Optimization Strategies

- Cache common queries
- Use cheaper models for simple tasks
- Batch requests when possible
- Set max token limits

---

## Related Documentation

- [RAGFlow](ragflow.md) - RAG Engine
- [Ollama](ollama.md) - Local LLM Server
- [Paperflow](paperflow.md) - Document Processing
- [Registry](../applications/registry.yml)

---

## API Documentation

**To be completed:** Full OpenAPI/Swagger documentation

Potential URL: http://69.62.108.82:5000/docs

---

## Action Items

- [ ] Document all API endpoints
- [ ] Add authentication
- [ ] Set up monitoring dashboard
- [ ] Create OpenAPI schema
- [ ] Add to nginx reverse proxy
- [ ] Configure domain (langchain.srv759970.hstgr.cloud)
- [ ] Add to registry.yml

---

**Last Updated:** 2025-12-04
**Maintainer:** DevOps Team
**API Version:** 1.0
