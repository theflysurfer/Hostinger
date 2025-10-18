# 🔧 Guide de Troubleshooting Nginx - Problèmes et Solutions

> **Guide pratique pour diagnostiquer et corriger les problèmes Nginx courants sur VPS**

---

## 🎯 Objectif

Ce guide documente **tous les problèmes réels rencontrés** et leurs solutions pour éviter de les reproduire.

---

## ⚠️ Problème #1 : Redirections HTTPS automatiques empêchent Certbot

### Symptômes
- Certbot échoue avec `unauthorized` ou `404` sur `.well-known/acme-challenge`
- Le site redirige vers HTTPS alors qu'il n'a pas encore de certificat
- Erreur : `Invalid response from https://... 404`

### Cause
Un autre serveur block ou une configuration globale redirige **tout le trafic HTTP vers HTTPS** avant même que Certbot puisse valider le domaine.

### Diagnostic
```bash
# Tester si l'accès HTTP redirige
curl -I http://whisper.srv759970.hstgr.cloud/

# Si résultat : HTTP/1.1 301 → HTTPS, c'est le problème !
```

### Solution 1 : Utiliser le mode standalone
```bash
# Arrêter Nginx temporairement
systemctl stop nginx

# Obtenir le certificat en mode standalone
certbot certonly --standalone -d whisper.srv759970.hstgr.cloud --non-interactive --agree-tos --email admin@srv759970.hstgr.cloud

# Redémarrer Nginx
systemctl start nginx
```

### Solution 2 : Configurer le site après avoir le certificat
```nginx
# 1. Config initiale (SANS redirect HTTPS)
server {
    listen 80;
    server_name whisper.srv759970.hstgr.cloud;

    location / {
        proxy_pass http://localhost:8001;
    }
}

# 2. Obtenir le certificat
# certbot certonly --standalone ...

# 3. Ajouter le bloc HTTPS et la redirection
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

### Prévention
- **Ne jamais** ajouter de redirection HTTPS avant d'avoir le certificat
- Utiliser `certbot certonly --standalone` pour premier certificat
- Ensuite utiliser `certbot --nginx` pour renouvellements

---

## ⚠️ Problème #2 : Conflit SNI - Mauvais certificat SSL servi

### Symptômes
- `https://sharepoint.srv759970.hstgr.cloud/` affiche le certificat de `blog.cristina.srv759970.hstgr.cloud`
- Erreur SSL dans le navigateur : "Certificate mismatch"
- Le site affiche le contenu d'un autre site

### Cause
**SNI (Server Name Indication)** : Quand plusieurs sites HTTPS sont sur le même serveur, Nginx utilise le **premier bloc HTTPS** par défaut si SNI échoue ou si l'ordre est incorrect.

### Diagnostic
```bash
# Vérifier quel certificat est servi
openssl s_client -connect sharepoint.srv759970.hstgr.cloud:443 -servername sharepoint.srv759970.hstgr.cloud | openssl x509 -noout -subject

# Résultat attendu : subject=CN = sharepoint.srv759970.hstgr.cloud
# Résultat problème : subject=CN = blog.cristina.srv759970.hstgr.cloud
```

### Solution
**Ordre des blocs server dans Nginx** :
1. Les blocs HTTPS doivent avoir `listen 443 ssl http2;` **ET** `server_name` spécifique
2. Éviter les blocs catch-all `server_name _;` en HTTPS
3. S'assurer que chaque domaine a son propre certificat

```nginx
# ✅ BON : Certificat et server_name correspondent
server {
    listen 443 ssl http2;
    server_name sharepoint.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/sharepoint.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sharepoint.srv759970.hstgr.cloud/privkey.pem;
    # ...
}

# ❌ MAUVAIS : server_name _ en HTTPS
server {
    listen 443 ssl;
    server_name _;  # ← Intercepte TOUS les domaines !
}
```

### Vérifier l'ordre de chargement
```bash
# Voir l'ordre des configs
nginx -T | grep -E 'configuration file|server_name'

# S'assurer que chaque domaine HTTPS a son bloc dédié
```

---

## ⚠️ Problème #3 : Conteneur Docker avec Nginx interne affiche page par défaut

### Symptômes
- Le site affiche "Welcome to nginx!" au lieu du vrai contenu
- Le conteneur tourne correctement (`docker ps` montre UP)
- Logs du conteneur montrent des 200 OK mais mauvaise page

### Cause
**Double Nginx** : Le conteneur Docker a son propre Nginx interne avec une configuration qui sert `/usr/share/nginx/html/index.html` (page par défaut) au lieu du vrai contenu.

