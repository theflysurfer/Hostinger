# Scripts Utilitaires - Infrastructure srv759970

Documentation complète de tous les scripts d'automatisation pour la gestion de l'infrastructure.

---

## 📂 Organisation

```
scripts/
├── deployment/           # Scripts de déploiement et configuration
├── monitoring/          # Scripts de monitoring et génération de rapports
└── utils/              # Scripts utilitaires et synchronisation
```

---

## 🚀 Scripts de Déploiement

### `deployment/check-autostart-status.sh`

**Description:** Vérifie le statut et l'utilisation RAM des services avec auto-start.

**Usage:**
```bash
ssh root@69.62.108.82 "bash /root/hostinger/scripts/deployment/check-autostart-status.sh"
```

**Fonctionnalités:**
- ✅ Affiche le statut de chaque service (running/stopped)
- ✅ Affiche le temps d'uptime
- ✅ Affiche l'utilisation RAM en temps réel
- ✅ Liste les services configurés avec leur timeout

**Services surveillés:**
- RAGFlow (6.5GB) - 3 min timeout
- XTTS-API (2.5GB) - 3 min timeout
- Paperless (1.3GB) - 3 min timeout
- Nextcloud, MemVid, Jitsi, WordPress sites

**Exemple de sortie:**
```
=== Services Auto-Start - Status & RAM ===

Configuration actuelle:
- RAGFlow (6.5GB) : 3 min timeout
- XTTS-API (2.5GB) : 3 min timeout
...

=== État Actuel ===
ragflow-server     : ✅ RUNNING | Up 2 hours | RAM: 4.2GB / 6.5GB
xtts-api           : ⏸️  STOPPED | Exited (0) 3 hours ago
```

---

### `deployment/deploy-bot-protection.sh`

**Description:** Déploie la protection anti-bot sur Nginx (rate limiting + fail2ban).

**Usage:**
```bash
ssh root@69.62.108.82 "bash /root/hostinger/scripts/deployment/deploy-bot-protection.sh"
```

**Fonctionnalités:**
- ✅ Configure le rate limiting Nginx (10 req/s par IP)
- ✅ Configure fail2ban pour bannir les bots agressifs
- ✅ Crée les règles de bannissement automatique
- ✅ Reload Nginx et redémarre fail2ban
- ✅ Affiche le statut post-déploiement

**Configuration appliquée:**
- **Rate limit:** 10 requêtes/seconde par IP
- **Burst:** 20 requêtes max
- **Ban duration:** 1 heure après 10 violations en 5 minutes
- **Protection:** Tous les sites HTTPS

**Fichiers modifiés:**
- `/etc/nginx/conf.d/rate-limit.conf`
- `/etc/fail2ban/filter.d/nginx-rate-limit.conf`
- `/etc/fail2ban/jail.d/nginx-rate-limit.conf`

---

### `deployment/set-autostart-timeout.sh`

**Description:** Configure le timeout d'auto-stop pour les services Docker.

**Usage:**
```bash
ssh root@69.62.108.82 "bash /root/hostinger/scripts/deployment/set-autostart-timeout.sh <service-name> <timeout-minutes>"
```

**Exemples:**
```bash
# Set RAGFlow timeout to 5 minutes
./set-autostart-timeout.sh ragflow 5

# Set all heavy services to 3 minutes
./set-autostart-timeout.sh ragflow 3
./set-autostart-timeout.sh xtts 3
./set-autostart-timeout.sh paperless 3
```

**Services supportés:**
- ragflow, xtts, paperless, nextcloud, memvid, jitsi
- clemence, solidarlink (WordPress sites)

**Fonctionnalités:**
- ✅ Met à jour la config JSON sur le serveur
- ✅ Redémarre le service docker-autostart
- ✅ Affiche la nouvelle configuration
- ✅ Valide les changements

---

## 📊 Scripts de Monitoring

### `monitoring/generate-services-status-simple.sh`

**Description:** Génère une page de statut en temps réel de tous les services Docker (version rapide).

**Usage:**
```bash
# Local
./scripts/monitoring/generate-services-status-simple.sh

# Sur le serveur (avec alias)
update-services-status
```

**Sortie:** `docs/SERVICES_STATUS.md`

**Fonctionnalités:**
- ✅ Liste tous les containers Docker (actifs et arrêtés)
- ✅ Affiche le statut (🟢 running, 🔴 stopped, 🟡 restarting)
- ✅ Statistiques globales (total, actifs, arrêtés)
- ✅ Ressources système (RAM, disque)
- ✅ Top 10 consommateurs de RAM
- ✅ Mise à jour automatique toutes les 5 minutes via cron

**Cron Job:**
```bash
# Vérifie le cron actuel
crontab -l | grep services-status

# Configuration recommandée:
*/5 * * * * cd /root/hostinger && ./scripts/monitoring/generate-services-status-simple.sh >> /var/log/services-status.log 2>&1
```

