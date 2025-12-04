#!/bin/bash
# Generate Claude Code skills for all categories

SKILLS_BASE=".claude/skills"
mkdir -p "$SKILLS_BASE/apps"
mkdir -p "$SKILLS_BASE/infrastructure"
mkdir -p "$SKILLS_BASE/operations"

# Skills Apps - 13 catégories
cat > "$SKILLS_BASE/apps/dashboards.md" << 'EOF'
# Dashboards Apps Skill

Context pour LLM concernant les dashboards du serveur srv759970.

## Applications Disponibles

- **DownTo40 (energie-40eur-dashboard)** : `apps/11-dashboards/energie-40eur-dashboard/`
  - Dashboard Streamlit principal (🔴 haute priorité)
  - Documentation : `new-docs/docs/02-applications/dashboards/energie-dashboard.md`

## Commandes Rapides

```bash
# Accéder à l'app
cd apps/11-dashboards/energie-40eur-dashboard/

# Voir la config
cat docker-compose.yml

# Consulter la doc
cat new-docs/docs/02-applications/dashboards/energie-dashboard.md
```

## Références Utiles

- Guides déploiement : `new-docs/docs/02-applications/guides/`
- Server status : `new-docs/docs/99-dynamic/server-status.md`
EOF

cat > "$SKILLS_BASE/apps/wordpress.md" << 'EOF'
# WordPress Apps Skill

Context pour LLM concernant les sites WordPress.

## Applications Disponibles

- **Clemence** : `apps/01-wordpress/clemence/`
  - Site client production clemencefouquet.fr
  - Documentation : `new-docs/docs/02-applications/wordpress/clemence.md`

## Commandes Rapides

```bash
cd apps/01-wordpress/clemence/
docker-compose logs -f
```

## Références

- WordPress guides : `new-docs/docs/02-applications/guides/wordpress-*.md`
EOF

cat > "$SKILLS_BASE/apps/ai-transcription.md" << 'EOF'
# AI Transcription Skill

## Applications

- **WhisperX** : `apps/02-ai-transcription/whisperx/`
  - Transcription avec diarization
  - Doc : `new-docs/docs/02-applications/ai-transcription/whisperx.md`

## Guides

- `new-docs/docs/02-applications/guides/whisper-deployment.md`
- `new-docs/docs/02-applications/guides/whisperx-monitoring.md`
EOF

cat > "$SKILLS_BASE/apps/ai-rag.md" << 'EOF'
# AI RAG Skill

## Applications

- **RAGFlow** : `apps/04-ai-rag/ragflow/`
  - RAG multimodal production
  - Doc : `new-docs/docs/02-applications/ai-rag/ragflow.md`
EOF

cat > "$SKILLS_BASE/apps/monitoring.md" << 'EOF'
# Monitoring Apps Skill

## Applications

- **Dashy** : `apps/12-monitoring/dashy/`
  - Portal principal toujours actif
  - Doc : `new-docs/docs/02-applications/monitoring/dashy.md`

- **Monitoring Stack** : `apps/12-monitoring/monitoring-stack/`
  - Grafana + Prometheus + Loki
  - Doc : `new-docs/docs/02-applications/monitoring/monitoring-stack.md`
EOF

cat > "$SKILLS_BASE/apps/collaboration.md" << 'EOF'
# Collaboration Apps Skill

## Applications

- **Nextcloud** : `apps/08-collaboration/nextcloud/`
  - Cloud storage
  - Doc : `new-docs/docs/02-applications/collaboration/nextcloud.md`
EOF

cat > "$SKILLS_BASE/apps/documents.md" << 'EOF'
# Documents Apps Skill

## Applications

- **Paperless NGX** : `apps/09-documents/paperless-ngx/`
  - DMS principal
  - Doc : `new-docs/docs/02-applications/documents/paperless-ngx.md`
EOF

cat > "$SKILLS_BASE/apps/automation.md" << 'EOF'
# Automation Apps Skill

## Applications

- **N8N** : `apps/10-automation/n8n/`
  - Workflow automation
  - Doc : `new-docs/docs/02-applications/automation/n8n.md`
  - Guide : `new-docs/docs/02-applications/guides/n8n-setup.md`
EOF

cat > "$SKILLS_BASE/apps/infrastructure.md" << 'EOF'
# Infrastructure Apps Skill

## Applications

- **Databases Shared** : `apps/13-infrastructure/databases-shared/`
  - PostgreSQL + Redis + MongoDB
  - Doc : `new-docs/docs/01-infrastructure/databases-shared-detailed.md`
