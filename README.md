# 🏠 Hostinger VPS - Documentation

Documentation complète pour le déploiement et la gestion d'applications sur le VPS Hostinger.

---

## 📚 Fichiers de documentation

| Fichier | Description | Public cible |
|---------|-------------|--------------|
| **GUIDE_DEPLOIEMENT_VPS.md** | Déploiement d'applications Docker (Streamlit, Flask, React...) | Humains et LLM |
| **GUIDE_SERVICES_SYSTEMD.md** | Déploiement de services systemd (Ollama, PostgreSQL...) | Humains et LLM |
| **GUIDE_NGINX.md** | Configuration Nginx (sites statiques, reverse proxy, multi-sites) | Humains et LLM |
| **GUIDE_TROUBLESHOOTING_NGINX.md** | 🆕 Problèmes Nginx courants et solutions (SNI, SSL, redirections) | Humains et LLM |
| **GUIDE_WORDPRESS_DOCKER.md** | 🆕 WordPress en Docker (PHP-FPM, MySQL, permissions, migration complète, bonnes pratiques) | Humains et LLM |
| **GUIDE_WORDPRESS_MULTISITE.md** | Installation et configuration WordPress multisite | Humains et LLM |
| **GUIDE_ASTRO.md** | Déploiement sites Astro (SSG, build statique, troubleshooting) | Humains et LLM |
| **GUIDE_STRAPI.md** | Déploiement Strapi CMS (Docker, Node 22, solutions bugs Vite) | Humains et LLM |
| **GUIDE_TIKA.md** | 🆕 Apache Tika Server - Document parsing API (PDF, Office, OCR) | Humains et LLM |
| **GUIDE_WHISPER_SERVICES.md** | 🆕 Whisper APIs - Speech-to-text (faster-whisper + WhisperX diarization) | Humains et LLM |
| **GUIDE_API_PORTAL.md** | 🆕 API & Admin Portal - Swagger UI + Monitoring (Portainer, Dozzle, Netdata) | Humains et LLM |
| **GUIDE_EMAIL.md** | 🆕 Serveur email Postfix + OpenDKIM (SMTP, SPF/DKIM/DMARC, WordPress) | Humains et LLM |
| **GUIDE_DOCKER_AUTOSTART.md** | 🆕 Auto-start/stop Docker - Économise RAM (pages d'attente, mode blocking) | Humains et LLM |
| **INSTRUCTIONS_LLM.md** | Workflows et règles pour assistants IA (principe DRY) | LLM uniquement |
| **README.md** | Ce fichier - Vue d'ensemble | Tous |

---

## 🚀 Quick Start

### Scripts automatisés (Recommandé)

**Nouveau !** Utilisez les scripts batch interactifs :

```bash
# Déployer une nouvelle application
deploy.bat

# Mettre à jour une application existante
update.bat

# Gérer les applications (logs, redémarrer, etc.)
manage.bat
```

### Pour un humain

**Application Docker** (Streamlit, Flask, React, etc.) :
1. Ouvrez **GUIDE_DEPLOIEMENT_VPS.md**
2. Suivez la section "Déployer une nouvelle application"
3. Utilisez les templates fournis

**Service systemd** (Ollama, PostgreSQL, etc.) :
1. Ouvrez **GUIDE_SERVICES_SYSTEMD.md**
2. Suivez les exemples (ex: Ollama)
3. Adaptez à votre service

### Pour un LLM

1. Lisez **INSTRUCTIONS_LLM.md** (workflow + règles DRY)
2. Identifiez le type de déploiement (Docker vs systemd)
3. Lisez le guide technique approprié
4. Suivez le workflow autonome

---

## 📊 État actuel du serveur

### Informations serveur

- **IP** : `69.62.108.82`
- **Hostname** : `srv759970.hstgr.cloud`
- **OS** : Ubuntu 24.04.2 LTS
- **Uptime** : 195+ jours

### Applications et services déployés

| Application/Service | Type | Port(s) | Status | Path/Service |
|---------------------|------|---------|--------|--------------|
| Support Dashboard | Docker | 8501 | ✅ En ligne | `/opt/support-dashboard/` |
| SharePoint Dashboards | Docker | 8502 | ✅ En ligne | `/opt/sharepoint-dashboards/` |
| Cristina Site (Astro) | Static | 80 (Nginx) | ✅ En ligne | `/opt/cristina-site/` |
| Cristina Admin (Strapi) | Docker | 1337 | ✅ En ligne | `/opt/cristina-backend/` |
| **Clémence Site** | **Docker (WordPress FPM + MySQL)** | **9002** | ✅ **En ligne** | `/opt/wordpress-clemence/` |
| SolidarLink Site | WordPress (PHP 8.3) | 80 (Nginx) | ⏸️ Suspendu | `/var/www/solidarlink/` |
| ~~WordPress Multisite~~ | ~~PHP 8.3~~ | ~~80~~ | ⛔ À décommissionner | ~~`/var/www/wordpress/`~~ |
| Whisper API (faster-whisper) | Docker | 8001 | ✅ En ligne (auto-start) | `/opt/whisper-faster/` |
| WhisperX API (diarization) | Docker | 8002 | ✅ En ligne (auto-start) | `/opt/whisperx/` |
| Ollama API | Systemd | 11434 (local), 11435 (public) | ✅ En ligne | `ollama.service` |
| Apache Tika Server | Docker | 9998 | ✅ En ligne (auto-start) | `/opt/tika-server/` |
| API Portal (Swagger UI) | Docker | 8503 | ✅ En ligne | `/opt/api-portal/` |
| Portainer (Docker GUI) | Docker | 9000 | ✅ En ligne | Container: portainer |
| Dozzle (Logs Viewer) | Docker | 8888 | ✅ En ligne | Container: dozzle |
| Netdata (System Monitor) | Docker | 19999 | ✅ En ligne | Container: netdata |
| Postfix Email Server | Systemd | 25, 587 | ✅ En ligne | `postfix.service` |
| OpenDKIM | Systemd | - | ✅ En ligne | `opendkim.service` |

### Ports disponibles

- `8503` ➡️ Disponible
- `8504` ➡️ Disponible
- `8505` ➡️ Disponible
- ...

---

## 🔑 Accès rapide

### SSH

```bash
ssh root@69.62.108.82
```

### Panel Hostinger

https://hpanel.hostinger.com/

### Applications et services

- **Support Dashboard** : https://dashboard.srv759970.hstgr.cloud ou https://srv759970.hstgr.cloud
- **SharePoint Dashboards** : https://sharepoint.srv759970.hstgr.cloud
- **Cristina Site** : https://cristina.srv759970.hstgr.cloud
- **Cristina Admin** : https://admin.cristina.srv759970.hstgr.cloud/admin
- **Clémence Site** : https://clemence.srv759970.hstgr.cloud
- **SolidarLink Site** : https://solidarlink.srv759970.hstgr.cloud
- **Whisper API (faster-whisper)** : https://whisper.srv759970.hstgr.cloud
- **WhisperX API (diarization)** : https://whisperx.srv759970.hstgr.cloud
- **Ollama API** : http://69.62.108.82:11435
- **Apache Tika API** : https://tika.srv759970.hstgr.cloud
- **🎯 API & Admin Portal** : https://portal.srv759970.hstgr.cloud

---

## 🛠️ Scripts disponibles

### 1. `deploy.bat` - Déploiement automatique

Script interactif qui automatise **tout le workflow** de déploiement :

**Ce qu'il fait** :
1. ✅ Vérifie la connexion SSH
2. ✅ Vous demande le type d'application (Streamlit, Flask, FastAPI, Node, React)
3. ✅ Génère automatiquement Dockerfile et docker-compose.yml
4. ✅ Trouve un port disponible automatiquement
5. ✅ Crée la structure sur le VPS
6. ✅ Transfère les fichiers
7. ✅ Build l'image Docker
8. ✅ Lance le conteneur
9. ✅ Vérifie que tout fonctionne
10. ✅ Vous donne l'URL finale

**Utilisation** :
```bash
cd C:\Users\JulienFernandez\OneDrive\Coding\_référentiels de code\Hostinger
deploy.bat
```

Suivez simplement les questions à l'écran !

---

### 2. `update.bat` - Mise à jour d'application

Met à jour une application déjà déployée.

**Ce qu'il fait** :
- Liste toutes les applications déployées
- Vous laisse choisir ce que vous voulez mettre à jour :
  - **Tout** : Code + rebuild complet (slow mais safe)
  - **Code seulement** : Sans rebuild (rapide)
  - **Base de données seulement** : Juste les fichiers .db
  - **Redémarrer** : Sans changement

**Utilisation** :
```bash
update.bat
```

---

### 3. `manage.bat` - Gestion des applications

Interface interactive pour gérer toutes vos applications.

**Fonctionnalités** :
1. 📋 Voir les logs (temps réel ou historique)
2. 🔄 Redémarrer une application
3. ⏸️ Arrêter une application
4. ▶️ Démarrer une application
5. 🗑️ Supprimer une application
6. 📊 Voir les ressources (CPU/RAM)
7. 🧹 Nettoyer Docker
8. 📂 Lister toutes les applications

**Utilisation** :
```bash
manage.bat
```

Un menu interactif s'affiche, choisissez simplement l'action.

---

## 📞 Commandes rapides (manuelles)

Si vous préférez la ligne de commande :

### Voir tous les conteneurs

```bash
ssh root@69.62.108.82 "docker ps"
```

### Logs d'une application

```bash
ssh root@69.62.108.82 "docker logs [nom-conteneur] --tail=50"
```

### Redémarrer une application

```bash
ssh root@69.62.108.82 "cd /opt/[nom-app] && docker-compose restart"
```

### État des ressources

```bash
ssh root@69.62.108.82 "docker stats --no-stream"
```

---

## 🛠️ Services installés

- ✅ Docker 28.2.2
- ✅ Docker Compose
- ✅ Nginx 1.24.0
- ✅ PHP 8.3-FPM (WordPress)
- ✅ MySQL 8.0 (WordPress)
- ✅ Git
- ✅ Certbot (Let's Encrypt)
- ✅ Curl, rsync

---

## 🔋 Optimisation RAM - Auto-Start/Stop Docker

**Problème** : Services peu utilisés consomment constamment de la RAM (7.1GB/8GB = 89%)

**Solution** : Système custom Node.js qui démarre/arrête automatiquement les conteneurs Docker

### 📊 Impact

| État | RAM utilisée | Services actifs |
|------|-------------|-----------------|
| **Avant** (tous actifs) | 7.1GB / 8GB (89%) | Tous les conteneurs running |
| **Après** (auto-start) | 2.4GB / 8GB (30%) | Seulement services critiques |
| **Économie** | **4.7GB (66%)** | Conteneurs arrêtés au repos |

### ⚙️ Services avec auto-start

| Service | Mode | Page d'attente | Idle timeout |
|---------|------|----------------|--------------|
| Support Dashboard | Dynamic | ✅ Matrix theme | 30 min |
| SharePoint Dashboards | Dynamic | ✅ Shuffle theme | 30 min |
| Cristina Admin (Strapi) | Dynamic | ✅ Ghost theme | 30 min |
| Clémence Site (WordPress) | Dynamic | ✅ Ghost theme | 30 min |
| SolidarLink (WordPress) | Dynamic | ✅ Hacker Terminal | 30 min |
| Whisper API (faster-whisper) | Blocking | ❌ Attend silencieusement | 30 min |
| WhisperX API (diarization) | Blocking | ❌ Attend silencieusement | 30 min |
| Tika API | Blocking | ❌ Attend silencieusement | 30 min |

### 🚀 Comment ça marche

1. **Accès à l'URL** : https://dashboard.srv759970.hstgr.cloud
2. **Conteneurs arrêtés ?**
   - **Mode Dynamic** : Affiche page d'attente animée pendant ~15-20s
   - **Mode Blocking** : Attend silencieusement que l'API démarre
3. **Démarrage automatique** : `docker-compose start` lancé en arrière-plan
4. **Redirection** : Une fois prêt, proxifie vers le conteneur
5. **Auto-stop** : Après 30 min sans requête, conteneurs arrêtés automatiquement

### 📁 Commandes utiles

```bash
# Voir logs auto-start
journalctl -u docker-autostart -f

# Statut service
systemctl status docker-autostart

# Forcer arrêt pour test
cd /opt/support-dashboard && docker-compose stop
```

**Documentation complète** : [GUIDE_DOCKER_AUTOSTART.md](GUIDE_DOCKER_AUTOSTART.md)

---

## 📖 Pour aller plus loin

Consultez les guides détaillés :

- **[GUIDE_DEPLOIEMENT_VPS.md](GUIDE_DEPLOIEMENT_VPS.md)** - Déploiement Docker (Streamlit, Flask, React...)
- **[GUIDE_SERVICES_SYSTEMD.md](GUIDE_SERVICES_SYSTEMD.md)** - Services systemd (Ollama, PostgreSQL...)
- **[GUIDE_NGINX.md](GUIDE_NGINX.md)** - Configuration Nginx (sites statiques, reverse proxy, troubleshooting)
- **[GUIDE_TROUBLESHOOTING_NGINX.md](GUIDE_TROUBLESHOOTING_NGINX.md)** - 🆕 Résolution de problèmes Nginx (SNI, SSL, redirections)
- **[GUIDE_WORDPRESS_DOCKER.md](GUIDE_WORDPRESS_DOCKER.md)** - 🆕 WordPress en Docker (PHP-FPM, MySQL, permissions, migration complète, commandes, bonnes pratiques)
- **[GUIDE_WORDPRESS_MULTISITE.md](GUIDE_WORDPRESS_MULTISITE.md)** - Installation WordPress multisite
- **[GUIDE_ASTRO.md](GUIDE_ASTRO.md)** - Déploiement sites Astro (build statique, solutions 404)
- **[GUIDE_STRAPI.md](GUIDE_STRAPI.md)** - Déploiement Strapi CMS (Docker Node 22, bugs Vite résolus)
- **[GUIDE_TIKA.md](GUIDE_TIKA.md)** - 🆕 Apache Tika Server (document parsing API, PDF/Office/OCR)
- **[GUIDE_WHISPER_SERVICES.md](GUIDE_WHISPER_SERVICES.md)** - 🆕 Whisper APIs (faster-whisper + WhisperX diarization, auto-start)
- **[GUIDE_API_PORTAL.md](GUIDE_API_PORTAL.md)** - 🆕 API & Admin Portal (Swagger UI + Monitoring)
- **[GUIDE_EMAIL.md](GUIDE_EMAIL.md)** - 🆕 Serveur email Postfix + OpenDKIM (SMTP, SPF/DKIM/DMARC)
- **[GUIDE_DOCKER_AUTOSTART.md](GUIDE_DOCKER_AUTOSTART.md)** - 🆕 Auto-start/stop Docker (économie RAM 66%, pages d'attente)
- **[INSTRUCTIONS_LLM.md](INSTRUCTIONS_LLM.md)** - Workflows pour assistants IA (principe DRY)

---

---

## 🎯 Migrations récentes

### WordPress Clémence vers Docker (2025-10-17)

**Migration réussie** : Site WordPress Clémence de native (PHP-FPM + MySQL) vers Docker (3 conteneurs)

**Avant** :
- Type : Installation native (PHP 8.3-FPM + MySQL 8.0)
- Emplacement : `/var/www/clemence/`
- Stack : Nginx → PHP-FPM socket → MySQL natif

**Après** :
- Type : Docker (3 conteneurs : WordPress FPM + Nginx + MySQL)
- Emplacement : `/opt/wordpress-clemence/`
- Stack : Nginx host (443) → nginx-clemence (9002) → wordpress-clemence (9000) → mysql-clemence (3306)

**Détails techniques** :
- ✅ Backup complet : 1.2MB SQL + 36MB fichiers (5,015 fichiers)
- ✅ Plugins migrés : Elementor, Header Footer Elementor, WP Mail SMTP, Akismet, WordPress Importer
- ✅ Theme : hello-elementor
- ✅ Uploads : 1.6MB (médias 2025 + assets Elementor)
- ✅ Permissions : `user: "33:33"` (www-data)
- ✅ DB_HOST fixé : `mysql-clemence:3306`
- ✅ Reverse proxy HTTPS : Détection correcte configurée
- ✅ URLs uniformisées : siteurl et home en HTTPS

**Problèmes rencontrés et résolus** :
1. Permissions denied → `user: "33:33"` + `define('FS_METHOD', 'direct');`
2. Boucle redirection 301 → Fix reverse proxy HTTPS dans wp-config.php
3. DB_HOST localhost → Changement vers `mysql-clemence:3306`
4. URLs mixtes http/https → Uniformisation en HTTPS

**Résultat** :
- ✅ Site en ligne : https://clemence.srv759970.hstgr.cloud
- ✅ HTTP 200 OK
- ✅ Tous les plugins fonctionnels
- ✅ Header/Footer Elementor chargent correctement
- ✅ Admin WordPress accessible
- ✅ Uploads fonctionnent
- ✅ Installation plugins fonctionne (pas de demande FTP)

**Temps migration** : ~45 minutes (dont ~30 minutes de debug)

**Documentation créée** :
- **[GUIDE_WORDPRESS_DOCKER.md](GUIDE_WORDPRESS_DOCKER.md)** - Guide complet migration (architecture, 9 étapes, commandes, bonnes pratiques validées)

**Commandes utiles** :
```bash
# Logs
docker logs wordpress-clemence --tail=50

# Redémarrer
cd /opt/wordpress-clemence && docker-compose restart

# Stats
docker stats --no-stream | grep clemence

# Backup
docker exec mysql-clemence mysqldump -u root -p$MYSQL_ROOT_PASSWORD clemence_db > backup.sql
```

---

**Dernière mise à jour** : Octobre 2025
