# 🏠 Hostinger Server Management

**Documentation complète pour srv759970.hstgr.cloud**

[![Documentation](https://img.shields.io/badge/docs-MkDocs-blue)](https://docs.srv759970.hstgr.cloud)
[![Server Status](https://img.shields.io/badge/status-online-green)]()
[![Apps](https://img.shields.io/badge/apps-45-orange)]()

---

## 📚 Documentation

**🆕 Version 2.0 - Structure Restructurée**

La documentation a été complètement reorganisée pour une meilleure clarté :

### Accès Rapide
- **[Documentation MkDocs](new-docs/)** - Documentation complète navigable
- **[Migration Report](MIGRATION_REPORT.md)** - Détails de la restructuration
- **[Emergency Runbook](docs/EMERGENCY_RUNBOOK.md)** - Procédures d'urgence

### Structure
```
Hostinger/
├── apps/                    # 45 applications (13 catégories)
│   ├── 01-wordpress/       # Sites WordPress (5)
│   ├── 02-ai-transcription/# WhisperX, Faster-Whisper
│   ├── 11-dashboards/      # Energie Dashboard (DownTo40) 🔴
│   └── 13-infrastructure/  # Services infrastructure
├── infrastructure/          # Infrastructure serveur
│   ├── nginx/              # Nginx Manager (repo externe)
│   ├── server/             # Config serveur, users, fail2ban
│   └── ssl/                # Gestion certificats SSL
├── new-docs/               # Documentation MkDocs
└── scripts/                # Scripts d'administration
```

---

## 🎯 Quick Start

### Accès Serveur

```bash
# SSH (compte automation)
ssh automation@69.62.108.82

# Voir les conteneurs actifs
docker ps --format 'table {{.Names}}\t{{.Status}}'

# Ressources système
free -h && df -h
```

### Applications Principales

| Application | URL | Status |
|-------------|-----|--------|
| **Energie Dashboard** 🔴 | https://energie.srv759970.hstgr.cloud | `production` |
| **Dashy Portal** | https://dashy.srv759970.hstgr.cloud | `production` |
| **WordPress Clemence** | https://clemencefouquet.fr | `production` |
| **WhisperX API** | https://whisperx.srv759970.hstgr.cloud | `production` |
| **RAGFlow** | https://ragflow.srv759970.hstgr.cloud | `production` |
| **Grafana** | https://monitoring.srv759970.hstgr.cloud | `production` |

---

## 📊 État du Serveur

### Infrastructure

| Composant | Status | Notes |
|-----------|--------|-------|
| **Serveur** | 🟢 Online | Ubuntu 24.04.2 LTS |
| **RAM** | 🟢 9 GB libre / 15 GB | 60% utilisée |
| **Disque** | 🟢 116 GB libre / 193 GB | 40% utilisé |
| **Conteneurs** | 🟢 36 actifs / 64 | Optimisé auto-start |
| **Nginx** | 🟢 Active | 30+ sites configurés |

### Applications par Catégorie

| Catégorie | Nombre | Exemples |
|-----------|--------|----------|
| 🌐 WordPress | 5 | clemence, solidarlink |
| 🎤 AI Transcription | 3 | whisperx, faster-whisper |
| 🤖 AI RAG | 3 | ragflow, memvid |
| 📊 Dashboards | 5 | energie-dashboard 🔴, photos-chantier |
| 🔧 Infrastructure | 5 | databases-shared, docker-autostart |
| *(8 autres catégories)* | 24 | Voir [documentation](new-docs/) |

---

## 🛠️ Outils et Scripts

### Scripts Batch (Windows)

```bash
# Déployer une application
scripts/deploy.bat

# Mettre à jour une application
scripts/update.bat

# Gérer les applications (logs, restart, etc.)
scripts/manage.bat
```

### Nginx Manager

**⚠️ Repo externe actif** : `C:\Users\JulienFernandez\OneDrive\Coding\_Projets de code\2025.10 Nginx Manager`

```bash
# Health check
./scripts/health-check.sh

# Déployer une config (avec backup automatique)
./scripts/nginx-deploy.sh configs/sites-available/mon-site mon-site

# Rollback si problème
./scripts/nginx-rollback.sh --list mon-site
```

**Documentation** : Voir [infrastructure/nginx/README.md](infrastructure/nginx/README.md)

---

## 🔒 Sécurité

### Compte Automation

Le serveur utilise le compte `automation` au lieu de root :
- ✅ Sudo quasi-total (sauf reboot/shutdown)
- ✅ Logs séparés (`/var/log/sudo-automation.log`)
- ✅ Révocable sans casser le système

**Documentation** : [Automation User Security](docs/guides/infrastructure/automation-user-security.md)

### Nginx Security

**Audit complété le 2025-10-28** :
- ✅ Score moyen : 85% (+39% amélioration)
- ✅ 4/4 sites WordPress sécurisés
- ✅ Fail2ban actif (3 jails)
- ✅ Rate limiting configuré
- ✅ SSL/TLS hardening

---

## 📖 Documentation Guides

### Infrastructure
- **[Serveur](new-docs/docs/01-infrastructure/server.md)** - Configuration système
- **[Nginx](new-docs/docs/01-infrastructure/nginx.md)** - Reverse proxy, SSL
- **[Bases de Données](new-docs/docs/01-infrastructure/databases.md)** - PostgreSQL, Redis, MongoDB
- **[Docker](new-docs/docs/01-infrastructure/docker.md)** - Architecture conteneurs

### Applications
- **[WordPress Clemence](new-docs/docs/02-applications/wordpress/clemence.md)** - Site client principal
- **[WhisperX](new-docs/docs/02-applications/ai-transcription/whisperx.md)** - API transcription
- **[Energie Dashboard](new-docs/docs/02-applications/dashboards/energie-dashboard.md)** - Projet DownTo40 🔴

### Operations
- **[Déploiement](docs/guides/GUIDE_DEPLOIEMENT_VPS.md)** - Déployer apps Docker
- **[Backup & Restore](docs/guides/operations/backup-restore.md)** - Stratégie sauvegarde
- **[Troubleshooting](docs/guides/infrastructure/nginx-troubleshooting.md)** - Résolution problèmes

---

## 🔄 Auto-Start/Stop System

**Optimisation RAM** : Économie de 4.7GB (66%) via auto-start/stop

| Service | Mode | Économie RAM | Auto-stop |
|---------|------|--------------|-----------|
| Support Dashboard | Dynamic | ~200 MB | 30 min idle |
| Cristina Strapi | Dynamic | ~300 MB | 30 min idle |
| WhisperX API | Blocking | ~2 GB | 30 min idle |
| Tika API | Blocking | ~500 MB | 30 min idle |

**Comment ça marche** :
1. Accès URL → Détection conteneur arrêté
2. Page d'attente (mode Dynamic) ou attente silencieuse (mode Blocking)
3. Démarrage automatique du conteneur (~15-20s)
4. Redirection vers l'app
5. Auto-stop après 30 min sans requête

**Documentation** : [GUIDE_DOCKER_AUTOSTART.md](docs/guides/GUIDE_DOCKER_AUTOSTART.md)

---

## 🚨 Emergency

### En cas de problème

1. **Check health** : `./scripts/health-check-all.sh`
2. **Voir logs** : `docker logs <container> --tail 50`
3. **Restart service** : `docker restart <container>`
4. **Nginx rollback** : Voir [Nginx Manager](infrastructure/nginx/README.md)

### Contacts
- **Emergency Runbook** : [docs/EMERGENCY_RUNBOOK.md](docs/EMERGENCY_RUNBOOK.md)
- **Incident History** : [infrastructure/nginx/sessions/](infrastructure/nginx/sessions/)

---

## 📝 Changelog

### v2.0.0 (2025-10-28) - Restructuration Majeure
- ✅ 45 apps organisées en 13 catégories
- ✅ Documentation MkDocs restructurée
- ✅ Placeholder Nginx Manager
- ✅ Tags prod/staging ajoutés
- ✅ Infrastructure séparée des apps

### v1.x (2025-10) - Améliorations continues
- ✅ Auto-start/stop Docker (-4.7GB RAM)
- ✅ Nginx Manager sécurisé (score 85%)
- ✅ Monitoring WhisperX (Grafana + Prometheus)
- ✅ Migration WordPress Clemence vers Docker
- ✅ 30+ guides détaillés

---

## 🔗 Liens Utiles

### Dashboards & Monitoring
- **[Dashy](https://dashy.srv759970.hstgr.cloud)** - Portal principal
- **[Grafana](https://monitoring.srv759970.hstgr.cloud)** - Métriques
- **[Portainer](http://69.62.108.82:9000)** - Gestion Docker
- **[Dozzle](https://dozzle.srv759970.hstgr.cloud)** - Logs temps réel

### Documentation
- **[MkDocs Local](new-docs/)** - Documentation navigable
- **[Hostinger Panel](https://hpanel.hostinger.com/)** - Gestion VPS

### External Repos
- **[Nginx Manager](C:\Users\JulienFernandez\OneDrive\Coding\_Projets de code\2025.10 Nginx Manager)** - Repo actif

---

## 📞 Support

**En cas de question** :
1. Consulter [Documentation MkDocs](new-docs/)
2. Voir [MIGRATION_REPORT.md](MIGRATION_REPORT.md) pour changements récents
3. Check [Emergency Runbook](docs/EMERGENCY_RUNBOOK.md)

---

**Serveur** : srv759970.hstgr.cloud (69.62.108.82)
**OS** : Ubuntu 24.04.2 LTS
**Uptime** : 195+ jours
**Dernière mise à jour** : 2025-10-28
