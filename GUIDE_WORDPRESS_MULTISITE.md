# Guide d'installation WordPress Multisite sur VPS Hostinger

Ce guide vous accompagne dans l'installation et la configuration de WordPress en mode multisite sur votre VPS Hostinger.

## Prérequis

- VPS Hostinger avec accès SSH
- Nginx installé et configuré
- PHP 8.1+ installé avec les extensions nécessaires
- MySQL/MariaDB installé
- Nom de domaine configuré avec DNS pointant vers votre VPS

## 1. Installation des dépendances PHP pour WordPress

```bash
# Se connecter en SSH
ssh root@votre-ip-vps

# Installer PHP et les extensions requises
apt update
apt install -y php8.2-fpm php8.2-mysql php8.2-curl php8.2-gd php8.2-mbstring \
  php8.2-xml php8.2-xmlrpc php8.2-soap php8.2-intl php8.2-zip php8.2-imagick

# Vérifier l'installation
php -v
php -m | grep -E 'mysql|curl|gd|mbstring|xml'
```

## 2. Configuration de la base de données

### Créer la base de données et l'utilisateur

```bash
# Se connecter à MySQL
mysql -u root -p

# Dans MySQL, créer la base et l'utilisateur
CREATE DATABASE wordpress_multisite CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'wp_user'@'localhost' IDENTIFIED BY 'VotreMotDePasseSecurise';
GRANT ALL PRIVILEGES ON wordpress_multisite.* TO 'wp_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Optimisations MySQL pour WordPress

```bash
# Éditer la configuration MySQL
nano /etc/mysql/mysql.conf.d/mysqld.cnf

# Ajouter ces paramètres dans la section [mysqld]
[mysqld]
max_allowed_packet = 256M
innodb_buffer_pool_size = 512M
innodb_log_file_size = 128M
query_cache_type = 1
query_cache_size = 64M
query_cache_limit = 2M

# Redémarrer MySQL
systemctl restart mysql
```

## 3. Téléchargement et installation de WordPress

```bash
# Créer le répertoire pour WordPress
mkdir -p /var/www/wordpress
cd /var/www/wordpress

# Télécharger WordPress
wget https://wordpress.org/latest.tar.gz
tar -xzvf latest.tar.gz
mv wordpress/* .
rm -rf wordpress latest.tar.gz

# Configurer les permissions
chown -R www-data:www-data /var/www/wordpress
find /var/www/wordpress -type d -exec chmod 755 {} \;
find /var/www/wordpress -type f -exec chmod 644 {} \;
```

## 4. Configuration de wp-config.php

```bash
# Copier le fichier de configuration exemple
cp wp-config-sample.php wp-config.php

# Éditer wp-config.php
nano wp-config.php
```

Configurer les paramètres de base de données :

```php
<?php
// ** Réglages MySQL ** //
define('DB_NAME', 'wordpress_multisite');
define('DB_USER', 'wp_user');
define('DB_PASSWORD', 'VotreMotDePasseSecurise');
define('DB_HOST', 'localhost');
define('DB_CHARSET', 'utf8mb4');
define('DB_COLLATE', '');

// Clés de sécurité - À générer sur https://api.wordpress.org/secret-key/1.1/salt/
define('AUTH_KEY',         'votre-clé-unique');
define('SECURE_AUTH_KEY',  'votre-clé-unique');
define('LOGGED_IN_KEY',    'votre-clé-unique');
define('NONCE_KEY',        'votre-clé-unique');
define('AUTH_SALT',        'votre-clé-unique');
define('SECURE_AUTH_SALT', 'votre-clé-unique');
define('LOGGED_IN_SALT',   'votre-clé-unique');
define('NONCE_SALT',       'votre-clé-unique');

// Préfixe de tables
$table_prefix = 'wp_';

// Mode debug (désactiver en production)
define('WP_DEBUG', false);

// Optimisations
define('WP_MEMORY_LIMIT', '256M');
define('WP_MAX_MEMORY_LIMIT', '512M');
define('AUTOSAVE_INTERVAL', 300);
define('WP_POST_REVISIONS', 5);
define('EMPTY_TRASH_DAYS', 30);

/* C'est tout, ne touchez pas à ce qui suit ! Bonne publication. */
if ( !defined('ABSPATH') )
    define('ABSPATH', dirname(__FILE__) . '/');
