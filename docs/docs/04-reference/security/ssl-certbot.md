# Génération Certificat SSL avec Certbot

Procédure pour générer des certificats SSL Let's Encrypt avec Certbot.

## Prérequis

- Nginx installé et configuré
- DNS pointant vers le serveur (A record)
- Port 80 ouvert pour validation HTTP

## Génération Certificat Simple

```bash
certbot certonly --nginx \
  -d <subdomain>.srv759970.hstgr.cloud \
  --non-interactive \
  --agree-tos \
  -m julien@julienfernandez.xyz
```

## Génération Multi-domaines

```bash
certbot certonly --nginx \
  -d domain1.srv759970.hstgr.cloud \
  -d domain2.srv759970.hstgr.cloud \
  --non-interactive \
  --agree-tos \
  -m julien@julienfernandez.xyz
```

## Génération Wildcard (DNS Challenge)

```bash
certbot certonly --manual \
  --preferred-challenges dns \
  -d "*.srv759970.hstgr.cloud" \
  -m julien@julienfernandez.xyz
```

**Note**: Nécessite de créer un enregistrement TXT DNS manuellement.

## Renouvellement Automatique

Certbot configure automatiquement le renouvellement via systemd timer.

### Vérifier le timer

```bash
systemctl status certbot.timer
```

### Tester le renouvellement

```bash
certbot renew --dry-run
```

### Renouvellement Manuel

```bash
certbot renew
systemctl reload nginx
```

## Vérifier les Certificats

```bash
# Lister tous les certificats
certbot certificates

# Détails d'un certificat spécifique
openssl x509 -in /etc/letsencrypt/live/<domain>/cert.pem -text -noout
```

## Localisation des Fichiers

```
/etc/letsencrypt/
├── live/<domain>/
│   ├── fullchain.pem    # Certificat complet (à utiliser dans nginx)
│   ├── privkey.pem      # Clé privée (à utiliser dans nginx)
│   ├── cert.pem         # Certificat seul
│   └── chain.pem        # Chaîne de certification
├── archive/             # Archives des certificats
└── renewal/             # Configurations de renouvellement
```

## Supprimer un Certificat

```bash
certbot delete --cert-name <domain>.srv759970.hstgr.cloud
```

## Troubleshooting

### Erreur: Port 80 non accessible

```bash
# Vérifier que Nginx écoute sur port 80
netstat -tlnp | grep :80

# Vérifier le firewall
ufw status | grep 80
```

### Erreur: DNS non résolu

```bash
# Vérifier la résolution DNS
dig <subdomain>.srv759970.hstgr.cloud +short
nslookup <subdomain>.srv759970.hstgr.cloud
```

### Certificat expiré

```bash
# Forcer le renouvellement
certbot renew --force-renewal --cert-name <domain>.srv759970.hstgr.cloud
systemctl reload nginx
```

## Common Issues

### HTTPS Redirect Blocking Certbot

**Problem**: Certbot validation fails because existing HTTPS redirect prevents HTTP-01 challenge.

**Symptoms**:
```
Failed authorization procedure. example.com (http-01):
urn:ietf:params:acme:error:connection :: The server could not connect to the client
Invalid response from https://... 404
```

**Diagnosis**:
```bash
# Test if HTTP access redirects to HTTPS
curl -I http://whisper.srv759970.hstgr.cloud/

# If result shows: HTTP/1.1 301 → HTTPS, this is the problem!
```

**Solution 1**: Use standalone mode (temporarily stop Nginx):

```bash
# Stop Nginx temporarily
systemctl stop nginx

# Get certificate in standalone mode
certbot certonly --standalone \
  -d whisper.srv759970.hstgr.cloud \
  --non-interactive \
  --agree-tos \
  -m julien@julienfernandez.xyz

# Restart Nginx
systemctl start nginx
```

**Solution 2**: Configure site after obtaining certificate:

