# 🚀 Plan d'Action - Sécurisation VPS & Infrastructure Entreprise

**Dernière mise à jour** : 2025-01-17
**Contexte** : Nouvelle entreprise (4 personnes), VPS Hostinger srv759970.hstgr.cloud, besoin Office mais pas full 365

---

## 📊 Vue d'ensemble

### Périmètres

1. **VPS Hostinger** (srv759970.hstgr.cloud)
   - IP fixe : 69.62.108.82
   - Multiples services Docker (Whisper, Strapi, WordPress, Node...)
   - Actuellement : Basic Auth + accès SSH root pour Claude Code

2. **Nouvelle entreprise (4 utilisateurs)**
   - Besoin Office obligatoire
   - Emails simples
   - Calendriers/contacts partagés obligatoires
   - Collaboration avec clients Teams/SharePoint occasionnelle
   - Budget optimisé, stack technique maîtrisée

---

## 🔴 PRIORITÉ 1 : Sécurisation VPS (URGENT - Cette semaine)

### 1.1 Créer compte automation et révoquer root SSH

**Pourquoi** : Claude Code a actuellement accès root illimité = risque maximum

**Actions** :

```bash
# 1. Créer compte automation
ssh root@69.62.108.82 <<'EOF'
adduser --disabled-password --gecos '' automation
usermod -aG docker automation
mkdir -p /home/automation/.ssh
cp /root/.ssh/authorized_keys /home/automation/.ssh/
chown -R automation:automation /home/automation/.ssh
chmod 700 /home/automation/.ssh
chmod 600 /home/automation/.ssh/authorized_keys
EOF

# 2. Configurer sudo restreint
ssh root@69.62.108.82 "cat > /etc/sudoers.d/automation" <<'SUDO'
# Services systemd
automation ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart nginx
automation ALL=(ALL) NOPASSWD: /usr/bin/systemctl reload nginx
automation ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart *.service
automation ALL=(ALL) NOPASSWD: /usr/bin/systemctl status *

# Docker (déjà dans groupe, mais sudo utile)
automation ALL=(ALL) NOPASSWD: /usr/bin/docker
automation ALL=(ALL) NOPASSWD: /usr/bin/docker-compose

# Nginx
automation ALL=(ALL) NOPASSWD: /usr/bin/nginx -t
automation ALL=(ALL) NOPASSWD: /usr/bin/nginx -T

# Certbot
automation ALL=(ALL) NOPASSWD: /usr/bin/certbot *

# UFW
automation ALL=(ALL) NOPASSWD: /usr/bin/ufw *

# WordPress CLI
automation ALL=(ALL) NOPASSWD: /usr/bin/wp *

# APT (lecture + whitelist)
automation ALL=(ALL) NOPASSWD: /usr/bin/apt-get update
automation ALL=(ALL) NOPASSWD: /usr/bin/apt-get install nginx docker.io certbot curl git rsync htpasswd python3-certbot-nginx
SUDO

# 3. Tester accès automation
ssh automation@69.62.108.82 "whoami && sudo nginx -t"

# 4. Désactiver root SSH (APRÈS vérification)
ssh automation@69.62.108.82 <<'EOF'
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl reload sshd
EOF
```

**⚠️ Important** : Mettre à jour tes scripts `.bat` pour utiliser `automation@` au lieu de `root@`

**Statut** : ⏳ À faire
**Durée estimée** : 30 min
**Test de validation** : `ssh automation@69.62.108.82 "sudo systemctl status nginx"`

---

### 1.2 Activer UFW + Fail2ban

**Pourquoi** : Pare-feu + protection bruteforce

**Actions** :

```bash
# UFW
ssh automation@69.62.108.82 <<'EOF'
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80,443/tcp
sudo ufw --force enable
sudo ufw status verbose
EOF

# Fail2ban
ssh automation@69.62.108.82 <<'EOF'
sudo apt update && sudo apt install -y fail2ban

sudo cat > /etc/fail2ban/jail.d/custom.conf <<'JAIL'
[sshd]
enabled = true
port = 22
maxretry = 3
bantime = 3600

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/*error.log
maxretry = 5
bantime = 3600

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/*error.log
maxretry = 10
findtime = 60
bantime = 600
JAIL

sudo systemctl enable fail2ban
sudo systemctl restart fail2ban
EOF
```

**Statut** : ⏳ À faire
**Durée estimée** : 30 min
**Test de validation** : `ssh automation@69.62.108.82 "sudo fail2ban-client status"`

---

### 1.3 Remplacer Basic Auth par OAuth2-proxy

**Pourquoi** : Basic Auth = mot de passe en base64, facilement décodable. OAuth2 = SSO avec Google

**Prérequis** :
1. Créer une Google OAuth App (Google Cloud Console)
2. Obtenir Client ID et Client Secret

**Actions** :

```bash
# 1. Créer structure
ssh automation@69.62.108.82 "sudo mkdir -p /opt/oauth2-proxy"

# 2. Générer cookie secret
python3 -c 'import os,base64; print(base64.b64encode(os.urandom(32)).decode())'
# Sauvegarder la sortie
```

Créer `/opt/oauth2-proxy/docker-compose.yml` :

