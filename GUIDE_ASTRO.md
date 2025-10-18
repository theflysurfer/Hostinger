# 🚀 Guide Astro - Déploiement sur VPS

> **Guide complet pour déployer des sites Astro sur VPS Hostinger avec Nginx**

---

## 📋 Vue d'ensemble

**Astro** : Framework SSG (Static Site Generator) qui génère du HTML/CSS/JS pur
**Avantage** : Sites ultra-rapides, zéro JavaScript côté client par défaut
**Déploiement** : Fichiers statiques servis par Nginx (pas de Node.js nécessaire en prod)

---

## 🏗️ Architecture de déploiement

```
Développement local (Windows)
│
├── pnpm dev          # Serveur de développement (port 4321)
└── pnpm build        # Génère le dossier dist/
    │
    └── dist/         # Fichiers statiques optimisés
        ├── index.html
        ├── about/index.html
        ├── contact/index.html
        └── _astro/   # Assets (CSS, JS, fonts)

↓ Transfer (scp)

VPS Hostinger (69.62.108.82)
│
└── /opt/mon-site/    # Contenu de dist/
    │
    └── Nginx (port 80/443)
        └── Servir fichiers statiques
```

**Résultat** : Site ultra-rapide, pas de serveur Node.js nécessaire

---

## 🚀 Workflow de déploiement

### Étape 1 : Build local

```bash
cd "C:\Users\JulienFernandez\OneDrive\Coding\_Projets de code\[PROJET]"

# Build pour production
pnpm build
# Ou : npm run build

# Vérifier le dossier dist/ créé
ls dist/
```

**Résultat** : Dossier `dist/` avec tous les fichiers optimisés

### Étape 2 : Créer la structure sur VPS

```bash
# Créer le dossier destination
ssh root@69.62.108.82 "mkdir -p /opt/mon-site"
```

### Étape 3 : Transférer les fichiers

```bash
# Depuis le dossier du projet local
cd "C:\Users\JulienFernandez\OneDrive\Coding\_Projets de code\[PROJET]"

# Transférer le contenu de dist/
scp -r dist/* root@69.62.108.82:/opt/mon-site/

# Alternative : rsync (plus rapide pour mise à jour)
# rsync -avz --delete dist/ root@69.62.108.82:/opt/mon-site/
```

### Étape 4 : Configurer Nginx

**Créer le fichier de configuration** :

```bash
ssh root@69.62.108.82 "cat > /etc/nginx/sites-available/mon-site" <<'EOF'
server {
    listen 80;
    server_name mon-site.srv759970.hstgr.cloud;

    root /opt/mon-site;
    index index.html;

    # Logs
    access_log /var/log/nginx/mon-site-access.log;
    error_log /var/log/nginx/mon-site-error.log;

    # Servir fichiers Astro
    location / {
        # Ordre important pour Astro !
        # 1. Fichier exact
        # 2. Fichier avec .html
        # 3. Répertoire avec trailing slash
        # 4. Répertoire/index.html
        # 5. 404
        try_files $uri $uri.html $uri/ $uri/index.html =404;
    }

    # Cache assets statiques (CSS, JS, images, fonts)
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript image/svg+xml;
    gzip_comp_level 6;
}
EOF
```

### Étape 5 : Activer le site

```bash
# Créer le symlink
ssh root@69.62.108.82 "ln -s /etc/nginx/sites-available/mon-site /etc/nginx/sites-enabled/"

# Tester la config
ssh root@69.62.108.82 "nginx -t"

# Recharger Nginx
ssh root@69.62.108.82 "systemctl reload nginx"
```

### Étape 6 : Configurer SSL/HTTPS (recommandé)

#### Méthode Certbot Standalone

**Cette méthode est recommandée pour les sites statiques** car elle est simple et fiable.

```bash
# 1. Arrêter Nginx temporairement
ssh root@69.62.108.82 "systemctl stop nginx"

# 2. Obtenir le certificat SSL avec Certbot
ssh root@69.62.108.82 "certbot certonly --standalone -d mon-site.srv759970.hstgr.cloud --non-interactive --agree-tos --email contact@srv759970.hstgr.cloud"

# 3. Redémarrer Nginx
ssh root@69.62.108.82 "systemctl start nginx"
```

**Résultat** : Certificat SSL installé dans `/etc/letsencrypt/live/mon-site.srv759970.hstgr.cloud/`

#### Mettre à jour la config Nginx avec HTTPS