**Intégration MkDocs:**
- URL: https://docs.srv759970.hstgr.cloud/SERVICES_STATUS/
- Menu: "🚀 Services Status (Live)"

---

### `monitoring/generate-services-status.sh`

**Description:** Version avancée avec catégorisation des services et URLs automatiques.

**Usage:**
```bash
./scripts/monitoring/generate-services-status.sh
```

**Différences avec la version simple:**
- ✅ Catégorisation des services (AI, Apps, Infrastructure, etc.)
- ✅ Détection automatique des URLs publiques
- ✅ Informations de ports détaillées
- ✅ Génération plus lente mais plus complète

**Note:** Utilisez la version simple pour les mises à jour fréquentes automatiques.

---

### `monitoring/generate-server-status.sh`

**Description:** Génère un rapport complet de l'état du serveur (services + système).

**Usage:**
```bash
./scripts/monitoring/generate-server-status.sh
```

**Sortie:** `docs/SERVER_STATUS.md`

**Contenu du rapport:**
- ✅ Informations serveur (hostname, IP, uptime)
- ✅ Ressources système (CPU, RAM, disque)
- ✅ Services systemd actifs
- ✅ Containers Docker avec statuts
- ✅ Ports en écoute
- ✅ Dernières lignes de logs critiques

---

### `monitoring/analyze-docker-dependencies.py`

**Description:** Analyse en profondeur les dépendances Docker (conteneurs, réseaux, volumes).

**Usage:**
```bash
python scripts/monitoring/analyze-docker-dependencies.py
```

**Fonctionnalités:**
- ✅ État détaillé de tous les conteneurs (actifs, arrêtés, unhealthy)
- ✅ Cartographie des réseaux et leurs conteneurs
- ✅ Identification des conteneurs multi-réseaux
- ✅ Analyse des volumes par projet
- ✅ Détection des volumes orphelins potentiels
- ✅ Statistiques globales (conteneurs, réseaux, volumes)

**Rapport généré:**
```
ANALYSE DES DÉPENDANCES DOCKER
===============================
Date: 2025-10-27 16:00:00

ÉTAT DES CONTENEURS
- 🟢 Actifs: 23
- 🔴 Arrêtés: 13
- ⚠️  Unhealthy: 2 (human-chain-backend, discord-voice-bot)

RÉSEAUX ET CONTENEURS
- 📡 ragflow_default (5 conteneurs)
- 📡 nextcloud_default (3 conteneurs)
...

VOLUMES POTENTIELLEMENT ORPHELINS
- invidious_*, paperless-ai_*, rag-anything_*
- 💡 18 volumes peuvent probablement être supprimés
```

**Cas d'usage:**
- Audit de l'infrastructure Docker
- Identification de ressources orphelines
- Planification de nettoyage
- Documentation de l'architecture
- Debugging de problèmes réseau

**Résultats récents (2025-10-27):**
- 23 conteneurs actifs, 13 arrêtés
- 2 conteneurs unhealthy détectés
- 17 réseaux customs configurés
- 41 volumes avec 18 potentiellement orphelins

---

## 🔧 Scripts Utilitaires

### `utils/sync-from-server.sh`

**Description:** Synchronise TOUTES les configurations du serveur vers le repo local.

**Usage:**
```bash
./scripts/utils/sync-from-server.sh
```

**Fichiers synchronisés:**
- `/opt/*/docker-compose.yml` → `server-configs/docker-compose/`
- `/etc/nginx/sites-available/*` → `server-configs/nginx/sites-available/`
- `/etc/nginx/snippets/*` → `server-configs/nginx/snippets/`
- `/opt/dashy/conf.yml` → `server-configs/dashy/`
- `/etc/systemd/system/*.service` → `server-configs/systemd/`
- `/etc/letsencrypt/renewal/*.conf` → `server-configs/certbot/`
- Fichiers `.env` (sensibles) → `server-configs/env/`

**Fonctionnalités:**
- ✅ Backup automatique avant sync
- ✅ Création de la structure si inexistante
- ✅ Logs détaillés de chaque opération
- ✅ Préserve les permissions

**Cas d'usage:**
- Backup régulier des configs
- Documentation de l'état actuel
- Préparation de migration
- Audit de sécurité

---

### `utils/sync-to-server.sh`

**Description:** Déploie les configurations locales vers le serveur.

**Usage:**
```bash
./scripts/utils/sync-to-server.sh [service-name]

# Exemples:
./scripts/utils/sync-to-server.sh nginx        # Sync Nginx uniquement
./scripts/utils/sync-to-server.sh dashy        # Sync Dashy uniquement
./scripts/utils/sync-to-server.sh              # Sync tout (prompt)
```

**Fonctionnalités:**
- ✅ Validation avant déploiement
- ✅ Backup automatique sur le serveur
- ✅ Reload/restart des services après changement
- ✅ Rollback automatique en cas d'erreur
- ✅ Mode dry-run disponible