require_once(ABSPATH . 'wp-settings.php');
```

## 5. Configuration Nginx pour WordPress

Créer un fichier de configuration Nginx :

```bash
nano /etc/nginx/sites-available/wordpress
```

Configuration Nginx optimisée pour WordPress :

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name votre-domaine.com www.votre-domaine.com;

    root /var/www/wordpress;
    index index.php index.html index.htm;

    # Logs
    access_log /var/log/nginx/wordpress-access.log;
    error_log /var/log/nginx/wordpress-error.log;

    # Sécurité - Cacher les fichiers sensibles
    location ~ /\. {
        deny all;
    }

    location ~ /wp-config.php {
        deny all;
    }

    # Limits des uploads
    client_max_body_size 100M;

    # WordPress Multisite - fichiers uploadés
    location ~ ^/files/(.*)$ {
        try_files /wp-content/blogs.dir/$blogid/$uri /wp-includes/ms-files.php?file=$1 ;
        access_log off;
        log_not_found off;
        expires max;
    }

    # WordPress
    location / {
        try_files $uri $uri/ /index.php?$args;
    }

    # PHP-FPM
    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php8.2-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;

        # Optimisations PHP
        fastcgi_buffer_size 128k;
        fastcgi_buffers 256 16k;
        fastcgi_busy_buffers_size 256k;
        fastcgi_temp_file_write_size 256k;
        fastcgi_read_timeout 300;
    }

    # Cache pour les fichiers statiques
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 365d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Sécurité supplémentaire
    location = /xmlrpc.php {
        deny all;
    }
}
```

Activer le site et redémarrer Nginx :

```bash
# Créer le lien symbolique
ln -s /etc/nginx/sites-available/wordpress /etc/nginx/sites-enabled/

# Tester la configuration
nginx -t

# Redémarrer Nginx
systemctl restart nginx
```

## 6. Installation initiale de WordPress

1. Accéder à votre domaine dans un navigateur : `http://votre-domaine.com`
2. Suivre l'assistant d'installation WordPress
3. Renseigner :
   - Titre du site
   - Nom d'utilisateur admin
   - Mot de passe fort
   - Email admin

## 7. Activation du mode Multisite

### Étape 1 : Modifier wp-config.php

```bash
nano /var/www/wordpress/wp-config.php
```

Ajouter AVANT la ligne `/* C'est tout, ne touchez pas à ce qui suit ! */` :

```php
/* Activation du multisite */
define('WP_ALLOW_MULTISITE', true);
```

### Étape 2 : Configurer le réseau multisite

1. Se connecter au tableau de bord WordPress
2. Aller dans **Outils > Configuration du réseau**
3. Choisir le type de multisite :
   - **Sous-domaines** : site1.domaine.com, site2.domaine.com
   - **Sous-répertoires** : domaine.com/site1, domaine.com/site2

### Étape 3 : Finaliser la configuration

WordPress vous donnera du code à ajouter dans `wp-config.php` et `.htaccess` (que nous allons adapter pour Nginx).

Exemple de code pour wp-config.php (à ajouter APRÈS `WP_ALLOW_MULTISITE`) :

```php
define('MULTISITE', true);
define('SUBDOMAIN_INSTALL', false); // true pour sous-domaines, false pour sous-répertoires
define('DOMAIN_CURRENT_SITE', 'votre-domaine.com');
define('PATH_CURRENT_SITE', '/');
define('SITE_ID_CURRENT_SITE', 1);
define('BLOG_ID_CURRENT_SITE', 1);
```

