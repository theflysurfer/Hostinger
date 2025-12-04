# Jokers Hockey - Site Web du Club

Site web vitrine pour le club de hockey sur glace Les Jokers, incluant actualités, équipes, boutique et informations de contact.

## Accès

- **URL Production**: https://jokers.xxx.fr
- **Tech Stack**: React + Vite (frontend) + Express (backend)
- **Base de données**: Neon PostgreSQL (serverless)
- **Port interne**: 5000 (configurable via `PORT`)

## Caractéristiques

- Application React moderne avec Vite
- Backend Express pour API et serving statique
- Base de données PostgreSQL via Neon
- ORM Drizzle pour gestion BDD
- UI avec shadcn/ui + Tailwind CSS
- Routing SPA avec Wouter
- Build optimisé pour production

## 🚀 Quick Start - Déploiement en 10 Minutes

### Prérequis

- Node.js 20.x ou supérieur
- Compte Neon Database (gratuit)
- Accès SSH au serveur Hostinger

### 1. Configuration de la Base de Données Neon

```bash
# 1. Créer un projet sur https://console.neon.tech
# 2. Créer une nouvelle database "jokers_prod"
# 3. Récupérer la connection string (format: postgresql://user:pass@host/db?sslmode=require)
```

### 2. Déploiement sur Hostinger VPS

#### A. Connexion et préparation du serveur

```bash
# Connexion SSH
ssh root@srv759970.hstgr.cloud

# Installation de Node.js 20.x (si pas déjà installé)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
apt-get install -y nodejs

# Vérification
node --version  # devrait afficher v20.x.x
npm --version

# Installation de PM2 pour la gestion des processus
npm install -g pm2

# Créer le répertoire pour l'application
mkdir -p /var/www/jokers
cd /var/www/jokers
```

#### B. Upload et build du projet

```bash
# Option 1: Via Git (recommandé)
git clone <votre-repo-git> .

# Option 2: Via SCP depuis votre machine locale
# Depuis votre machine Windows (PowerShell):
# scp -r "C:\Users\julien\OneDrive\Coding\_Projets de code\2025.11 Site Web Jokers\*" root@srv759970.hstgr.cloud:/var/www/jokers/

# Installer les dépendances
npm install --production=false

# Créer le fichier .env
cat > .env << 'EOF'
NODE_ENV=production
PORT=5000
DATABASE_URL=postgresql://user:password@ep-xxx.neon.tech/jokers_prod?sslmode=require
EOF

# IMPORTANT: Remplacer la DATABASE_URL par votre vraie connection string Neon

# Push du schéma vers la base de données
npm run db:push

# Build du projet
npm run build

# Vérifier que le dossier dist a été créé
ls -la dist/
ls -la dist/public/
```

#### C. Configuration de PM2

```bash
# Créer le fichier de configuration PM2
cat > ecosystem.config.cjs << 'EOF'
module.exports = {
  apps: [{
    name: 'jokers-hockey',
    script: './dist/index.js',
    instances: 1,
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production',
      PORT: 5000
    },
    env_file: '.env',
    max_memory_restart: '500M',
    error_file: './logs/error.log',
    out_file: './logs/output.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    autorestart: true,
    watch: false
  }]
}
EOF

# Créer le dossier logs
mkdir -p logs

# Démarrer l'application avec PM2
pm2 start ecosystem.config.cjs

# Sauvegarder la configuration PM2
pm2 save

# Configurer PM2 pour démarrer au boot
pm2 startup

# Vérifier le statut
pm2 status
pm2 logs jokers-hockey --lines 50
```

#### D. Configuration Nginx (Reverse Proxy)

