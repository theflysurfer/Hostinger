# Applications Registry

This directory contains **metadata only** for the 45 applications deployed on srv759970.

## Documentation Strategy

Application-specific documentation lives in **individual project repositories**, not here.

This registry provides:
- ✅ Application inventory (name, URL, status)
- ✅ Links to project repositories
- ✅ Deployment metadata (ports, auto-start config)
- ❌ NOT detailed application documentation
- ❌ NOT deployment procedures (see project repos)

## Registry File

See [registry.yml](./registry.yml) for complete application inventory.

## Application Categories

### WordPress Sites (5)
Client websites built on WordPress.
- Documentation: In individual project repos
- Infrastructure: See [../services/wordpress-base/](../services/wordpress-base/)

### AI/ML Services (8)
Transcription, RAG, TTS, and other AI services.
- Documentation: See [../services/](../services/)

### Dashboards (5)
Custom Streamlit/React dashboards for clients.
- Documentation: In individual project repos

### Monitoring (4)
Infrastructure monitoring tools.
- Documentation: See [../services/monitoring-stack/](../services/monitoring-stack/)

### CMS & Collaboration (6)
Strapi, Nextcloud, Jitsi, RocketChat, etc.
- Documentation: Mixed (some services/, some project repos)

### Infrastructure Services (5)
Databases, Redis, MongoDB shared instances.
- Documentation: See [../infrastructure/](../infrastructure/)

## Finding Documentation

1. **Infrastructure** (Docker, Nginx, SSH, etc.)
   → See [../infrastructure/](../infrastructure/)

2. **Technical Services** (WhisperX, Tika, RAGFlow, etc.)
   → See [../services/](../services/)

3. **Client Applications** (WordPress sites, dashboards, etc.)
   → See project repository (linked in registry.yml)

4. **Operations** (Deployment, backup, maintenance)
   → See [../operations/](../operations/)

## Adding a New Application

When deploying a new application:

1. **Add metadata to registry.yml**
   ```yaml
   - name: my-new-app
     url: https://mynewapp.srv759970.hstgr.cloud
     type: client_app | shared_service
     status: production | staging | development
     repo: "Path or GitHub URL"
     docker_autostart: true | false
   ```

2. **Create project repository** (if client app)
   - Structure: See templates in project repos
   - Include: README.md, CLAUDE.md, DEPLOY.md, INFRASTRUCTURE.md

3. **OR add to services/** (if shared technical service)
   - Create: `services/my-service/README.md`
   - Document: API, deployment, troubleshooting

4. **Update mkdocs navigation** (if needed)
   - Edit: `../../mkdocs.yml`

## Quick Links

- **Infrastructure Docs**: [../infrastructure/](../infrastructure/)
- **Services Docs**: [../services/](../services/)
- **Operations Docs**: [../operations/](../operations/)
- **Application Registry**: [registry.yml](./registry.yml)
