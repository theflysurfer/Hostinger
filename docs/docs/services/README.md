# Technical Services Documentation

This directory contains documentation for **shared technical services** deployed on srv759970.

## What Are Technical Services?

Technical services are **reusable infrastructure components** that:
- ✅ Expose APIs or interfaces used by multiple applications
- ✅ Provide specialized functionality (transcription, parsing, RAG, etc.)
- ✅ Are maintained independently of client applications
- ✅ May have their own dedicated repositories

**Examples**: WhisperX (transcription API), Tika (document parsing), RAGFlow (RAG system)

---

## Services vs Applications

### Technical Services (Documented Here)

**Criteria**:
- Reusable across projects
- Has API/interface
- Infrastructure-level component
- Not client-specific

**Examples**:
- WhisperX → Transcription API used by multiple apps
- Tika → Document parsing for any project
- RAGFlow → RAG system for knowledge bases
- Monitoring Stack → Grafana/Prometheus for all apps

### Client Applications (Documented in Project Repos)

**Criteria**:
- Specific to one client/project
- Has own business logic
- Own deployment lifecycle
- Not reused by other projects

**Examples**:
- WordPress Clemence → Client website
- Energie Dashboard → DownTo40 project
- Jokers Hockey → Specific sports site

**Documentation**: See `../applications/registry.yml` for links to project repos

---

## Available Services

### AI/ML Services

#### Transcription & Speech

| Service | URL | Documentation | Status |
|---------|-----|---------------|--------|
| **WhisperX** | https://whisperx.srv759970.hstgr.cloud | [whisperx.md](./whisperx.md) | Production |
| **Faster-Whisper** | https://faster-whisper.srv759970.hstgr.cloud | [faster-whisper.md](./faster-whisper.md) | Production |

**Use cases**: Audio/video transcription, speaker diarization, subtitle generation

#### RAG Systems

| Service | URL | Documentation | Status |
|---------|-----|---------------|--------|
| **RAGFlow** | https://ragflow.srv759970.hstgr.cloud | [ragflow.md](./ragflow.md) | Production |
| **RAG-Anything** | https://rag-anything.srv759970.hstgr.cloud | TBD | Production |
| **MemVid** | https://memvid.srv759970.hstgr.cloud | TBD | Production |

**Use cases**: Knowledge base search, document Q&A, semantic search

#### Document Processing

| Service | URL | Documentation | Status |
|---------|-----|---------------|--------|
| **Tika** | https://tika.srv759970.hstgr.cloud | [tika.md](./tika.md) | Production |
| **Ollama** | http://localhost:11434 | [ollama.md](./ollama.md) | Production |

**Use cases**: PDF parsing, OCR, metadata extraction, local LLM inference

### Infrastructure Services

#### Monitoring

| Service | URL | Documentation | Status |
|---------|-----|---------------|--------|
| **Grafana** | https://monitoring.srv759970.hstgr.cloud | [monitoring-stack.md](./monitoring-stack.md) | Production |
| **Prometheus** | Internal | [monitoring-stack.md](./monitoring-stack.md) | Production |
| **Loki + Promtail** | Internal | [monitoring-stack.md](./monitoring-stack.md) | Production |

**Use cases**: Metrics visualization, log aggregation, alerting

#### Collaboration

| Service | URL | Documentation | Status |
|---------|-----|---------------|--------|
| **Nextcloud** | https://nextcloud.srv759970.hstgr.cloud | TBD | Production |
| **Jitsi** | https://meet.srv759970.hstgr.cloud | TBD | Production |
| **RocketChat** | https://chat.srv759970.hstgr.cloud | TBD | Staging |

**Use cases**: File sharing, video conferencing, team chat

### Base Templates

#### WordPress Base

| Documentation | Description |
|---------------|-------------|
| [wordpress-base/](./wordpress-base/) | WordPress Docker setup patterns, optimization, security |

**Note**: Individual WordPress sites documented in their project repos. This is the **template/patterns** only.

---

## Service Documentation Structure

Each service should have:

