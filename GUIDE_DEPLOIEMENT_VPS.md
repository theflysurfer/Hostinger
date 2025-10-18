# 🚀 Guide de déploiement sur VPS Hostinger

## 📋 Informations du serveur

**Serveur** : Hostinger VPS Ubuntu 24.04.2 LTS
**IP** : `69.62.108.82`
**Hostname** : `srv759970.hstgr.cloud`
**User** : `root`
**Uptime** : 195+ jours (serveur stable)

---

## 🔑 Accès SSH

### Configuration déjà en place

Une clé SSH est déjà configurée sur la machine locale de l'utilisateur :
- **Clé privée** : `~/.ssh/id_rsa` (C:\Users\JulienFernandez\.ssh\id_rsa)
- **Clé publique** : Déjà ajoutée sur le serveur dans `/root/.ssh/authorized_keys`

### Test de connexion

```bash
ssh root@69.62.108.82
```

✅ **Devrait fonctionner sans demander de mot de passe**

### Si la connexion échoue

Si un autre LLM ou session n'a pas accès à la clé SSH :

```bash
# Vérifier que la clé existe
ls -la ~/.ssh/id_rsa

# Si elle n'existe pas, demander à l'utilisateur le mot de passe root
# puis configurer la clé :
ssh-copy-id root@69.62.108.82
```

---

## 🏗️ Architecture actuelle du serveur

### Applications déployées

```
/opt/
├── support-dashboard/          # Dashboard Support IT (Streamlit) [DOCKER]
│   ├── dashboard/app.py
│   ├── data/tickets.db
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── clemence-site/              # Site Clémence - RH Diversité [STATIC]
│   ├── index.html
│   ├── a-propos/
│   ├── services/
│   ├── projets-engages/
│   ├── cadre-juridique/
│   ├── contact/
│   └── _astro/
│
├── cristina-site/              # Site Cristina - Coaching [STATIC]
│   ├── index.html
│   ├── ateliers/
│   ├── a-propos/
│   └── _astro/
│
└── [vos futures applications ici]
```

### Services systemd

| Service | Type | Status | Port/Path |
|---------|------|--------|-----------|
| **Ollama** | ML/AI | ✅ Actif | 11434 (local) |
| **Strapi** | CMS | ✅ Actif | Node.js backend |
| **WordPress** | CMS | ✅ Actif | PHP/MySQL |

### Ports et URLs

| Port/URL | Application | Type | Status |
|----------|-------------|------|--------|
| **80/443** | Nginx (reverse proxy) | Proxy | ✅ Actif |
| **8501** | Support Dashboard | Docker | ✅ Actif |
| **11434** | Ollama API (local) | systemd | ✅ Actif |

### Sites web via Nginx (HTTPS)

| URL | Application | SSL | Type |
|-----|-------------|-----|------|
| https://clemence.srv759970.hstgr.cloud | Site Clémence | ✅ | Static (Astro) |
| https://cristina.srv759970.hstgr.cloud | Site Cristina | ✅ | Static (Astro) |
| https://dashboard.srv759970.hstgr.cloud | Dashboard | ✅ | Reverse proxy |
| https://sharepoint.srv759970.hstgr.cloud | SharePoint API | ✅ | Node.js |
| https://whisper.srv759970.hstgr.cloud | Whisper API | ✅ | Python/Node.js |
| https://strapi.srv759970.hstgr.cloud | Strapi CMS | ✅ | Node.js |
| https://wordpress.srv759970.hstgr.cloud | WordPress | ✅ | PHP |
| https://ollama.srv759970.hstgr.cloud | Ollama API | ✅ | Reverse proxy |

### Services installés

- ✅ **Docker** : version 28.2.2
- ✅ **Docker Compose** : installé
- ✅ **Nginx** : version 1.24.0 (Ubuntu)
- ✅ **Git** : disponible
- ✅ **Curl, rsync** : disponibles

---

## 📦 Déployer une nouvelle application

### Workflow recommandé

#### 1. Préparer l'application localement