### Étape 4 : Configuration Nginx pour Multisite

#### Pour installation en sous-répertoires :

```nginx
# Dans le bloc server, remplacer la directive location /
location / {
    try_files $uri $uri/ /index.php?$args;
}

# Ajouter le support multisite
if (!-e $request_filename) {
    rewrite /wp-admin$ $scheme://$host$uri/ permanent;
    rewrite ^(/[^/]+)?(/wp-.*) $2 last;
    rewrite ^(/[^/]+)?(/.*\.php) $2 last;
}
```

#### Pour installation en sous-domaines :

Modifier la directive `server_name` :

```nginx
server_name votre-domaine.com *.votre-domaine.com;
```

Et configurer les wildcards DNS :

```bash
# Dans votre panneau DNS, ajouter un enregistrement A wildcard :
*.votre-domaine.com    A    votre-ip-vps
```

Redémarrer Nginx :

```bash
nginx -t
systemctl restart nginx
```

## 8. Configuration SSL avec Let's Encrypt (Recommandé)

```bash
# Installer Certbot
apt install -y certbot python3-certbot-nginx

# Obtenir un certificat SSL
certbot --nginx -d votre-domaine.com -d www.votre-domaine.com

# Pour multisite avec sous-domaines, utiliser wildcard
certbot certonly --manual --preferred-challenges=dns \
  -d votre-domaine.com -d *.votre-domaine.com

# Renouvellement automatique (déjà configuré par défaut)
certbot renew --dry-run
```

Après SSL, mettre à jour wp-config.php :

```php
// Forcer HTTPS
define('FORCE_SSL_ADMIN', true);
if (strpos($_SERVER['HTTP_X_FORWARDED_PROTO'], 'https') !== false)
    $_SERVER['HTTPS']='on';
```

## 9. Optimisations PHP-FPM pour WordPress

```bash
# Éditer la configuration PHP-FPM
nano /etc/php/8.2/fpm/pool.d/www.conf

# Modifier ces paramètres
pm = dynamic
pm.max_children = 50
pm.start_servers = 10
pm.min_spare_servers = 5
pm.max_spare_servers = 20
pm.max_requests = 500

# Éditer php.ini
nano /etc/php/8.2/fpm/php.ini

# Optimisations
memory_limit = 256M
upload_max_filesize = 100M
post_max_size = 100M
max_execution_time = 300
max_input_time = 300

# Redémarrer PHP-FPM
systemctl restart php8.2-fpm
```

## 10. Gestion des sites du réseau

### Ajouter un nouveau site

1. Aller dans **Mes sites > Administration du réseau > Sites**
2. Cliquer sur **Ajouter**
3. Renseigner :
   - Adresse du site (sous-domaine ou sous-répertoire)
   - Titre du site
   - Email de l'admin
4. Le site est créé instantanément

### Gestion des utilisateurs

- **Super Admin** : Accès à tous les sites et paramètres réseau
- **Administrateur de site** : Gestion d'un seul site
- Les utilisateurs peuvent être ajoutés à plusieurs sites avec différents rôles

### Plugins et thèmes

- Les plugins peuvent être **activés pour le réseau** (disponibles pour tous les sites)
- Ou activés individuellement par site
- Les thèmes doivent être **activés pour le réseau** avant d'être utilisables

## 11. Sauvegarde et maintenance

### Script de sauvegarde automatique

```bash
nano /root/backup-wordpress.sh
```

```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/root/backups/wordpress"
DATE=$(date +%Y%m%d_%H%M%S)
WP_DIR="/var/www/wordpress"
DB_NAME="wordpress_multisite"
DB_USER="wp_user"
DB_PASS="VotreMotDePasseSecurise"

# Créer le répertoire de sauvegarde
mkdir -p $BACKUP_DIR

# Sauvegarder les fichiers
tar -czf $BACKUP_DIR/wp-files-$DATE.tar.gz $WP_DIR

# Sauvegarder la base de données
mysqldump -u $DB_USER -p$DB_PASS $DB_NAME | gzip > $BACKUP_DIR/wp-db-$DATE.sql.gz

# Supprimer les sauvegardes de plus de 30 jours
find $BACKUP_DIR -name "wp-*" -mtime +30 -delete

echo "Sauvegarde terminée : $DATE"
```

