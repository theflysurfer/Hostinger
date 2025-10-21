# Nginx - Guide de Dépannage

Solutions aux problèmes Nginx réels rencontrés sur srv759970.hstgr.cloud.

---

## Vue d'ensemble

Ce guide couvre les problèmes réels rencontrés lors du déploiement de services sur srv759970. Pour la configuration de base, voir [infrastructure/nginx.md](../infrastructure/nginx.md).

**Contenu :**
- Solutions à 5 problèmes critiques rencontrés en production
- Checklist de déploiement condensée
- Commandes de diagnostic rapide

**Guides complémentaires :**
- [Configuration Reference](../reference/nginx/configuration.md) - Templates complets
- [Nginx Debugging](../reference/nginx/debugging.md) - Commandes de diagnostic avancées
- [Certbot SSL](../reference/security/certbot-ssl.md) - Gestion des certificats

---

## Problèmes Courants

### Problème #1 : Les Redirections HTTPS Bloquent Certbot

#### Symptômes
- Certbot échoue avec `unauthorized` ou `404` sur `.well-known/acme-challenge`
- Le site redirige vers HTTPS alors qu'il n'a pas encore de certificat
- Erreur : `Invalid response from https://... 404`

#### Cause
Un autre serveur block ou une configuration globale redirige **tout le trafic HTTP vers HTTPS** avant même que Certbot puisse valider le domaine.

#### Diagnostic
```bash
# Tester si l'accès HTTP redirige
curl -I http://whisper.srv759970.hstgr.cloud/

# Si résultat : HTTP/1.1 301 → HTTPS, c'est le problème !
```

#### Solution 1 : Utiliser le mode standalone
```bash
# Arrêter Nginx temporairement
systemctl stop nginx

# Obtenir le certificat en mode standalone
certbot certonly --standalone -d whisper.srv759970.hstgr.cloud --non-interactive --agree-tos --email admin@srv759970.hstgr.cloud

# Redémarrer Nginx
systemctl start nginx
```

#### Solution 2 : Configurer le site après avoir le certificat
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

#### Prévention
- **Ne jamais** ajouter de redirection HTTPS avant d'avoir le certificat
- Utiliser `certbot certonly --standalone` pour premier certificat
- Ensuite utiliser `certbot --nginx` pour renouvellements

**Voir aussi :** [Certbot SSL Reference](../reference/security/certbot-ssl.md) pour toutes les méthodes de validation et résolution de problèmes avancés.

---

### Problème #2 : Erreur SNI "Certificate Doesn't Match"

#### Symptômes
- `https://sharepoint.srv759970.hstgr.cloud/` affiche le certificat de `blog.cristina.srv759970.hstgr.cloud`
- Erreur SSL dans le navigateur : "Certificate mismatch"
- Le site affiche le contenu d'un autre site

#### Cause
**SNI (Server Name Indication)** : Quand plusieurs sites HTTPS sont sur le même serveur, Nginx utilise le **premier bloc HTTPS** par défaut si SNI échoue ou si l'ordre est incorrect.

#### Diagnostic
```bash
# Vérifier quel certificat est servi
openssl s_client -connect sharepoint.srv759970.hstgr.cloud:443 -servername sharepoint.srv759970.hstgr.cloud | openssl x509 -noout -subject

# Résultat attendu : subject=CN = sharepoint.srv759970.hstgr.cloud
# Résultat problème : subject=CN = blog.cristina.srv759970.hstgr.cloud
```

#### Solution
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

#### Vérifier l'ordre de chargement
```bash
# Voir l'ordre des configs
nginx -T | grep -E 'configuration file|server_name'

# S'assurer que chaque domaine HTTPS a son bloc dédié
```

---

### Problème #3 : Docker Nginx Sert la Page Par Défaut

#### Symptômes
- Le site affiche "Welcome to nginx!" au lieu du vrai contenu
- Le conteneur tourne correctement (`docker ps` montre UP)
- Logs du conteneur montrent des 200 OK mais mauvaise page

