# 🔧 Guide Strapi - Déploiement sur VPS avec Docker

> **Guide complet pour déployer Strapi CMS sur VPS Hostinger - Solutions aux problèmes courants**

---

## ⚠️ AVERTISSEMENT IMPORTANT

**Ce guide vous fera gagner 3+ heures de debugging** en évitant les pièges suivants :
1. ❌ Bug Vite 6 avec `server.allowedHosts` en mode `develop`
2. ❌ Strapi nécessite Node.js <=22 (pas 23+)
3. ❌ Rebuild admin requis après modification `vite.config.ts`
4. ❌ Mode production OBLIGATOIRE avec reverse proxy

---

## 📋 Vue d'ensemble

**Strapi** : Headless CMS open-source (Node.js)
**Version supportée** : Strapi 5.x
**Déploiement** : Docker avec Node.js 22 + SQLite
**Admin panel** : Interface web sur `/admin`

---

## 🏗️ Architecture de déploiement

```
VPS Hostinger (69.62.108.82)
│
├── Nginx (port 80)
│   └── Reverse proxy vers localhost:1337
│       └── admin.mon-site.srv759970.hstgr.cloud
│
└── Docker Container (cristina-strapi)
    ├── Node.js 22-slim
    ├── Strapi 5.27.0
    ├── SQLite database
    ├── Mode: PRODUCTION (important !)
    └── Port: 1337
```

**Pourquoi Docker ?** :
- Node.js 22 isolé (système peut avoir Node 23)
- Dépendances gérées
- Facile à rebuild/redémarrer

---

## 🚀 Déploiement initial

### Étape 1 : Créer le projet Strapi localement (avec Node 22)

**⚠️ Prérequis** : Node.js 22 (pas 23 !)

```bash
# Vérifier version Node
node -v
# Doit afficher : v22.x.x

# Si version 23+, installer Node 22 via NVM
# Ou utiliser Docker directement sur le VPS
```

**Option A : Créer localement (si Node 22 disponible)**

```bash
cd "C:\Users\JulienFernandez\OneDrive\Coding\_Projets de code\[PROJET]"

# Créer projet Strapi
pnpm create strapi-app@latest mon-backoffice --quickstart --typescript --skip-cloud

# Structure créée :
# mon-backoffice/
# ├── src/
# ├── config/
# ├── public/
# └── package.json
```

**Option B : Créer directement sur VPS avec Docker (recommandé si pas Node 22)**

```bash
# Créer avec conteneur temporaire Node 22
ssh root@69.62.108.82 "docker run --rm -v /opt/mon-backend:/opt -w /opt node:22-slim sh -c 'npx create-strapi-app@latest backend --quickstart --typescript --skip-cloud'"
```

---

### Étape 2 : Créer la structure Docker

**Sur le VPS** :

```bash
ssh root@69.62.108.82 "mkdir -p /opt/mon-backend"
```

**Créer `Dockerfile`** :

```bash
ssh root@69.62.108.82 "cat > /opt/mon-backend/Dockerfile" <<'EOF'
FROM node:22-slim

WORKDIR /app

# Copier le projet Strapi
COPY backend/ /app/

# Installer les dépendances
RUN npm install

# Build l'admin panel (IMPORTANT !)
RUN npm run build

# Exposer le port
EXPOSE 1337

# ⚠️ IMPORTANT : Utiliser 'start' (production), PAS 'develop'
CMD ["npm", "run", "start"]
EOF
```

**Créer `docker-compose.yml`** :

```bash
ssh root@69.62.108.82 "cat > /opt/mon-backend/docker-compose.yml" <<'EOF'
version: '3.8'

services:
  strapi:
    build: .
    container_name: mon-strapi
    ports:
      - "1337:1337"
    volumes:
      # Données persistantes (SQLite + uploads)
      - ./data:/app/.tmp
      - ./uploads:/app/public/uploads
    restart: unless-stopped
    environment:
      # ⚠️ IMPORTANT : Production mode obligatoire avec reverse proxy !
      - NODE_ENV=production
      - TZ=Europe/Paris
      - STRAPI_ADMIN_BACKEND_URL=http://admin.mon-site.srv759970.hstgr.cloud
      - HOST=0.0.0.0
      - PORT=1337
EOF
```