```yaml
version: '3.8'

services:
  oauth2-proxy:
    image: quay.io/oauth2-proxy/oauth2-proxy:latest
    container_name: oauth2-proxy
    restart: unless-stopped
    ports:
      - "4180:4180"
    environment:
      OAUTH2_PROXY_PROVIDER: google
      OAUTH2_PROXY_CLIENT_ID: "TON_CLIENT_ID.apps.googleusercontent.com"
      OAUTH2_PROXY_CLIENT_SECRET: "TON_CLIENT_SECRET"
      OAUTH2_PROXY_COOKIE_SECRET: "LE_SECRET_GENERE_CI_DESSUS"

      # Domaines
      OAUTH2_PROXY_EMAIL_DOMAINS: "*"
      OAUTH2_PROXY_WHITELIST_DOMAINS: ".srv759970.hstgr.cloud"

      # Cookies
      OAUTH2_PROXY_COOKIE_SECURE: "true"
      OAUTH2_PROXY_COOKIE_HTTPONLY: "true"
      OAUTH2_PROXY_COOKIE_SAMESITE: "lax"
      OAUTH2_PROXY_COOKIE_DOMAINS: ".srv759970.hstgr.cloud"

      # Redirect
      OAUTH2_PROXY_REDIRECT_URL: "https://auth.srv759970.hstgr.cloud/oauth2/callback"

      # Mode auth-only
      OAUTH2_PROXY_HTTP_ADDRESS: "0.0.0.0:4180"
      OAUTH2_PROXY_UPSTREAMS: "static://202"

      # Logs
      OAUTH2_PROXY_REQUEST_LOGGING: "true"
      OAUTH2_PROXY_AUTH_LOGGING: "true"

networks:
  default:
    external:
      name: proxy
```

**Template Nginx** (exemple pour Whisper) :

```nginx
server {
    listen 443 ssl http2;
    server_name whisper.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/whisper.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/whisper.srv759970.hstgr.cloud/privkey.pem;

    # Auth OAuth2
    location /oauth2/ {
        proxy_pass http://localhost:4180;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        auth_request /oauth2/auth;
        error_page 401 = /oauth2/sign_in;

        auth_request_set $user $upstream_http_x_auth_request_user;
        auth_request_set $email $upstream_http_x_auth_request_email;
        proxy_set_header X-User $user;
        proxy_set_header X-Email $email;

        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**Statut** : ⏳ À faire
**Durée estimée** : 2h
**Test de validation** : Accéder à https://whisper.srv759970.hstgr.cloud → redirection Google OAuth

---

### 1.4 Setup Restic + Dropbox

**Pourquoi** : Sauvegardes automatiques chiffrées, versionnées

**Actions** :

```bash
# 1. Installer
ssh automation@69.62.108.82 "sudo apt install -y rclone restic"

# 2. Configurer rclone (interactif)
ssh automation@69.62.108.82 "rclone config"
# Suivre assistant : choisir Dropbox, autoriser via navigateur

# 3. Init Restic
ssh automation@69.62.108.82 <<'EOF'
export RESTIC_REPOSITORY="rclone:dropbox:Backups/VPS-Hostinger"
export RESTIC_PASSWORD_FILE="/home/automation/.restic-password"
echo "MOT_DE_PASSE_FORT_RESTIC" > ~/.restic-password
chmod 600 ~/.restic-password
restic init
EOF
```

**Script backup** `/usr/local/bin/backup-vps.sh` :

```bash
#!/bin/bash
set -e

export RESTIC_REPOSITORY="rclone:dropbox:Backups/VPS-Hostinger"
export RESTIC_PASSWORD_FILE="/home/automation/.restic-password"

DATE=$(date +%F-%H%M)
BACKUP_DIR="/tmp/backup-$DATE"

echo "🔄 Début backup $DATE"
mkdir -p $BACKUP_DIR

# 1. MySQL (WordPress)
echo "📦 Backup MySQL..."
sudo mysqldump -u root --all-databases > $BACKUP_DIR/mysql-all.sql 2>/dev/null || echo "Pas de MySQL root password configuré"

# 2. Configs système
echo "📦 Backup configs..."
sudo tar czf $BACKUP_DIR/configs-system.tar.gz \
  /etc/nginx \
  /etc/letsencrypt \
  /etc/ssh \
  /etc/fail2ban \
  /etc/sudoers.d

# 3. Volumes Docker importants
echo "📦 Backup Docker volumes..."
for vol in $(docker volume ls -q | grep -E 'data|uploads'); do
  docker run --rm \
    -v $vol:/data \
    -v $BACKUP_DIR:/backup \
    alpine tar czf /backup/docker-vol-$vol.tar.gz /data 2>/dev/null || true
done

# 4. Apps critiques (/opt)
echo "📦 Backup applications..."
sudo tar czf $BACKUP_DIR/opt-apps.tar.gz \
  --exclude='*/node_modules' \
  --exclude='*/__pycache__' \
  --exclude='*/venv' \
  /opt

# 5. Restic backup
echo "☁️  Upload vers Dropbox..."
restic backup $BACKUP_DIR \
  --tag automated \
  --tag vps-hostinger

# 6. Nettoyage local
rm -rf $BACKUP_DIR

# 7. Rétention
echo "🗑️  Nettoyage anciennes sauvegardes..."
restic forget \
  --keep-daily 7 \
  --keep-weekly 4 \
  --keep-monthly 6 \
  --prune

echo "✅ Backup terminé !"
restic snapshots --last
```

```bash
# Déployer script
scp backup-vps.sh automation@69.62.108.82:/tmp/
ssh automation@69.62.108.82 "sudo mv /tmp/backup-vps.sh /usr/local/bin/ && sudo chmod +x /usr/local/bin/backup-vps.sh"

