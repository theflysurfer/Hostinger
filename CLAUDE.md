# Hostinger VPS Infrastructure Repository

**Single source of truth** for srv759970.hstgr.cloud infrastructure documentation.

---

## 🎯 Context

This repository documents the **infrastructure layer** of srv759970.hstgr.cloud:
- Server: 69.62.108.82 (automation user, not root)
- OS: Ubuntu 24.04.2 LTS
- 45 applications deployed across 13 categories
- Docker-based infrastructure with auto-start/stop system
- Nginx reverse proxy with SSL/Let's Encrypt
- Shared database instances (PostgreSQL, Redis, MongoDB)

---

## 🤖 For Claude: How to Use This Repository

### Available Infrastructure Skills

This repository relies on **global personal skills** from the marketplace that are auto-loaded from `~/.claude/skills/`. These skills are developed in:

**Marketplace repo**: `C:\Users\julien\OneDrive\Coding\_Projets de code\2025.11 Claude Code MarketPlace`

#### Core Infrastructure Skills

**hostinger-ssh**
- Purpose: SSH connection, server management, system status
- Invoke when: User needs to connect, check resources, system operations
- Key operations: SSH access, disk space, RAM usage, system logs

**hostinger-docker**
- Purpose: Docker container operations, image optimization, troubleshooting
- Invoke when: Managing containers, deploying services, cleaning resources
- Key operations: Container management, image optimization, docker cleanup

**hostinger-nginx**
- Purpose: Nginx reverse proxy configuration, SSL management
- Invoke when: Configuring sites, SSL setup, 502/504 errors, site not accessible
- Key operations: Site configuration, SSL/Let's Encrypt, reverse proxy, debugging

**hostinger-database**
- Purpose: PostgreSQL, Redis, MongoDB operations
- Invoke when: Database connections, backups, user management, performance issues
- Key operations: Database queries, backups, user management, performance monitoring

**hostinger-maintenance**
- Purpose: Recurring maintenance tasks, runbooks
- Invoke when: Scheduled maintenance, cleanup operations, system health checks
- Key operations: Docker cleanup, disk space monitoring, SSL verification, system updates

### Documentation Structure

```
docs/
├── infrastructure/          Infrastructure bas niveau (server, nginx, docker)
├── services/               Services techniques partagés (whisperx, tika, ragflow)
├── operations/             Procédures opérationnelles (backup, deployment, emergency)
├── reference/              Best practices & patterns (docker, nginx, security)
├── applications/           Applications registry (metadata only)
└── advanced/               Guides avancés (api-portal, llm-usage, mcp-servers)
```

**Key principle**:
- Infrastructure docs → This repo (`docs/`)
- Service docs → This repo (`docs/services/`) OR dedicated repo
- Application docs → Individual project repos

---

## 📋 Documentation Strategy

### Layer 1: Infrastructure (This Repo)

**What belongs here**:
- ✅ Server configuration (SSH, users, system)
- ✅ Nginx reverse proxy setup
- ✅ Docker engine & networks
- ✅ Shared databases (PostgreSQL, Redis, MongoDB)
- ✅ Security policies (fail2ban, firewall, SSL)
- ✅ Operations (backup, deployment, maintenance)

**What does NOT belong here**:
- ❌ Application-specific code
- ❌ Client project details
- ❌ Project deployment procedures (those go in project repos)

### Layer 2: Technical Services

**Shared services documented in `docs/services/`**:
- WhisperX (AI transcription)
- Tika (document parsing)
- RAGFlow, MemVid (RAG systems)
- Ollama (local LLM)
- Monitoring stack (Grafana, Prometheus)