#### Cause
**Double Nginx** : Le conteneur Docker a son propre Nginx interne avec une configuration qui sert `/usr/share/nginx/html/index.html` (page par défaut) au lieu du vrai contenu.

#### Diagnostic
```bash
# Tester le conteneur directement
curl http://localhost:8502/

# Si résultat : "Welcome to nginx!", le problème est dans le conteneur

# Vérifier la structure dans le conteneur
docker exec sharepoint-dashboards ls -la /usr/share/nginx/html/

# Trouver où sont les vrais fichiers
docker exec sharepoint-dashboards find /usr/share/nginx/html -name "*.html" -type f
```

#### Solution 1 : Redirection Nginx externe
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

#### Solution 2 : Reconstruire le conteneur
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

### Problème #4 : HTTP 404 sur Tous les Sous-domaines

#### Symptômes
- Tous les nouveaux sous-domaines retournent 404
- Dashboard, Whisper, etc. ne fonctionnent pas
- Nginx répond mais avec 404

#### Cause
Les blocs server HTTP (port 80) configurés par Certbot font `return 404;` au lieu de rediriger correctement vers HTTPS.

#### Exemple de mauvaise config (générée par Certbot)
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

#### Solution : Config propre HTTP → HTTPS
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

#### Correction en masse
```bash
# Lister tous les sites avec return 404
nginx -T | grep -B 5 "return 404"

# Pour chaque site, remplacer la config par le template propre ci-dessus
```

---

## Checklist de Déploiement

### Étape 1 : Configuration Nginx HTTP seulement
```nginx
server {
    listen 80;
    listen [::]:80;
    server_name nouveau-site.srv759970.hstgr.cloud;

    location / {
        proxy_pass http://localhost:PORT;
        # ou root /opt/nouveau-site;
    }
}
```

### Étape 2 : Activer et tester
```bash
# Créer et activer
nano /etc/nginx/sites-available/nouveau-site
ln -s /etc/nginx/sites-available/nouveau-site /etc/nginx/sites-enabled/

# Tester et recharger
nginx -t && systemctl reload nginx

# Vérifier
curl -I http://nouveau-site.srv759970.hstgr.cloud/
```

### Étape 3 : Obtenir le certificat SSL
```bash
# Méthode standalone (recommandée pour première installation)
systemctl stop nginx
certbot certonly --standalone -d nouveau-site.srv759970.hstgr.cloud --email admin@srv759970.hstgr.cloud --agree-tos --non-interactive
systemctl start nginx
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

**Voir aussi :** [Configuration Reference](../reference/nginx/configuration.md) pour templates complets par cas d'usage.

---

## Diagnostic Rapide

Pour les commandes de diagnostic complètes, voir :
- [Nginx Debugging Reference](../reference/nginx/debugging.md)
- [Common Commands](../reference/docker/common-commands.md)

### Vérifications rapides essentielles

```bash
# Vérifier quelle config répond
curl -I -H "Host: example.srv759970.hstgr.cloud" http://localhost/

# Tester le SSL
openssl s_client -connect example.srv759970.hstgr.cloud:443 -servername example.srv759970.hstgr.cloud | openssl x509 -noout -subject

# Voir tous les server_name configurés
nginx -T | grep 'server_name' | grep -v '#' | sort | uniq

# Tester les redirections
curl -L -I http://example.srv759970.hstgr.cloud/

# Logs en temps réel
tail -f /var/log/nginx/access.log /var/log/nginx/error.log
```

---

## Voir Aussi

- [Infrastructure Nginx](../infrastructure/nginx.md) - Configuration de base et architecture
- [Configuration Reference](../reference/nginx/configuration.md) - Templates complets
- [Nginx Debugging](../reference/nginx/debugging.md) - Commandes de diagnostic avancées
- [Certbot SSL](../reference/security/certbot-ssl.md) - Gestion des certificats SSL
- [Docker Common Commands](../reference/docker/common-commands.md) - Diagnostic conteneurs

---

**Dernière mise à jour** : Octobre 2025
**Basé sur** : Problèmes réels rencontrés lors du déploiement de 7 sites sur le VPS