Votre application doit avoir :
- `Dockerfile` (obligatoire)
- `docker-compose.yml` (recommandé)
- Fichiers de l'application

#### 2. Choisir un port unique

```bash
# Vérifier les ports déjà utilisés
ssh root@69.62.108.82 "docker ps --format '{{.Ports}}'"
```

**Ports disponibles** : 8502, 8503, 8504, etc.

#### 3. Créer la structure sur le serveur

```bash
# Exemple pour une app "mon-app"
ssh root@69.62.108.82 "mkdir -p /opt/mon-app"
```

#### 4. Transférer les fichiers

```bash
# Depuis la machine locale
cd "C:\Users\JulienFernandez\OneDrive\Coding\_Projets de code\[VOTRE_PROJET]"

# Transférer avec scp
scp -r * root@69.62.108.82:/opt/mon-app/

# OU fichier par fichier
scp Dockerfile root@69.62.108.82:/opt/mon-app/
scp docker-compose.yml root@69.62.108.82:/opt/mon-app/
```

#### 5. Construire et lancer

```bash
ssh root@69.62.108.82 "cd /opt/mon-app && docker-compose build && docker-compose up -d"
```

#### 6. Vérifier

```bash
ssh root@69.62.108.82 "docker ps"
ssh root@69.62.108.82 "docker logs [container-name]"
```

---

## 🎯 Template docker-compose.yml

### Pour une application Streamlit

```yaml
version: '3.8'

services:
  mon-app:
    build: .
    container_name: mon-app
    ports:
      - "8502:8501"  # Port externe:Port interne
    volumes:
      - ./data:/app/data  # Si vous avez des données persistantes
    restart: unless-stopped
    environment:
      - TZ=Europe/Paris
```

### Pour une application Flask/FastAPI

```yaml
version: '3.8'

services:
  mon-api:
    build: .
    container_name: mon-api
    ports:
      - "8502:8000"
    restart: unless-stopped
    environment:
      - TZ=Europe/Paris
```

### Pour une application Node.js

```yaml
version: '3.8'

services:
  mon-app-node:
    build: .
    container_name: mon-app-node
    ports:
      - "8502:3000"
    restart: unless-stopped
    environment:
      - TZ=Europe/Paris
      - NODE_ENV=production
```

---

## 🌐 Configuration Nginx (pour plusieurs sites)

### Structure recommandée

Chaque application a son propre fichier de configuration dans `/etc/nginx/sites-available/`

### Ajouter un nouveau site

#### Étape 1 : Créer la configuration

```bash
ssh root@69.62.108.82 "cat > /etc/nginx/sites-available/mon-app" <<'EOF'
server {
    listen 80;
    server_name mon-app.srv759970.hstgr.cloud;  # Sous-domaine

    location / {
        proxy_pass http://localhost:8502;  # Port de votre app
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_read_timeout 86400;
    }
}
EOF
```

#### Étape 2 : Activer le site

```bash
ssh root@69.62.108.82 "ln -s /etc/nginx/sites-available/mon-app /etc/nginx/sites-enabled/"
```

#### Étape 3 : Tester et recharger

```bash
ssh root@69.62.108.82 "nginx -t && systemctl reload nginx"
```

### Configuration pour plusieurs applications

```bash
# Exemple avec 3 applications
/etc/nginx/sites-available/
├── dashboard              # support-dashboard
├── app-budgets           # Nouvelle app budgets
└── app-planning          # Nouvelle app planning

# Chaque app sur son sous-domaine
- dashboard.srv759970.hstgr.cloud   → localhost:8501
- budgets.srv759970.hstgr.cloud     → localhost:8502
- planning.srv759970.hstgr.cloud    → localhost:8503
```

---

## 🔧 Commandes Docker utiles

### Gestion des conteneurs

```bash
# Lister tous les conteneurs
ssh root@69.62.108.82 "docker ps -a"

# Voir les logs d'un conteneur
ssh root@69.62.108.82 "docker logs [container-name] --tail=50 -f"

# Redémarrer un conteneur
ssh root@69.62.108.82 "cd /opt/mon-app && docker-compose restart"

# Arrêter un conteneur
ssh root@69.62.108.82 "cd /opt/mon-app && docker-compose down"

# Reconstruire et relancer
ssh root@69.62.108.82 "cd /opt/mon-app && docker-compose up -d --build"
```