```bash
# Rendre le script exécutable
chmod +x /root/backup-wordpress.sh

# Ajouter au cron pour exécution quotidienne à 2h
crontab -e
# Ajouter cette ligne :
0 2 * * * /root/backup-wordpress.sh >> /var/log/wordpress-backup.log 2>&1
```

## 12. Plugins recommandés pour multisite

- **WP Super Cache** ou **W3 Total Cache** : Cache et performance
- **Wordfence Security** : Sécurité et firewall
- **UpdraftPlus** : Sauvegardes automatiques
- **Multisite Enhancements** : Améliore l'interface multisite
- **WP Multisite Feed** : Agrégateur de contenu entre sites

## 13. Sécurité

### Protéger wp-login.php contre les attaques brute-force

```bash
nano /etc/nginx/sites-available/wordpress
```

Ajouter dans le bloc server :

```nginx
# Limiter les tentatives de connexion
location = /wp-login.php {
    limit_req zone=one burst=5 nodelay;
    include snippets/fastcgi-php.conf;
    fastcgi_pass unix:/run/php/php8.2-fpm.sock;
}
```

Dans la section http de `/etc/nginx/nginx.conf` :

```nginx
http {
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=one:10m rate=5r/m;

    # ...
}
```

### Désactiver l'éditeur de fichiers WordPress

Dans wp-config.php :

```php
define('DISALLOW_FILE_EDIT', true);
```

## 14. Monitoring et performance

### Installer des outils de monitoring

```bash
# Installer htop pour monitoring CPU/RAM
apt install -y htop

# Installer mytop pour monitoring MySQL
apt install -y mytop
```

### Activer les logs lents MySQL

```bash
nano /etc/mysql/mysql.conf.d/mysqld.cnf
```

```ini
[mysqld]
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow-queries.log
long_query_time = 2
```

## Résumé des commandes essentielles

```bash
# Redémarrer les services
systemctl restart nginx
systemctl restart php8.2-fpm
systemctl restart mysql

# Vérifier les statuts
systemctl status nginx
systemctl status php8.2-fpm
systemctl status mysql

# Logs
tail -f /var/log/nginx/wordpress-error.log
tail -f /var/log/php8.2-fpm.log

# Permissions WordPress
chown -R www-data:www-data /var/www/wordpress
find /var/www/wordpress -type d -exec chmod 755 {} \;
find /var/www/wordpress -type f -exec chmod 644 {} \;
```

## Dépannage

### Erreur "Error establishing database connection"

- Vérifier les credentials dans wp-config.php
- Vérifier que MySQL est démarré : `systemctl status mysql`
- Tester la connexion : `mysql -u wp_user -p wordpress_multisite`

### Erreur 502 Bad Gateway

- Vérifier PHP-FPM : `systemctl status php8.2-fpm`
- Vérifier les logs : `tail -f /var/log/nginx/error.log`
- Vérifier le socket PHP dans la config Nginx

### Problèmes de permissions

```bash
chown -R www-data:www-data /var/www/wordpress
chmod -R 755 /var/www/wordpress
```

## Ressources

- [Documentation officielle WordPress Multisite](https://wordpress.org/support/article/create-a-network/)
- [Nginx et WordPress](https://www.nginx.com/resources/wiki/start/topics/recipes/wordpress/)
- [Codex WordPress](https://codex.wordpress.org/)

---

**Note** : Remplacez toutes les valeurs `votre-domaine.com`, `votre-ip-vps`, et `VotreMotDePasseSecurise` par vos propres valeurs.