```bash
ssh root@69.62.108.82 'cat > /etc/nginx/sites-available/mon-site <<'"'"'EOF'"'"'
# HTTP -> HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name mon-site.srv759970.hstgr.cloud;
    return 301 https://$host$request_uri;
}

# HTTPS
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name mon-site.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/mon-site.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mon-site.srv759970.hstgr.cloud/privkey.pem;

    root /opt/mon-site;
    index index.html;

    # Logs
    access_log /var/log/nginx/mon-site-access.log;
    error_log /var/log/nginx/mon-site-error.log;

    # Pages Astro
    location / {
        try_files $uri $uri.html $uri/ $uri/index.html =404;
    }

    # Cache assets statiques
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot|webp|avif)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Compression Gzip
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript image/svg+xml;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
EOF
'

# Tester et recharger
ssh root@69.62.108.82 "nginx -t && systemctl reload nginx"
```

### Étape 7 : Vérifier

```bash
# Tester HTTPS
curl -I https://mon-site.srv759970.hstgr.cloud/

# Tester toutes les pages
curl -I https://mon-site.srv759970.hstgr.cloud/about/
curl -I https://mon-site.srv759970.hstgr.cloud/contact/
```

**Attendu** : HTTP 200 pour toutes les pages, redirection HTTP→HTTPS

---

## ⚠️ Problèmes courants - Astro spécifiques

### Problème 1 : 404 sur pages secondaires

**Symptômes** :
- Homepage (/) fonctionne
- /about, /contact retournent 404

**Cause** : Mauvaise config `try_files` dans Nginx

**Diagnostic** :
```bash
# Vérifier structure dist/
ssh root@69.62.108.82 "ls -la /opt/mon-site/"
ssh root@69.62.108.82 "ls -la /opt/mon-site/about/"

# Astro génère : about/index.html
```

**Solution** : Utiliser le bon ordre `try_files`

```nginx
location / {
    # ✅ CORRECT pour Astro
    try_files $uri $uri.html $uri/ $uri/index.html =404;
}

# ❌ INCORRECT (manque $uri/)
location / {
    try_files $uri $uri.html $uri/index.html =404;
}
```

**Pourquoi** : Astro génère `about/index.html`, donc Nginx doit essayer `$uri/` puis `$uri/index.html`

---

### Problème 2 : Assets (CSS/JS) ne chargent pas (404)

**Symptômes** :
- HTML charge mais pas de style
- Console navigateur : `404 Not Found` sur `/_astro/xxx.css`

**Cause** : Chemin incorrect ou fichiers non transférés

**Diagnostic** :
```bash
# Vérifier que _astro/ existe
ssh root@69.62.108.82 "ls -la /opt/mon-site/_astro/"

# Tester un asset
ssh root@69.62.108.82 "curl -I http://localhost/_astro/index.xxx.css"
```

**Solution** :
1. Vérifier que `dist/_astro/` a bien été transféré
2. Retransférer :
```bash
scp -r dist/_astro root@69.62.108.82:/opt/mon-site/
```

---

### Problème 3 : Rewrite loop (500 Internal Server Error)

**Symptômes** :
- Erreur 500
- Logs Nginx : `rewrite or internal redirection cycle`

**Cause** : `error_page 404 /index.html` combiné avec `try_files`

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
    try_files $uri $uri.html $uri/ $uri/index.html =404;
    # Pas de error_page 404 !
}
```

---

### Problème 4 : SPA mode (client-side routing) ne fonctionne pas

**Symptômes** :
- Liens internes cassés
- Refresh sur `/about` → 404

**Cause** : Astro en mode SPA nécessite une config différente

**Solution** : Si vous utilisez `@astrojs/react` ou `@astrojs/vue` avec client-side routing :

```nginx
location / {
    # SPA mode : toujours servir index.html
    try_files $uri $uri/ /index.html;
}
```

**Note** : Pour Astro en mode SSG normal (défaut), utiliser la config standard.

---

## 🔧 Configuration Nginx optimale pour Astro

### Configuration de base (recommandée)

```nginx
server {
    listen 80;
    server_name mon-site.srv759970.hstgr.cloud;

    root /opt/mon-site;
    index index.html;

    # Logs
    access_log /var/log/nginx/mon-site-access.log;
    error_log /var/log/nginx/mon-site-error.log;

    # Pages Astro (SSG mode)
    location / {
        try_files $uri $uri.html $uri/ $uri/index.html =404;
    }

    # Cache assets statiques
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot|webp|avif)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Compression Gzip
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript image/svg+xml;
}
```

### Configuration avancée (avec Brotli)

```nginx
server {
    listen 80;
    server_name mon-site.srv759970.hstgr.cloud;

    root /opt/mon-site;
    index index.html;

    # Logs
    access_log /var/log/nginx/mon-site-access.log;
    error_log /var/log/nginx/mon-site-error.log;

    # Pages Astro
    location / {
        try_files $uri $uri.html $uri/ $uri/index.html =404;
    }

    # Cache assets avec hash (Astro génère des noms de fichiers avec hash)
    location /_astro/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        # Pas besoin de revalidation, hash change = nouveau fichier
    }

    # Images et fonts
    location ~* \.(png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot|webp|avif)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Compression Gzip
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript image/svg+xml;

    # Sécurité headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

