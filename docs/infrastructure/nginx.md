# Nginx - Reverse Proxy & Web Server

Infrastructure reference for Nginx on srv759970.hstgr.cloud.

## Overview

Nginx is the primary reverse proxy and web server on srv759970.hstgr.cloud, handling all HTTPS traffic and routing requests to backend services. It provides SSL/TLS termination via Let's Encrypt certificates, load balancing capabilities, and serves as a security layer with authentication and rate limiting.

The server runs multiple services (Grafana, WhisperX, Dozzle, WordPress, n8n, Strapi) all behind Nginx, which provides:
- **SSL/TLS termination** for all HTTPS traffic with automatic certificate management
- **Reverse proxying** to Docker containers and systemd services on various ports
- **Security features** including basic authentication, rate limiting, and security headers
- **WebSocket support** for real-time applications like Grafana Live and Dozzle log streaming
- **Static file serving** for web applications and media content

This infrastructure approach centralizes SSL management, simplifies firewall rules (only ports 80/443 exposed), and provides a unified access control point.

## Installation

```bash
apt-get update
apt-get install -y nginx certbot python3-certbot-nginx
```

## Directory Structure

```
/etc/nginx/
├── nginx.conf              # Main configuration file
├── sites-available/        # All site configurations
├── sites-enabled/          # Symlinks to active sites
├── snippets/               # Reusable configuration fragments
└── conf.d/                 # Additional configurations
```

See [Nginx Configuration Reference](../reference/nginx/configuration.md) for detailed layouts and service-specific configs (Grafana, WhisperX, Dozzle, WordPress, etc.).

## Global Configuration

### /etc/nginx/nginx.conf

Configuration de base avec optimisations pour production:

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

**Key optimizations:**
- `worker_processes auto` - Auto-detects CPU cores for optimal performance
- `sendfile on` - Efficient file transfer using kernel sendfile()
- `tcp_nopush` and `tcp_nodelay` - Optimizes packet transmission
- `server_tokens off` - Hides Nginx version for security
- `gzip on` - Compresses responses to reduce bandwidth

## Creating New Sites

Quick workflow for adding a new service to Nginx:

1. Create configuration in `/etc/nginx/sites-available/myservice`
2. Symlink to sites-enabled: `ln -sf /etc/nginx/sites-available/myservice /etc/nginx/sites-enabled/`
3. Test configuration: `nginx -t`
4. Reload Nginx: `systemctl reload nginx`
5. Obtain SSL certificate: `certbot certonly --nginx -d myservice.srv759970.hstgr.cloud`

See [Nginx Configuration Reference](../reference/nginx/configuration.md) for complete templates including reverse proxy configs, WebSocket support, file upload handling, WordPress multisite, and static site hosting.

## Reusable Snippets

### Basic Authentication

**/etc/nginx/snippets/basic-auth.conf**

```nginx
auth_basic "Restricted Access";
auth_basic_user_file /etc/nginx/.htpasswd;
```

Create password file:
```bash
htpasswd -c /etc/nginx/.htpasswd admin
```

Usage in site configs:
```nginx
location / {
    include snippets/basic-auth.conf;
    proxy_pass http://127.0.0.1:3000;
}
```

See [Basic Auth Setup](../reference/security/basic-auth-setup.md) for multi-user configuration and troubleshooting.

### Standard Proxy Headers

**/etc/nginx/snippets/proxy-params.conf**

```nginx
proxy_http_version 1.1;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

See [Proxy Headers Reference](../reference/nginx/proxy-headers.md) for detailed explanations.

## Essential Commands

```bash
# Service management
systemctl start nginx          # Start Nginx
systemctl stop nginx           # Stop Nginx
systemctl restart nginx        # Restart (drops connections)
systemctl reload nginx         # Reload config (graceful, no downtime)
systemctl status nginx         # Check service status

# Configuration testing
nginx -t                       # Test configuration syntax
nginx -T                       # Show full parsed configuration

# Log viewing
tail -f /var/log/nginx/access.log     # Follow access log
tail -f /var/log/nginx/error.log      # Follow error log
```

See [Nginx Debugging Reference](../reference/nginx/debugging.md) for comprehensive diagnostic commands.

## Security Best Practices

### Security Headers

Add to all server blocks:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
```