# Cron quotidien (3h du matin)
ssh automation@69.62.108.82 <<'EOF'
(crontab -l 2>/dev/null; echo "0 3 * * * /usr/local/bin/backup-vps.sh >> /var/log/backup-vps.log 2>&1") | crontab -
EOF

# Test manuel
ssh automation@69.62.108.82 "/usr/local/bin/backup-vps.sh"
```

**Statut** : ⏳ À faire
**Durée estimée** : 1h
**Test de validation** : `ssh automation@69.62.108.82 "restic snapshots"`

---

### 1.5 Docker sécurisé (progressif)

**Pourquoi** : Limiter les droits des conteneurs

**Actions** : À appliquer sur les NOUVELLES apps (pas urgent pour existantes)

```yaml
# Template pour nouvelles apps
services:
  mon-app:
    image: node:20-alpine
    user: "1000:1000"  # Non-root
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    # read_only: true  # Tester app par app
    tmpfs:
      - /tmp
    volumes:
      - ./config:/app/config:ro  # Read-only où possible
```

**Statut** : 📝 Best practice (à appliquer progressivement)

---

## 🟡 PRIORITÉ 2 : Stack Entreprise (Semaine 2-3)

### 2.1 Décisions d'architecture

**Synthèse besoins** :
- 4 utilisateurs
- Office obligatoire (compatibilité .docx/.xlsx/.pptx)
- Emails simples
- Calendriers/contacts partagés obligatoires
- Collaboration occasionnelle avec clients Teams/SharePoint
- Budget optimisé

**Recommandation stratégie hybride** :

| Fonction | Solution retenue | Justification |
|----------|------------------|---------------|
| **Bureautique** | 2x Microsoft 365 Apps for Business + ONLYOFFICE (Nextcloud) | 2 licences MS pour compat client externe, ONLYOFFICE pour interne |
| **Email/Calendrier/Contacts** | Infomaniak Mail Business (ou Proton Business) | Souverain, CalDAV/CardDAV, pas de maintenance serveur |
| **Stockage/Collaboration** | Nextcloud + ONLYOFFICE Docs | Souverain, co-édition, contrôle total |
| **Chat** | Rocket.Chat + Jitsi | Open source, auto-hébergé |
| **Visio** | Jitsi (interne) + 2x Teams (externe) | Jitsi pour réunions internes, Teams pour clients qui invitent |

**Budget mensuel estimé** :

| Poste | Coût/mois (4 users) |
|-------|---------------------|
| 2x Microsoft 365 Apps for Business | 2 × 8,80€ = **17,60€** |
| Infomaniak Mail Business | 4 × 7,50€ = **30€** |
| VPS Nextcloud/Rocket.Chat (2 vCPU) | **15€** |
| **TOTAL** | **62,60€/mois** |

**Comparé à full M365 E3** : 4 × 34€ = 136€/mois → **Économie : 73€/mois (880€/an)**

---

### 2.2 Setup Nextcloud + ONLYOFFICE

**Serveur** : VPS dédié ou sur Hostinger actuel ?

**Option A** : VPS dédié Infomaniak (recommandé)
- Nextcloud Swiss Made 100 GB : 6,50€/mois
- Inclut ONLYOFFICE, backups, maintenance

**Option B** : Auto-hébergé sur srv759970.hstgr.cloud

```yaml
# /opt/nextcloud/docker-compose.yml
version: '3.8'

services:
  nextcloud-db:
    image: postgres:16-alpine
    restart: unless-stopped
    volumes:
      - nextcloud-db:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: nextcloud
      POSTGRES_USER: nextcloud
      POSTGRES_PASSWORD: ${DB_PASSWORD}

  nextcloud:
    image: nextcloud:latest
    restart: unless-stopped
    ports:
      - "8505:80"
    volumes:
      - nextcloud-data:/var/www/html
    environment:
      POSTGRES_HOST: nextcloud-db
      POSTGRES_DB: nextcloud
      POSTGRES_USER: nextcloud
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      NEXTCLOUD_ADMIN_USER: admin
      NEXTCLOUD_ADMIN_PASSWORD: ${ADMIN_PASSWORD}
      NEXTCLOUD_TRUSTED_DOMAINS: nextcloud.srv759970.hstgr.cloud
    depends_on:
      - nextcloud-db

  onlyoffice:
    image: onlyoffice/documentserver:latest
    restart: unless-stopped
    ports:
      - "8506:80"
    environment:
      JWT_ENABLED: "true"
      JWT_SECRET: ${JWT_SECRET}

volumes:
  nextcloud-db:
  nextcloud-data:
```

**Statut** : ⏳ À décider (VPS dédié ou auto-hébergé)
**Durée estimée** : 2h

---

### 2.3 Setup Rocket.Chat + Jitsi

```yaml
# /opt/rocketchat/docker-compose.yml
version: '3.8'

services:
  rocketchat-db:
    image: mongo:6
    restart: unless-stopped
    volumes:
      - rocketchat-db:/data/db
    command: mongod --oplogSize 128 --replSet rs0

  rocketchat:
    image: rocket.chat:latest
    restart: unless-stopped
    ports:
      - "8507:3000"
    environment:
      MONGO_URL: mongodb://rocketchat-db:27017/rocketchat?replicaSet=rs0
      MONGO_OPLOG_URL: mongodb://rocketchat-db:27017/local?replicaSet=rs0
      ROOT_URL: https://chat.srv759970.hstgr.cloud
      PORT: 3000
    depends_on:
      - rocketchat-db

volumes:
  rocketchat-db:
```

**Post-install** :
1. Installer app Jitsi Meet depuis Marketplace
2. Configurer URL Jitsi : https://meet.jit.si (ou instance self-hosted)

**Statut** : ⏳ À faire
**Durée estimée** : 2h

---

### 2.4 Licences Microsoft 365

**À acheter** :
- 2x Microsoft 365 Apps for Business (8,80€/user/mois)
- Permet : Word/Excel/PowerPoint desktop + 1 To OneDrive (optionnel)
- **Pas besoin** de Exchange, SharePoint, Teams complet

**Usage** :
- Personne 1 & 2 : licences MS (interaction fréquente clients)
- Personne 3 & 4 : ONLYOFFICE uniquement

**Cas d'usage Teams** :
- Client t'invite → rejoindre en guest (gratuit)
- Tu invites client → utiliser les 2 comptes licenciés

**Statut** : ⏳ À acheter
**Durée estimée** : 30 min

---

### 2.5 Infrastructure bases de données + Monitoring (MongoDB + PostgreSQL + Grafana)

**Objectif :** Stack centralisée pour bases de données et monitoring des services

**Pourquoi :**
- Bases de données partagées entre applications (éviter 1 instance par app)
- Monitoring unifié de tous les services Docker
- Alerting sur métriques critiques (CPU, RAM, disk, uptime)

**Architecture :**

```yaml
# /opt/databases-monitoring/docker-compose.yml
version: '3.8'

services:
  # MongoDB - Base NoSQL partagée
  mongodb:
    image: mongo:7
    container_name: mongodb-shared
    restart: unless-stopped
    ports:
      - "27017:27017"
    volumes:
      - mongodb-data:/data/db
      - mongodb-config:/data/configdb
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD}
    command: mongod --auth

  # PostgreSQL - Base SQL partagée
  postgresql:
    image: postgres:17-alpine
    container_name: postgresql-shared
    restart: unless-stopped
    ports:
      - "5432:5432"
    volumes:
      - postgresql-data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Grafana - Dashboards monitoring
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
      GF_SERVER_ROOT_URL: https://grafana.srv759970.hstgr.cloud
      GF_INSTALL_PLUGINS: grafana-clock-panel,grafana-simple-json-datasource
    depends_on:
      - prometheus

  # Prometheus - Collecte métriques
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - prometheus-data:/prometheus
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=90d'

  # Node Exporter - Métriques système VPS
  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    restart: unless-stopped
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'

  # cAdvisor - Métriques Docker containers
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    restart: unless-stopped
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    privileged: true

volumes:
  mongodb-data:
  mongodb-config:
  postgresql-data:
  grafana-data:
  prometheus-data:
```

**Configuration Prometheus** (`prometheus/prometheus.yml`) :

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Métriques système VPS
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  # Métriques Docker containers
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  # Métriques Prometheus lui-même
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Métriques MongoDB (via mongodb_exporter si installé)
  - job_name: 'mongodb'
    static_configs:
      - targets: ['mongodb-exporter:9216']

  # Métriques PostgreSQL (via postgres_exporter si installé)
  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres-exporter:9187']
```

**Dashboards Grafana pré-configurés :**

1. **Dashboard VPS Système** :
   - CPU usage par core
   - RAM usage (used/free/cache)
   - Disk I/O et espace disque
   - Network traffic
   - Load average

2. **Dashboard Docker Containers** :
   - Containers running/stopped
   - CPU/RAM par container
   - Network I/O par container
   - Restart count
   - Top 10 containers by resource usage

3. **Dashboard Databases** :
   - MongoDB : connections, queries/sec, storage size
   - PostgreSQL : connections, transactions/sec, cache hit ratio

**Déploiement :**

```bash
# 1. Créer structure
ssh automation@69.62.108.82 "mkdir -p /opt/databases-monitoring/{prometheus,grafana/provisioning}"

# 2. Créer configs
cat > prometheus.yml <<'PROM'
[Contenu du fichier prometheus.yml ci-dessus]
PROM

scp prometheus.yml automation@69.62.108.82:/opt/databases-monitoring/prometheus/

# 3. Configurer .env
cat > .env <<'ENV'
MONGO_ROOT_PASSWORD=genere_password_fort_mongo
POSTGRES_PASSWORD=genere_password_fort_postgres
GRAFANA_PASSWORD=genere_password_fort_grafana
ENV

scp .env automation@69.62.108.82:/opt/databases-monitoring/

# 4. Démarrer stack
ssh automation@69.62.108.82 <<'EOF'
cd /opt/databases-monitoring
docker-compose up -d
docker-compose logs -f
EOF

# 5. Configurer Nginx pour Grafana
ssh automation@69.62.108.82 <<'NGINX'
cat > /etc/nginx/sites-available/grafana <<'CONF'
server {
    listen 443 ssl http2;
    server_name grafana.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/grafana.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/grafana.srv759970.hstgr.cloud/privkey.pem;

    include snippets/basic-auth.conf;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
CONF

ln -sf /etc/nginx/sites-available/grafana /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
NGINX

# 6. Certificat SSL
ssh automation@69.62.108.82 "certbot --nginx -d grafana.srv759970.hstgr.cloud --non-interactive --agree-tos --email julien.fernandez.work@gmail.com"
```

**Utilisation des bases de données partagées :**

**MongoDB - Connexion depuis applications :**
```javascript
// Node.js
const { MongoClient } = require('mongodb');
const uri = "mongodb://admin:PASSWORD@69.62.108.82:27017/?authSource=admin";
const client = new MongoClient(uri);
```

