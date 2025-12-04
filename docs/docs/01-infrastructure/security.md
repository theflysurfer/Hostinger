# Sécurité - SSL, Authentification et Bonnes Pratiques

## Vue d'ensemble

Configuration de sécurité multi-couches pour protéger les services du serveur srv759970.

## SSL/TLS avec Let's Encrypt

### Certificats déployés

| Domaine | Service | Expiration | Auto-renewal |
|---------|---------|------------|--------------|
| monitoring.srv759970.hstgr.cloud | Grafana | 2026-01-18 | ✅ |
| whisperx.srv759970.hstgr.cloud | WhisperX API | 2026-01-18 | ✅ |
| dozzle.srv759970.hstgr.cloud | Dozzle | 2026-01-18 | ✅ |
| faster-whisper.srv759970.hstgr.cloud | Faster-Whisper Queue API | 2026-01-18 | ✅ |

### Création d'un nouveau certificat

```bash
certbot certonly --nginx \
  -d <subdomain>.srv759970.hstgr.cloud \
  --non-interactive \
  --agree-tos \
  -m julien@julienfernandez.xyz
```

### Configuration SSL Nginx

```nginx
ssl_certificate /etc/letsencrypt/live/<domain>/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/<domain>/privkey.pem;
include /etc/letsencrypt/options-ssl-nginx.conf;
ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
```

### Renouvellement automatique

```bash
# Vérifier le timer
systemctl status certbot.timer

# Renouvellement manuel
certbot renew

# Vérifier les certificats
certbot certificates
```

## Authentification

### Basic Auth Nginx

Configuration pour services sensibles (Grafana, Dashy, Dozzle, RQ Dashboard):

#### Création des credentials

```bash
# Créer le fichier .htpasswd
htpasswd -c /etc/nginx/.htpasswd admin

# Ajouter un utilisateur supplémentaire
htpasswd /etc/nginx/.htpasswd user2
```

#### Snippet réutilisable

**/etc/nginx/snippets/basic-auth.conf**

```nginx
auth_basic "Restricted Access";
auth_basic_user_file /etc/nginx/.htpasswd;
```

### Grafana Login

Double authentification:

1. **Basic Auth Nginx** (première couche)
2. **Grafana Login** (deuxième couche)
   - User: `admin`
   - Password: `YourSecurePassword2025!`

### Services protégés vs publics

**Services protégés par Basic Auth:**

- Grafana (monitoring.srv759970.hstgr.cloud)
- Dashy (dashy.srv759970.hstgr.cloud)
- Dozzle (dozzle.srv759970.hstgr.cloud)
- RQ Dashboard (whisperx-dashboard.srv759970.hstgr.cloud)

**Services publics:**

- WhisperX API (whisperx.srv759970.hstgr.cloud)
- Faster-Whisper API (faster-whisper.srv759970.hstgr.cloud)
- MkDocs Documentation (docs.srv759970.hstgr.cloud)

## Pare-feu (UFW)

### Ports ouverts

```bash
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

## Logs et Audit

### Logs Nginx

```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Logs Docker

Via Dozzle: https://dozzle.srv759970.hstgr.cloud

```bash
docker logs <container_name>
```

## SSH Hardening

### Configuration recommandée

```bash
PermitRootLogin prohibit-password
PasswordAuthentication no
PubkeyAuthentication yes
```

## Checklist Sécurité

**✅ Implémenté:**

- [x] Certificats SSL valides
- [x] Renouvellement auto configuré
- [x] Force HTTPS sur tous les services
- [x] Basic Auth sur services sensibles
- [x] UFW configuré
- [x] Services internes sur 127.0.0.1

**⚠️ Recommandations:**

- [ ] Installer fail2ban pour SSH
- [ ] Configurer alertes Grafana
- [ ] Backup automatique quotidien
- [ ] Rate limiting sur API endpoints

## Ressources

- [Mozilla SSL Configuration](https://ssl-config.mozilla.org/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Docker Security](https://docs.docker.com/engine/security/)