```bash
# Créer la configuration Nginx pour le sous-domaine
cat > /etc/nginx/sites-available/jokers << 'EOF'
server {
    listen 80;
    server_name jokers.xxx.fr;

    # Logs
    access_log /var/log/nginx/jokers_access.log;
    error_log /var/log/nginx/jokers_error.log;

    # Redirection HTTP vers HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name jokers.xxx.fr;

    # SSL Configuration (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/jokers.xxx.fr/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/jokers.xxx.fr/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Logs
    access_log /var/log/nginx/jokers_ssl_access.log;
    error_log /var/log/nginx/jokers_ssl_error.log;

    # Sécurité
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Client body size (pour uploads)
    client_max_body_size 10M;

    # Proxy vers Node.js
    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Cache pour les assets statiques
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        proxy_pass http://localhost:5000;
        proxy_cache_valid 200 7d;
        proxy_cache_valid 404 1m;
        add_header Cache-Control "public, max-age=604800, immutable";
        access_log off;
    }
}
EOF

# Activer le site
ln -sf /etc/nginx/sites-available/jokers /etc/nginx/sites-enabled/

# Tester la configuration Nginx
nginx -t

# Si le test est OK, recharger Nginx
systemctl reload nginx
```

#### E. Configuration SSL avec Let's Encrypt

```bash
# Installer Certbot si pas déjà fait
apt-get update
apt-get install -y certbot python3-certbot-nginx

# Obtenir le certificat SSL
# IMPORTANT: Assurez-vous que le DNS jokers.xxx.fr pointe vers votre serveur AVANT cette étape
certbot --nginx -d jokers.xxx.fr

# Le renouvellement automatique est configuré par défaut
# Tester le renouvellement:
certbot renew --dry-run
```

### 3. Configuration DNS

Dans votre panneau de contrôle Hostinger ou votre registrar de domaine:

```
Type: A
Nom: jokers
Valeur: [IP de srv759970.hstgr.cloud]
TTL: 3600
```

Attendez la propagation DNS (5-30 minutes).

## 🔧 Maintenance et Mises à Jour

### Déployer une nouvelle version

```bash
# Connexion SSH
ssh root@srv759970.hstgr.cloud
cd /var/www/jokers

# Pull des dernières modifications (si Git)
git pull origin main

# Ou upload via SCP si pas de Git

# Installer les nouvelles dépendances
npm install --production=false

# Rebuild
npm run build

# Push des migrations de base de données si nécessaire
npm run db:push

# Redémarrer l'application
pm2 restart jokers-hockey

# Vérifier les logs
pm2 logs jokers-hockey --lines 50
```

### Commandes utiles PM2

```bash
# Voir le statut
pm2 status

# Voir les logs en temps réel
pm2 logs jokers-hockey

# Voir les logs des 100 dernières lignes
pm2 logs jokers-hockey --lines 100

# Redémarrer l'application
pm2 restart jokers-hockey

# Arrêter l'application
pm2 stop jokers-hockey

# Démarrer l'application
pm2 start jokers-hockey

# Supprimer l'application de PM2
pm2 delete jokers-hockey

# Voir les métriques (CPU, RAM)
pm2 monit
```

### Vérifier les logs

```bash
# Logs PM2
pm2 logs jokers-hockey

# Logs Nginx
tail -f /var/log/nginx/jokers_access.log
tail -f /var/log/nginx/jokers_error.log

# Logs de l'application (si configuré)
tail -f /var/www/jokers/logs/output.log
tail -f /var/www/jokers/logs/error.log
```

### Backup de la base de données

```bash
# La base de données Neon fait des backups automatiques
# Pour un backup manuel via Neon console:
# 1. Aller sur https://console.neon.tech
# 2. Sélectionner le projet jokers_prod
# 3. Branches > Create branch (pour créer une copie)

# Pour un dump SQL local:
pg_dump "postgresql://user:password@ep-xxx.neon.tech/jokers_prod?sslmode=require" > backup_$(date +%Y%m%d).sql
```

## 📊 Monitoring

### Vérifier l'état de santé

```bash
# Vérifier que le serveur répond
curl -I https://jokers.xxx.fr

# Vérifier le processus Node.js
pm2 status

# Vérifier l'utilisation des ressources
pm2 monit

# Vérifier les connexions à la base de données
# (depuis l'interface Neon Console)
```

### Alertes et notifications

```bash
# Configurer PM2 Keymetrics (optionnel) pour monitoring avancé
pm2 link <secret_key> <public_key>
```

## 🔐 Variables d'Environnement

Fichier `.env` à créer dans `/var/www/jokers/`:

```bash
# Environnement
NODE_ENV=production

# Port du serveur (doit correspondre à la config Nginx)
PORT=5000

# Base de données Neon
DATABASE_URL=postgresql://username:password@ep-xxx-xxx.neon.tech/jokers_prod?sslmode=require
```

## 🐛 Troubleshooting

### Le site ne se charge pas

```bash
# 1. Vérifier que l'application tourne
pm2 status

# 2. Vérifier les logs
pm2 logs jokers-hockey --lines 50

# 3. Vérifier Nginx
systemctl status nginx
nginx -t

# 4. Vérifier les ports
netstat -tulpn | grep :5000
netstat -tulpn | grep :443

# 5. Redémarrer tout
pm2 restart jokers-hockey
systemctl restart nginx
```

### Erreur 502 Bad Gateway

```bash
# L'application Node.js ne répond pas
pm2 logs jokers-hockey

# Vérifier si le port 5000 est bien utilisé
netstat -tulpn | grep :5000

# Redémarrer l'application
pm2 restart jokers-hockey
```

### Erreur de base de données

```bash
# Vérifier la variable DATABASE_URL
cat /var/www/jokers/.env

# Tester la connexion à la base
# Installer psql si nécessaire: apt-get install -y postgresql-client
psql "$DATABASE_URL" -c "SELECT version();"

# Vérifier que le schéma est à jour
cd /var/www/jokers
npm run db:push
```

### Application lente ou qui crash

```bash
# Vérifier l'utilisation mémoire
pm2 monit

# Si trop de mémoire utilisée, augmenter la limite dans ecosystem.config.cjs
# Puis redémarrer:
pm2 restart jokers-hockey
```

## 📝 Structure du Projet

```
jokers-hockey/
├── client/                 # Frontend React
│   ├── src/
│   │   ├── components/    # Composants React
│   │   ├── pages/         # Pages du site
│   │   ├── hooks/         # Custom hooks
│   │   └── lib/           # Utilitaires
│   └── index.html
├── server/                # Backend Express
│   ├── index.ts           # Point d'entrée
│   ├── routes.ts          # Routes API
│   └── vite.ts            # Config Vite dev/prod
├── shared/                # Code partagé
│   └── schema.ts          # Schéma Drizzle
├── dist/                  # Build production
│   ├── index.js           # Serveur compilé
│   └── public/            # Assets statiques
├── package.json
├── vite.config.ts
├── drizzle.config.ts
└── ecosystem.config.cjs   # Config PM2 (à créer)
```

## 🔄 Workflow de Développement

```bash
# Développement local
npm run dev              # Démarre dev server (port 5000)

# Vérification TypeScript
npm run check

# Push du schéma BDD
npm run db:push

# Build production
npm run build

# Test du build localement
NODE_ENV=production npm start
```

## 📚 Technologies Utilisées

- **Frontend**: React 18, Vite 5, TypeScript
- **UI**: shadcn/ui, Tailwind CSS, Radix UI
- **Backend**: Express, Node.js
- **Base de données**: Neon PostgreSQL, Drizzle ORM
- **Routing**: Wouter (SPA routing)
- **Build**: Vite (frontend), esbuild (backend)
- **Process Manager**: PM2
- **Reverse Proxy**: Nginx
- **SSL**: Let's Encrypt

## 🔗 Liens Utiles

- **Neon Console**: https://console.neon.tech
- **Documentation Drizzle**: https://orm.drizzle.team/docs/overview
- **PM2 Documentation**: https://pm2.keymetrics.io/docs/usage/quick-start/
- **Nginx Documentation**: https://nginx.org/en/docs/

## 📞 Support

Pour toute question ou problème:
- Vérifier les logs PM2 et Nginx
- Consulter la documentation des technologies utilisées
- Vérifier l'état de la base de données sur Neon Console

## ⚠️ Notes Importantes

1. **Sécurité**: Ne jamais commiter le fichier `.env` dans Git
2. **Backup**: Neon fait des backups automatiques, mais créer des branches régulièrement
3. **SSL**: Le certificat Let's Encrypt se renouvelle automatiquement tous les 90 jours
4. **Mémoire**: Surveiller l'utilisation mémoire avec `pm2 monit`
5. **Updates**: Tester les mises à jour sur une branche Neon de staging avant production