### Rate Limiting

Protect APIs from abuse:

```nginx
# In http block of nginx.conf
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

# In location block
location /api/ {
    limit_req zone=api burst=20 nodelay;
    proxy_pass http://backend;
}
```

### Additional Security

- Always use HTTPS (redirect HTTP to HTTPS)
- Keep Nginx and OpenSSL updated
- Use strong SSL/TLS configuration (see SSL Configuration section)
- Implement basic authentication for admin interfaces
- Restrict access by IP when possible

## SSL/HTTPS Configuration

All services use Let's Encrypt SSL certificates. Nginx handles SSL termination and forwards traffic to backend services over HTTP.

### Quick Certificate Setup

```bash
# Obtain certificate
certbot certonly --nginx -d subdomain.srv759970.hstgr.cloud \
  --non-interactive --agree-tos -m julien@julienfernandez.xyz

# Verify certificates
certbot certificates

# Test renewal
certbot renew --dry-run
```

### SSL Configuration Template

```nginx
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name subdomain.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/subdomain.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/subdomain.srv759970.hstgr.cloud/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # ... proxy configuration ...
}

# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name subdomain.srv759970.hstgr.cloud;
    return 301 https://$host$request_uri;
}
```

### Automatic Renewal

Certbot configures a systemd timer for automatic renewal (30 days before expiration):

```bash
systemctl status certbot.timer       # Check timer status
systemctl list-timers certbot.timer  # View schedule
```

For comprehensive SSL configuration including cipher suites, OCSP stapling, HSTS, and troubleshooting, see:
- [SSL Configuration Reference](../reference/nginx/ssl-config.md)
- [Certbot SSL Management](../reference/security/certbot-ssl.md)

## Troubleshooting

### Quick Diagnostic Steps

1. Check Nginx status: `systemctl status nginx`
2. Test configuration: `nginx -t`
3. Check error logs: `tail -50 /var/log/nginx/error.log`
4. Verify backend service: `netstat -tlnp | grep <port>` or `ss -tlnp | grep <port>`

### Common Issues

**502 Bad Gateway**
- Backend service stopped or crashed
- Wrong port in `proxy_pass` directive
- Backend not listening on expected address

**504 Gateway Timeout**
- Backend service slow to respond
- Timeout values too short for long-running operations
- Solution: Increase `proxy_read_timeout`, `proxy_connect_timeout`, `proxy_send_timeout`

**SSL Certificate Errors**
- Certificate expired (check with `certbot certificates`)
- Wrong certificate path in Nginx config
- Renewal failed (check `/var/log/letsencrypt/letsencrypt.log`)

For detailed troubleshooting:
- [Nginx Debugging Reference](../reference/nginx/debugging.md) - Diagnostic commands and log analysis
- [Nginx Troubleshooting Guide](../guides/GUIDE_TROUBLESHOOTING_NGINX.md) - Common problems and solutions

## See Also

### Configuration & Setup
- [Nginx Configuration Reference](../reference/nginx/configuration.md) - All templates (Grafana, WhisperX, Dozzle, WordPress)
- [Proxy Headers Reference](../reference/nginx/proxy-headers.md) - HTTP headers for reverse proxying
- [SSL Configuration Reference](../reference/nginx/ssl-config.md) - Detailed HTTPS/TLS setup

### Security
- [Basic Auth Setup](../reference/security/basic-auth-setup.md) - HTTP authentication
- [Certbot SSL Management](../reference/security/certbot-ssl.md) - Certificate lifecycle

### Troubleshooting
- [Nginx Debugging Reference](../reference/nginx/debugging.md) - Diagnostic commands
- [Nginx Troubleshooting Guide](../guides/GUIDE_TROUBLESHOOTING_NGINX.md) - Common issues

### Service-Specific Guides
- [WordPress Setup](../guides/GUIDE_WORDPRESS_DOCKER.md) - WordPress with Nginx
- [n8n Setup](../guides/GUIDE_N8N_SETUP.md) - n8n workflow automation
- [Strapi Setup](../guides/GUIDE_STRAPI.md) - Strapi CMS

### External Resources
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [Let's Encrypt](https://letsencrypt.org/)
