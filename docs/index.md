# Hostinger Server Documentation

**Serveur** : srv759970.hstgr.cloud (69.62.108.82)
**OS** : Ubuntu 24.04.2 LTS
**Compte Admin** : `automation`

---

## 🎯 Vue d'Ensemble

Documentation complète pour la gestion du serveur Hostinger avec :
- **45 applications** déployées (13 catégories)
- **Infrastructure** : Nginx, bases de données, SSL, monitoring
- **Automation** : Scripts, auto-start, backups
- **Documentation dynamique** : État en temps réel

---

## 📚 Navigation Rapide

### 🏗️ Infrastructure
- [Serveur & Configuration](01-infrastructure/server.md) - Setup, users, sécurité
- [Nginx Manager](01-infrastructure/nginx.md) - Reverse proxy, SSL, configs
- [Bases de Données](01-infrastructure/databases.md) - PostgreSQL, Redis, MongoDB partagés
- [Docker Architecture](01-infrastructure/docker.md) - Conteneurs, réseaux, volumes

### 🚀 Applications
- [WordPress Sites](02-applications/wordpress/) - 4 sites WordPress (Clemence, SolidarLink, etc.)
- [AI Transcription](02-applications/ai-transcription/) - WhisperX, Faster-Whisper
- [AI RAG](02-applications/ai-rag/) - RAGFlow, MemVid, RAG-Anything
- [Dashboards](02-applications/dashboards/) - Energie Dashboard (DownTo40), Photos Chantier

### ⚙️ Opérations
- [Déploiement](03-operations/deployment.md) - Procédures de déploiement
- [Backup & Restore](03-operations/backup.md) - Stratégie de sauvegarde
- [Troubleshooting](03-operations/troubleshooting.md) - Résolution de problèmes

### 📊 État en Temps Réel
- [System Status](99-dynamic/system-status.md) - RAM, CPU, disque
- [Containers Status](99-dynamic/containers.md) - Docker containers actifs
- [Services Health](99-dynamic/services-health.md) - Health checks

---

## 🚨 Liens Rapides

### Emergency
- **[Emergency Runbook](operations/emergency-runbook.md)** - Procédures d'urgence
- **[Incident History](operations/incidents.md)** - Historique des incidents

### Dashboards
- **[Dashy Portal](https://dashy.srv759970.hstgr.cloud)** - Dashboard visuel
- **[Grafana Monitoring](https://monitoring.srv759970.hstgr.cloud)** - Métriques
- **[Portainer](http://69.62.108.82:9000)** - Gestion Docker

### External Repos
- **[Nginx Manager](https://github.com/julien/nginx-manager)** - Repo Nginx séparé (en activité)

---

## 🏷️ Tags

La documentation utilise des tags pour filtrer les apps :

- `production` - Applications en production
- `staging` - Applications de test
- `wordpress` - Sites WordPress
- `ai` - Services IA/ML
- `dashboard` - Dashboards custom
- `monitoring` - Services de monitoring

**Rechercher par tag** : Utiliser la barre de recherche avec `tag:production`

---

## 🔧 Quick Commands

```bash
# Se connecter au serveur
ssh automation@69.62.108.82

# Voir les conteneurs actifs
docker ps --format 'table {{.Names}}\t{{.Status}}'

# Health check global
./scripts/health-check-all.sh

# Sync configs depuis serveur
./scripts/sync-from-server.sh
```

---

## 📖 Structure du Repo

```
Hostinger/
├── apps/                    # 45 applications (13 catégories)
├── infrastructure/          # Configs serveur, nginx, SSL
├── docs/                    # Cette documentation (MkDocs)
├── scripts/                 # Scripts d'administration
└── .claude/                 # Skills Claude Code
```

---

**Dernière mise à jour** : 2025-10-28
**Version** : 2.0.0 (Restructuration complète)