---

### Étape 3 : **CRITIQUE** - Créer `vite.config.ts`

**⚠️ SANS CE FICHIER, VOUS AUREZ "host not allowed" ERROR !**

```bash
ssh root@69.62.108.82 "mkdir -p /opt/mon-backend/backend/src/admin"

ssh root@69.62.108.82 "cat > /opt/mon-backend/backend/src/admin/vite.config.ts" <<'EOF'
import { mergeConfig, type UserConfig } from 'vite';

export default (config: UserConfig) => {
  return mergeConfig(config, {
    server: {
      // ✅ SOLUTION : allowedHosts: true
      // ❌ NE MARCHE PAS : Liste spécifique en mode develop
      allowedHosts: true,
    },
  });
};
EOF
```

**Pourquoi `allowedHosts: true` ?** :
- Bug Vite 6.0.11+ : liste d'hosts ne fonctionne qu'en production
- `true` = accepte tous les hosts (OK pour reverse proxy)
- **Alternative** : Passer en mode production (recommandé)

---

### Étape 4 : Transférer le code Strapi

```bash
# Depuis le dossier local
cd "C:\Users\JulienFernandez\OneDrive\Coding\_Projets de code\[PROJET]"

# Transférer le code Strapi (backend/)
scp -r mon-backoffice/* root@69.62.108.82:/opt/mon-backend/backend/

# ⚠️ NE PAS transférer node_modules/ (trop gros, inutile)
```

---

### Étape 5 : Build et lancer Docker

```bash
# Build l'image Docker
ssh root@69.62.108.82 "cd /opt/mon-backend && docker-compose build"

# Lancer le conteneur
ssh root@69.62.108.82 "cd /opt/mon-backend && docker-compose up -d"

# Attendre 15s que Strapi démarre
sleep 15

# Vérifier les logs
ssh root@69.62.108.82 "docker logs mon-strapi --tail=30"
```

**Logs attendus** :
```
┌──────────────────────────────────────────────────────┐
│ Strapi started successfully                          │
└──────────────────────────────────────────────────────┘

Create your first administrator 💻 by going to:
http://localhost:1337/admin
```

---

### Étape 6 : Configurer Nginx (reverse proxy)

```bash
ssh root@69.62.108.82 "cat > /etc/nginx/sites-available/mon-admin" <<'EOF'
server {
    listen 80;
    server_name admin.mon-site.srv759970.hstgr.cloud;

    # Logs
    access_log /var/log/nginx/mon-admin-access.log;
    error_log /var/log/nginx/mon-admin-error.log;

    location / {
        # Reverse proxy vers Strapi Docker
        proxy_pass http://localhost:1337;

        proxy_http_version 1.1;

        # Headers essentiels
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (admin panel en temps réel)
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeout long (admin panel peut avoir des requêtes longues)
        proxy_read_timeout 86400;
    }
}
EOF
```

**Activer le site** :

```bash
# Créer symlink
ssh root@69.62.108.82 "ln -s /etc/nginx/sites-available/mon-admin /etc/nginx/sites-enabled/"

# Tester config
ssh root@69.62.108.82 "nginx -t"

# Recharger Nginx
ssh root@69.62.108.82 "systemctl reload nginx"
```

---

### Étape 7 : Vérifier le déploiement

```bash
# Test via Nginx proxy
ssh root@69.62.108.82 "curl -s -o /dev/null -w 'Admin HTTP: %{http_code}\n' -H 'Host: admin.mon-site.srv759970.hstgr.cloud' http://localhost/admin"

# Attendu : HTTP 200
```

**Ouvrir dans navigateur** : http://admin.mon-site.srv759970.hstgr.cloud/admin

