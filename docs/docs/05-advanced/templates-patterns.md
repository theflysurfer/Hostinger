# Templates & Patterns Réutilisables

Modèles et patterns standardisés pour déployer rapidement de nouveaux services sur srv759970.

---

## 🐳 Docker Compose Templates

### Template Service Web Standard

```yaml
# /opt/<service-name>/docker-compose.yml
version: '3.8'

services:
  <service-name>:
    image: <image:tag>
    container_name: <service-name>
    restart: unless-stopped
    ports:
      - '<external-port>:<internal-port>'
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    environment:
      - NODE_ENV=production
      - TZ=Europe/Paris
    networks:
      - <service-name>-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:<internal-port>/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

networks:
  <service-name>-network:
    driver: bridge
```

### Template Service avec Database

```yaml
version: '3.8'

services:
  app:
    image: <app-image:tag>
    container_name: <service>-app
    restart: unless-stopped
    ports:
      - '<port>:<internal-port>'
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/dbname
    depends_on:
      - db
    networks:
      - <service>-network

  db:
    image: postgres:15-alpine
    container_name: <service>-db
    restart: unless-stopped
    volumes:
      - db-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=dbname
    networks:
      - <service>-network

volumes:
  db-data:

networks:
  <service>-network:
    driver: bridge
```

### Template Service Auto-Start

```yaml
version: '3.8'

services:
  <service-name>:
    image: <image:tag>
    container_name: <service-name>
    restart: "no"  # Important: pas de restart auto pour auto-start
    ports:
      - '<port>:<internal-port>'
    volumes:
      - ./data:/data
    networks:
      - <service>-network
    labels:
      - "autostart.enable=true"
      - "autostart.idle-timeout=900"  # 15 minutes

networks:
  <service>-network:
    driver: bridge
```

---

## 🌐 Nginx Configuration Templates

### Template Reverse Proxy HTTPS Basique

```nginx
# /etc/nginx/sites-available/<service>

# HTTPS
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name <service>.srv759970.hstgr.cloud;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/<domain>/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/<domain>/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Logs
    access_log /var/log/nginx/<service>-access.log;
    error_log /var/log/nginx/<service>-error.log;

    location / {
        proxy_pass http://127.0.0.1:<port>;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
}

# HTTP -> HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name <service>.srv759970.hstgr.cloud;
    return 301 https://$host$request_uri;
}
```

### Template Reverse Proxy avec Basic Auth

```nginx
# HTTPS
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name <service>.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/<domain>/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/<domain>/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    access_log /var/log/nginx/<service>-access.log;
    error_log /var/log/nginx/<service>-error.log;

    # Basic Authentication
    include snippets/basic-auth.conf;

    location / {
        proxy_pass http://127.0.0.1:<port>;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTP -> HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name <service>.srv759970.hstgr.cloud;
    return 301 https://$host$request_uri;
}
```

### Template Reverse Proxy avec Auto-Start

```nginx
# HTTPS avec Auto-Start Proxy
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name <service>.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/<domain>/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/<domain>/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    access_log /var/log/nginx/<service>-access.log;
    error_log /var/log/nginx/<service>-error.log;

    # Bot Protection (optionnel)
    include snippets/bot-protection.conf;

    location / {
        # Auto-start proxy
        proxy_pass http://127.0.0.1:8890;
        proxy_set_header X-Autostart-Target "<service>.srv759970.hstgr.cloud";

        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts élevés pour boot time
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
}

# HTTP -> HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name <service>.srv759970.hstgr.cloud;
    return 301 https://$host$request_uri;
}
```

### Template WebSocket Support

```nginx
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name <service>.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/<domain>/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/<domain>/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    access_log /var/log/nginx/<service>-access.log;
    error_log /var/log/nginx/<service>-error.log;

    location / {
        proxy_pass http://127.0.0.1:<port>;
        proxy_http_version 1.1;

        # WebSocket headers
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Standard headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts pour WebSocket
        proxy_read_timeout 3600;
        proxy_send_timeout 3600;

        # Disable buffering
        proxy_buffering off;
    }
}
```

---

## 🚀 Workflows de Déploiement

### Workflow Nouveau Service Standard

```bash
#!/bin/bash
# deploy-service.sh <service-name> <port> <image>

SERVICE_NAME=$1
PORT=$2
IMAGE=$3
DOMAIN="${SERVICE_NAME}.srv759970.hstgr.cloud"

# 1. Créer structure
mkdir -p /opt/$SERVICE_NAME
cd /opt/$SERVICE_NAME

# 2. Créer docker-compose.yml
cat > docker-compose.yml <<EOF
version: '3.8'
services:
  $SERVICE_NAME:
    image: $IMAGE
    container_name: $SERVICE_NAME
    restart: unless-stopped
    ports:
      - "$PORT:8000"
    volumes:
      - ./data:/data
EOF

# 3. Démarrer service
docker-compose up -d

# 4. Attendre healthcheck
sleep 10
docker ps | grep $SERVICE_NAME

# 5. Créer config Nginx
cat > /etc/nginx/sites-available/$SERVICE_NAME <<'EOF'
server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    ssl_certificate /etc/letsencrypt/live/faster-whisper.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/faster-whisper.srv759970.hstgr.cloud/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://\$host\$request_uri;
}
EOF

# 6. Activer Nginx
ln -s /etc/nginx/sites-available/$SERVICE_NAME /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# 7. Tester
curl -I https://$DOMAIN

echo "✅ Service $SERVICE_NAME déployé sur https://$DOMAIN"
```

### Workflow Ajout Auto-Start

