# Backup & Restore - srv759970

Guide complet pour sauvegarder et restaurer les configurations et données du serveur.

## Vue d'Ensemble

Nous utilisons une **approche hybride** pour backup/restore:

1. **Configurations** → Versionnées dans Git (`server-configs/`)
2. **Données Docker** → Backup automatique serveur (`/root/backups/`)
3. **Bases de données** → Dumps inclus dans backups serveur

## Structure de Backup

```
Repository Git (Local)
└── server-configs/          # Configurations versionnées
    ├── docker-compose/      # 8 services
    ├── nginx/               # 20+ sites
    ├── dashy/               # conf.yml
    ├── systemd/             # Services custom
    └── scripts/             # Scripts de backup

Serveur (/root/backups/)
└── server-state-YYYYMMDD-HHMMSS.tar.gz    # Backup complet quotidien
    ├── configs/             # Configs + .env avec secrets
    ├── docker/              # État Docker
    ├── volumes/             # Volumes critiques (tar.gz)
    └── databases/           # Dumps SQL
```

## 📥 Synchroniser Configurations (Serveur → Local)

### Sync Complet

```bash
# Depuis la racine du repo
cd /path/to/Hostinger
bash scripts/sync-from-server.sh
```

**Ce qui est synchronisé:**
- ✅ Docker Compose files (8 services)
- ✅ Nginx configs (20+ sites)
- ✅ Dashy configuration
- ✅ Systemd services
- ✅ État Docker (conteneurs, images, volumes, networks)
- ✅ Certificats SSL (liste)
- ✅ .env templates (SANS secrets)
- ✅ Inventaire serveur

**Durée:** ~2-3 minutes

### Commit dans Git

```bash
# Après sync
git add server-configs/
git commit -m "backup: server state $(date +%Y-%m-%d)"
git push
```

## 📤 Déployer Configurations (Local → Serveur)

### Dry-Run (Test)

```bash
bash scripts/sync-to-server.sh --dry-run
```

Affiche ce qui serait modifié **sans** faire de changements.

### Déploiement Complet

```bash
bash scripts/sync-to-server.sh
```

**Actions:**
- Backup automatique des fichiers existants (`*.backup-YYYYMMDD`)
- Upload des nouvelles configs
- Test Nginx (`nginx -t`)
- Prompts pour reload/restart services

### Déploiement Partiel

```bash
# Seulement Nginx
bash scripts/sync-to-server.sh --service nginx

# Seulement Dashy
bash scripts/sync-to-server.sh --service dashy

# Seulement Docker Compose
bash scripts/sync-to-server.sh --service docker-compose
```

## 💾 Backup Automatique Serveur

### Installation

```bash
# Déployer le script
scp server-configs/scripts/backup-server-state.sh root@69.62.108.82:/root/scripts/
ssh root@69.62.108.82 "chmod +x /root/scripts/backup-server-state.sh"

# Setup cron
ssh root@69.62.108.82
crontab -e

# Ajouter (backup quotidien à 3h)
0 3 * * * /root/scripts/backup-server-state.sh >> /var/log/backup-cron.log 2>&1
```

### Exécution Manuelle

```bash
ssh root@69.62.108.82 "/root/scripts/backup-server-state.sh"
```

### Contenu du Backup

**Un backup `server-state-*.tar.gz` contient:**

```
configs/
├── docker-compose.yml (tous les services)
├── nginx-sites/ (tous les sites nginx)
├── nginx-snippets/ (snippets réutilisables)
├── dashy-conf.yml
├── .env files (AVEC secrets)
└── systemd/*.service

docker/
├── containers-running.txt
├── containers-all.txt
├── images.txt
├── volumes.txt
└── networks.txt

volumes/
├── dashy_icons.tar.gz
├── grafana_data.tar.gz
├── prometheus_data.tar.gz
└── loki_data.tar.gz

databases/
└── clemence_db.sql

server-info.txt
```

### Gestion des Backups