**Si HTTP 200** : ✅ Créer le compte administrateur !

---

## ⚠️ PROBLÈMES COURANTS - SOLUTIONS DÉTAILLÉES

### Problème 1 : "Blocked request. This host is not allowed"

**Symptôme** :
```
Blocked request. This host ("admin.mon-site.srv759970.hstgr.cloud") is not allowed.
To allow this host, add "admin.mon-site.srv759970.hstgr.cloud" to `server.allowedHosts` in vite.config.js.
```

**Cause** : Bug Vite 6.0.11+ avec Strapi 5.12+

**Solutions (par ordre de priorité)** :

#### ✅ Solution 1 : Mode production (RECOMMANDÉE)

```bash
# Modifier docker-compose.yml
ssh root@69.62.108.82 "cat > /opt/mon-backend/docker-compose.yml" <<'EOF'
version: '3.8'
services:
  strapi:
    build: .
    environment:
      - NODE_ENV=production  # ← IMPORTANT !
      # ... autres variables
EOF

# Rebuild et redémarrer
ssh root@69.62.108.82 "cd /opt/mon-backend && docker-compose down && docker-compose build --no-cache && docker-compose up -d"
```

**Avantages** :
- Admin panel optimisé
- Plus rapide
- Plus stable
- `allowedHosts` fonctionne correctement

#### ✅ Solution 2 : `allowedHosts: true` (si vraiment en develop)

```bash
# Créer vite.config.ts
ssh root@69.62.108.82 "cat > /opt/mon-backend/backend/src/admin/vite.config.ts" <<'EOF'
import { mergeConfig, type UserConfig } from 'vite';

export default (config: UserConfig) => {
  return mergeConfig(config, {
    server: {
      allowedHosts: true,  // Accepte tous les hosts
    },
  });
};
EOF

# ⚠️ REBUILD ADMIN REQUIS !
ssh root@69.62.108.82 "docker exec mon-strapi npm run build"
ssh root@69.62.108.82 "docker restart mon-strapi"
```

#### ❌ Solution qui NE MARCHE PAS

```typescript
// ❌ CETTE CONFIG NE FONCTIONNE PAS EN MODE DEVELOP !
server: {
  allowedHosts: [
    'admin.mon-site.srv759970.hstgr.cloud',
    'localhost',
  ],
}
```

**Pourquoi ça ne marche pas** : Bug Vite 6 en mode develop, la liste est ignorée.

---

### Problème 2 : Erreur "Node.js version incompatible"

**Symptôme** :
```
error Strapi requires Node.js >=18.0.0 <=22.x.x
```

**Cause** : Système a Node.js 23+

**Solution** : Utiliser Docker avec Node 22

```dockerfile
# Dockerfile
FROM node:22-slim  # ← Version spécifique
```

