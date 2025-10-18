# 🌐 Guide Nginx - VPS Hostinger

> **Guide complet de configuration Nginx pour héberger plusieurs sites et applications sur un seul VPS**

---

## 📋 Informations VPS

**IP** : `69.62.108.82`
**Hostname** : `srv759970.hstgr.cloud`
**OS** : Ubuntu 24.04.2 LTS
**Nginx** : 1.24.0 (Ubuntu)

---

## 🎯 Cas d'usage

Ce guide couvre :
- ✅ Hébergement de **plusieurs sites statiques** (HTML, Astro, React build)
- ✅ **Reverse proxy** vers applications (Docker, services systemd)
- ✅ **Sous-domaines multiples** sur un seul VPS
- ✅ Gestion des **conflits entre sites**
- ✅ **Optimisations performance** (cache, compression)

---

## 📁 Structure Nginx sur Ubuntu

```
/etc/nginx/
├── nginx.conf                  # Configuration globale
├── sites-available/            # Configurations de sites (tous)
│   ├── cristina                # Site 1
│   ├── dashboard               # Site 2
│   └── mon-app                 # Site 3
├── sites-enabled/              # Symlinks vers sites actifs
│   ├── cristina -> ../sites-available/cristina
│   ├── dashboard -> ../sites-available/dashboard
│   └── mon-app -> ../sites-available/mon-app
└── snippets/                   # Configurations réutilisables
    └── ssl-params.conf

/var/log/nginx/
├── access.log                  # Logs d'accès global
├── error.log                   # Logs d'erreurs global
├── cristina-access.log         # Logs spécifiques par site
└── cristina-error.log
```

---

## 🚀 Workflow de création d'un nouveau site

### Étape 1 : Créer la configuration

```bash
ssh root@69.62.108.82 "cat > /etc/nginx/sites-available/mon-site" <<'EOF'
server {
    listen 80;
    server_name mon-site.srv759970.hstgr.cloud;

    # Configuration ici (voir templates ci-dessous)
}
EOF
```

### Étape 2 : Activer le site

```bash
ssh root@69.62.108.82 "ln -s /etc/nginx/sites-available/mon-site /etc/nginx/sites-enabled/"
```

### Étape 3 : Tester et recharger

```bash
# Tester la syntaxe
ssh root@69.62.108.82 "nginx -t"

# Si OK, recharger Nginx
ssh root@69.62.108.82 "systemctl reload nginx"
```

### Étape 4 : Vérifier

```bash
# Tester l'accès
ssh root@69.62.108.82 "curl -I -H 'Host: mon-site.srv759970.hstgr.cloud' http://localhost/"
```

---

## 📚 Templates de configuration

### Template 1 : Site statique (HTML/CSS/JS)

**Cas d'usage** : Site HTML, build Astro/React/Vue