```bash
# Lister les backups
ssh root@69.62.108.82 "ls -lh /root/backups/"

# Voir le contenu d'un backup
ssh root@69.62.108.82 "tar tzf /root/backups/server-state-20250121-030000.tar.gz | head -30"

# Télécharger un backup en local
scp root@69.62.108.82:/root/backups/server-state-20250121-030000.tar.gz ./backups/

# Supprimer les anciens backups (>30 jours)
ssh root@69.62.108.82 "find /root/backups -name 'server-state-*.tar.gz' -mtime +30 -delete"
```

**Rétention:** 30 jours (configurable dans le script)

## 🔄 Restauration

### Restaurer Configurations (depuis Git)

#### 1. Checkout Version Voulue

```bash
# Voir l'historique
git log --oneline server-configs/

# Checkout une version spécifique
git checkout <commit-hash> -- server-configs/

# Ou revenir à la dernière version
git checkout HEAD -- server-configs/
```

#### 2. Déployer

```bash
# Test
bash scripts/sync-to-server.sh --dry-run

# Déploiement
bash scripts/sync-to-server.sh
```

#### 3. Redémarrer Services

```bash
# Exemple: Dashy
ssh root@69.62.108.82 "cd /opt/dashy && docker-compose restart"

# Exemple: Nginx
ssh root@69.62.108.82 "nginx -t && systemctl reload nginx"

# Exemple: Tous les services monitoring
ssh root@69.62.108.82 "cd /opt/monitoring && docker-compose restart"
```

### Restaurer depuis Backup Serveur

#### 1. Extraire le Backup

```bash
ssh root@69.62.108.82
cd /tmp
tar xzf /root/backups/server-state-20250121-030000.tar.gz
cd server-state-20250121-030000/
```

#### 2. Restaurer Configs Spécifiques

```bash
# Nginx
cp -r configs/nginx-sites/* /etc/nginx/sites-available/
nginx -t && systemctl reload nginx

# Docker Compose
cp configs/opt/dashy/docker-compose.yml /opt/dashy/
cd /opt/dashy && docker-compose up -d

# Dashy config
cp configs/dashy-conf.yml /opt/dashy/conf.yml
cd /opt/dashy && docker-compose restart
```

#### 3. Restaurer Volumes Docker

```bash
# Exemple: Grafana data
docker run --rm \
    -v grafana_data:/volume \
    -v /tmp/server-state-20250121-030000/volumes:/backup \
    alpine sh -c "cd /volume && tar xzf /backup/grafana_data.tar.gz --strip 1"

# Redémarrer le service
cd /opt/monitoring && docker-compose restart grafana
```

#### 4. Restaurer Base de Données

```bash
# MySQL (Clemence)
docker exec -i mysql-clemence mysql -u clemence_user -pClemenceDB2025 clemence_db \
    < databases/clemence_db.sql

# Vérifier
docker exec mysql-clemence mysql -u clemence_user -pClemenceDB2025 -e "SHOW TABLES;" clemence_db
```

## 🚨 Disaster Recovery

### Scénario: Serveur Complètement Détruit

#### Étape 1: Nouveau Serveur

1. Provisionner nouveau VPS Ubuntu 24.04
2. Installer Docker, Docker Compose, Nginx, Certbot
3. Configurer SSH avec ta clé publique

#### Étape 2: Restaurer Configurations

```bash
# Clone le repo Git
git clone https://github.com/julienfernandez/hostinger.git
cd hostinger

# Déployer TOUTES les configs
bash scripts/sync-to-server.sh
```

#### Étape 3: Restaurer Données

```bash
# Upload backup le plus récent
scp local-backups/server-state-latest.tar.gz root@NEW_IP:/tmp/

# Extraire et restaurer
ssh root@NEW_IP
cd /tmp
tar xzf server-state-latest.tar.gz
cd server-state-*/

# Restaurer volumes critiques
# (voir section "Restaurer Volumes Docker" ci-dessus)

# Restaurer databases
# (voir section "Restaurer Base de Données" ci-dessus)
```

#### Étape 4: Certificats SSL

```bash
# Regénérer tous les certificats
ssh root@NEW_IP
systemctl stop nginx

certbot certonly --standalone \
    -d dashy.srv759970.hstgr.cloud \
    -d whisperx.srv759970.hstgr.cloud \
    -d monitoring.srv759970.hstgr.cloud \
    # ... (tous les domaines)

systemctl start nginx
```

