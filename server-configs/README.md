# Server Configurations - srv759970.hstgr.cloud

Ce dossier contient **toutes les configurations** du serveur VPS srv759970.hstgr.cloud, versionnées dans Git pour sauvegarde, restauration et déploiement automatisé.

## 📁 Structure

```
server-configs/
├── docker-compose/        # Fichiers docker-compose.yml de tous les services
│   ├── dashy.yml
│   ├── whisperx.yml
│   ├── faster-whisper-queue.yml
│   ├── monitoring.yml
│   ├── neutts-air.yml
│   ├── memvid.yml
│   └── mkdocs.yml
├── nginx/
│   ├── sites-available/   # Configurations Nginx par site
│   ├── snippets/          # Snippets réutilisables (basic-auth, proxy-headers, ssl)
│   └── nginx.conf         # Configuration globale Nginx
├── dashy/
│   └── conf.yml           # Configuration Dashy portal
├── systemd/
│   ├── *.service          # Services systemd custom
│   └── enabled-services.txt  # Liste des services enabled
├── certbot/
│   └── certificates-list.txt  # Liste des certificats SSL
├── env/
│   └── *.env.template     # Templates .env (SANS secrets)
├── scripts/
│   ├── backup-server-state.sh     # Script de backup automatique
│   └── sync-configs-to-git.sh     # Script de sync auto vers Git
├── docker-running.txt     # État des conteneurs Docker
├── docker-volumes.txt     # Liste des volumes Docker
├── server-info.txt        # Informations système
└── INVENTORY.md           # Inventaire complet du serveur
```

## 🚀 Utilisation

### Synchroniser depuis le serveur (Server → Local)

```bash
# Depuis la racine du repo
bash scripts/sync-from-server.sh
```

Ceci copie **toutes** les configurations du serveur vers le repo local.

### Déployer vers le serveur (Local → Server)

```bash
# Dry-run (sans modification)
bash scripts/sync-to-server.sh --dry-run

# Déploiement réel
bash scripts/sync-to-server.sh

# Déployer un service spécifique
bash scripts/sync-to-server.sh --service dashy
bash scripts/sync-to-server.sh --service nginx
```

## 📦 Services Inclus

### Docker Compose Services

- **dashy** - Portail centralisé de services
- **whisperx** - Transcription avec diarization
- **faster-whisper-queue** - Transcription async avec RQ
- **monitoring** - Stack Grafana + Prometheus + Loki
- **neutts-air** - Text-to-speech avec voice cloning
- **memvid** - RAG sémantique avec encodage vidéo
- **mkdocs** - Documentation technique

### Services Nginx