---

## 🔄 Workflow de mise à jour

### Mise à jour complète

```bash
# 1. Local : Rebuild
cd "C:\Users\JulienFernandez\OneDrive\Coding\_Projets de code\[PROJET]"
pnpm build

# 2. Transférer (écrase tout)
scp -r dist/* root@69.62.108.82:/opt/mon-site/

# 3. Pas de redémarrage nécessaire (fichiers statiques)
# Optionnel : vider cache Nginx
ssh root@69.62.108.82 "nginx -s reload"
```

### Mise à jour partielle (plus rapide)

```bash
# Utiliser rsync (ne transfère que les différences)
rsync -avz --delete dist/ root@69.62.108.82:/opt/mon-site/
```

**Avantage rsync** :
- Transfère seulement les fichiers modifiés
- `--delete` supprime les vieux fichiers sur le VPS
- Plus rapide pour gros sites

---

## 🤖 Scripts de déploiement automatisés

### Script Bash (Linux/Mac)

Créer `deploy.sh` dans votre projet :

```bash
#!/bin/bash

# Script de déploiement automatisé pour Astro sur VPS Hostinger
set -e

# Configuration
VPS_HOST="root@69.62.108.82"
VPS_PATH="/opt/mon-site"
DOMAIN="mon-site.srv759970.hstgr.cloud"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Déploiement du site sur Hostinger VPS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Étape 1: Build local
echo -e "${YELLOW}[1/5]${NC} Build du site Astro..."
pnpm build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Build réussi"
else
    echo -e "${RED}✗${NC} Erreur lors du build"
    exit 1
fi
echo ""

# Étape 2: Sauvegarde du site actuel
echo -e "${YELLOW}[2/5]${NC} Sauvegarde du site actuel sur le VPS..."
ssh $VPS_HOST "if [ -d $VPS_PATH ]; then cp -r $VPS_PATH ${VPS_PATH}_backup_\$(date +%Y%m%d_%H%M%S); echo 'Sauvegarde créée'; else echo 'Pas de site existant à sauvegarder'; fi"
echo -e "${GREEN}✓${NC} Sauvegarde effectuée"
echo ""

# Étape 3: Nettoyage du répertoire cible
echo -e "${YELLOW}[3/5]${NC} Nettoyage du répertoire cible..."
ssh $VPS_HOST "rm -rf $VPS_PATH/* && mkdir -p $VPS_PATH"
echo -e "${GREEN}✓${NC} Répertoire nettoyé"
echo ""

# Étape 4: Transfer des fichiers
echo -e "${YELLOW}[4/5]${NC} Transfer des fichiers vers le VPS..."
scp -r dist/* $VPS_HOST:$VPS_PATH/

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Fichiers transférés avec succès"
else
    echo -e "${RED}✗${NC} Erreur lors du transfert"
    echo -e "${YELLOW}Restauration de la sauvegarde...${NC}"
    ssh $VPS_HOST "BACKUP=\$(ls -t ${VPS_PATH}_backup_* 2>/dev/null | head -1); if [ -n \"\$BACKUP\" ]; then rm -rf $VPS_PATH && mv \$BACKUP $VPS_PATH; echo 'Sauvegarde restaurée'; fi"
    exit 1
fi
echo ""

# Étape 5: Vérification du déploiement
echo -e "${YELLOW}[5/5]${NC} Vérification du déploiement..."
ssh $VPS_HOST "ls -lh $VPS_PATH | head -10"

# Test HTTP
HTTP_CODE=$(curl -o /dev/null -s -w "%{http_code}" https://$DOMAIN/)
if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓${NC} Site accessible (HTTP $HTTP_CODE)"
else
    echo -e "${RED}✗${NC} Site non accessible (HTTP $HTTP_CODE)"
fi
echo ""

# Résumé
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Déploiement terminé avec succès !${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "Site accessible sur: ${GREEN}https://$DOMAIN${NC}"
echo ""
```