### Diagnostic
```bash
# Tester le conteneur directement
curl http://localhost:8502/

# Si résultat : "Welcome to nginx!", le problème est dans le conteneur

# Vérifier la structure dans le conteneur
docker exec sharepoint-dashboards ls -la /usr/share/nginx/html/

# Trouver où sont les vrais fichiers
docker exec sharepoint-dashboards find /usr/share/nginx/html -name "*.html" -type f
```

### Solution 1 : Redirection Nginx externe
Si les fichiers sont dans un sous-dossier (ex: `/html/`) :

```nginx
server {
    listen 443 ssl http2;
    server_name sharepoint.srv759970.hstgr.cloud;

    # Rediriger / vers /html/
    location = / {
        return 301 https://$host/html/;
    }

    location / {
        proxy_pass http://localhost:8502;
        # headers proxy...
    }
}
```

### Solution 2 : Reconstruire le conteneur
Modifier le Dockerfile pour copier les fichiers à la racine :

```dockerfile
# ❌ MAUVAIS
COPY html/ /usr/share/nginx/html/html/

# ✅ BON
COPY html/ /usr/share/nginx/html/
```

Puis reconstruire :
```bash
cd /opt/sharepoint-dashboards
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## ⚠️ Problème #4 : WordPress Multisite - Domaine incorrect dans la base de données

### Symptômes
- `wp site list` retourne une erreur "Site not found"
- WordPress affiche "Error establishing database connection" après conversion multisite
- L'URL du site principal est incorrecte

### Cause
La commande `wp core multisite-convert` utilise le `DOMAIN_CURRENT_SITE` du fichier wp-config.php, mais si celui-ci a été changé après l'installation initiale, la base de données contient encore l'ancien domaine.

### Diagnostic
```bash
# Vérifier le domaine dans wp-config.php
grep DOMAIN_CURRENT_SITE /var/www/wordpress/wp-config.php

# Vérifier le domaine dans la base de données
mysql -e "SELECT domain FROM wordpress_multisite.wp_site;"
mysql -e "SELECT blog_id, domain, path FROM wordpress_multisite.wp_blogs;"
```

### Solution : Search-Replace dans la base
```bash
cd /var/www/wordpress

# Remplacer l'ancien domaine par le nouveau dans toute la base
wp search-replace 'ancien-domaine.com' 'nouveau-domaine.com' --allow-root

# Vérifier que ça a fonctionné
wp site list --allow-root
```

### Alternative : Update SQL direct
```sql
-- Mettre à jour la table wp_site (réseau)
UPDATE wordpress_multisite.wp_site
SET domain = 'blog.cristina.srv759970.hstgr.cloud'
WHERE id = 1;

-- Mettre à jour la table wp_blogs (sites)
UPDATE wordpress_multisite.wp_blogs
SET domain = 'blog.cristina.srv759970.hstgr.cloud'
WHERE blog_id = 1;

-- Vérifier
SELECT * FROM wordpress_multisite.wp_site;
SELECT * FROM wordpress_multisite.wp_blogs;
```

---

## ⚠️ Problème #5 : HTTP 404 sur tous les sous-domaines

### Symptômes
- Tous les nouveaux sous-domaines retournent 404
- Dashboard, Whisper, etc. ne fonctionnent pas
- Nginx répond mais avec 404

### Cause
Les blocs server HTTP (port 80) configurés par Certbot font `return 404;` au lieu de rediriger correctement vers HTTPS.

### Exemple de mauvaise config (générée par Certbot)
```nginx
server {
    if ($host = cristina.srv759970.hstgr.cloud) {
        return 301 https://$host$request_uri;
    }

    listen 80;
    server_name cristina.srv759970.hstgr.cloud;
    return 404; # ← PROBLÈME : si le if() ne match pas, retourne 404
}
```

### Solution : Config propre HTTP → HTTPS
```nginx
# ✅ BON : Redirection simple et claire
server {
    listen 80;
    listen [::]:80;
    server_name cristina.srv759970.hstgr.cloud;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name cristina.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/cristina.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cristina.srv759970.hstgr.cloud/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Configuration du site...
}
```

### Correction en masse
```bash
# Lister tous les sites avec return 404
nginx -T | grep -B 5 "return 404"

# Pour chaque site, remplacer la config par le template propre ci-dessus
```

---

## 📋 Checklist de déploiement d'un nouveau site

### Étape 1 : Préparer la configuration Nginx (HTTP seulement)
```nginx
server {
    listen 80;
    listen [::]:80;
    server_name nouveau-site.srv759970.hstgr.cloud;

    # Pas de redirect HTTPS encore !

    location / {
        proxy_pass http://localhost:PORT;
        # ou root /opt/nouveau-site;
    }
}
```

### Étape 2 : Tester et activer
```bash
# Créer le fichier
nano /etc/nginx/sites-available/nouveau-site