```nginx
# 1. Initial config (WITHOUT HTTPS redirect)
server {
    listen 80;
    server_name whisper.srv759970.hstgr.cloud;

    location / {
        proxy_pass http://localhost:8001;
    }
}

# 2. Obtain certificate
# certbot certonly --standalone ...

# 3. Add HTTPS block and redirect
server {
    listen 443 ssl http2;
    server_name whisper.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/whisper.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/whisper.srv759970.hstgr.cloud/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        proxy_pass http://localhost:8001;
    }
}

server {
    listen 80;
    server_name whisper.srv759970.hstgr.cloud;
    return 301 https://$host$request_uri;
}
```

**Solution 3**: Add exception for .well-known path:

```nginx
server {
    listen 80;
    server_name example.srv759970.hstgr.cloud;

    # Allow certbot validation
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Redirect everything else
    location / {
        return 301 https://$host$request_uri;
    }
}
```

**Solution 4**: Use webroot plugin:

```bash
certbot certonly --webroot -w /var/www/html \
  -d example.srv759970.hstgr.cloud \
  --non-interactive \
  --agree-tos \
  -m julien@julienfernandez.xyz
```

**Prevention**:
- **Never** add HTTPS redirect before obtaining the certificate
- Use `certbot certonly --standalone` for first certificate
- Then use `certbot --nginx` for renewals

### Certificate Already Exists

**Problem**: Certbot says certificate already exists.

**Solution**: Use `--force-renewal`:

```bash
certbot renew --force-renewal --cert-name example.srv759970.hstgr.cloud
```

### Multiple Domains on Same Certificate

**Best Practice**: Each service should have its own certificate for easier management:

```bash
# Separate certificates (recommended)
certbot certonly --nginx -d service1.srv759970.hstgr.cloud
certbot certonly --nginx -d service2.srv759970.hstgr.cloud

# vs Single certificate for multiple domains
certbot certonly --nginx -d service1.srv759970.hstgr.cloud -d service2.srv759970.hstgr.cloud
```

## Best Practices

1. **One certificate per service** - Easier renewal and management
2. **Use --nginx plugin** - Automatically handles configuration
3. **Test renewal early** - Run `certbot renew --dry-run` regularly
4. **Monitor expiration** - Certificates expire after 90 days
5. **Keep .well-known accessible** - Never block /.well-known/acme-challenge/
6. **Never add HTTPS redirect before certificate** - Prevents validation failures

## Integration with Nginx

### Certificate Creation

```bash
certbot certonly --nginx \
  -d <subdomain>.srv759970.hstgr.cloud \
  --non-interactive \
  --agree-tos \
  -m julien@julienfernandez.xyz
```

### Automatic Renewal

Certbot automatically configures a systemd timer for renewal:

```bash
# Check timer status
systemctl status certbot.timer

# Test renewal process
certbot renew --dry-run
```

### Check Certificate Expiration

```bash
certbot certificates
```

## Exemples pour srv759970

### WhisperX

```bash
certbot certonly --nginx \
  -d whisperx.srv759970.hstgr.cloud \
  --non-interactive \
  --agree-tos \
  -m julien@julienfernandez.xyz
```

### Dozzle

```bash
certbot certonly --nginx \
  -d dozzle.srv759970.hstgr.cloud \
  --non-interactive \
  --agree-tos \
  -m julien@julienfernandez.xyz
```

### Dashy

```bash
certbot certonly --nginx \
  -d dashy.srv759970.hstgr.cloud \
  --non-interactive \
  --agree-tos \
  -m julien@julienfernandez.xyz
```

## See Also

- [../nginx/ssl-config.md](../nginx/ssl-config.md) - Nginx SSL configuration reference
- [../../infrastructure/security.md](../../infrastructure/security.md) - Security overview
- [../../infrastructure/nginx.md](../../infrastructure/nginx.md) - Nginx infrastructure setup