#### Étape 5: Démarrer Services

```bash
# Démarrer tous les Docker Compose stacks
for service in dashy whisperx faster-whisper-queue monitoring neutts-air memvid mkdocs; do
    echo "Starting $service..."
    ssh root@NEW_IP "cd /opt/$service && docker-compose up -d"
done
```

#### Étape 6: Vérification

```bash
# Vérifier tous les conteneurs
ssh root@NEW_IP "docker ps"

# Vérifier Nginx
ssh root@NEW_IP "nginx -t"
ssh root@NEW_IP "systemctl status nginx"

# Tester les URLs
curl -I https://dashy.srv759970.hstgr.cloud
curl -I https://docs.srv759970.hstgr.cloud
```

## 📅 Calendrier de Backup Recommandé

### Automatique

- **Quotidien (3h):** Backup complet serveur (`/root/backups/`)
- **Toutes les 6h:** Sync Git (optionnel via cron local)

### Manuel

- **Avant changement majeur:** Backup manuel + commit Git
- **Après déploiement:** Sync configs vers Git
- **Mensuel:** Télécharger backup serveur en local

## 🔐 Sécurité des Backups

### ⚠️ Secrets dans les Backups

**Repository Git:**
- ❌ `.env` réels **PAS** dans Git
- ✅ `.env.template` seulement (valeurs masquées)

**Backups Serveur:**
- ✅ Contiennent les `.env` avec secrets
- ⚠️ **DANGER:** `/root/backups/` sur serveur non chiffré
- ✅ **Recommandation:** Télécharger en local et chiffrer

### Chiffrer un Backup Local

```bash
# Télécharger
scp root@69.62.108.82:/root/backups/server-state-20250121.tar.gz ./

# Chiffrer avec GPG
gpg --symmetric --cipher-algo AES256 server-state-20250121.tar.gz

# Fichier chiffré: server-state-20250121.tar.gz.gpg
# Supprimer original
rm server-state-20250121.tar.gz
```

### Déchiffrer

```bash
gpg --decrypt server-state-20250121.tar.gz.gpg > server-state-20250121.tar.gz
```

## 📊 Monitoring des Backups

### Vérifier Derniers Backups

```bash
# Sur le serveur
ssh root@69.62.108.82 "ls -lht /root/backups/ | head -5"

# Vérifier le log cron
ssh root@69.62.108.82 "tail -50 /var/log/backup-cron.log"
```

### Tester un Backup

```bash
# Tester l'intégrité
ssh root@69.62.108.82 "tar tzf /root/backups/server-state-latest.tar.gz > /dev/null && echo 'OK' || echo 'CORRUPTED'"

# Voir la taille
ssh root@69.62.108.82 "du -h /root/backups/server-state-latest.tar.gz"
```

## 🛠️ Troubleshooting

### Sync Failed

```bash
# Vérifier connexion SSH
ssh root@69.62.108.82 "echo OK"

# Re-exécuter avec debug
bash -x scripts/sync-from-server.sh
```

### Backup Failed

```bash
# Vérifier espace disque
ssh root@69.62.108.82 "df -h /"

# Vérifier permissions
ssh root@69.62.108.82 "ls -la /root/scripts/backup-server-state.sh"

# Exécuter manuellement avec verbose
ssh root@69.62.108.82 "bash -x /root/scripts/backup-server-state.sh"
```

### Restore Failed

```bash
# Vérifier le backup
tar tzf backup.tar.gz | grep -i error

# Extraire partiellement
tar xzf backup.tar.gz configs/nginx-sites/

# Vérifier Docker
docker ps -a
docker logs <container>
```

## 📚 Voir Aussi

- [server-configs/README.md](../../server-configs/README.md) - Documentation structure
- [INVENTORY.md](../../server-configs/INVENTORY.md) - Inventaire serveur
- [Docker Infrastructure](../../infrastructure/docker.md)
- [Nginx Infrastructure](../../infrastructure/nginx.md)
- [Security](../../infrastructure/security.md)

---

**Dernière mise à jour:** 2025-01-21
**Prochaine révision:** Après premier disaster recovery test