**Alternative locale** : Installer Node 22 via NVM (pas d'admin requis)

---

### Problème 3 : Rebuild admin panel ne prend pas effet

**Symptôme** :
- Modification `vite.config.ts` ignorée
- Config anciennes toujours actives

**Cause** : Cache du build précédent

**Solution** :

```bash
# 1. Build complet avec --no-cache
ssh root@69.62.108.82 "cd /opt/mon-backend && docker-compose build --no-cache"

# 2. Redémarrer proprement
ssh root@69.62.108.82 "cd /opt/mon-backend && docker-compose down && docker-compose up -d"

# 3. Vérifier logs
ssh root@69.62.108.82 "docker logs mon-strapi --tail=50"
```

**Alternative** : Build inside container

```bash
ssh root@69.62.108.82 "docker exec mon-strapi npm run build"
ssh root@69.62.108.82 "docker restart mon-strapi"
```

---

### Problème 4 : SQLite database locked

**Symptôme** :
```
Error: SQLITE_BUSY: database is locked
```

**Cause** : Plusieurs instances Strapi accèdent à la même DB

**Solution** :

```bash
# Arrêter TOUS les conteneurs Strapi
ssh root@69.62.108.82 "docker ps | grep strapi"
ssh root@69.62.108.82 "docker stop [tous-les-conteneurs-strapi]"

# Supprimer fichiers lock
ssh root@69.62.108.82 "rm -f /opt/mon-backend/data/.tmp/data.db-*"

# Redémarrer
ssh root@69.62.108.82 "cd /opt/mon-backend && docker-compose up -d"
```

---

### Problème 5 : Port 1337 déjà utilisé

**Symptôme** :
```
Error starting userland proxy: listen tcp4 0.0.0.0:1337: bind: address already in use
```

**Cause** : Autre Strapi ou service sur port 1337

**Solution** :

```bash
# Trouver qui utilise le port
ssh root@69.62.108.82 "lsof -i :1337"
ssh root@69.62.108.82 "docker ps | grep 1337"

# Option 1 : Arrêter l'autre service
ssh root@69.62.108.82 "docker stop [autre-conteneur]"

# Option 2 : Changer le port dans docker-compose.yml
# ports:
#   - "1338:1337"  # Port externe différent
```

---

### Problème 6 : Admin panel lent / ne charge pas

**Symptômes** :
- Page blanche
- Console : `Uncaught Error`
- Très lent

**Causes possibles** :

#### Cause 1 : Mode develop en production

**Solution** : Passer en mode production

```yaml
environment:
  - NODE_ENV=production  # Pas 'development' !
```

#### Cause 2 : Admin pas rebuild

**Solution** :

```bash
ssh root@69.62.108.82 "docker exec mon-strapi npm run build"
ssh root@69.62.108.82 "docker restart mon-strapi"
```

#### Cause 3 : Mémoire insuffisante

**Solution** : Augmenter limite mémoire Docker

```yaml
services:
  strapi:
    deploy:
      resources:
        limits:
          memory: 1G
```

---

## 🔄 Workflow de mise à jour

### Mise à jour du code Strapi

```bash
# 1. Modifier code localement
cd "C:\Users\JulienFernandez\OneDrive\Coding\_Projets de code\[PROJET]\mon-backoffice"

# 2. Transférer modifications
scp -r src/ root@69.62.108.82:/opt/mon-backend/backend/
scp -r config/ root@69.62.108.82:/opt/mon-backend/backend/

# 3. Rebuild Docker
ssh root@69.62.108.82 "cd /opt/mon-backend && docker-compose build --no-cache"

# 4. Redémarrer
ssh root@69.62.108.82 "cd /opt/mon-backend && docker-compose down && docker-compose up -d"

# 5. Vérifier
ssh root@69.62.108.82 "docker logs mon-strapi --tail=30"
```

### Mise à jour Strapi version

```bash
# 1. Localement, mettre à jour package.json
cd mon-backoffice
npm install @strapi/strapi@latest

# 2. Transférer package.json et package-lock.json
scp package.json package-lock.json root@69.62.108.82:/opt/mon-backend/backend/

# 3. Rebuild complet
ssh root@69.62.108.82 "cd /opt/mon-backend && docker-compose build --no-cache && docker-compose down && docker-compose up -d"
```

---

## 📊 Configuration optimale

### docker-compose.yml complet

```yaml
version: '3.8'

services:
  strapi:
    build: .
    container_name: mon-strapi
    ports:
      - "1337:1337"
    volumes:
      # Données persistantes
      - ./data:/app/.tmp
      - ./uploads:/app/public/uploads
    restart: unless-stopped
    environment:
      # ⚠️ Production obligatoire avec reverse proxy
      - NODE_ENV=production
      - TZ=Europe/Paris

      # URL admin (pour génération liens)
      - STRAPI_ADMIN_BACKEND_URL=http://admin.mon-site.srv759970.hstgr.cloud

      # Network
      - HOST=0.0.0.0
      - PORT=1337

      # Database (SQLite par défaut)
      # - DATABASE_CLIENT=sqlite
      # - DATABASE_FILENAME=.tmp/data.db

    # Limites ressources (optionnel)
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
```

### vite.config.ts optimal

```typescript
// src/admin/vite.config.ts
import { mergeConfig, type UserConfig } from 'vite';

export default (config: UserConfig) => {
  return mergeConfig(config, {
    server: {
      // En production, allowedHosts n'est pas nécessaire
      // Mais on le met au cas où
      allowedHosts: true,
    },
  });
};
```

---

## 🔍 Commandes de diagnostic

### Vérifier status Strapi

```bash
# Container en cours
ssh root@69.62.108.82 "docker ps | grep strapi"

# Logs récents
ssh root@69.62.108.82 "docker logs mon-strapi --tail=50"

# Logs en temps réel
ssh root@69.62.108.82 "docker logs -f mon-strapi"

# Entrer dans le container
ssh root@69.62.108.82 "docker exec -it mon-strapi sh"
```

### Tester accès

```bash
# Direct (sans Nginx)
ssh root@69.62.108.82 "curl -I http://localhost:1337/admin"

# Via Nginx proxy
ssh root@69.62.108.82 "curl -I -H 'Host: admin.mon-site.srv759970.hstgr.cloud' http://localhost/admin"
```

### Vérifier fichiers

```bash
# Structure Strapi
ssh root@69.62.108.82 "ls -la /opt/mon-backend/backend/"

# vite.config.ts existe ?
ssh root@69.62.108.82 "cat /opt/mon-backend/backend/src/admin/vite.config.ts"

# Database SQLite
ssh root@69.62.108.82 "ls -lh /opt/mon-backend/data/"
```

---

## ✅ Checklist de déploiement

- [ ] Node.js 22 utilisé (Docker `node:22-slim`)
- [ ] Strapi créé avec `--quickstart --typescript`
- [ ] `vite.config.ts` créé dans `src/admin/`
- [ ] `allowedHosts: true` dans vite.config.ts
- [ ] `NODE_ENV=production` dans docker-compose.yml
- [ ] `STRAPI_ADMIN_BACKEND_URL` configuré
- [ ] Dockerfile avec `npm run build`
- [ ] docker-compose.yml avec volumes persistants
- [ ] Code transféré sur VPS (`/opt/mon-backend/backend/`)
- [ ] Docker build réussi
- [ ] Container démarré (`docker ps` affiche le container)
- [ ] Logs propres (pas de "host not allowed")
- [ ] Nginx configuré avec reverse proxy
- [ ] Nginx rechargé (`systemctl reload nginx`)
- [ ] Admin accessible via navigateur (HTTP 200)
- [ ] Compte admin créé

---

## 🎯 Cas réel : Site Cristina

**Déploiement** : Octobre 2025
**URL Admin** : http://admin.cristina.srv759970.hstgr.cloud/admin
**Container** : `cristina-strapi`
**Port** : 1337

**Problèmes rencontrés** :
1. ❌ "host not allowed" → Solution : Mode production + `allowedHosts: true`
2. ❌ Node 23 incompatible → Solution : Docker `node:22-slim`
3. ❌ Rebuild admin ignoré → Solution : `docker-compose build --no-cache`

**Temps de debug** : 3+ heures
**Avec ce guide** : 15 minutes

---

## 📚 Ressources

- [Strapi 5 Documentation](https://docs.strapi.io/)
- [Strapi Deployment Guide](https://docs.strapi.io/dev-docs/deployment)
- [Strapi GitHub Issue #23433](https://github.com/strapi/strapi/issues/23433) (allowedHosts bug)
- [Guide Nginx](../infrastructure/nginx.md)
- [Guide Docker VPS](./GUIDE_DEPLOIEMENT_VPS.md)

---

**Dernière mise à jour** : Octobre 2025
**Version** : 1.0
**Strapi déployés** : 1 (Cristina Admin)
**Heures économisées** : 3+ par déploiement
