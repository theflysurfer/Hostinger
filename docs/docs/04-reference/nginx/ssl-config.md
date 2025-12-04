# Configuration SSL Standard

Configuration SSL/TLS pour serveurs Nginx avec Let's Encrypt.

## Configuration SSL de Base

```nginx
listen 443 ssl http2;
listen [::]:443 ssl http2;

ssl_certificate /etc/letsencrypt/live/<domain>/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/<domain>/privkey.pem;

include /etc/letsencrypt/options-ssl-nginx.conf;
ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
```

## Redirect HTTP → HTTPS

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name <domain>;
    return 301 https://$host$request_uri;
}
```

## Template Complet HTTPS

```nginx
# HTTPS
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name example.srv759970.hstgr.cloud;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/example.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.srv759970.hstgr.cloud/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Logs
    access_log /var/log/nginx/example-access.log;
    error_log /var/log/nginx/example-error.log;

    location / {
        proxy_pass http://127.0.0.1:8080;
        include snippets/proxy-headers.conf;  # Voir reference/nginx/proxy-headers.md
    }
}

# HTTP → HTTPS Redirect
server {
    listen 80;
    listen [::]:80;
    server_name example.srv759970.hstgr.cloud;
    return 301 https://$host$request_uri;
}
```

## Headers de Sécurité Recommandés

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
```

## Voir aussi

- [Certbot SSL](../security/ssl-certbot.md) - Procédure de génération de certificats
- [Proxy Headers](proxy-headers.md) - Configuration headers reverse proxy
