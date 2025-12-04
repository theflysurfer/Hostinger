# Cristina - Site Astro

**URL**: https://cristina.srv759970.hstgr.cloud
**Type**: Site statique Astro SSG
**Statut**: ✅ Opérationnel (Basic Auth)

---

## Vue d'ensemble

Site web professionnel pour Cristina, construit avec Astro (Static Site Generator). Le site est protégé par Basic Auth pour environnement de développement.

### Caractéristiques

- **Framework**: Astro SSG
- **Type**: Site statique (HTML/CSS/JS pré-généré)
- **Hébergement**: Nginx direct (pas de Docker)
- **Sécurité**: Basic Auth activé
- **HTTPS**: ✅ Let's Encrypt

---

## Architecture

```
Internet (HTTPS 443)
    ↓
Nginx (reverse proxy + Basic Auth)
    ↓
/opt/cristina-site/ (fichiers statiques)
```

---

## Emplacements

- **Répertoire site**: `/opt/cristina-site/`
- **Backend (optionnel)**: `/opt/cristina-backend/`
- **Nginx config**: `/etc/nginx/sites-available/cristina`
- **Certificat SSL**: Let's Encrypt

### Structure du site

```
/opt/cristina-site/
├── index.html           # Page d'accueil
├── _astro/              # Assets Astro (CSS, JS)
├── a-propos/            # Page à propos
├── ateliers/            # Page ateliers
├── contact/             # Page contact
├── cristina-photo.jpg   # Photo
├── favicon.svg          # Favicon
├── robots.txt           # SEO
└── sitemap.xml          # Sitemap
```

---

## Accès

### Site Web

**URL**: https://cristina.srv759970.hstgr.cloud

**Credentials Basic Auth**:
- User: Voir `/etc/nginx/.htpasswd`
- Pass: Voir configuration nginx

### SSH

```bash
ssh root@69.62.108.82
cd /opt/cristina-site
```

---

## Gestion

### Déploiement / Mise à jour

Le site est statique, donc mis à jour par build Astro local puis upload :

```bash
# Sur votre machine locale (où le code source existe)
cd cristina-site-source
npm run build

# Upload vers le serveur
scp -r dist/* root@69.62.108.82:/opt/cristina-site/

# Ou via rsync
rsync -avz --delete dist/ root@69.62.108.82:/opt/cristina-site/
```

### Rebuild depuis le serveur (si code source présent)

```bash
ssh root@69.62.108.82
cd /opt/cristina-site
# Si package.json existe
npm install
npm run build
```

### Vérifier les permissions

```bash
ssh root@69.62.108.82
ls -la /opt/cristina-site/
# S'assurer que nginx peut lire
chown -R www-data:www-data /opt/cristina-site/
chmod -R 755 /opt/cristina-site/
```

### Reload Nginx après changements

```bash
ssh root@69.62.108.82
nginx -t
systemctl reload nginx
```

---

## Configuration Nginx

Fichier: `/etc/nginx/sites-available/cristina`

```nginx
server {
    listen 443 ssl http2;
    server_name cristina.srv759970.hstgr.cloud;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/cristina.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cristina.srv759970.hstgr.cloud/privkey.pem;

    # Basic Auth (dev environment)
    include snippets/basic-auth.conf;

    root /opt/cristina-site;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}

server {
    listen 80;
    server_name cristina.srv759970.hstgr.cloud;
    return 301 https://$host$request_uri;
}
```

---

## Basic Auth

### Gérer les utilisateurs

```bash
# Ajouter un utilisateur
htpasswd /etc/nginx/.htpasswd username

# Changer le mot de passe
htpasswd /etc/nginx/.htpasswd username

# Supprimer un utilisateur
htpasswd -D /etc/nginx/.htpasswd username

# Reload nginx
systemctl reload nginx
```

### Désactiver Basic Auth (production)

```bash
nano /etc/nginx/sites-available/cristina
# Commenter la ligne:
# include snippets/basic-auth.conf;

nginx -t && systemctl reload nginx
```

---

## Backend (Optionnel)

Le dossier `/opt/cristina-backend/` existe mais n'est pas utilisé actuellement. Il pourrait contenir :
- Une API Strapi/Node.js
- Un backend de gestion de contenu
- Des scripts de build

**Status actuel** : Backend non actif, site 100% statique.

---

## Monitoring

### Logs Nginx

```bash
# Access logs
tail -f /var/log/nginx/access.log | grep cristina

# Error logs
tail -f /var/log/nginx/error.log | grep cristina
```

### Test disponibilité

```bash
# Depuis le serveur
curl -I https://cristina.srv759970.hstgr.cloud

# Avec Basic Auth
curl -u username:password https://cristina.srv759970.hstgr.cloud
```

---

## SEO

### Fichiers présents

- ✅ `robots.txt` - Configuration robots
- ✅ `sitemap.xml` - Plan du site
- ✅ `favicon.svg` - Icône du site

### Vérifier le sitemap

```bash
curl https://cristina.srv759970.hstgr.cloud/sitemap.xml
```

---

## Backup

### Backup du site

```bash
# Backup fichiers
tar -czf backup_cristina_$(date +%Y%m%d).tar.gz /opt/cristina-site/

# Backup config Nginx
cp /etc/nginx/sites-available/cristina backup_cristina_nginx_$(date +%Y%m%d).conf
```

### Restauration

```bash
# Restaurer fichiers
tar -xzf backup_cristina_YYYYMMDD.tar.gz -C /

# Vérifier permissions
chown -R www-data:www-data /opt/cristina-site/
chmod -R 755 /opt/cristina-site/
```

---

## Troubleshooting

### Site inaccessible (404)

```bash
# Vérifier que le site existe
ls -la /opt/cristina-site/index.html

# Vérifier config nginx
nginx -t
cat /etc/nginx/sites-available/cristina

# Vérifier symlink
ls -la /etc/nginx/sites-enabled/ | grep cristina
```

### Problème Basic Auth

```bash
# Vérifier que le fichier htpasswd existe
cat /etc/nginx/.htpasswd

# Tester avec curl
curl -u username:password https://cristina.srv759970.hstgr.cloud
```

### Erreur SSL

```bash
# Vérifier certificat
certbot certificates | grep cristina

# Renouveler si expiré
certbot renew --cert-name cristina.srv759970.hstgr.cloud
```

---

## Voir aussi

- [Guide Astro](../../guides/services/cms/astro-deployment.md) - Déploiement sites Astro
- [Guide Nginx](../../infrastructure/nginx.md) - Configuration Nginx
- [Guide Basic Auth](../../guides/infrastructure/basic-auth.md) - Configuration Basic Auth
- [Guide Cloudflare](../../guides/operations/cloudflare-setup.md) - Setup DNS/CDN