```bash
#!/bin/bash
# add-to-autostart.sh <service-name> <port>

SERVICE_NAME=$1
PORT=$2
DOMAIN="${SERVICE_NAME}.srv759970.hstgr.cloud"
CONFIG_FILE="/opt/docker-autostart/config.json"

# 1. Modifier docker-compose pour auto-start
cd /opt/$SERVICE_NAME
sed -i 's/restart: unless-stopped/restart: "no"/' docker-compose.yml

# 2. Ajouter à config auto-start
# (Éditer manuellement /opt/docker-autostart/config.json)
echo "Ajouter cette entrée dans services:"
cat <<EOF
    "$DOMAIN": {
      "name": "$SERVICE_NAME",
      "composeDir": "/opt/$SERVICE_NAME",
      "proxyPort": $PORT,
      "idleTimeout": 900,
      "theme": "matrix",
      "containers": [
        "$SERVICE_NAME"
      ]
    }
EOF

# 3. Modifier Nginx pour pointer vers auto-start
sed -i "s|proxy_pass http://127.0.0.1:$PORT;|proxy_pass http://127.0.0.1:8890;|" \
    /etc/nginx/sites-available/$SERVICE_NAME

# Ajouter header auto-start
sed -i "/location \/ {/a\        proxy_set_header X-Autostart-Target \"$DOMAIN\";" \
    /etc/nginx/sites-available/$SERVICE_NAME

# 4. Redémarrer services
nginx -t && systemctl reload nginx
cd /opt/docker-autostart && docker-compose restart

echo "✅ Service ajouté à auto-start"
```

---

## 📋 Checklist Déploiement

### Avant Déploiement

- [ ] Port libre: `netstat -tlnp | grep <port>`
- [ ] Image disponible: `docker pull <image>`
- [ ] Espace disque: `df -h` (>10% libre)
- [ ] RAM disponible: `free -h` (<25GB utilisés)
- [ ] Nom DNS résolu: `ping <service>.srv759970.hstgr.cloud`

### Pendant Déploiement

- [ ] Docker-compose valide: `docker-compose config`
- [ ] Service démarre: `docker-compose up -d`
- [ ] Healthcheck OK: `docker ps | grep <service>`
- [ ] Port écoute: `netstat -tlnp | grep <port>`
- [ ] Nginx config valide: `nginx -t`
- [ ] SSL actif: `curl -I https://<service>.srv759970.hstgr.cloud`

### Après Déploiement

- [ ] Logs sans erreur: `docker-compose logs`
- [ ] Service accessible externe
- [ ] Ajouter à Dashy dashboard
- [ ] Documentation créée dans `docs/services/`
- [ ] Changelog mis à jour
- [ ] Backup config: `tar -czf /root/backups/<service>-config.tar.gz /opt/<service>`

---

## 🔧 Patterns Communs

### Pattern: Service avec Queue Redis

**Use case:** Transcription, traitement long, jobs asynchrones

**Composants:**
1. API FastAPI (endpoints + soumission jobs)
2. Worker RQ (traitement background)
3. Redis partagé (queue)

**Structure:**
```
/opt/<service>/
├── docker-compose.yml      # API + Worker
├── api/
│   ├── main.py            # FastAPI app
│   └── tasks.py           # Fonctions RQ
└── worker/
    └── worker.py          # RQ worker
```

**Docker Compose:**
```yaml
services:
  api:
    build: ./api
    ports:
      - "<port>:8000"
    environment:
      - REDIS_URL=redis://rq-queue-redis:6379/2
    networks:
      - whisperx_rq-network  # Réseau partagé Redis

  worker:
    build: ./worker
    environment:
      - REDIS_URL=redis://rq-queue-redis:6379/2
      - QUEUE_NAME=my-service-queue
    networks:
      - whisperx_rq-network

networks:
  whisperx_rq-network:
    external: true
```

### Pattern: WordPress Docker

**Structure:**
```
/opt/wordpress-<site>/
├── docker-compose.yml
├── nginx.conf
├── php.ini
└── wp-content/  # Volume persistant
```

**Docker Compose:**
```yaml
version: '3.8'

services:
  wordpress:
    image: wordpress:latest
    container_name: wordpress-<site>
    restart: unless-stopped
    environment:
      - WORDPRESS_DB_HOST=mysql-<site>
      - WORDPRESS_DB_NAME=<dbname>
      - WORDPRESS_DB_USER=<user>
      - WORDPRESS_DB_PASSWORD=<password>
    volumes:
      - ./wp-content:/var/www/html/wp-content
    networks:
      - <site>-network

  mysql:
    image: mysql:8.0
    container_name: mysql-<site>
    restart: unless-stopped
    environment:
      - MYSQL_DATABASE=<dbname>
      - MYSQL_USER=<user>
      - MYSQL_PASSWORD=<password>
      - MYSQL_ROOT_PASSWORD=<root_password>
    volumes:
      - mysql-data:/var/lib/mysql
    networks:
      - <site>-network

  nginx:
    image: nginx:alpine
    container_name: nginx-<site>
    restart: unless-stopped
    ports:
      - "<port>:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./wp-content:/var/www/html/wp-content:ro
    depends_on:
      - wordpress
    networks:
      - <site>-network

volumes:
  mysql-data:

networks:
  <site>-network:
```

---

## 📚 Voir Aussi

- [Docker Commands Reference](../../reference/docker/commands.md)
- [Nginx Configuration Reference](../../reference/nginx/proxy-config.md)
- [VPS Initial Setup](../getting-started/vps-initial-setup.md)
- [Docker Autostart Guide](../deployment/docker-autostart-setup.md)

---

**Contributeurs:** Julien Fernandez
**Dernière mise à jour:** 2025-10-27