**PostgreSQL - Connexion depuis applications :**
```python
# Python
import psycopg2
conn = psycopg2.connect(
    host="69.62.108.82",
    port=5432,
    database="myapp_db",
    user="myapp_user",
    password="myapp_password"
)
```

**Créer bases et users applicatifs :**

```bash
# MongoDB - Créer DB et user pour application
ssh automation@69.62.108.82 <<'EOF'
docker exec -it mongodb-shared mongosh -u admin -p PASSWORD --authenticationDatabase admin <<'MONGO'
use rocketchat
db.createUser({
  user: "rocketchat",
  pwd: "rocketchat_password",
  roles: [{ role: "readWrite", db: "rocketchat" }]
})
MONGO
EOF

# PostgreSQL - Créer DB et user pour application
ssh automation@69.62.108.82 <<'EOF'
docker exec -it postgresql-shared psql -U admin -c "
CREATE DATABASE nextcloud;
CREATE USER nextcloud WITH PASSWORD 'nextcloud_password';
GRANT ALL PRIVILEGES ON DATABASE nextcloud TO nextcloud;
"
EOF
```

**URLs d'accès :**

- **Grafana** : https://grafana.srv759970.hstgr.cloud (admin/GRAFANA_PASSWORD)
- **Prometheus** : http://69.62.108.82:9090 (métriques brutes)
- **MongoDB** : mongodb://69.62.108.82:27017
- **PostgreSQL** : postgresql://69.62.108.82:5432

**Alerting Grafana (optionnel) :**

Configuration d'alertes email/Slack sur :
- CPU > 80% pendant 5min
- RAM > 90% pendant 5min
- Disk > 85%
- Container down/restart
- Database connections > 80% max

**Statut** : ⏳ À faire
**Durée estimée** : 2-3h
**Test de validation** : Accès Grafana + dashboards fonctionnels + connexion test aux DBs

---

## 🟢 PRIORITÉ 3 : Features avancées (Optionnel, après P1+P2)

### 3.1 Pipeline transcription/résumé réunions

> **📄 Analyse détaillée disponible :** Voir **[ANALYSE_JITSI_WITH_INTELLIGENT_TRANSCRIPTION.md](ANALYSE_JITSI_WITH_INTELLIGENT_TRANSCRIPTION.md)** pour architecture complète avec OCR local optimisé

**Contexte :** ~5h réunions/semaine, pas de GPU disponible, **OCR local** avec détection intelligente de slides

**⚠️ Architecture mise à jour :** La solution initialement prévue avec Claude Vision API (110€/mois) a été remplacée par une solution 100% locale et gratuite utilisant PaddleOCR + ImageHash. Détails complets dans le document d'analyse.

**Architecture adaptée** :

```
┌─────────┐     ┌───────────┐     ┌──────────────────────┐
│  Jitsi  │────▶│   Jibri   │────▶│ faster-whisper CPU   │ (déjà installé port 8001)
│ Meeting │     │ Recording │     │ Transcription audio  │
└─────────┘     └───────────┘     └──────────┬───────────┘
                      │                       │
                      ▼                       │
                 ┌─────────┐                  │
                 │  MinIO  │                  │
                 │ Storage │                  │
                 └────┬────┘                  │
                      │                       │
                      └───────────┬───────────┘
                                  ▼
                     ┌─────────────────────────┐
                     │   Transcription API     │
                     │   (FastAPI + Redis)     │
                     └────────────┬────────────┘
                                  │
                     ┌────────────┴──────────────┐
                     ▼                           ▼
          ┌──────────────────┐       ┌──────────────────┐
          │ Claude 3.5 Vision│       │  pyannote.audio  │
          │ OCR screenshots  │       │  Diarization CPU │
          └──────────────────┘       └──────────────────┘
                     │                           │
                     └────────────┬──────────────┘
                                  ▼
                     ┌─────────────────────────┐
                     │  Ollama (qwen2.5:7b)    │
                     │  Résumé + Action Items  │
                     └────────────┬────────────┘
                                  │
                     ┌────────────┴────────────┐
                     ▼                         ▼
          ┌──────────────────┐     ┌──────────────────┐
          │  Rocket.Chat     │     │     Notion       │
          │  Notification    │     │   Page résumé    │
          └──────────────────┘     └──────────────────┘
```

**Composants détaillés** :

1. **Jibri** : Enregistrement automatique réunions Jitsi (MP4 vidéo + audio)
2. **faster-whisper** : Transcription CPU (déjà opérationnel sur port 8001)
   - Modèle : base ou small (compromis vitesse/qualité CPU)
   - Temps : ~10min pour 1h réunion
3. **pyannote.audio** : Diarisation (qui parle quand) - CPU acceptable
   - Temps : ~15min pour 1h réunion
4. **Claude 3.5 Sonnet Vision** : OCR screenshots partages d'écran
   - 1 frame/10sec analysée
   - API Anthropic : 0.003$/image
   - Coût : 21,60€/mois pour 5h réunions/semaine
5. **Ollama qwen2.5:7b** : Résumé + extraction action items (déjà installé)
6. **PostgreSQL + Redis** : Metadata + job queue
7. **Intégrations** : Rocket.Chat webhook + Notion API

**Budget mensuel (5h réunions/semaine = 20h/mois)** :