### Nettoyage

```bash
# Supprimer les conteneurs arrêtés
ssh root@69.62.108.82 "docker container prune -f"

# Supprimer les images inutilisées
ssh root@69.62.108.82 "docker image prune -a -f"

# Nettoyer tout (ATTENTION: supprime tout ce qui n'est pas utilisé)
ssh root@69.62.108.82 "docker system prune -a -f"
```

---

## 📊 Monitoring et logs

### Vérifier l'état du système

```bash
# Utilisation ressources
ssh root@69.62.108.82 "docker stats --no-stream"

# Espace disque
ssh root@69.62.108.82 "df -h"

# Mémoire
ssh root@69.62.108.82 "free -h"

# Load average
ssh root@69.62.108.82 "uptime"
```

### Logs Nginx

```bash
# Logs d'accès
ssh root@69.62.108.82 "tail -f /var/log/nginx/access.log"

# Logs d'erreur
ssh root@69.62.108.82 "tail -f /var/log/nginx/error.log"
```

---

## 🔄 Mise à jour d'une application

### Workflow standard

```bash
# 1. Mettre à jour les fichiers locaux
cd "C:\Users\JulienFernandez\OneDrive\Coding\_Projets de code\[PROJET]"

# 2. Transférer vers le serveur
scp -r * root@69.62.108.82:/opt/mon-app/

# 3. Reconstruire et redémarrer
ssh root@69.62.108.82 "cd /opt/mon-app && docker-compose down && docker-compose build --no-cache && docker-compose up -d"

# 4. Vérifier les logs
ssh root@69.62.108.82 "cd /opt/mon-app && docker-compose logs -f"
```

### Script de déploiement automatisé

Créer `scripts/deploy_to_vps.bat` dans votre projet :

```batch
@echo off
set APP_NAME=mon-app
set VPS_HOST=root@69.62.108.82
set VPS_PATH=/opt/%APP_NAME%

echo Deploiement de %APP_NAME%...

echo [1/3] Transfert des fichiers...
scp -r * %VPS_HOST%:%VPS_PATH%/

echo [2/3] Rebuild Docker...
ssh %VPS_HOST% "cd %VPS_PATH% && docker-compose build"

echo [3/3] Redemarrage...
ssh %VPS_HOST% "cd %VPS_PATH% && docker-compose up -d"

echo Deploiement termine!
ssh %VPS_HOST% "cd %VPS_PATH% && docker-compose ps"
```

---

## 🛡️ Sécurité

### Bonnes pratiques

#### 1. Ne jamais committer de secrets

```bash
# Dans .gitignore
.env
*.key
*.pem
config/secrets.yml
```

#### 2. Utiliser des variables d'environnement

Dans `docker-compose.yml` :

```yaml
services:
  mon-app:
    environment:
      - API_KEY=${API_KEY}
      - DB_PASSWORD=${DB_PASSWORD}
    env_file:
      - .env
```

#### 3. Limiter les permissions

```bash
# Ne pas laisser les fichiers en 777
ssh root@69.62.108.82 "chmod 644 /opt/mon-app/config.yml"
```

---

## 🆘 Troubleshooting

### Le conteneur ne démarre pas

```bash
# Voir les logs complets
ssh root@69.62.108.82 "cd /opt/mon-app && docker-compose logs"

# Vérifier la config
ssh root@69.62.108.82 "cd /opt/mon-app && docker-compose config"

# Rebuild from scratch
ssh root@69.62.108.82 "cd /opt/mon-app && docker-compose down && docker-compose build --no-cache && docker-compose up -d"
```

### Port déjà utilisé

```bash
# Vérifier quel processus utilise le port
ssh root@69.62.108.82 "lsof -i :8502"

# Ou
ssh root@69.62.108.82 "netstat -tulpn | grep 8502"

# Changer le port dans docker-compose.yml
```