**Utilisation** :
```bash
chmod +x deploy.sh
./deploy.sh
```

### Script PowerShell (Windows)

Créer `deploy.ps1` dans votre projet :

```powershell
# Script de déploiement automatisé pour Astro sur VPS Hostinger

# Configuration
$VPS_HOST = "root@69.62.108.82"
$VPS_PATH = "/opt/mon-site"
$DOMAIN = "mon-site.srv759970.hstgr.cloud"

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "  Déploiement du site sur Hostinger VPS" -ForegroundColor Blue
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Blue

# Étape 1: Build local
Write-Host "[1/5] Build du site Astro..." -ForegroundColor Yellow
pnpm build

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Build réussi`n" -ForegroundColor Green
} else {
    Write-Host "✗ Erreur lors du build" -ForegroundColor Red
    exit 1
}

# Étape 2: Sauvegarde
Write-Host "[2/5] Sauvegarde du site actuel sur le VPS..." -ForegroundColor Yellow
ssh $VPS_HOST "if [ -d $VPS_PATH ]; then cp -r $VPS_PATH ${VPS_PATH}_backup_`$(date +%Y%m%d_%H%M%S); echo 'Sauvegarde créée'; else echo 'Pas de site existant à sauvegarder'; fi"
Write-Host "✓ Sauvegarde effectuée`n" -ForegroundColor Green

# Étape 3: Nettoyage
Write-Host "[3/5] Nettoyage du répertoire cible..." -ForegroundColor Yellow
ssh $VPS_HOST "rm -rf $VPS_PATH/* && mkdir -p $VPS_PATH"
Write-Host "✓ Répertoire nettoyé`n" -ForegroundColor Green