| Poste | Coût ancien (Claude) | Coût nouveau (Local) |
|-------|----------------------|----------------------|
| faster-whisper (ton VPS) | Gratuit | Gratuit |
| Jibri (ton VPS) | Gratuit | Gratuit |
| MinIO storage (ton VPS) | Gratuit | Gratuit |
| ~~Claude API OCR (7200 frames/mois)~~ | ~~21,60€~~ | - |
| **PaddleOCR local (30-50 slides/h)** | - | **Gratuit** ✅ |
| **ImageHash détection slides** | - | **Gratuit** ✅ |
| **PySceneDetect détection screenshare** | - | **Gratuit** ✅ |
| Ollama résumé (ton VPS) | Gratuit | Gratuit |
| PostgreSQL + Redis (ton VPS) | Gratuit | Gratuit |
| **TOTAL** | ~~21,60€/mois~~ | **0€/mois** 🎉 |

**Économie réalisée :** 21,60€/mois → **260€/an** (vs Claude Vision API)

**Temps de processing** : ~30min pour 1h réunion (acceptable pour traitement asynchrone)

**Workflow utilisateur** :

1. User clique **"Enregistrer"** dans Jitsi
2. Réunion continue normalement
3. À la fin : **upload automatique** vers MinIO
4. **30min plus tard** : Notification Rocket.Chat avec résumé
5. Lien vers page Notion avec transcription complète

**Stack Docker Compose** :

```yaml
# /opt/transcription-pipeline/docker-compose.yml
version: '3.8'

services:
  jibri:
    image: jitsi/jibri:latest
    restart: unless-stopped
    volumes:
      - /tmp/recordings:/recordings
      - /dev/shm:/dev/shm
    cap_add:
      - SYS_ADMIN
      - NET_BIND_SERVICE
    devices:
      - /dev/snd:/dev/snd
    environment:
      JIBRI_XMPP_USER: recorder
      JIBRI_XMPP_PASSWORD: ${JIBRI_PASSWORD}
      JIBRI_RECORDER_USER: recorder
      JIBRI_RECORDER_PASSWORD: ${JIBRI_PASSWORD}
      ENABLE_RECORDING: 1
      JIBRI_FINALIZE_RECORDING_SCRIPT: /opt/finalize-recording.sh

  minio:
    image: minio/minio:latest
    restart: unless-stopped
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio-data:/data
    environment:
      MINIO_ROOT_USER: admin
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}
    command: server /data --console-address ":9001"

  postgres:
    image: postgres:17-alpine
    restart: unless-stopped
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: transcriptions
      POSTGRES_USER: transcribe
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis-data:/data

  transcription-api:
    build: ./transcription-service
    restart: unless-stopped
    ports:
      - "8508:8000"
    environment:
      # Whisper API
      WHISPER_API_URL: http://69.62.108.82:8001

      # Claude API
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}

      # Ollama
      OLLAMA_URL: http://69.62.108.82:11435
      OLLAMA_MODEL: qwen2.5:7b

      # Storage
      MINIO_ENDPOINT: minio:9000
      MINIO_ACCESS_KEY: admin
      MINIO_SECRET_KEY: ${MINIO_PASSWORD}

      # Database
      POSTGRESQL_URL: postgresql://transcribe:${POSTGRES_PASSWORD}@postgres/transcriptions
      REDIS_URL: redis://redis:6379

      # Integrations
      ROCKETCHAT_WEBHOOK: ${ROCKETCHAT_WEBHOOK}
      NOTION_API_KEY: ${NOTION_API_KEY}
      NOTION_DATABASE_ID: ${NOTION_DATABASE_ID}

      # HuggingFace (pyannote)
      HF_TOKEN: ${HF_TOKEN}
    depends_on:
      - postgres
      - redis
      - minio
    volumes:
      - /tmp/transcriptions:/tmp/transcriptions

volumes:
  minio-data:
  postgres-data:
  redis-data:
```

**Code FastAPI (transcription-service/main.py)** :

