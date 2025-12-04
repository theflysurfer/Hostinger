# Nginx Configuration Reference

Comprehensive reference for Nginx server block configurations.

## Directory Structure

```
/etc/nginx/
├── nginx.conf                  # Global configuration
├── sites-available/            # All site configurations
│   ├── site-1                  # Site 1
│   ├── site-2                  # Site 2
│   └── site-3                  # Site 3
├── sites-enabled/              # Symlinks to active sites
│   ├── site-1 -> ../sites-available/site-1
│   ├── site-2 -> ../sites-available/site-2
│   └── site-3 -> ../sites-available/site-3
└── snippets/                   # Reusable configurations
    └── ssl-params.conf

/var/log/nginx/
├── access.log                  # Global access logs
├── error.log                   # Global error logs
├── site-1-access.log           # Site-specific logs
└── site-1-error.log
```

## Creating a New Site

### Step 1: Create the configuration

```bash
cat > /etc/nginx/sites-available/my-site <<'EOF'
server {
    listen 80;
    server_name my-site.example.com;

    # Configuration here (see templates below)
}
EOF
```

### Step 2: Activate the site

```bash
ln -s /etc/nginx/sites-available/my-site /etc/nginx/sites-enabled/
```

### Step 3: Test and reload

```bash
# Test syntax
nginx -t

# If OK, reload Nginx
systemctl reload nginx
```

### Step 4: Verify

```bash
# Test access
curl -I -H 'Host: my-site.example.com' http://localhost/
```

## Configuration Templates

### Template 1: Static Site

**Use case**: HTML site, Astro/React/Vue build

```nginx
server {
    listen 80;
    server_name my-site.example.com;

    root /opt/my-site;
    index index.html;

    # Site-specific logs
    access_log /var/log/nginx/my-site-access.log;
    error_log /var/log/nginx/my-site-error.log;

    # Serve files and directories
    location / {
        # For Astro/React builds: try file, then .html, then dir/, then dir/index.html
        try_files $uri $uri.html $uri/ $uri/index.html =404;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

### Template 2: Docker Reverse Proxy

**Use case**: Streamlit, FastAPI, Strapi, Node.js in Docker

```nginx
server {
    listen 80;
    server_name my-app.example.com;

    # Logs
    access_log /var/log/nginx/my-app-access.log;
    error_log /var/log/nginx/my-app-error.log;

    location / {
        # Docker port of the application (e.g., 8502, 1337, 3000)
        proxy_pass http://localhost:8502;

        proxy_http_version 1.1;

        # Essential headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (Streamlit, Strapi admin)
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeout for long polling
        proxy_read_timeout 86400;
    }
}
```

### Template 3: Systemd Service Proxy

**Use case**: Ollama, PostgreSQL, local API

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        # Systemd service port
        proxy_pass http://localhost:11434;

        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # CORS if public API
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;

        # Timeouts for long requests (LLM)
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;

        # No buffering (streaming)
        proxy_buffering off;
        proxy_cache off;
    }
}
```

### Template 4: Multiple Apps (Sub-paths)

**Use case**: `site.com/app1`, `site.com/app2`

```nginx
server {
    listen 80;
    server_name example.com;

    # App 1: /dashboard -> Streamlit
    location /dashboard {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # App 2: /api -> FastAPI
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Main site: / -> Static files
    location / {
        root /opt/main-site;
        index index.html;
        try_files $uri $uri/ /index.html =404;
    }
}
```

### Template 5: Frontend + Backend

**Use case**: Frontend + Backend CMS (Strapi, Ghost, WordPress)

```nginx
# Frontend
server {
    listen 80;
    server_name my-site.example.com;

    root /opt/my-site;
    index index.html;

    location / {
        try_files $uri $uri.html $uri/ $uri/index.html =404;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# Backend admin
server {
    listen 80;
    server_name admin.my-site.example.com;

    location / {
        proxy_pass http://localhost:1337;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

## Global nginx.conf

Configuration with optimizations:

```nginx
user www-data;
worker_processes auto;
pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    # Basic Settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;

    # MIME Types
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Virtual Host Configs
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
```

## Best Practices

### 1. Always use specific `server_name`

```nginx
# GOOD
server {
    server_name my-site.example.com www.my-site.com;
}

# BAD (creates conflicts)
server {
    server_name _;  # Catch-all
}
```

### 2. One file = One site (or logical group)

```
sites-available/
├── frontend              # Frontend site
├── dashboard             # Dashboard app
└── api                   # API service
```

### 3. Separate logs per site

```nginx
server {
    access_log /var/log/nginx/my-site-access.log;
    error_log /var/log/nginx/my-site-error.log;
}
```

### 4. Test before reload

```bash
# ALWAYS run nginx -t before reload
nginx -t && systemctl reload nginx
```

### 5. Comment your configurations

```nginx
server {
    listen 80;
    server_name my-site.example.com;

    # Site-specific logs
    access_log /var/log/nginx/my-site-access.log;

    # Reverse proxy to Docker container (port 8502)
    location / {
        proxy_pass http://localhost:8502;
        # ...
    }
}
```

## See Also

- [Proxy Headers](proxy-headers.md) - Standard headers for reverse proxy
- [SSL Config](ssl-config.md) - HTTPS configuration
- [../security/ssl-certbot.md](../security/ssl-certbot.md) - SSL certificate generation
- [../../infrastructure/nginx.md](../../infrastructure/nginx.md) - Nginx installation and setup
- [../../guides/infrastructure/nginx-troubleshooting.md](../../guides/infrastructure/nginx-troubleshooting.md) - Troubleshooting guide