Tous les sites exposés via reverse proxy Nginx avec SSL/TLS (Let's Encrypt):

- dashy.srv759970.hstgr.cloud
- whisperx.srv759970.hstgr.cloud
- faster-whisper.srv759970.hstgr.cloud
- whisper.srv759970.hstgr.cloud
- monitoring.srv759970.hstgr.cloud
- docs.srv759970.hstgr.cloud
- dashboard.srv759970.hstgr.cloud
- sharepoint.srv759970.hstgr.cloud
- portal.srv759970.hstgr.cloud
- clemence.srv759970.hstgr.cloud
- cristina.srv759970.hstgr.cloud
- admin.cristina.srv759970.hstgr.cloud
- solidarlink.srv759970.hstgr.cloud
- neutts.srv759970.hstgr.cloud
- neutts-api.srv759970.hstgr.cloud
- memvid.srv759970.hstgr.cloud
- tika.srv759970.hstgr.cloud
- ollama.srv759970.hstgr.cloud
- ragflow.srv759970.hstgr.cloud
- rag-anything.srv759970.hstgr.cloud
- dozzle.srv759970.hstgr.cloud
- whisperx-dashboard.srv759970.hstgr.cloud

## 🔐 Sécurité

### ⚠️ IMPORTANT: Secrets

Les fichiers `.env` contiennent des **secrets** (mots de passe, API keys, tokens).

**Dans ce repo:**
- ✅ `.env.template` files sont versionnés (valeurs masquées: `***MASKED***`)
- ❌ `.env` files réels ne sont PAS dans Git (`.gitignore`)

**Sur le serveur:**
- Les vrais `.env` sont dans `/opt/*/` sur le serveur
- Le script `backup-server-state.sh` les sauvegarde (backups locaux serveur uniquement)

### Backup des Secrets

Pour backup complet avec secrets:

```bash
# Sur le serveur
ssh root@69.62.108.82
/root/scripts/backup-server-state.sh

# Les backups sont dans /root/backups/
# Contiennent les .env avec secrets
```

## 🔄 Workflow Recommandé

### Modifier une Configuration

1. **Modifier localement** dans `server-configs/`
2. **Tester avec dry-run:**
   ```bash
   bash scripts/sync-to-server.sh --dry-run
   ```
3. **Déployer:**
   ```bash
   bash scripts/sync-to-server.sh
   ```
4. **Commit dans Git:**
   ```bash
   git add server-configs/
   git commit -m "config: update nginx for service X"
   git push
   ```

### Sauvegarder l'État Actuel

```bash
# Synchroniser toutes les configs
bash scripts/sync-from-server.sh

# Commit
git add server-configs/
git commit -m "backup: server state $(date +%Y-%m-%d)"
git push
```

### Restaurer une Configuration

```bash
# 1. Checkout la version voulue
git checkout <commit-hash> -- server-configs/

# 2. Dry-run
bash scripts/sync-to-server.sh --dry-run

# 3. Déployer
bash scripts/sync-to-server.sh

# 4. Redémarrer les services concernés
ssh root@69.62.108.82 "cd /opt/dashy && docker-compose restart"
```

## 📊 Inventaire

Le fichier `INVENTORY.md` contient l'inventaire complet du serveur:

- Liste de tous les services Docker
- Liste de tous les sites Nginx
- État des certificats SSL
- Conteneurs running

Mis à jour automatiquement par `sync-from-server.sh`.

## 🤖 Automatisation

### Sur le Serveur (Backup Automatique)

Script à déployer: `server-configs/scripts/backup-server-state.sh`

```bash
# Déployer sur le serveur
scp server-configs/scripts/backup-server-state.sh root@69.62.108.82:/root/scripts/
ssh root@69.62.108.82 "chmod +x /root/scripts/backup-server-state.sh"

# Setup cron (backup quotidien à 3h)
ssh root@69.62.108.82
crontab -e

# Ajouter:
0 3 * * * /root/scripts/backup-server-state.sh >> /var/log/backup-cron.log 2>&1
```

### En Local (Sync Automatique)

Optionnel: Cron local pour sync automatique

```bash
# Sync toutes les 6h
0 */6 * * * cd /path/to/repo && bash scripts/sync-from-server.sh && git add server-configs/ && git commit -m "auto: sync $(date)" && git push
```

## 📚 Documentation

Documentation complète:
- [Guide Backup & Restore](../docs/infrastructure/backup-restore.md)
- [Nginx Infrastructure](../docs/infrastructure/nginx.md)
- [Docker Infrastructure](../docs/infrastructure/docker.md)
- [Security](../docs/infrastructure/security.md)

## 🆘 Troubleshooting

### Sync Failed

```bash
# Vérifier la connexion SSH
ssh root@69.62.108.82 "echo OK"

# Re-exécuter le sync avec verbose
bash -x scripts/sync-from-server.sh
```

### Déploiement Failed

```bash
# Vérifier Nginx config
ssh root@69.62.108.82 "nginx -t"

# Vérifier les conteneurs
ssh root@69.62.108.82 "docker ps"

# Logs
ssh root@69.62.108.82 "docker logs <container_name>"
```

### Restaurer depuis Backup Serveur

```bash
# Lister les backups
ssh root@69.62.108.82 "ls -lh /root/backups/"

# Extraire un backup
ssh root@69.62.108.82
cd /tmp
tar xzf /root/backups/server-state-YYYYMMDD-HHMMSS.tar.gz

# Restaurer manuellement les fichiers voulus
cp -r /tmp/server-state-*/configs/nginx-sites/* /etc/nginx/sites-available/
nginx -t && systemctl reload nginx
```

## 🎯 Voir Aussi

- [Analyse Auth Strategy](../docs/analysis/auth-strategy-oauth-vs-basic.md)
- [Dashy Portal](../docs/services/dashy-portal.md)
- [MkDocs Documentation](https://docs.srv759970.hstgr.cloud)

---

**Dernière mise à jour:** 2025-01-21
**Prochaine révision:** Après chaque modification importante du serveur