```python
from fastapi import FastAPI, BackgroundTasks, File, UploadFile
from pydantic import BaseModel
import anthropic
import requests
from pyannote.audio import Pipeline
import subprocess
import base64
from pathlib import Path

app = FastAPI()

# Init
claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
diarization = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=HF_TOKEN
)

class RecordingComplete(BaseModel):
    meeting_id: str
    video_path: str
    participants: list[str]
    duration_minutes: int

@app.post("/webhook/recording-complete")
async def process_recording(data: RecordingComplete, bg: BackgroundTasks):
    """Webhook appelé par Jibri après enregistrement"""
    bg.add_task(transcribe_and_summarize, data)
    return {"status": "processing", "meeting_id": data.meeting_id}

async def transcribe_and_summarize(data: RecordingComplete):
    try:
        # 1. Extract audio from video
        audio_path = extract_audio(data.video_path)

        # 2. Transcribe with faster-whisper (API call)
        transcript_raw = transcribe_audio(audio_path)

        # 3. Diarization with pyannote
        diarization_result = diarization(audio_path)
        transcript_with_speakers = align_transcript_with_diarization(
            transcript_raw, diarization_result
        )

        # 4. OCR screenshots with Claude Vision
        screenshots = extract_screenshots(data.video_path, interval=10)
        ocr_results = []
        for screenshot in screenshots:
            ocr = analyze_screenshot_claude(screenshot)
            ocr_results.append(ocr)

        # 5. Generate summary with Ollama
        summary = generate_summary_ollama(
            transcript_with_speakers,
            ocr_results,
            data.participants,
            data.duration_minutes
        )

        # 6. Save to database
        save_to_db(data.meeting_id, transcript_with_speakers, summary)

        # 7. Create Notion page
        notion_url = create_notion_page(
            data.meeting_id,
            transcript_with_speakers,
            ocr_results,
            summary
        )

        # 8. Notify Rocket.Chat
        notify_rocketchat(data.meeting_id, summary, notion_url)

        print(f"✅ Meeting {data.meeting_id} processed successfully")

    except Exception as e:
        print(f"❌ Error processing meeting {data.meeting_id}: {e}")
        # TODO: notify error to Rocket.Chat

def transcribe_audio(audio_path: str) -> dict:
    """Call faster-whisper API (déjà installé sur port 8001)"""
    with open(audio_path, 'rb') as f:
        response = requests.post(
            "http://69.62.108.82:8001/v1/audio/transcriptions",
            files={"file": f},
            data={"model": "base", "language": "fr"}
        )
    return response.json()

def extract_screenshots(video_path: str, interval: int = 10) -> list[str]:
    """Extract 1 frame every `interval` seconds"""
    output_pattern = f"/tmp/screenshots/{Path(video_path).stem}_%04d.jpg"
    subprocess.run([
        "ffmpeg", "-i", video_path,
        "-vf", f"fps=1/{interval}",
        output_pattern
    ], check=True)

    return sorted(Path("/tmp/screenshots").glob(f"{Path(video_path).stem}_*.jpg"))

def analyze_screenshot_claude(screenshot_path: Path) -> dict:
    """OCR + analysis with Claude 3.5 Sonnet Vision"""
    image_data = base64.standard_b64encode(screenshot_path.read_bytes()).decode()

    message = claude.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data
                    }
                },
                {
                    "type": "text",
                    "text": """Analyse ce screenshot de partage d'écran de réunion.

Extrait en JSON :
{
  "timestamp": "HH:MM:SS estimé depuis nom fichier",
  "title": "Titre de la slide/page",
  "text": "Texte complet visible",
  "key_points": ["point 1", "point 2"],
  "visual_elements": ["graphique montrant X", "schéma de Y"],
  "has_important_data": true/false
}

Si c'est juste une webcam sans contenu utile, retourne {"has_important_data": false}."""
                }
            ]
        }]
    )

    return {
        "screenshot": str(screenshot_path),
        "analysis": message.content[0].text
    }

def generate_summary_ollama(
    transcript: str,
    ocr_results: list[dict],
    participants: list[str],
    duration: int
) -> dict:
    """Generate meeting summary with Ollama"""

    # Build context
    ocr_context = "\n\n".join([
        f"[{ocr['timestamp']}] Écran : {ocr['analysis']}"
        for ocr in ocr_results
        if ocr.get('has_important_data', True)
    ])

    prompt = f"""Tu es un assistant qui résume des réunions professionnelles.

**Réunion** :
- Participants : {', '.join(participants)}
- Durée : {duration} minutes

**Transcription avec speakers** :
{transcript}

**Contenu des partages d'écran** :
{ocr_context}

**Consignes** : Génère un résumé structuré en format JSON :

{{
  "executive_summary": "Résumé en 3-5 lignes",
  "key_topics": [
    {{"topic": "Sujet 1", "discussion": "Ce qui a été dit"}}
  ],
  "decisions": [
    "Décision 1", "Décision 2"
  ],
  "action_items": [
    {{"person": "@nom", "task": "Faire X", "deadline": "date si mentionnée"}}
  ],
  "next_steps": [
    "Point à aborder prochaine réunion"
  ]
}}

Réponds UNIQUEMENT avec le JSON, rien d'autre."""

    response = requests.post(
        "http://69.62.108.82:11435/api/generate",
        json={
            "model": "qwen2.5:7b",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]

def create_notion_page(meeting_id, transcript, ocr_results, summary):
    """Create Notion page with full transcript"""
    # TODO: Implement Notion API integration
    pass

def notify_rocketchat(meeting_id, summary, notion_url):
    """Send notification to Rocket.Chat channel"""
    payload = {
        "text": f"📝 Résumé de réunion disponible",
        "attachments": [{
            "title": f"Réunion {meeting_id}",
            "text": summary["executive_summary"],
            "fields": [
                {
                    "title": "Décisions",
                    "value": "\n".join(f"• {d}" for d in summary["decisions"])
                },
                {
                    "title": "Actions",
                    "value": "\n".join(
                        f"• {a['person']}: {a['task']}"
                        for a in summary["action_items"]
                    )
                }
            ],
            "actions": [{
                "type": "button",
                "text": "Voir transcription complète",
                "url": notion_url
            }],
            "color": "#4CAF50"
        }]
    }

    requests.post(ROCKETCHAT_WEBHOOK, json=payload)
```

**Dockerfile transcription-service** :

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Télécharger modèle pyannote (nécessite HF token en build-time)
ARG HF_TOKEN
RUN python -c "from pyannote.audio import Pipeline; Pipeline.from_pretrained('pyannote/speaker-diarization-3.1', use_auth_token='${HF_TOKEN}')"

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**requirements.txt** :

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
anthropic==0.18.0
pyannote.audio==3.1.1
requests==2.31.0
psycopg2-binary==2.9.9
redis==5.0.1
minio==7.2.3
notion-client==2.2.1
```

**Prérequis déploiement** :

1. **HuggingFace Token** (gratuit) :
   - Créer compte https://huggingface.co
   - Créer token : https://huggingface.co/settings/tokens
   - Accepter termes pyannote : https://huggingface.co/pyannote/speaker-diarization-3.1

2. **Anthropic API Key** (21,60€/mois pour ton usage) :
   - Créer compte https://console.anthropic.com
   - Add payment method
   - Créer API key

3. **Notion Integration** (gratuit) :
   - https://www.notion.so/my-integrations
   - Créer integration
   - Copier secret token
   - Partager database avec integration

4. **Rocket.Chat Webhook** (gratuit) :
   - Admin → Integrations → New Webhook
   - Choisir channel destination
   - Copier webhook URL

**Déploiement** :

```bash
# 1. Créer structure
ssh automation@69.62.108.82 "mkdir -p /opt/transcription-pipeline/transcription-service"