**Services supportés:**
- nginx (sites-available, snippets)
- dashy (conf.yml)
- docker-compose (par service)
- systemd (service files)

**⚠️ Attention:** Ce script modifie la production ! Toujours tester en dry-run d'abord.

---

### `utils/sync-autostart-config.sh`

**Description:** Synchronise dynamiquement la configuration docker-autostart et met à jour la doc.

**Usage:**
```bash
./scripts/utils/sync-autostart-config.sh [--commit]

# Options:
# --commit    Commit automatiquement les changements dans Git
```

**Workflow:**
1. Récupère `/opt/docker-autostart/config.json` depuis le serveur
2. Parse la configuration et extrait les valeurs
3. Met à jour `configs/docker/docker-autostart-config-optimized.json` localement
4. Met à jour la documentation concernée (README, guides)
5. (Optionnel) Commit les changements dans Git

**Fonctionnalités:**
- ✅ Synchronisation bidirectionnelle
- ✅ Validation du JSON
- ✅ Mise à jour automatique de la doc
- ✅ Git commit optionnel
- ✅ Logs détaillés

**Cas d'usage:**
- Après modification des timeouts sur le serveur
- Avant/après ajout d'un nouveau service
- Audit de la configuration actuelle

---

### `utils/fix-tsx.py`

**Description:** Script Python pour corriger des problèmes de syntaxe TSX.

**Usage:**
```bash
python scripts/utils/fix-tsx.py <file.tsx>
```

**Note:** Script utilitaire ponctuel, peu utilisé dans l'infrastructure actuelle.

---

## 🔄 Workflows Courants

### Déployer un nouveau service

```bash
# 1. Créer la config docker-compose localement
# 2. Sync vers le serveur
./scripts/utils/sync-to-server.sh mon-service

# 3. Configurer l'auto-start (optionnel)
ssh root@69.62.108.82 "bash /root/hostinger/scripts/deployment/set-autostart-timeout.sh mon-service 3"

# 4. Vérifier le déploiement
./scripts/monitoring/generate-services-status-simple.sh
```

---

### Backup complet avant maintenance

```bash
# 1. Sync toutes les configs
./scripts/utils/sync-from-server.sh

# 2. Générer rapport d'état
./scripts/monitoring/generate-server-status.sh

# 3. Commit dans Git
git add server-configs/ docs/SERVER_STATUS.md
git commit -m "chore: backup configs before maintenance"
```

---

### Monitoring quotidien

```bash
# 1. Vérifier les services auto-start
ssh root@69.62.108.82 "bash /root/hostinger/scripts/deployment/check-autostart-status.sh"

# 2. Vérifier la page de statut (mise à jour auto via cron)
# https://docs.srv759970.hstgr.cloud/SERVICES_STATUS/
```

---

## 🛠️ Dépannage

### Script ne s'exécute pas

**Vérifier les permissions:**
```bash
ls -l scripts/**/*.sh
# Tous doivent être exécutables (-rwxr-xr-x)

# Rendre exécutable:
chmod +x scripts/**/*.sh
```

---

### Cron ne fonctionne pas

**Vérifier le cron:**
```bash
ssh root@69.62.108.82 "crontab -l"

# Vérifier les logs:
ssh root@69.62.108.82 "grep CRON /var/log/syslog | tail -20"

# Vérifier les logs spécifiques:
ssh root@69.62.108.82 "tail -f /var/log/services-status.log"
```

---

### Sync échoue

**Vérifier la connexion SSH:**
```bash
ssh root@69.62.108.82 "echo OK"
# Doit afficher: OK

# Vérifier les clés SSH:
ssh-add -l
```

---

## 📋 Maintenance

### Nettoyage des logs

```bash
# Sur le serveur
ssh root@69.62.108.82 "
  tail -1000 /var/log/services-status.log > /tmp/services-status.log.tmp
  mv /tmp/services-status.log.tmp /var/log/services-status.log
"
```

---

### Mise à jour des scripts sur le serveur

```bash
# Sync les scripts locaux vers le serveur
./scripts/utils/sync-to-server.sh scripts

# Ou manuellement:
scp scripts/**/*.sh root@69.62.108.82:/root/hostinger/scripts/
```

---

## 🔗 Ressources

- [Documentation principale](../README.md)
- [MkDocs Documentation](https://docs.srv759970.hstgr.cloud)
- [Dashy Portal](https://dashy.srv759970.hstgr.cloud)
- [Services Status (Live)](https://docs.srv759970.hstgr.cloud/SERVICES_STATUS/)

---

## 🚀 Évolutions Futures

- [ ] Script de déploiement automatique complet (CI/CD)
- [ ] Intégration Telegram pour notifications
- [ ] Dashboard temps réel des métriques
- [ ] Tests automatisés des scripts
- [ ] Rollback automatique en cas d'erreur

---

**Dernière mise à jour:** 2025-10-27
**Mainteneur:** Infrastructure Team