```
service-name/
├── README.md              Main documentation
├── api-reference.md       API endpoints (if applicable)
├── deployment.md          How to deploy/update
├── configuration.md       Config options
├── troubleshooting.md     Common issues
└── examples/              Usage examples
```

**Minimal documentation**: At least a `README.md` or single markdown file

---

## Documentation Standards

### What to Include

1. **Overview**
   - What the service does
   - Key features
   - Use cases

2. **Access Information**
   - URL
   - Authentication
   - Ports

3. **API Reference** (if applicable)
   - Endpoints
   - Request/response formats
   - Examples with curl

4. **Deployment**
   - Docker compose location
   - Environment variables
   - Dependencies

5. **Troubleshooting**
   - Common errors
   - Debug steps
   - Logs location

### What NOT to Include

- ❌ General Docker knowledge (link to `../infrastructure/docker.md`)
- ❌ General Nginx config (link to `../infrastructure/nginx.md`)
- ❌ SSH access (link to `../infrastructure/server.md`)
- ❌ Client application details (those go in project repos)

---

## Adding a New Service

### Step 1: Determine if it's a Service

**Is it**:
- Reusable across projects?
- Has an API/interface?
- Infrastructure-level?

**YES** → Document here
**NO** → Document in project repo

### Step 2: Create Documentation

**Option A: Simple service (single file)**
```bash
# Create markdown file
docs/services/my-service.md
```

**Option B: Complex service (folder)**
```bash
# Create folder with multiple docs
docs/services/my-service/
├── README.md
├── api-reference.md
├── deployment.md
└── troubleshooting.md
```

### Step 3: Add to Registry

Update `../applications/registry.yml`:

```yaml
ai_services:
  - name: my-service
    url: https://myservice.srv759970.hstgr.cloud
    port: 8000
    type: shared_service
    status: production
    docker_autostart: true
    documentation: "docs/services/my-service.md"
```

### Step 4: Update Navigation

Edit `../../mkdocs.yml` to add to navigation

---

## Service-Specific vs Dedicated Repos

### When to Keep Docs Here

**Criteria**:
- Service is simple/small
- Single purpose API
- Tightly coupled to infrastructure
- Low change frequency

**Examples**:
- Tika → Simple document parsing API
- Monitoring stack → Infrastructure component

### When to Create Dedicated Repo

**Criteria**:
- Service is complex/large
- Active development
- Has own codebase/contributors
- Can be deployed independently

**Examples**:
- WhisperX → May have own repo with code + docs
- RAGFlow → Large system, own development cycle
- Wake Chain → Complex dependency analysis tool

**Note**: Even with dedicated repos, keep a **summary** in `docs/services/` with link to full docs

---

## Migration Status

### ✅ Migrated to services/

- Tika (from `02-applications/ai-services/`)
- WhisperX (from `02-applications/ai-transcription/`)
- RAGFlow (from `02-applications/ai-rag/`)

### 🔄 To Be Migrated

Services still in old structure that should be moved/documented:
- Faster-Whisper
- RAG-Anything
- MemVid
- Ollama
- NeuTTS, XTTS
- Nextcloud, Jitsi, RocketChat
- N8N
- Paperless-NGX, Paperless AI
- Telegram Bot

### 📝 To Be Created

New docs needed:
- WordPress Base (patterns/templates)
- Monitoring Stack (consolidated)
- Databases documentation (shared instances)

---

## Quick Links

- **Infrastructure Docs**: [../infrastructure/](../infrastructure/)
- **Applications Registry**: [../applications/registry.yml](../applications/registry.yml)
- **Operations**: [../operations/](../operations/)
- **Reference**: [../reference/](../reference/)

---

## For Contributors

When documenting a service:
1. **Be concise** - Focus on what's unique to this service
2. **Link don't duplicate** - Reference infrastructure docs
3. **Examples over theory** - Show curl commands, code samples
4. **Keep updated** - Update when service changes
5. **Think user** - What would someone integrating this service need to know?

---

**Last updated**: 2025-12-04
