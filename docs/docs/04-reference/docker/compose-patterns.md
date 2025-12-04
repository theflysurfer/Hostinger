# Docker Compose - Snippets Réutilisables

Configurations Docker Compose standards à réutiliser dans vos services.

## Healthcheck Standard

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 10s
  timeout: 5s
  retries: 3
  start_period: 30s
```

### Variantes

**Pour services sans endpoint /health:**

```yaml
healthcheck:
  test: ["CMD", "pgrep", "-x", "python"]  # Vérifie que le processus tourne
  interval: 30s
  timeout: 10s
  retries: 3
```

**Pour bases de données (MySQL):**

```yaml
healthcheck:
  test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
  interval: 10s
  timeout: 5s
  retries: 5
```

**Pour bases de données (PostgreSQL):**

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 10s
  timeout: 5s
  retries: 5
```

**Pour Redis:**

```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 5s
  timeout: 3s
  retries: 5
```

## Rotation des Logs

```yaml
logging:
  driver: json-file
  options:
    max-size: '10m'
    max-file: '3'
```

**Variantes selon taille attendue:**

```yaml
# Services légers
logging:
  driver: json-file
  options:
    max-size: '5m'
    max-file: '2'

# Services verbeux (transcription, processing)
logging:
  driver: json-file
  options:
    max-size: '50m'
    max-file: '5'
```

## Restart Policy

```yaml
restart: unless-stopped
```

**Alternatives:**

- `no`: Ne jamais redémarrer automatiquement
- `always`: Toujours redémarrer (même après reboot)
- `on-failure`: Redémarrer seulement si échec
- `unless-stopped`: Redémarrer sauf si arrêt manuel (**recommandé**)

## Networks

```yaml
networks:
  - app-network

# Déclaration en bas du fichier
networks:
  app-network:
    driver: bridge
```

**Réseau externe (partagé entre services):**

```yaml
networks:
  whisperx_whisperx:
    external: true
```

## Volumes

```yaml
volumes:
  - app-data:/var/lib/app       # Volume nommé
  - ./config:/app/config:ro      # Mount read-only
  - /host/path:/container/path   # Bind mount

# Déclaration en bas du fichier
volumes:
  app-data:
```

## Environment Variables

```yaml
environment:
  - NODE_ENV=production
  - DEBUG=false
  - TZ=Europe/Paris
```

**Depuis fichier .env:**

```yaml
env_file:
  - .env
```

## Dépendances

```yaml
depends_on:
  db:
    condition: service_healthy
  redis:
    condition: service_started
```

## Resource Limits

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      cpus: '0.5'
      memory: 1G
```

## User & Permissions

```yaml
user: "1000:1000"  # UID:GID
```

## Security

```yaml
security_opt:
  - no-new-privileges:true

cap_drop:
  - ALL

cap_add:
  - NET_ADMIN  # Si besoin réseau avancé
```

## Exemple Complet

```yaml
version: '3.8'

services:
  app:
    image: myapp:latest
    container_name: myapp
    restart: unless-stopped

    ports:
      - '8080:8080'

    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://db:5432/mydb

    volumes:
      - app-data:/var/lib/app
      - ./config:/app/config:ro

    networks:
      - app-network

    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started

    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s

    logging:
      driver: json-file
      options:
        max-size: '10m'
        max-file: '3'

    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G

  db:
    image: postgres:15
    container_name: myapp-db
    restart: unless-stopped

    environment:
      - POSTGRES_DB=mydb
      - POSTGRES_USER=myuser
      - POSTGRES_PASSWORD=${DB_PASSWORD}

    volumes:
      - db-data:/var/lib/postgresql/data

    networks:
      - app-network

    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U myuser"]
      interval: 10s
      timeout: 5s
      retries: 5

    logging:
      driver: json-file
      options:
        max-size: '10m'
        max-file: '3'

  redis:
    image: redis:7-alpine
    container_name: myapp-redis
    restart: unless-stopped

    networks:
      - app-network

    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

    logging:
      driver: json-file
      options:
        max-size: '5m'
        max-file: '2'

volumes:
  app-data:
  db-data:

networks:
  app-network:
    driver: bridge
```

## Voir aussi

- [Infrastructure > Docker](../../infrastructure/docker.md) - Commandes et gestion Docker
- [Guides > Docker Autostart](../../guides/deployment/docker-autostart-setup.md) - Configuration auto-start