# 2. Transférer fichiers
scp -r transcription-service/* automation@69.62.108.82:/opt/transcription-pipeline/transcription-service/
scp docker-compose.yml automation@69.62.108.82:/opt/transcription-pipeline/

# 3. Configurer .env
cat > .env <<'ENV'
JIBRI_PASSWORD=genere_password_fort
MINIO_PASSWORD=genere_password_fort
POSTGRES_PASSWORD=genere_password_fort
ANTHROPIC_API_KEY=sk-ant-xxx
HF_TOKEN=hf_xxx
ROCKETCHAT_WEBHOOK=https://chat.srv759970.hstgr.cloud/hooks/xxx
NOTION_API_KEY=secret_xxx
NOTION_DATABASE_ID=xxx
ENV

scp .env automation@69.62.108.82:/opt/transcription-pipeline/

# 4. Build et démarrer
ssh automation@69.62.108.82 <<'EOF'
cd /opt/transcription-pipeline
docker-compose up -d
docker-compose logs -f transcription-api
EOF

# 5. Tester l'API
curl http://69.62.108.82:8508/docs  # Swagger UI
```

**Bibliothèques clés** :
- `paddleocr` : OCR local CPU
- `ImageHash` : Détection perceptuelle changements slides
- `PySceneDetect` : Détection zones screenshare
- `pyannote.audio` : Diarisation speakers

**Statut** : 📋 Backlog (après P1 + P2)
**Durée estimée** : 3-4 jours
**Budget additionnel** : ~~21,60€/mois~~ → **0€/mois** (100% local)

---

### 3.2 Intranet Elyse Energy (si applicable)

**Recommandation** : SharePoint natif (pas de sur-couche)

**Stack** :
- Site communication SharePoint
- Viva Connections (mobile)
- Power Apps (workflows RH/IT)
- Microsoft Graph API (pilotage LLM)

**Voir analyse complète dans conversation ChatGPT (partie intranet)**

**Statut** : 📋 Backlog (projet séparé)

---

## 📅 Planning de déploiement

### Semaine 1 (URGENT)
- [x] ⏳ Lundi : Compte automation + sudo
- [x] ⏳ Mardi : UFW + Fail2ban
- [x] ⏳ Mercredi : OAuth2-proxy (préparation Google OAuth)
- [x] ⏳ Jeudi : OAuth2-proxy (déploiement + config Nginx)
- [x] ⏳ Vendredi : Restic + test backup/restore

### Semaine 2-3
- [x] ⏳ Décision : Nextcloud hébergé ou self-hosted
- [x] ⏳ Setup Nextcloud + ONLYOFFICE
- [x] ⏳ Setup Rocket.Chat + Jitsi
- [x] ⏳ Achat licences Microsoft 365 Apps (2x)
- [x] ⏳ Configuration calendriers/contacts (Infomaniak ou Nextcloud)

### Semaine 4
- [x] ⏳ Tests utilisateurs
- [x] ⏳ Documentation
- [x] ⏳ Formation équipe

---

## 📊 Métriques de succès

| Objectif | Métrique | Cible |
|----------|----------|-------|
| **Sécurité VPS** | Accès root SSH désactivé | ✅ |
| **Sauvegardes** | Backup quotidien + test restore réussi | ✅ |
| **Stack entreprise** | 4 users opérationnels | ✅ |
| **Budget** | Coût mensuel | < 100€/mois |
| **Compatibilité** | Co-édition avec clients MS | ✅ |

---

## 🆘 Contacts & ressources

- **Documentation VPS** : `README.md`, `GUIDE_NGINX.md`, `GUIDE_BASIC_AUTH.md`
- **Support Infomaniak** : https://www.infomaniak.com/fr/support
- **Nextcloud docs** : https://docs.nextcloud.com/
- **Rocket.Chat docs** : https://docs.rocket.chat/

---

## 📝 Notes & décisions

### Décisions techniques prises

1. **Pas de serveur mail self-hosted** : trop de maintenance, préférer Infomaniak/Proton
2. **Pas de FortiSASE/Pexip** : overkill pour 4 users, trop cher
3. **Pas d'Authentik** : oauth2-proxy + Google suffit
4. **Pas de sur-couche SharePoint** : natif couvre 80% des besoins Elyse

### Questions en suspens

- [ ] VPS dédié Nextcloud ou sur srv759970 ?
- [ ] Quel provider email : Infomaniak ou Proton ?
- [x] ~~GPU nécessaire pour pipeline transcription ?~~ → **Non**, solution 100% CPU locale (PaddleOCR + ImageHash) - **0€/mois**

### À décommissionner

- [ ] WordPress Multisite (`/var/www/wordpress`) → Remplacé par 2× WordPress solo (Clémence + SolidarLink)

---

**Version** : 1.0
**Auteur** : Claude Code + Julien
**Prochaine revue** : Après déploiement P1
