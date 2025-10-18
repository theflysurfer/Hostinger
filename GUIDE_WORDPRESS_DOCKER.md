# 🐳 Guide WordPress en Docker - srv759970.hstgr.cloud

Guide complet pour déployer WordPress en Docker avec PHP-FPM, MySQL, Nginx, permissions correctes et migration complète depuis une installation native.

---

## 📚 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture](#architecture)
3. [Stack Docker recommandée](#stack-docker-recommandée)
4. [Migration depuis installation native](#migration-depuis-installation-native)
5. [Problèmes courants et solutions](#problèmes-courants-et-solutions)
6. [Commandes de gestion](#commandes-de-gestion)
7. [Bonnes pratiques](#bonnes-pratiques)

---

## 📖 Vue d'ensemble

### Pourquoi dockeriser WordPress ?

✅ **Avantages** :
- Isolation complète (PHP, MySQL, Nginx dans des conteneurs)
- Pas de conflits de versions PHP entre différents sites
- Backups simplifiés (volumes Docker)
- Facilité de migration entre serveurs
- Mises à jour contrôlées
- Monitoring centralisé

⚠️ **Défis à connaître** :
- **Permissions** : UID/GID mismatch entre host et conteneur
- **Reverse proxy** : Détection HTTPS derrière Nginx host
- **Migration** : Doit inclure TOUS les fichiers (plugins, themes, uploads)
- **DB_HOST** : Change de `localhost` au nom du conteneur MySQL

---

## 🏗️ Architecture

### Stack complète (3 conteneurs)

```
┌─────────────────────────────────────────────┐
│   Nginx Host (Port 443 HTTPS + SSL)        │
│   - Basic Auth                              │
│   - Let's Encrypt SSL                       │
│   - Reverse Proxy                           │
└────────────────┬────────────────────────────┘
                 │ proxy_pass http://localhost:9002
                 ▼
┌─────────────────────────────────────────────┐
│   Conteneur nginx-clemence (Port 9002)     │
│   - Nginx Alpine                            │
│   - Sert les fichiers statiques             │
│   - Passe les .php à PHP-FPM                │
└────────────────┬────────────────────────────┘
                 │ fastcgi_pass wordpress:9000
                 ▼
┌─────────────────────────────────────────────┐
│   Conteneur wordpress-clemence (Port 9000) │
│   - PHP 8.3-FPM Alpine                      │
│   - WordPress 6                             │
│   - user: "33:33" (www-data)                │
│   - Volume: wordpress-data                  │
└────────────────┬────────────────────────────┘
                 │ mysql://mysql-clemence:3306
                 ▼
┌─────────────────────────────────────────────┐
│   Conteneur mysql-clemence (Port 3306)     │
│   - MySQL 8.0                               │
│   - Volume: mysql-data                      │
│   - Base: clemence_db                       │
└─────────────────────────────────────────────┘
```

---

## 🚀 Stack Docker recommandée

### Structure des fichiers

```
/opt/wordpress-clemence/
├── docker-compose.yml    # Configuration des services
├── nginx.conf            # Config Nginx pour PHP-FPM
├── .env                  # Variables d'environnement (mots de passe)
└── backups/              # Optionnel : backups locaux
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  wordpress:
    image: wordpress:6-php8.3-fpm-alpine
    container_name: wordpress-clemence
    restart: unless-stopped

    # ⚠️ CRITIQUE : Fix permissions avec UID/GID de www-data
    user: "33:33"

    ports:
      - "9001:9000"

    volumes:
      # Named volumes (recommandé pour Docker)
      - wordpress-data:/var/www/html

    environment:
      # ⚠️ IMPORTANT : DB_HOST doit être le nom du conteneur MySQL
      WORDPRESS_DB_HOST: mysql-clemence:3306
      WORDPRESS_DB_NAME: clemence_db
      WORDPRESS_DB_USER: clemence_user
      WORDPRESS_DB_PASSWORD: ${WP_DB_PASSWORD}
      WORDPRESS_TABLE_PREFIX: wp_

      # ⚠️ CRITIQUE : Configurations WordPress obligatoires
      WORDPRESS_CONFIG_EXTRA: |
        /* Évite les demandes de credentials FTP */
        define('FS_METHOD', 'direct');

        /* Augmente la mémoire disponible */
        define('WP_MEMORY_LIMIT', '256M');
        define('WP_MAX_MEMORY_LIMIT', '256M');

    depends_on:
      - mysql-clemence

    networks:
      - clemence-network

  mysql-clemence:
    image: mysql:8.0
    container_name: mysql-clemence
    restart: unless-stopped

    volumes:
      - mysql-data:/var/lib/mysql

    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: clemence_db
      MYSQL_USER: clemence_user
      MYSQL_PASSWORD: ${WP_DB_PASSWORD}

    # MySQL 8 recommandé pour compatibilité WordPress
    command: --default-authentication-plugin=mysql_native_password

    networks:
      - clemence-network

  # Nginx container to serve PHP-FPM
  nginx-clemence:
    image: nginx:alpine
    container_name: nginx-clemence
    restart: unless-stopped

    ports:
      - "9002:80"

    volumes:
      # :ro = read-only (Nginx sert juste les fichiers)
      - wordpress-data:/var/www/html:ro
      - ./nginx.conf:/etc/nginx/nginx.conf:ro

    depends_on:
      - wordpress

    networks:
      - clemence-network

volumes:
  wordpress-data:
  mysql-data:

networks:
  clemence-network:
    driver: bridge
```

### nginx.conf (pour le conteneur Nginx)

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    keepalive_timeout 65;
    gzip on;

    # Limite uploads WordPress (fichiers média, plugins, etc.)
    client_max_body_size 64M;

    server {
        listen 80;
        server_name _;
        root /var/www/html;
        index index.php index.html;

        # Permaliens WordPress
        location / {
            try_files $uri $uri/ /index.php?$args;
        }

        # ⚠️ CRITIQUE : Passer les requêtes PHP à PHP-FPM
        location ~ \.php$ {
            # Nom du conteneur WordPress (pas localhost!)
            fastcgi_pass wordpress-clemence:9000;
            fastcgi_index index.php;
            fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
            include fastcgi_params;
        }

        # Sécurité : bloquer accès fichiers cachés
        location ~ /\.ht {
            deny all;
        }
    }
}
```

### .env (fichier de variables)

```bash
# WordPress Database Password
WP_DB_PASSWORD=VotreMotDePasseSecurise2025

# MySQL Root Password
MYSQL_ROOT_PASSWORD=RootMotDePasseTresSecurise2025!
```

⚠️ **Important** : Ajouter `.env` dans `.gitignore` si vous versionnez !

---

## 🔄 Migration depuis installation native

### Exemple : Migration WordPress Clémence

Suivi de la migration réelle effectuée le 2025-10-17.

### Étape 1 : Backups complets

```bash
# 1. Backup base de données (TOUTE la base)
ssh root@69.62.108.82 "mysqldump -u root clemence_db > /tmp/clemence_wp_backup_$(date +%Y%m%d_%H%M%S).sql"

# 2. Backup TOUS les fichiers WordPress (plugins, themes, uploads)
ssh root@69.62.108.82 "tar czf /tmp/clemence_complete_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /var/www/clemence wp-content wp-config.php"

# 3. Vérifier le contenu du backup
ssh root@69.62.108.82 "tar tzf /tmp/clemence_complete_backup_*.tar.gz | grep -E '(plugins|themes|uploads)' | head -20"
```

✅ **Vérifications critiques** :
- Le dump SQL doit contenir toutes les tables (`wp_*`)
- Le tar.gz doit contenir :
  - `wp-content/plugins/` (TOUS les plugins, y compris Elementor, Header Footer Elementor)
  - `wp-content/themes/` (theme actif + themes de base)
  - `wp-content/uploads/` (médias, assets Elementor)

### Étape 2 : Créer la stack Docker

```bash
# 1. Créer la structure
ssh root@69.62.108.82 "mkdir -p /opt/wordpress-clemence"

# 2. Créer les fichiers (docker-compose.yml, nginx.conf, .env)
# Voir section "Stack Docker recommandée" ci-dessus

# 3. Déployer la stack
ssh root@69.62.108.82 "cd /opt/wordpress-clemence && docker-compose up -d"

# 4. Vérifier que tout tourne
ssh root@69.62.108.82 "docker ps | grep clemence"
```

### Étape 3 : Restaurer la base de données

```bash
# Copier le dump SQL dans le conteneur MySQL
ssh root@69.62.108.82 "docker exec -i mysql-clemence mysql -u root -p\$MYSQL_ROOT_PASSWORD clemence_db < /tmp/clemence_wp_backup_*.sql"

# Vérifier les tables
ssh root@69.62.108.82 "docker exec mysql-clemence mysql -u root -p\$MYSQL_ROOT_PASSWORD clemence_db -e 'SHOW TABLES;'"
```

### Étape 4 : Restaurer les fichiers WordPress

```bash
# 1. Copier le backup dans le conteneur WordPress
ssh root@69.62.108.82 "docker cp /tmp/clemence_complete_backup_*.tar.gz wordpress-clemence:/tmp/"

# 2. Extraire dans /var/www/html
ssh root@69.62.108.82 "docker exec wordpress-clemence sh -c 'cd /var/www/html && tar xzf /tmp/clemence_complete_backup_*.tar.gz --strip-components=0'"

# 3. Vérifier plugins et themes
ssh root@69.62.108.82 "docker exec wordpress-clemence sh -c 'ls /var/www/html/wp-content/plugins/'"
ssh root@69.62.108.82 "docker exec wordpress-clemence sh -c 'ls /var/www/html/wp-content/themes/'"
```

✅ **Vérifications** :
- Plugins présents : `elementor`, `header-footer-elementor`, etc.
- Themes présents : `hello-elementor`, etc.
- Uploads présents : `/var/www/html/wp-content/uploads/2025/`

### Étape 5 : Fixer wp-config.php

⚠️ **Problème critique** : Le wp-config.php restauré a `DB_HOST = 'localhost'` mais doit être `mysql-clemence:3306`

```bash
# Fix DB_HOST
ssh root@69.62.108.82 "docker exec wordpress-clemence sed -i \"s/'localhost'/'mysql-clemence:3306'/g\" /var/www/html/wp-config.php"

# Vérifier
ssh root@69.62.108.82 "docker exec wordpress-clemence grep DB_HOST /var/www/html/wp-config.php"
```

**Sortie attendue** :
```php
define( 'DB_HOST', 'mysql-clemence:3306' );
```

### Étape 6 : Ajouter fix reverse proxy HTTPS

⚠️ **Problème découvert** : WordPress derrière un reverse proxy HTTPS ne détecte pas HTTPS correctement → boucles de redirection 301

**Solution** : Ajouter ce code dans `wp-config.php` **AVANT** la ligne `/* That's all, stop editing! */` :

```php
/* Fix for reverse proxy - HTTPS detection */
if (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https') {
    $_SERVER['HTTPS'] = 'on';
}
```

**Comment l'ajouter proprement** :

```bash
ssh root@69.62.108.82 bash << 'EOFBASH'
# Créer le snippet
cat > /tmp/proxy_fix.txt << 'EOF'

/* Fix for reverse proxy - HTTPS detection */
if (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https') {
    $_SERVER['HTTPS'] = 'on';
}
EOF

# Trouver la ligne "stop editing"
LINE=$(docker exec wordpress-clemence grep -n "stop editing" /var/www/html/wp-config.php | head -1 | cut -d: -f1)

# Insérer le fix avant cette ligne
docker exec wordpress-clemence sh -c "head -$(($LINE - 1)) /var/www/html/wp-config.php > /tmp/wp-config-new.php"
docker cp /tmp/proxy_fix.txt wordpress-clemence:/tmp/proxy_fix.txt
docker exec wordpress-clemence sh -c "cat /tmp/proxy_fix.txt >> /tmp/wp-config-new.php"
docker exec wordpress-clemence sh -c "tail -n +$LINE /var/www/html/wp-config.php >> /tmp/wp-config-new.php"
docker exec wordpress-clemence sh -c "cp /tmp/wp-config-new.php /var/www/html/wp-config.php"
EOFBASH
```

### Étape 7 : Fixer les URLs dans la base de données

⚠️ **Problème découvert** : Si `siteurl` et `home` ont des protocoles différents (http vs https), boucle de redirection !

```bash
# Vérifier les URLs actuelles
ssh root@69.62.108.82 "docker exec mysql-clemence mysql -u root -p\$MYSQL_ROOT_PASSWORD clemence_db -e \"SELECT option_name, option_value FROM wp_options WHERE option_name IN ('siteurl', 'home');\""
```

**Si `siteurl` est en `http://` et `home` en `https://`** → **PROBLÈME !**

**Fix** :
```bash
ssh root@69.62.108.82 "docker exec mysql-clemence mysql -u root -p\$MYSQL_ROOT_PASSWORD clemence_db -e \"UPDATE wp_options SET option_value = 'https://clemence.srv759970.hstgr.cloud' WHERE option_name IN ('siteurl', 'home');\""
```

### Étape 8 : Configurer Nginx host (reverse proxy)

```bash
# Backup config actuelle
ssh root@69.62.108.82 "cp /etc/nginx/sites-available/clemence /etc/nginx/sites-available/clemence.backup_$(date +%Y%m%d)"

# Nouvelle config : proxy vers le conteneur Nginx Docker
ssh root@69.62.108.82 "cat > /etc/nginx/sites-available/clemence << 'EOF'
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name clemence.srv759970.hstgr.cloud;

    # SSL Certificate
    ssl_certificate /etc/letsencrypt/live/clemence.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/clemence.srv759970.hstgr.cloud/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Logs
    access_log /var/log/nginx/clemence-access.log;
    error_log /var/log/nginx/clemence-error.log;

    # Limite uploads
    client_max_body_size 100M;

    # Basic Auth
    include snippets/basic-auth.conf;

    # ⚠️ Proxy vers le conteneur Docker
    location / {
        proxy_pass http://localhost:9002;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;

        # ⚠️ CRITIQUE : Indique à WordPress qu'on est en HTTPS
        proxy_set_header X-Forwarded-Proto \$scheme;

        # Timeouts pour WordPress
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;

        # Buffers
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 256 16k;
        proxy_busy_buffers_size 256k;
    }

    # Cache fichiers statiques
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        proxy_pass http://localhost:9002;
        proxy_set_header Host \$host;
        expires 365d;
        add_header Cache-Control \"public, immutable\";
        access_log off;
    }
}

# HTTP -> HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name clemence.srv759970.hstgr.cloud;
    return 301 https://\$host\$request_uri;
}
EOF
"

# Tester la config
ssh root@69.62.108.82 "nginx -t"

# Recharger Nginx
ssh root@69.62.108.82 "systemctl reload nginx"
```

### Étape 9 : Tester !

```bash
# Test basique
curl -I -u julien:DevAccess2025 https://clemence.srv759970.hstgr.cloud/

# Attendu : HTTP/1.1 200 OK
```

**Vérifier que** :
- ✅ Pas de boucle de redirection (301 vers la même URL)
- ✅ HTTP 200 OK
- ✅ Les CSS Elementor se chargent
- ✅ Le header/footer s'affichent
- ✅ Les images se chargent

---

## ⚠️ Problèmes courants et solutions

### Problème 1 : Permissions denied (wp-content)

**Symptômes** :
- "Could not move uploaded file to wp-content/uploads"
- WordPress demande FTP credentials pour installer plugins
- Erreurs 500 lors de l'upload

**Cause** : UID/GID mismatch entre le conteneur WordPress et le host

**Solution** :
```yaml
# Dans docker-compose.yml
services:
  wordpress:
    user: "33:33"  # www-data UID/GID
```

ET ajouter dans `WORDPRESS_CONFIG_EXTRA` :
```php
define('FS_METHOD', 'direct');
```

### Problème 2 : Boucle de redirection 301 infinie

**Symptômes** :
- `curl` retourne "301 Moved Permanently" en boucle
- "Too many redirects" dans le navigateur
- URL redirige vers elle-même

**Causes possibles** :

#### Cause 2a : siteurl != home (protocoles différents)

```bash
# Vérifier
docker exec mysql-clemence mysql -u root -p$MYSQL_ROOT_PASSWORD clemence_db -e "SELECT option_name, option_value FROM wp_options WHERE option_name IN ('siteurl', 'home');"
```

**Solution** : Les deux doivent être identiques (HTTPS) :
```sql
UPDATE wp_options SET option_value = 'https://clemence.srv759970.hstgr.cloud' WHERE option_name IN ('siteurl', 'home');
```

#### Cause 2b : WordPress ne détecte pas HTTPS derrière le proxy

**Solution** : Ajouter dans `wp-config.php` (voir Étape 6)

#### Cause 2c : Nginx host ne passe pas X-Forwarded-Proto

**Solution** : Vérifier que Nginx host a :
```nginx
proxy_set_header X-Forwarded-Proto $scheme;
```

### Problème 3 : Erreur 500 après ajout dans wp-config.php

**Cause** : Syntaxe PHP incorrecte (souvent due à l'échappement de variables)

**Solution** : Vérifier la syntaxe :
```bash
docker exec wordpress-clemence php -l /var/www/html/wp-config.php
```

Si erreur, restaurer depuis backup :
```bash
docker cp /tmp/clemence_complete_backup_*.tar.gz wordpress-clemence:/tmp/
docker exec wordpress-clemence sh -c "cd /tmp && tar xzf clemence_complete_backup_*.tar.gz wp-config.php && cp wp-config.php /var/www/html/"
```

### Problème 4 : Cannot connect to MySQL

**Symptômes** :
- "Error establishing a database connection"
- WordPress affiche page blanche

**Causes** :

#### Cause 4a : DB_HOST incorrect

**Vérifier** :
```bash
docker exec wordpress-clemence grep DB_HOST /var/www/html/wp-config.php
```

**Attendu** : `define( 'DB_HOST', 'mysql-clemence:3306' );`

Si `localhost` → **ERREUR** (les conteneurs sont isolés)

**Fix** :
```bash
docker exec wordpress-clemence sed -i "s/'localhost'/'mysql-clemence:3306'/g" /var/www/html/wp-config.php
```

#### Cause 4b : MySQL n'a pas fini de démarrer

**Vérifier** :
```bash
docker logs mysql-clemence --tail=20
```

**Attendu** : `mysqld: ready for connections`

Si "still initializing" → Attendre 30-60 secondes

#### Cause 4c : Mot de passe incorrect

**Vérifier** :
```bash
cat /opt/wordpress-clemence/.env
docker exec wordpress-clemence env | grep WORDPRESS_DB_PASSWORD
```

Les deux doivent correspondre.

### Problème 5 : Plugins/themes manquants après migration

**Cause** : Backup incomplet (oubli de wp-content/plugins ou wp-content/themes)

**Vérification** :
```bash
# Vérifier plugins
docker exec wordpress-clemence ls /var/www/html/wp-content/plugins/

# Vérifier themes
docker exec wordpress-clemence ls /var/www/html/wp-content/themes/
```

**Solution** : Refaire le backup en incluant **TOUT** wp-content :
```bash
tar czf backup.tar.gz -C /var/www/site wp-content wp-config.php
```

---

## 🛠️ Commandes de gestion

### Logs

```bash
# Logs WordPress (PHP-FPM)
docker logs wordpress-clemence --tail=50 -f

# Logs MySQL
docker logs mysql-clemence --tail=50 -f

# Logs Nginx conteneur
docker logs nginx-clemence --tail=50 -f

# Logs Nginx host
tail -f /var/log/nginx/clemence-error.log
```

### Redémarrer

```bash
# Redémarrer tout
cd /opt/wordpress-clemence && docker-compose restart

# Redémarrer juste WordPress
docker restart wordpress-clemence

# Redémarrer juste MySQL
docker restart mysql-clemence
```

### Arrêter / Démarrer

```bash
# Arrêter tout
cd /opt/wordpress-clemence && docker-compose down

# Démarrer tout
cd /opt/wordpress-clemence && docker-compose up -d

# Avec rebuild des images
cd /opt/wordpress-clemence && docker-compose up -d --build
```

### Accès shell

```bash
# Shell WordPress
docker exec -it wordpress-clemence sh

# Shell MySQL
docker exec -it mysql-clemence bash

# MySQL CLI
docker exec -it mysql-clemence mysql -u root -p
```

### Backups

```bash
# Backup base de données
docker exec mysql-clemence mysqldump -u root -p$MYSQL_ROOT_PASSWORD clemence_db > backup_$(date +%Y%m%d).sql

# Backup fichiers WordPress (via volume)
docker run --rm -v wordpress-clemence_wordpress-data:/data -v $(pwd):/backup alpine tar czf /backup/wordpress-data_$(date +%Y%m%d).tar.gz -C /data .

# Backup complet (db + files)
./backup.sh  # Script custom recommandé
```

### Monitoring

```bash
# Ressources (CPU, RAM)
docker stats --no-stream | grep clemence

# Taille des volumes
docker system df -v | grep clemence

# Vérifier santé
docker ps | grep clemence
```

---

## ✅ Paramètres critiques (validés en production)

### 1. Permissions Docker (CRITIQUE ⚠️)

**Problème** : WordPress ne peut pas écrire dans wp-content → uploads/plugins impossible

**Solution obligatoire** :
```yaml
# docker-compose.yml
services:
  wordpress:
    user: "33:33"  # ⚠️ OBLIGATOIRE
```

**ET** dans WORDPRESS_CONFIG_EXTRA :
```php
define('FS_METHOD', 'direct');  // ⚠️ OBLIGATOIRE
```

**Pourquoi** : UID 33 = www-data sur Ubuntu. Sans ça, permission denied partout.

### 2. DB_HOST (CRITIQUE ⚠️)

**Problème** : wp-config.php restauré a `localhost` → conteneurs isolés = échec connexion

**Solution** : **TOUJOURS** vérifier après restauration
```bash
docker exec wordpress-sitename sed -i "s/'localhost'/'mysql-sitename:3306'/g" /var/www/html/wp-config.php
```

**Pourquoi** : `mysql-sitename` = nom du conteneur MySQL dans le réseau Docker.

### 3. Reverse proxy HTTPS (CRITIQUE ⚠️)

**Problème** : WordPress derrière proxy HTTPS ne détecte pas HTTPS → boucles 301 infinies

**Solution** : Ajouter dans wp-config.php **AVANT** `/* That's all, stop editing! */`
```php
/* Fix for reverse proxy - HTTPS detection */
if (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https') {
    $_SERVER['HTTPS'] = 'on';
}
```

**ET** dans Nginx host :
```nginx
proxy_set_header X-Forwarded-Proto $scheme;  # ⚠️ CRITIQUE
```

**Pourquoi** : WordPress vérifie `$_SERVER['HTTPS']` pour détecter HTTPS. Sans ce fix, il pense être en HTTP et redirige infiniment.

### 4. URLs WordPress (CRITIQUE ⚠️)

**Problème** : Si `siteurl` (http) != `home` (https) → boucle 301

**Solution** : **TOUJOURS** uniformiser en HTTPS
```sql
UPDATE wp_options
SET option_value = 'https://sitename.srv759970.hstgr.cloud'
WHERE option_name IN ('siteurl', 'home');
```

**Pourquoi** : WordPress redirige vers `siteurl` si différent de l'URL de requête.

### 5. Architecture 3 conteneurs

**Stack complète** : WordPress FPM → Nginx → MySQL

**Pourquoi 3 et pas 2** :
- Image WordPress officielle = PHP-FPM seulement (pas de serveur web)
- Nginx indispensable pour servir fichiers statiques + passer PHP à FPM
- MySQL séparé = backups indépendants, scalabilité

### 6. Migration complète

**CRITIQUE** : Backup COMPLET = base + wp-content + wp-config.php

**Vérifier AVANT de continuer** :
```bash
tar tzf backup.tar.gz | grep -E 'plugins|themes|uploads' | head -20
```

**Leçon apprise** : L'utilisateur a dit "la dernière fois ça a été oublié" → TOUJOURS vérifier plugins/themes/uploads présents.

### 7. Named volumes (recommandé)

**Utiliser** : Named volumes (gérés par Docker)
```yaml
volumes:
  wordpress-data:/var/www/html  # ✅ Bon
  # PAS: ./wp-content:/var/www/html  # ❌ Bind mount = problèmes permissions
```

**Pourquoi** : Docker gère les permissions automatiquement avec named volumes.

### 8. Configuration Nginx conteneur

**Dans nginx.conf** :
```nginx
fastcgi_pass wordpress-clemence:9000;  # ⚠️ Nom conteneur, PAS localhost!
```

**Pourquoi** : `localhost` dans le conteneur Nginx ≠ conteneur WordPress.

### 9. Variables environnement

**Memory WordPress** :
```yaml
WORDPRESS_CONFIG_EXTRA: |
  define('WP_MEMORY_LIMIT', '256M');  # Minimum pour Elementor
  define('WP_MAX_MEMORY_LIMIT', '256M');
```

**Pourquoi** : 256M = suffisant pour plugins lourds (Elementor, WooCommerce).

### 10. MySQL authentication

**Dans docker-compose.yml** :
```yaml
mysql:
  command: --default-authentication-plugin=mysql_native_password
```

**Pourquoi** : WordPress préfère `mysql_native_password` (compatibilité PDO ancien).

---

## ⚠️ 10 Erreurs à éviter (expérience terrain)

### Erreur 1 : Oublier de fixer DB_HOST après restauration
**Symptôme** : "Error establishing a database connection"
**Fix** : `sed -i "s/'localhost'/'mysql-sitename:3306'/g" wp-config.php`

### Erreur 2 : Ne pas ajouter le fix reverse proxy
**Symptôme** : Boucle 301 infinie
**Fix** : Ajouter code HTTPS detection dans wp-config.php

### Erreur 3 : URLs mixtes (http/https)
**Symptôme** : Boucle 301
**Fix** : UPDATE wp_options SET siteurl et home en HTTPS

### Erreur 4 : Ajouter le fix APRÈS "stop editing"
**Symptôme** : Code ignoré ou erreur 500
**Fix** : Insérer **AVANT** `/* That's all, stop editing! */`

### Erreur 5 : Oublier `user: "33:33"`
**Symptôme** : Cannot upload, FTP credentials demandés
**Fix** : Ajouter `user: "33:33"` dans docker-compose.yml

### Erreur 6 : Backup incomplet (plugins/themes oubliés)
**Symptôme** : Site cassé, éléments manquants
**Fix** : TOUJOURS vérifier avec `tar tzf backup.tar.gz`

### Erreur 7 : Escaping incorrect dans wp-config.php
**Symptôme** : Erreur 500
**Fix** : Utiliser heredoc pour insérer code PHP proprement

### Erreur 8 : Ne pas tester le backup
**Symptôme** : Backup corrompu découvert trop tard
**Fix** : Tester extraction immédiatement après création

### Erreur 9 : Oublier `nginx -t && systemctl reload nginx`
**Symptôme** : Config modifiée mais site ne fonctionne pas
**Fix** : **TOUJOURS** tester et recharger Nginx

### Erreur 10 : Ne pas vérifier plugins/themes après restauration
**Symptôme** : Utilisateur signale éléments manquants
**Fix** : `ls /var/www/html/wp-content/plugins/` après restauration

---

## 🎓 10 Leçons apprises (migration Clémence)

1. **Backup complet non négociable** : "la dernière fois ça a été oublié" → frustration utilisateur
2. **Tester chaque étape** : Détecter problèmes tôt = debug facile
3. **Documenter les fixes** : Problèmes récurrents (301, permissions, DB_HOST)
4. **Ordre des fixes important** : DB_HOST → Proxy fix → URLs → Test
5. **Permissions critiques** : `user: "33:33"` + `FS_METHOD direct` = show-stopper si absent
6. **Named volumes > Bind mounts** : Docker gère permissions automatiquement
7. **Vérifier backup AVANT** : Découvrir fichiers manquants après = perte temps
8. **Communication claire** : Utilisateur frustré si migration incomplète
9. **Logs = amis** : `docker logs` révèle problèmes immédiatement
10. **Testing > Assumptions** : `nginx -t`, `curl -I`, `docker logs` après chaque changement

---

## 🔧 Commandes utiles supplémentaires

### Monitoring avancé
```bash
# Espace disque volumes
docker system df -v | grep sitename

# Taille base MySQL
docker exec mysql-sitename mysql -u root -p$MYSQL_ROOT_PASSWORD sitename_db -e \
  "SELECT table_schema AS 'Database', ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
   FROM information_schema.TABLES WHERE table_schema = 'sitename_db';"

# Santé MySQL
docker exec mysql-sitename mysqladmin -u root -p$MYSQL_ROOT_PASSWORD status
```

### Maintenance
```bash
# Optimiser MySQL
docker exec mysql-sitename mysqlcheck -u root -p$MYSQL_ROOT_PASSWORD --optimize sitename_db

# Nettoyer logs Docker
truncate -s 0 $(docker inspect --format='{{.LogPath}}' wordpress-sitename)

# Nettoyer images inutilisées
docker image prune -a
```

### Sécurité
```bash
# Audit secrets exposés
cat /opt/wordpress-sitename/docker-compose.yml | grep -i password
# Ne DOIT contenir QUE ${VAR}, jamais mots de passe en clair

# Permissions .env
ls -la /opt/wordpress-sitename/.env
# DOIT être 600 ou 644 (PAS 777)

# Users WordPress
docker exec mysql-sitename mysql -u root -p$MYSQL_ROOT_PASSWORD sitename_db -e \
  "SELECT user_login, user_email FROM wp_users;"
```

---

## 🛠️ Bonnes pratiques supplémentaires

### Performance
- ✅ Activer gzip dans Nginx conteneur
- ✅ Cache fichiers statiques (expires 365d)
- ✅ Utiliser Alpine Linux (images 5x plus légères)

### Sécurité
- ✅ `.env` dans `.gitignore`
- ✅ Mots de passe 20+ caractères
- ✅ Basic Auth Nginx host (double protection)
- ✅ `client_max_body_size` ≤ 100M

### Monitoring
- ✅ Alertes `docker stats` si CPU > 80%
- ✅ Surveiller logs erreurs Nginx
- ✅ Backups automatiques quotidiens

---

## 📊 Checklist de migration

Avant de basculer un site WordPress en production :

- [ ] Backup complet effectué (db + files)
- [ ] Backup testé (tar tzf, mysqldump valide)
- [ ] docker-compose.yml créé avec `user: "33:33"`
- [ ] nginx.conf créé avec `fastcgi_pass wordpress:9000`
- [ ] .env créé avec mots de passe sécurisés
- [ ] Stack déployée (`docker-compose up -d`)
- [ ] Tous les conteneurs UP (`docker ps`)
- [ ] Base de données restaurée
- [ ] Fichiers WordPress restaurés (plugins, themes, uploads)
- [ ] DB_HOST fixé (`mysql-clemence:3306`)
- [ ] Fix reverse proxy ajouté dans wp-config.php
- [ ] URLs fixées (siteurl et home en HTTPS)
- [ ] Nginx host configuré en reverse proxy
- [ ] `nginx -t` passé
- [ ] Nginx rechargé
- [ ] Test curl retourne HTTP 200
- [ ] CSS Elementor se charge
- [ ] Admin WordPress accessible
- [ ] Test upload fichier OK
- [ ] Test installation plugin OK
- [ ] Backup de l'ancienne installation gardé 7 jours

---

## 📚 Ressources

- **Docker Hub WordPress** : https://hub.docker.com/_/wordpress
- **Docker Hub MySQL** : https://hub.docker.com/_/mysql
- **WordPress Codex** : https://codex.wordpress.org/
- **Nginx FastCGI** : https://www.nginx.com/resources/wiki/start/topics/examples/phpfcgi/

---

## 🎯 Exemple réel : Site Clémence

Migration réussie le **2025-10-17** :

- **Ancien** : `/var/www/clemence/` (PHP 8.3-FPM natif + MySQL natif)
- **Nouveau** : `/opt/wordpress-clemence/` (Docker 3 conteneurs)
- **URL** : https://clemence.srv759970.hstgr.cloud
- **Plugins migrés** : Elementor, Header Footer Elementor, WP Mail SMTP, Akismet, WordPress Importer
- **Theme** : hello-elementor
- **Uploads** : 1.6MB (médias 2025 + assets Elementor)
- **Base** : 1.2MB (36MB total avec fichiers)
- **Temps migration** : ~45 minutes (avec debug)
- **Downtime** : 0 (basculement instantané Nginx)

**Commandes utiles** :
```bash
# Logs
docker logs wordpress-clemence --tail=50

# Redémarrer
cd /opt/wordpress-clemence && docker-compose restart

# Stats
docker stats --no-stream | grep clemence
```

---

**Créé le** : 2025-10-17
**Dernière mise à jour** : 2025-10-17
**Testé avec** : WordPress 6, PHP 8.3, MySQL 8.0, Docker 28.2.2