```nginx
server {
    listen 80;
    server_name mon-site.srv759970.hstgr.cloud;

    root /opt/mon-site;
    index index.html;

    # Logs spécifiques
    access_log /var/log/nginx/mon-site-access.log;
    error_log /var/log/nginx/mon-site-error.log;

    # Servir fichiers et répertoires
    location / {
        # Pour build Astro/React : essaie fichier, puis .html, puis dir/, puis dir/index.html
        try_files $uri $uri.html $uri/ $uri/index.html =404;
    }

    # Cache assets statiques
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

### Template 2 : Reverse proxy vers Docker

**Cas d'usage** : Streamlit, FastAPI, Strapi, Node.js en Docker

```nginx
server {
    listen 80;
    server_name mon-app.srv759970.hstgr.cloud;

    # Logs
    access_log /var/log/nginx/mon-app-access.log;
    error_log /var/log/nginx/mon-app-error.log;

    location / {
        # Port Docker de l'application (ex: 8502, 1337, 3000)
        proxy_pass http://localhost:8502;

        proxy_http_version 1.1;

        # Headers essentiels
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (Streamlit, Strapi admin)
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeout pour long polling
        proxy_read_timeout 86400;
    }
}
```

### Template 3 : Reverse proxy vers service systemd

**Cas d'usage** : Ollama, PostgreSQL, API locale

```nginx
server {
    listen 80;
    server_name ollama.srv759970.hstgr.cloud;

    location / {
        # Port du service systemd
        proxy_pass http://localhost:11434;

        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # CORS si API publique
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;

        # Timeouts pour requêtes longues (LLM)
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;

        # Pas de buffering (streaming)
        proxy_buffering off;
        proxy_cache off;
    }
}
```

### Template 4 : Plusieurs applications sur un domaine (sous-chemins)

**Cas d'usage** : `site.com/app1`, `site.com/app2`

```nginx
server {
    listen 80;
    server_name srv759970.hstgr.cloud;

    # App 1 : /dashboard -> Streamlit
    location /dashboard {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # App 2 : /api -> FastAPI
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Site principal : / -> Static files
    location / {
        root /opt/site-principal;
        index index.html;
        try_files $uri $uri/ /index.html =404;
    }
}
```

### Template 5 : Site principal + Admin sur sous-domaine

**Cas d'usage** : Frontend + Backend CMS (Strapi, Ghost, WordPress)

```nginx
# Frontend
server {
    listen 80;
    server_name mon-site.srv759970.hstgr.cloud;

    root /opt/mon-site;
    index index.html;

    location / {
        try_files $uri $uri.html $uri/ $uri/index.html =404;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# Backend admin
server {
    listen 80;
    server_name admin.mon-site.srv759970.hstgr.cloud;

    location / {
        proxy_pass http://localhost:1337;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

---

## ⚠️ Problèmes courants et solutions

### Problème 1 : 404 sur toutes les pages (ou certaines)

**Symptômes** :
- Homepage fonctionne mais `/page1`, `/page2` retournent 404
- Nginx logs montrent `404 Not Found`

**Causes possibles** :
1. `try_files` mal configuré
2. Conflit avec autre site (`server_name _`)
3. Fichiers manquants

**Diagnostic** :
```bash
# Vérifier que les fichiers existent
ssh root@69.62.108.82 "ls -la /opt/mon-site/"

# Tester directement avec curl
ssh root@69.62.108.82 "curl -I -H 'Host: mon-site.srv759970.hstgr.cloud' http://localhost/page1"

# Voir quel server block répond
ssh root@69.62.108.82 "nginx -T | grep -A 10 'server_name mon-site'"
```

**Solution** :

Pour builds Astro/React/Next.js :
```nginx
location / {
    # Ordre important !
    try_files $uri $uri.html $uri/ $uri/index.html =404;
}
```

Pour SPA (Single Page App) :
```nginx
location / {
    # Toujours servir index.html (client-side routing)
    try_files $uri /index.html;
}
```

### Problème 2 : Conflit entre sites (mauvais site affiché)

**Symptômes** :
- Accès à `site-a.com` affiche `site-b.com`
- Logs montrent que la requête va au mauvais server block

**Cause** : Un site utilise `server_name _` (catch-all)

**Diagnostic** :
```bash
# Trouver qui utilise server_name _
ssh root@69.62.108.82 "nginx -T | grep 'server_name _'"

# Lister tous les server_name
ssh root@69.62.108.82 "nginx -T | grep 'server_name' | sort | uniq"
```

**Solution** :
```nginx
# ❌ NE PAS FAIRE (sauf pour site par défaut)
server {
    server_name _;
}

# ✅ FAIRE : Utiliser des noms spécifiques
server {
    server_name mon-site.srv759970.hstgr.cloud autre-domaine.com;
}
```

### Problème 3 : 502 Bad Gateway

**Symptômes** :
- Nginx répond mais dit "502 Bad Gateway"
- Application backend inaccessible

**Causes** :
1. Application backend n'est pas démarrée
2. Port incorrect dans `proxy_pass`
3. Firewall bloque le port

**Diagnostic** :
```bash
# Vérifier que l'app tourne
ssh root@69.62.108.82 "docker ps | grep mon-app"  # Si Docker
ssh root@69.62.108.82 "systemctl status mon-service"  # Si systemd

# Tester l'app directement (sans Nginx)
ssh root@69.62.108.82 "curl -I http://localhost:8502"

# Vérifier les logs Nginx
ssh root@69.62.108.82 "tail -20 /var/log/nginx/error.log"
```

**Solution** :
```bash
# Démarrer l'application
ssh root@69.62.108.82 "docker start mon-app"  # Docker
ssh root@69.62.108.82 "systemctl start mon-service"  # Systemd

# Vérifier que le port dans nginx.conf correspond
# proxy_pass http://localhost:8502;  <- Doit matcher le port de l'app
```

### Problème 4 : 500 Internal Server Error (rewrite loop)

**Symptômes** :
- Erreur 500
- Logs Nginx : `rewrite or internal redirection cycle`

**Cause** : Boucle de redirection dans `try_files` + `error_page`

**Mauvaise config** :
```nginx
location / {
    try_files $uri $uri/ /index.html;
    error_page 404 /index.html;  # ← BOUCLE !
}
```

**Bonne config** :
```nginx
location / {
    try_files $uri $uri/ /index.html =404;  # Pas de error_page
}
```

### Problème 5 : WebSocket ne fonctionne pas (Streamlit, Strapi admin)

**Symptômes** :
- Page charge mais fonctionnalités temps réel cassées
- Console navigateur : `WebSocket connection failed`

**Solution** : Ajouter headers WebSocket

```nginx
location / {
    proxy_pass http://localhost:8501;
    proxy_http_version 1.1;  # Important !

    # Headers WebSocket obligatoires
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    # Autres headers
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

    # Timeout long pour connexions persistantes
    proxy_read_timeout 86400;
}
```

---

## 🔍 Commandes de diagnostic

### Tester la configuration Nginx

```bash
# Syntaxe complète
ssh root@69.62.108.82 "nginx -t"

# Voir configuration compilée (tous les sites)
ssh root@69.62.108.82 "nginx -T"

# Voir config d'un site spécifique
ssh root@69.62.108.82 "nginx -T | grep -A 50 'server_name mon-site.srv759970.hstgr.cloud'"
```

### Lister les sites actifs

```bash
# Sites disponibles
ssh root@69.62.108.82 "ls -la /etc/nginx/sites-available/"

# Sites activés (symlinks)
ssh root@69.62.108.82 "ls -la /etc/nginx/sites-enabled/"
```

### Tester un site sans DNS

```bash
# Avec header Host
ssh root@69.62.108.82 "curl -I -H 'Host: mon-site.srv759970.hstgr.cloud' http://localhost/"

# Depuis votre PC (ajoutez dans C:\Windows\System32\drivers\etc\hosts)
# 69.62.108.82 mon-site.srv759970.hstgr.cloud
# Puis ouvrir http://mon-site.srv759970.hstgr.cloud
```

### Voir les logs en temps réel

```bash
# Tous les sites
ssh root@69.62.108.82 "tail -f /var/log/nginx/access.log"
ssh root@69.62.108.82 "tail -f /var/log/nginx/error.log"

# Site spécifique
ssh root@69.62.108.82 "tail -f /var/log/nginx/mon-site-access.log"
```

### Redémarrer Nginx

```bash
# Reload (sans interruption)
ssh root@69.62.108.82 "systemctl reload nginx"

# Restart (interruption courte)
ssh root@69.62.108.82 "systemctl restart nginx"

# Status
ssh root@69.62.108.82 "systemctl status nginx"
```

---

## 🎯 Bonnes pratiques

### 1. Toujours utiliser `server_name` spécifiques

```nginx
# ✅ BON
server {
    server_name mon-site.srv759970.hstgr.cloud www.mon-site.com;
}

# ❌ MAUVAIS (crée des conflits)
server {
    server_name _;  # Catch-all
}
```

### 2. Un fichier = Un site (ou groupe logique)

```
sites-available/
├── cristina              # Site Cristina (frontend + admin)
├── dashboard             # Dashboard support
└── ollama-api            # API Ollama
```

### 3. Logs séparés par site

```nginx
server {
    access_log /var/log/nginx/mon-site-access.log;
    error_log /var/log/nginx/mon-site-error.log;
}
```

### 4. Tester avant de reload

```bash
# TOUJOURS faire nginx -t avant reload
ssh root@69.62.108.82 "nginx -t && systemctl reload nginx"
```

### 5. Commenter vos configs

```nginx
server {
    listen 80;
    server_name mon-site.srv759970.hstgr.cloud;

    # Logs spécifiques pour ce site
    access_log /var/log/nginx/mon-site-access.log;

    # Reverse proxy vers Docker container (port 8502)
    location / {
        proxy_pass http://localhost:8502;
        # ...
    }
}
```

---

## 📊 Cas réels déployés

### Site 1 : Dashboard Support (Streamlit)

```nginx
server {
    listen 80;
    server_name dashboard.srv759970.hstgr.cloud srv759970.hstgr.cloud;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

**Déploiement** : Docker (port 8501)
**Type** : Reverse proxy WebSocket

### Site 2 : Cristina (Astro static + Strapi admin)

```nginx
# Frontend
server {
    listen 80;
    server_name cristina.srv759970.hstgr.cloud;
    root /opt/cristina-site;
    index index.html;

    location / {
        try_files $uri $uri.html $uri/ $uri/index.html =404;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# Backend admin
server {
    listen 80;
    server_name admin.cristina.srv759970.hstgr.cloud;

    location / {
        proxy_pass http://localhost:1337;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

**Déploiement** : Static files + Docker Strapi
**Type** : Hybride (static + reverse proxy)

### Site 3 : Ollama API

```nginx
server {
    listen 0.0.0.0:11435;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:11434;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # CORS pour API publique
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;

        # Timeouts longs pour LLM
        proxy_read_timeout 300s;

        # Pas de buffering (streaming)
        proxy_buffering off;
        proxy_cache off;
    }
}
```

**Déploiement** : Service systemd
**Type** : API publique avec CORS

---

## 🔐 Sécurité

### TODO : SSL/TLS avec Let's Encrypt

```bash
# Installer Certbot
ssh root@69.62.108.82 "apt install -y certbot python3-certbot-nginx"

# Obtenir certificat
ssh root@69.62.108.82 "certbot --nginx -d mon-site.srv759970.hstgr.cloud"

# Auto-renouvellement
ssh root@69.62.108.82 "certbot renew --dry-run"
```

### Limiter les requêtes (rate limiting)

```nginx
# Dans http {} (nginx.conf)
limit_req_zone $binary_remote_addr zone=mylimit:10m rate=10r/s;

# Dans server {}
server {
    location / {
        limit_req zone=mylimit burst=20;
        # ...
    }
}
```

---

## 📚 Ressources

- [Nginx Documentation](https://nginx.org/en/docs/)
- [Nginx Pitfalls](https://www.nginx.com/resources/wiki/start/topics/tutorials/config_pitfalls/)
- [Guide VPS Deployment](./GUIDE_DEPLOIEMENT_VPS.md)
- [Guide Services Systemd](./GUIDE_SERVICES_SYSTEMD.md)

---

**Dernière mise à jour** : Octobre 2025
**Version** : 1.0
**Sites déployés** : 3 (Dashboard, Cristina, Ollama)