EOF

# Skills Infrastructure
cat > "$SKILLS_BASE/infrastructure/nginx.md" << 'EOF'
# Nginx Infrastructure Skill

## Documentation

- Overview : `new-docs/docs/01-infrastructure/nginx.md`
- Troubleshooting : `new-docs/docs/01-infrastructure/nginx-troubleshooting.md`
- Debugging : `new-docs/docs/04-reference/nginx/debugging.md`
- Proxy Config : `new-docs/docs/04-reference/nginx/proxy-config.md`
- SSL Config : `new-docs/docs/04-reference/nginx/ssl-config.md`

## Nginx Manager

Repo externe : `C:\Users\JulienFernandez\OneDrive\Coding\_Projets de code\2025.10 Nginx Manager`
Placeholder : `infrastructure/nginx/README.md`
EOF

cat > "$SKILLS_BASE/infrastructure/server.md" << 'EOF'
# Server Infrastructure Skill

## Documentation

- Server Config : `new-docs/docs/01-infrastructure/server.md`
- Docker Architecture : `new-docs/docs/01-infrastructure/docker.md`
- Security : `new-docs/docs/01-infrastructure/security.md`
- Environment Setup : `new-docs/docs/01-infrastructure/environment-setup.md`

## Accès

- SSH : `root@69.62.108.82`
- User automation : automation@69.62.108.82
EOF

cat > "$SKILLS_BASE/infrastructure/databases.md" << 'EOF'
# Databases Infrastructure Skill

## Documentation

- Overview : `new-docs/docs/01-infrastructure/databases.md`
- Shared Databases Detailed : `new-docs/docs/01-infrastructure/databases-shared-detailed.md`

## Stack

- PostgreSQL (multiple databases)
- Redis (queue system)
- MongoDB
EOF

# Skills Operations
cat > "$SKILLS_BASE/operations/backup.md" << 'EOF'
# Backup & Restore Skill

## Documentation

- Backup Strategy : `new-docs/docs/03-operations/backup.md`
- Emergency Runbook : `new-docs/docs/03-operations/emergency-runbook.md`
EOF

cat > "$SKILLS_BASE/operations/deployment.md" << 'EOF'
# Deployment Operations Skill

## Documentation

- Docker AutoStart : `new-docs/docs/03-operations/docker-autostart.md`
- Docker AutoStart Setup : `new-docs/docs/03-operations/deployment-docker-autostart.md`
- Systemd Services : `new-docs/docs/03-operations/deployment-systemd.md`
- VPS Setup : `new-docs/docs/03-operations/vps-setup.md`

## Dependency Chain

- `new-docs/docs/03-operations/dependency-wake-chain.md`
EOF

cat > "$SKILLS_BASE/operations/troubleshooting.md" << 'EOF'
# Troubleshooting Operations Skill

## Documentation

- Emergency Runbook : `new-docs/docs/03-operations/emergency-runbook.md`
- Nginx Troubleshooting : `new-docs/docs/01-infrastructure/nginx-troubleshooting.md`
- Docker Commands : `new-docs/docs/04-reference/docker/commands.md`

## Status Pages

- Server Status : `new-docs/docs/99-dynamic/server-status.md`
- Services Status : `new-docs/docs/99-dynamic/services-status.md`
EOF

# Index skill
cat > "$SKILLS_BASE/README.md" << 'EOF'
# Claude Code Skills - srv759970

Skills organisés par catégorie pour navigation intelligente de la documentation.

## Apps Skills

- `apps/dashboards.md` - Dashboards (DownTo40 🔴)
- `apps/wordpress.md` - Sites WordPress
- `apps/ai-transcription.md` - Services transcription
- `apps/ai-rag.md` - Services RAG
- `apps/monitoring.md` - Monitoring & Dashboards
- `apps/collaboration.md` - Outils collaboratifs
- `apps/documents.md` - Gestion documentaire
- `apps/automation.md` - Workflow automation
- `apps/infrastructure.md` - Services infrastructure

## Infrastructure Skills

- `infrastructure/nginx.md` - Nginx reverse proxy
- `infrastructure/server.md` - Server config
- `infrastructure/databases.md` - Databases stack

## Operations Skills

- `operations/backup.md` - Backup & restore
- `operations/deployment.md` - Deployment procedures
- `operations/troubleshooting.md` - Troubleshooting guides

## Usage

Ces skills permettent à Claude Code de naviguer rapidement vers la bonne documentation selon le contexte de la question posée.
EOF

echo "✓ All Claude Code skills generated successfully!"
