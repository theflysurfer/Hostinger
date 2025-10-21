# WordPress - Déploiement Docker

## Vue d'ensemble

Guide de déploiement de sites WordPress avec Docker sur srv759970.hstgr.cloud.

## Sites WordPress Déployés

### Clémence Site

- **URL**: https://clemence.srv759970.hstgr.cloud
- **Type**: Site vitrine projets engagés
- **Stack**: WordPress + MySQL + Nginx

### SolidarLink

- **URL**: https://solidarlink.srv759970.hstgr.cloud
- **Type**: Plateforme de mise en relation solidaire
- **Stack**: WordPress + MySQL + Nginx

## Architecture Docker

```
/opt/wordpress-clemence/
├── docker-compose.yml
└── nginx/
    └── default.conf

/opt/wordpress-solidarlink/
├── docker-compose.yml
└── nginx/
    └── default.conf
```

## Configuration Docker Compose

### Structure Basique

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: mysql-clemence
    restart: unless-stopped
    environment:
      - MYSQL_ROOT_PASSWORD=<root_password>
      - MYSQL_DATABASE=clemence_db
      - MYSQL_USER=clemence_user
      - MYSQL_PASSWORD=<user_password>
    volumes:
      - mysql-data:/var/lib/mysql
    networks:
      - wordpress-net

  wordpress:
    image: wordpress:latest
    container_name: wordpress-clemence
    restart: unless-stopped
    depends_on:
      - mysql
    environment:
      - WORDPRESS_DB_HOST=mysql-clemence:3306
      - WORDPRESS_DB_NAME=clemence_db
      - WORDPRESS_DB_USER=clemence_user
      - WORDPRESS_DB_PASSWORD=<user_password>
    volumes:
      - wordpress-data:/var/www/html
    ports:
      - "8080:80"
    networks:
      - wordpress-net

volumes:
  mysql-data:
  wordpress-data:

networks:
  wordpress-net:
    driver: bridge
```

## Déploiement

### 1. Créer la Structure

```bash
mkdir -p /opt/wordpress-clemence
cd /opt/wordpress-clemence
```

### 2. Créer docker-compose.yml

```bash
nano docker-compose.yml
# Coller la configuration ci-dessus
```

### 3. Démarrer les Services

```bash
docker-compose up -d
```

### 4. Vérifier les Logs

```bash
docker-compose logs -f
```

## Configuration Nginx

### Certificat SSL

```bash
certbot certonly --nginx \
  -d clemence.srv759970.hstgr.cloud \
  --non-interactive \
  --agree-tos \
  -m julien@julienfernandez.xyz
```

### Configuration Nginx

**/etc/nginx/sites-available/clemence**

```nginx
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name clemence.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/clemence.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/clemence.srv759970.hstgr.cloud/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    access_log /var/log/nginx/clemence-access.log;
    error_log /var/log/nginx/clemence-error.log;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WordPress specific
        proxy_set_header X-Forwarded-Host $host;
        proxy_redirect off;
    }
}

server {
    listen 80;
    listen [::]:80;
    server_name clemence.srv759970.hstgr.cloud;
    return 301 https://$host$request_uri;
}
```

### Activation

```bash
ln -sf /etc/nginx/sites-available/clemence /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

## Configuration WordPress

### 1. Accès Initial

Naviguer vers https://clemence.srv759970.hstgr.cloud

### 2. Installation WordPress

- Langue: Français
- Titre du site
- Nom d'utilisateur admin
- Mot de passe
- Email

### 3. Configuration HTTPS

Dans wp-config.php (via docker exec):

```php
define('FORCE_SSL_ADMIN', true);
if (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https') {
    $_SERVER['HTTPS'] = 'on';
}
```

## Plugins Recommandés

### Sécurité

- Wordfence Security
- iThemes Security

### Performance

- WP Super Cache
- Autoptimize

### SEO

- Yoast SEO
- Rank Math

### Backup

- UpdraftPlus
- BackWPup

## Maintenance

### Backup

```bash
# Backup volumes
docker run --rm \
  -v wordpress-clemence_wordpress-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/wordpress-$(date +%Y%m%d).tar.gz -C /data .

docker run --rm \
  -v wordpress-clemence_mysql-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/mysql-$(date +%Y%m%d).tar.gz -C /data .
```

### Mise à Jour WordPress

Via l'interface admin ou:

```bash
docker exec wordpress-clemence wp core update --allow-root
docker exec wordpress-clemence wp plugin update --all --allow-root
docker exec wordpress-clemence wp theme update --all --allow-root
```

### Logs

```bash
# WordPress
docker logs wordpress-clemence -f

# MySQL
docker logs mysql-clemence -f

# Nginx
tail -f /var/log/nginx/clemence-access.log
```

## Troubleshooting

### Erreur de connexion base de données

```bash
# Vérifier que MySQL est démarré
docker ps | grep mysql

# Voir les logs MySQL
docker logs mysql-clemence --tail 50

# Tester la connexion
docker exec -it mysql-clemence mysql -u clemence_user -p
```

### Permissions fichiers

```bash
# Réparer les permissions
docker exec wordpress-clemence chown -R www-data:www-data /var/www/html
```

### White Screen of Death

```bash
# Activer le debug dans wp-config.php
docker exec -it wordpress-clemence bash
nano /var/www/html/wp-config.php

# Ajouter:
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
define('WP_DEBUG_DISPLAY', false);

# Voir les logs
tail -f /var/www/html/wp-content/debug.log
```

## Performance

### Cache

Installer WP Super Cache et activer.

### CDN

Configurer Cloudflare pour servir les assets statiques.

### Optimisation Images

- Installer Imagify ou Smush
- Compression automatique

### Database Optimization

```bash
docker exec -it mysql-clemence mysql -u root -p

OPTIMIZE TABLE wp_posts;
OPTIMIZE TABLE wp_postmeta;
```

## Sécurité

### SSL/HTTPS

- Certificats Let's Encrypt
- Force HTTPS dans WordPress

### Firewall

- Basic Auth pour wp-admin (Nginx)
- Wordfence pour protection applicative

### Mises à Jour

- WordPress core
- Plugins
- Thèmes
- PHP (via image Docker)

### Backup Automatique

Configurer UpdraftPlus avec stockage sur Dropbox/Google Drive.

## Ressources

- [WordPress Docker](https://hub.docker.com/_/wordpress)
- [WordPress Codex](https://codex.wordpress.org/)
- [WP-CLI](https://wp-cli.org/)