# Activer
ln -s /etc/nginx/sites-available/nouveau-site /etc/nginx/sites-enabled/

# Tester
nginx -t

# Recharger
systemctl reload nginx

# Vérifier
curl -I http://nouveau-site.srv759970.hstgr.cloud/
```

### Étape 3 : Obtenir le certificat SSL
```bash
# Méthode 1 : Standalone (si config HTTP simple)
systemctl stop nginx
certbot certonly --standalone -d nouveau-site.srv759970.hstgr.cloud --email admin@srv759970.hstgr.cloud --agree-tos --non-interactive
systemctl start nginx

# Méthode 2 : Webroot (si site statique)
certbot certonly --webroot -w /opt/nouveau-site -d nouveau-site.srv759970.hstgr.cloud
```

### Étape 4 : Ajouter HTTPS et redirection
```nginx
# Bloc HTTPS
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name nouveau-site.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/nouveau-site.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/nouveau-site.srv759970.hstgr.cloud/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Configuration identique au bloc HTTP
    location / {
        proxy_pass http://localhost:PORT;
    }
}

# Bloc HTTP avec redirection
server {
    listen 80;
    listen [::]:80;
    server_name nouveau-site.srv759970.hstgr.cloud;
    return 301 https://$host$request_uri;
}
```

### Étape 5 : Tester et recharger
```bash
nginx -t && systemctl reload nginx

# Tester HTTPS
curl -skI https://nouveau-site.srv759970.hstgr.cloud/

# Tester redirection HTTP → HTTPS
curl -I http://nouveau-site.srv759970.hstgr.cloud/
```

---

## 🛠️ Commandes de diagnostic rapide

### Vérifier quel site répond
```bash
# Tester avec Host header
curl -I -H 'Host: mon-site.srv759970.hstgr.cloud' http://localhost/

# Voir quel server block Nginx utilise
nginx -T | grep -B 10 'server_name mon-site.srv759970.hstgr.cloud'
```

### Vérifier les certificats SSL
```bash
# Voir quel certificat est servi
openssl s_client -connect mon-site.srv759970.hstgr.cloud:443 -servername mon-site.srv759970.hstgr.cloud | openssl x509 -noout -subject -issuer

# Lister tous les certificats installés
ls -la /etc/letsencrypt/live/
```

### Vérifier les redirections
```bash
# Suivre les redirections HTTP
curl -L -I http://mon-site.srv759970.hstgr.cloud/

# Voir les headers de réponse
curl -v http://mon-site.srv759970.hstgr.cloud/
```

### Lister tous les sites et leurs ports
```bash
# Voir tous les server_name
nginx -T | grep 'server_name' | grep -v '#' | sort | uniq

# Voir tous les proxy_pass (ports backend)
nginx -T | grep 'proxy_pass' | sort | uniq

# Voir tous les listen
nginx -T | grep 'listen' | grep -v '#' | sort | uniq
```

---

## 📊 Templates corrects par cas d'usage

### Template : Site statique avec HTTPS
```nginx
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name mon-site.srv759970.hstgr.cloud;

    root /opt/mon-site;
    index index.html;

    ssl_certificate /etc/letsencrypt/live/mon-site.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mon-site.srv759970.hstgr.cloud/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        try_files $uri $uri.html $uri/ $uri/index.html =404;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

server {
    listen 80;
    listen [::]:80;
    server_name mon-site.srv759970.hstgr.cloud;
    return 301 https://$host$request_uri;
}
```

### Template : Reverse proxy Docker avec HTTPS
```nginx
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name mon-app.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/mon-app.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mon-app.srv759970.hstgr.cloud/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        proxy_pass http://localhost:8502;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}

server {
    listen 80;
    listen [::]:80;
    server_name mon-app.srv759970.hstgr.cloud;
    return 301 https://$host$request_uri;
}
```

---

## 🔍 Logs et debugging

### Activer les logs de debug Nginx
```nginx
error_log /var/log/nginx/error.log debug;
```

### Suivre les logs en temps réel
```bash
# Logs combinés
tail -f /var/log/nginx/access.log /var/log/nginx/error.log

# Filtrer par domaine
tail -f /var/log/nginx/access.log | grep 'mon-site.srv759970.hstgr.cloud'
```

### Voir les requêtes qui arrivent
```bash
# Activer tcpdump sur port 80/443
tcpdump -i any port 80 -A

# Logs Nginx en temps réel avec curl
tail -f /var/log/nginx/access.log &
curl http://mon-site.srv759970.hstgr.cloud/
```

---

**Dernière mise à jour** : Octobre 2025
**Basé sur** : Problèmes réels rencontrés lors du déploiement de 7 sites sur le VPS