**Criteria for services/**: Reusable service with API used by multiple apps

### Layer 3: Applications (Project Repos)

**Client applications documented in their own repos**:
- WordPress sites (Clemence, SolidarLink, etc.)
- Custom dashboards (Energie Dashboard, Support Dashboard)
- Client websites (Jokers, Cristina)

**See**: `docs/applications/registry.yml` for complete app inventory with repo links

---

## 🚫 IMPORTANT: No Duplication

**When working on project repositories, NEVER**:
- ❌ Copy infrastructure documentation to project repos
- ❌ Document SSH/Docker/Nginx procedures in project repos
- ❌ Duplicate server configuration details

**Instead**:
- ✅ Reference this repo's documentation
- ✅ Use infrastructure skills (they auto-load globally)
- ✅ Keep project repos focused on application-specific content

**Example for project repo**:
```markdown
## Infrastructure

For server operations, see Hostinger repo:
- SSH access → docs/infrastructure/server.md
- Docker operations → Use `hostinger-docker` skill
- Nginx config → Use `hostinger-nginx` skill

## Project-Specific Deployment

1. Connect: `ssh srv759970`
2. Deploy: `cd /opt/myproject && docker-compose up -d`
3. Verify: Check https://myproject.srv759970.hstgr.cloud
```

---

## 📊 Applications Registry

**45 applications deployed** - see `docs/applications/registry.yml` for:
- Application names and URLs
- Docker auto-start configuration
- Project repository links
- Documentation locations
- Container details

**Categories**:
- WordPress Sites (5)
- AI/ML Services (8)
- Dashboards (5)
- CMS & Content (3)
- Collaboration (4)
- Documents (2)
- Automation (1)
- Monitoring (8)
- Infrastructure (2)
- Specialty (4)

---

## 🔧 Quick Operations

### Check Server Status

Claude will automatically use `hostinger-ssh` skill:
```bash
# System resources
ssh srv759970 'free -h && df -h && uptime'

# Docker containers
ssh srv759970 'docker ps --format "table {{.Names}}\t{{.Status}}"'
```

### Deploy Application

Claude will automatically use `hostinger-docker` skill:
```bash
cd /opt/app-name
docker-compose up -d
```

### Configure Nginx Site

Claude will automatically use `hostinger-nginx` skill:
```bash
sudo nano /etc/nginx/sites-available/site
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔗 Related Repositories

### Marketplace (Skills Source)
**Location**: `C:\Users\julien\OneDrive\Coding\_Projets de code\2025.11 Claude Code MarketPlace`
**Purpose**: Develop and sync infrastructure skills globally
**Skills**: hostinger-ssh, hostinger-docker, hostinger-nginx, hostinger-database, hostinger-maintenance

### Nginx Manager
**Location**: `C:\Users\julien\OneDrive\Coding\_Projets de code\2025.10 Nginx Manager`
**Purpose**: Advanced Nginx configuration management tool
**Status**: Semi-independent repo with own scripts and workflows

### Wake Chain
**Location**: `C:\Users\julien\OneDrive\Coding\_Projets de code\2025.10 Wake chain`
**Purpose**: Dependency analysis for Docker auto-start optimization
**Documentation**: `docs/operations/dependency-wake-chain.md`

### Project Repositories
See `docs/applications/registry.yml` for links to all 45 application repos

---

## 🚨 Emergency Procedures

**Emergency runbook**: `docs/operations/emergency-runbook.md`

**Quick actions**:
- Disk space critical: Use `hostinger-maintenance` skill → Docker cleanup
- Container down: Use `hostinger-docker` skill → Restart container
- Nginx 502/504: Use `hostinger-nginx` skill → Check backend + reload
- Database issues: Use `hostinger-database` skill → Check connections
- SSL expired: Use `hostinger-nginx` skill → Certbot renewal

---

## 📝 Maintenance Tasks

**Weekly** (every Monday):
- Clean Docker resources (images, volumes)
- Check disk space (target: >20 GB free)
- Verify container health
- Monitor RAM usage (target: 9 GB free)

**Monthly** (1st of month):
- Verify SSL certificates auto-renewal
- Update Docker images for critical services
- Review Nginx logs
- System updates (coordinate with users)

**See**: `hostinger-maintenance` skill for detailed runbooks

---

## 🎓 Best Practices

### When Adding New Application

1. **Add to registry**: `docs/applications/registry.yml`
2. **Create project repo** (if client app) with:
   - README.md, CLAUDE.md, DEPLOY.md
   - INFRASTRUCTURE.md (links to this repo)
3. **OR add to services/** (if shared technical service)
4. **Configure Nginx**: Use `hostinger-nginx` skill
5. **Update documentation**: Update mkdocs.yml if needed

### When Modifying Infrastructure

1. **Update docs** in this repo (not project repos)
2. **Update skills** in marketplace repo (if skill-related)
3. **Sync skills**: Use `sync-personal-skills` in marketplace
4. **Test changes** before production
5. **Document in CHANGELOG**: `docs/changelog/`

### When Documenting

**Ask yourself**:
- Is this about the server itself? → `docs/infrastructure/`
- Is this a reusable service? → `docs/services/`
- Is this operational procedure? → `docs/operations/`
- Is this app-specific? → Project repo, NOT here

---

## 🔍 Finding Documentation

### For Infrastructure Topics
→ Browse `docs/infrastructure/` or use infrastructure skills

### For Technical Services
→ Browse `docs/services/` or check service-specific repos

### For Applications
→ See `docs/applications/registry.yml` then follow repo links

### For Operations
→ Browse `docs/operations/` or use `hostinger-maintenance` skill

### For Troubleshooting
→ Use relevant skill (auto-invoked) or check `docs/reference/`

---

## 🎯 Key Reminders for Claude

1. **Skills auto-load globally** - Don't need to install per project
2. **This repo = infrastructure only** - Apps documented elsewhere
3. **No duplication** - Reference, don't copy
4. **Use skills for operations** - They know the patterns
5. **Registry is metadata** - Detailed docs in project repos
6. **Maintenance = proactive** - Use `hostinger-maintenance` skill

---

## 📞 Resources

- **MkDocs site**: https://docs.srv759970.hstgr.cloud (when deployed)
- **Dashy portal**: https://dashy.srv759970.hstgr.cloud
- **Grafana monitoring**: https://monitoring.srv759970.hstgr.cloud
- **Portainer**: http://69.62.108.82:9000

---

**Last updated**: 2025-12-04
**Repository version**: 3.0.0 (Skills-first + Documentation restructure)