### Problème Nginx

```bash
# Tester la config
ssh root@69.62.108.82 "nginx -t"

# Voir les erreurs
ssh root@69.62.108.82 "tail -50 /var/log/nginx/error.log"

# Redémarrer Nginx
ssh root@69.62.108.82 "systemctl restart nginx"
```

### Manque d'espace disque

```bash
# Nettoyer Docker
ssh root@69.62.108.82 "docker system prune -a -f"

# Vérifier l'espace
ssh root@69.62.108.82 "df -h"

# Trouver les gros fichiers
ssh root@69.62.108.82 "du -sh /opt/* | sort -h"
```

---

## 📝 Checklist de déploiement

Avant de déployer une nouvelle application, vérifiez :

- [ ] SSH fonctionne sans mot de passe
- [ ] Application testée localement
- [ ] Dockerfile créé et testé
- [ ] docker-compose.yml configuré
- [ ] Port unique choisi (vérifier disponibilité)
- [ ] Variables d'environnement gérées (.env)
- [ ] Structure créée sur le serveur (`/opt/mon-app/`)
- [ ] Fichiers transférés
- [ ] Build Docker réussi
- [ ] Conteneur démarré (`docker ps`)
- [ ] Logs vérifiés (pas d'erreur)
- [ ] Application accessible via IP:PORT
- [ ] (Optionnel) Configuration Nginx créée
- [ ] (Optionnel) Sous-domaine configuré

---

## 🎓 Exemples de déploiement

### Exemple 1 : Dashboard Streamlit (déjà fait)

```bash
# Structure
/opt/support-dashboard/
├── dashboard/app.py
├── data/tickets.db
├── Dockerfile
├── docker-compose.yml
└── requirements.txt

# Commandes
ssh root@69.62.108.82 "cd /opt/support-dashboard && docker-compose up -d"

# Accessible sur : http://69.62.108.82:8501
```

### Exemple 2 : API FastAPI

```bash
# 1. Créer la structure
ssh root@69.62.108.82 "mkdir -p /opt/mon-api"

# 2. Transférer
scp -r * root@69.62.108.82:/opt/mon-api/

# 3. docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    container_name: mon-api
    ports:
      - "8502:8000"
    restart: unless-stopped

# 4. Lancer
ssh root@69.62.108.82 "cd /opt/mon-api && docker-compose up -d"

# Accessible sur : http://69.62.108.82:8502
```

### Exemple 3 : Frontend React + Backend Node

```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    container_name: mon-frontend
    ports:
      - "8502:3000"
    restart: unless-stopped
    depends_on:
      - backend

  backend:
    build: ./backend
    container_name: mon-backend
    ports:
      - "8503:5000"
    restart: unless-stopped
```

---

## 📞 Informations de contact

**Serveur** : srv759970.hstgr.cloud
**IP** : 69.62.108.82
**Accès SSH** : `ssh root@69.62.108.82`
**Panel Hostinger** : https://hpanel.hostinger.com/

---

## 📚 Ressources utiles

- **Docker Docs** : https://docs.docker.com/
- **Docker Compose** : https://docs.docker.com/compose/
- **Nginx Docs** : https://nginx.org/en/docs/
- **Streamlit Docs** : https://docs.streamlit.io/

---

**Dernière mise à jour** : Octobre 2025
**Version** : 3.0
**Scope** : Applications Docker et sites statiques
**Applications déployées** :
- Docker : 1 (Support Dashboard)
- Static (Astro) : 2 (Cristina, Clémence)
- Services systemd : Ollama, Strapi, WordPress
**Sites avec SSL** : 8 (tous les domaines HTTPS configurés)
**Ports Docker disponibles** : 8502+

**Pour déployer un site Astro statique** : voir [GUIDE_ASTRO.md](./GUIDE_ASTRO.md)
**Pour configurer Ollama** : voir section Ollama ci-dessous ou [GUIDE_SERVICES_SYSTEMD.md](./GUIDE_SERVICES_SYSTEMD.md)