# Étape 4: Transfer
Write-Host "[4/5] Transfer des fichiers vers le VPS..." -ForegroundColor Yellow
scp -r dist/* "${VPS_HOST}:${VPS_PATH}/"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Fichiers transférés avec succès`n" -ForegroundColor Green
} else {
    Write-Host "✗ Erreur lors du transfert" -ForegroundColor Red
    Write-Host "Restauration de la sauvegarde..." -ForegroundColor Yellow
    ssh $VPS_HOST "BACKUP=`$(ls -t ${VPS_PATH}_backup_* 2>/dev/null | head -1); if [ -n `"`$BACKUP`" ]; then rm -rf $VPS_PATH && mv `$BACKUP $VPS_PATH; echo 'Sauvegarde restaurée'; fi"
    exit 1
}

# Étape 5: Vérification
Write-Host "[5/5] Vérification du déploiement..." -ForegroundColor Yellow
ssh $VPS_HOST "ls -lh $VPS_PATH | head -10"

# Test HTTP
try {
    $response = Invoke-WebRequest -Uri "https://$DOMAIN/" -Method Head -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Site accessible (HTTP $($response.StatusCode))`n" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Site non accessible`n" -ForegroundColor Red
}

# Résumé
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "✓ Déploiement terminé avec succès !" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Blue

Write-Host "Site accessible sur: https://$DOMAIN`n" -ForegroundColor Green
```

**Utilisation** :
```powershell
.\deploy.ps1
```

### Fonctionnalités des scripts

Les deux scripts automatisent :
- ✅ Build avec `pnpm build`
- ✅ Sauvegarde automatique du site actuel avec timestamp
- ✅ Nettoyage du répertoire cible
- ✅ Transfer SCP vers le VPS
- ✅ Vérification HTTP post-déploiement
- ✅ **Rollback automatique en cas d'erreur de transfert**
- ✅ Interface colorée avec progression

---

## 📊 Optimisations performance

### 1. Vérifier la taille du build

```bash
# Analyser la taille des assets
cd dist
du -sh *
du -sh _astro/*
```

**Si trop gros** :
- Optimiser les images (WebP, AVIF)
- Vérifier que les node_modules ne sont pas inclus (ne devrait pas)
- Utiliser `astro build --mode production`

### 2. Preload des ressources critiques

Dans `Layout.astro` :

```astro
---
// Layout.astro
---
<head>
  <!-- Preload font critique -->
  <link rel="preload" href="/fonts/main.woff2" as="font" type="font/woff2" crossorigin>

  <!-- Preconnect CDN -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="dns-prefetch" href="https://fonts.googleapis.com">
</head>
```

### 3. Compression Brotli (meilleure que Gzip)

```bash
# Installer module Brotli (si pas déjà installé)
ssh root@69.62.108.82 "apt install -y nginx-module-brotli"
```

```nginx
# Dans nginx.conf ou site config
brotli on;
brotli_comp_level 6;
brotli_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript image/svg+xml;
```

---

## 🔍 Checklist de déploiement

Avant de déployer un site Astro :

- [ ] Build local réussi (`pnpm build`)
- [ ] Dossier `dist/` généré
- [ ] Structure vérifiée : `index.html`, `about/index.html`, `_astro/`
- [ ] Structure créée sur VPS (`/opt/mon-site/`)
- [ ] Fichiers transférés (`scp -r dist/*`)
- [ ] Config Nginx créée avec bon `try_files`
- [ ] Config Nginx testée (`nginx -t`)
- [ ] Site activé (symlink dans `sites-enabled/`)
- [ ] Nginx rechargé (`systemctl reload nginx`)
- [ ] Toutes les pages testées (HTTP 200)
- [ ] Assets chargent correctement (CSS, JS, images)
- [ ] Pas d'erreurs dans logs Nginx

---

## 🎯 Cas réels déployés

### Site 1 : Cristina (Astro 5.14 + Tailwind CSS)

**Structure** :
```
dist/
├── index.html
├── ateliers/
│   └── index.html
├── a-propos/
│   └── index.html
├── contact/
│   └── index.html
└── _astro/
    ├── index.xxx.css
    └── index.xxx.js
```

**Config Nginx** : `/etc/nginx/sites-available/cristina`
**URL** : https://cristina.srv759970.hstgr.cloud
**SSL** : ✅ Let's Encrypt

**Problèmes rencontrés** :
1. ❌ 404 sur `/ateliers` → Solution : `try_files $uri $uri.html $uri/ $uri/index.html`
2. ❌ Conflit avec autre site (`server_name _`) → Solution : server_name spécifique

**Résultat** : ✅ Toutes pages en HTTP 200, HTTPS actif

---

### Site 2 : Clémence (Astro 5.14 - Site RH Diversité & Inclusion)

**Structure** :
```
dist/
├── index.html
├── a-propos/
│   └── index.html
├── services/
│   └── index.html
├── projets-engages/
│   └── index.html
├── cadre-juridique/
│   └── index.html
├── contact/
│   └── index.html
└── _astro/
    ├── index.xxx.css
    └── index.xxx.js
```

**Config Nginx** : `/etc/nginx/sites-available/clemence`
**URL** : https://clemence.srv759970.hstgr.cloud
**Path VPS** : `/opt/clemence-site`
**SSL** : ✅ Let's Encrypt (Certbot standalone)

**Fonctionnalités** :
- 6 pages : Accueil, À propos, Services, Projets engagés, Cadre juridique, Contact
- Layout partagé avec navigation
- Design system avec couleurs personnalisées
- Scripts de déploiement automatisés (deploy.sh + deploy.ps1)

**Déploiement** :
- Méthode : Certbot standalone pour SSL
- HTTP→HTTPS redirect configuré
- Security headers ajoutés

**Résultat** : ✅ Toutes pages en HTTP 200, HTTPS actif, navigation fonctionnelle

---

## 📚 Ressources

- [Astro Documentation](https://docs.astro.build/)
- [Astro Deployment Guide](https://docs.astro.build/en/guides/deploy/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Guide Nginx VPS](./GUIDE_NGINX.md)

---

## 🆘 Troubleshooting rapide

| Symptôme | Cause probable | Solution |
|----------|----------------|----------|
| 404 sur pages secondaires | `try_files` mal configuré | `try_files $uri $uri.html $uri/ $uri/index.html =404;` |
| 404 sur assets CSS/JS | Dossier `_astro/` non transféré | `scp -r dist/_astro root@69.62.108.82:/opt/mon-site/` |
| 500 rewrite loop | `error_page 404` + `try_files` | Supprimer `error_page 404` |
| Homepage OK mais autres 404 | Conflit avec autre site | Vérifier `server_name` (pas de `_`) |
| Assets ne chargent pas | Mauvais cache headers | Vérifier config cache dans Nginx |

---

**Dernière mise à jour** : Octobre 2025
**Version** : 2.0
**Sites Astro déployés** : 2 (Cristina, Clémence)
**Nouvelles sections (v2.0)** : SSL/HTTPS avec Certbot standalone, Scripts de déploiement automatisés
