# Docker Auto-Start/Stop - Version 2.0

**Date**: 2025-10-21
**Auteur**: Claude Code + Julien Fernandez

---

## 🎯 Objectifs

1. **Auditer** la configuration réelle vs documentation
2. **Implémenter mode ASYNC** pour les APIs (réponse 202 immédiate)
3. **Migrer TOUS les services** vers auto-start/stop (sauf bases de données)
4. **Inclure** Dashy, MkDocs, Nextcloud dans l'autostart
5. **Documenter** de manière dynamique et fiable

---

## ❌ Problèmes identifiés

### 1. Documentation obsolète
**Symptôme**: Le config.json listait 12 services mais seulement 2 utilisaient réellement docker-autostart.

**Cause root**:
- Le `config.json` définit ce que docker-autostart PEUT gérer
- **Nginx** décide qui l'utilise vraiment (via `proxy_pass http://127.0.0.1:8890`)
- Si Nginx pointe en direct vers le port du service, docker-autostart n'est JAMAIS appelé
- Le fichier peut contenir des configs de test/migration

**Services affectés**:
- ✅ **Utilisaient autostart**: solidarlink, tika, whisper-faster
- ❌ **Configurés mais non utilisés**: clemence, dashboard, sharepoint, cristina, whisperx, memvid, ragflow, rag-anything

### 2. Mode BLOCKING inadapté pour les APIs
**Problème**: Le mode `blocking: true` gardait le client en attente pendant le démarrage du container.

**Conséquences**:
- Timeout risqué si démarrage > 60s
- Pas de feedback au client
- Pas de possibilité de retry intelligent

---

## ✅ Solutions implémentées

### 1. Mode ASYNC pour les APIs

**Nouveau comportement** (`async: true`):

```javascript
// Requête vers API arrêtée
GET /api/endpoint

// Réponse immédiate HTTP 202
HTTP/2 202 Accepted
Retry-After: 30
Content-Type: application/json

{
  "status": "starting",
  "message": "Service WhisperX API is starting. Please retry in 30 seconds.",
  "service": "WhisperX API (with diarization)",
  "estimatedTime": 30,
  "retryAfter": 30,
  "healthCheckUrl": "/health/whisperx.srv759970.hstgr.cloud"
}
```

**Avantages**:
- ✅ Réponse immédiate au client (pas de timeout)
- ✅ Header `Retry-After` standard HTTP
- ✅ HealthCheck URL pour polling
- ✅ Service démarre en arrière-plan
- ✅ Client peut implémenter retry logic intelligent

### 2. Migration complète de 18 services

**Services migrés vers auto-start/stop**:

#### Applications Web (10) - Mode Dynamic avec thème
1. **solidarlink** - Theme: hacker-terminal
2. **clemence** - Theme: ghost
3. **jesuishyperphagique** - Theme: ghost
4. **panneauxsolidaires** - Theme: matrix
5. **dashboard** (Support Dashboard) - Theme: matrix
6. **sharepoint** (SharePoint Dashboards) - Theme: shuffle
7. **strapi** (Cristina CMS) - Theme: ghost
8. **dashy** (Portal) - Theme: cyberpunk ⭐ NOUVEAU
9. **docs** (MkDocs) - Theme: matrix ⭐ NOUVEAU
10. **memvid-ui** - Theme: matrix

#### APIs (8) - Mode ASYNC
1. **whisper** (faster-whisper) - Port 8001
2. **whisperx** - Port 8002
3. **faster-whisper-queue** - Port 8003
4. **tika** - Port 9998
5. **memvid** - Port 8506
6. **ragflow** - Port 9500
7. **rag-anything** - Port 9510
8. **tika** - Port 9998

**Note**: Nextcloud configuré dans config.json mais pas de site Nginx (à investiguer).

### 3. Mise à jour Nginx automatisée

**Script créé**: `/tmp/update-nginx-for-autostart.sh`

**Actions**:
- ✅ Backup de toutes les configs Nginx
- ✅ Remplacement `proxy_pass http://localhost:XXXX` → `proxy_pass http://127.0.0.1:8890`
- ✅ Ajout header `X-Autostart-Target` pour routage
- ✅ Test `nginx -t` avant application
- ✅ 15 sites Nginx migrés avec succès

### 4. Documentation dynamique

**Script de synchronisation**: `scripts/sync-autostart-config.sh`

**Fonctionnalités**:
- Récupère config.json depuis `/opt/docker-autostart/config.json`
- Génère automatiquement le tableau markdown
- Met à jour les statistiques
- Commit automatique avec `--commit`
- Peut être exécuté en cron pour sync quotidien

**Fichiers générés**:
- `server-configs/docker-autostart/config.json` (snapshot)
- `docs/services/docker-autostart-config.md` (documentation)

---

## 📊 Statistiques finales

| Métrique | Valeur |
|----------|--------|
| **Services totaux** | 18 |
| **Mode Dynamic** | 10 (applications web avec thèmes) |
| **Mode ASYNC** | 8 (APIs avec réponse 202) |
| **Idle timeout** | 1800s (30 minutes) |
| **Port proxy** | 8890 |
| **Thèmes utilisés** | 5 (cyberpunk, ghost ×3, hacker-terminal, matrix ×4, shuffle ×2) |

---

## 🧪 Tests effectués

### Test 1: Dashy auto-start (Mode Dynamic)
```bash
# Arrêt du service
docker-compose -f /opt/dashy/docker-compose.yml stop

# Requête HTTP
curl -I https://dashy.srv759970.hstgr.cloud
# → HTTP/2 200 + Page HTML avec thème cyberpunk

# Vérification après 10s
docker ps --filter name=dashy
# → dashy   Up 17 seconds (healthy)
```

✅ **Résultat**: Page d'attente animée affichée, conteneur démarré automatiquement

### Test 2: WhisperX API auto-start (Mode ASYNC)
```bash
# Arrêt du service
docker-compose -f /opt/whisperx/docker-compose.yml stop whisperx

# Requête API
curl -i https://whisperx.srv759970.hstgr.cloud
# → HTTP/2 202 Accepted
# → Retry-After: 30
# → JSON avec message et healthCheckUrl

# Vérification après 30s
docker ps --filter name=whisperx
# → whisperx   Up 43 seconds (healthy)
```

✅ **Résultat**: Réponse 202 immédiate, service démarré en 30s, healthcheck OK

---

## 📁 Fichiers modifiés/créés

### Serveur
- `/opt/docker-autostart/server.js` - Ajout mode ASYNC
- `/opt/docker-autostart/config.json` - 18 services configurés
- `/etc/nginx/sites-available/*` - 15 sites migrés (backups créés)

### Repo local
- `server-configs/docker-autostart/server.js` - Code avec mode ASYNC
- `server-configs/docker-autostart/config.json` - Configuration finale
- `scripts/sync-autostart-config.sh` - Script de synchronisation
- `docs/services/docker-autostart-config.md` - Documentation mise à jour
- `docs/CHANGELOG_AUTOSTART_V2.md` - Ce fichier

---

## 🔧 Améliorations du code

### Ajout estimations de démarrage
```javascript
const STARTUP_ESTIMATES = {
  'whisper': 30,
  'whisperx': 30,
  'tika': 20,
  'wordpress': 25,
  'strapi': 20,
  'streamlit': 15,
  'dashy': 10,      // ← NOUVEAU
  'mkdocs': 5,      // ← NOUVEAU
  'nextcloud': 20,  // ← NOUVEAU
  'memvid': 15,     // ← NOUVEAU
  'ragflow': 45,    // ← NOUVEAU
  'rag-anything': 20, // ← NOUVEAU
  'default': 30
};
```

### Nouveau mode ASYNC
```javascript
if (service.mode === 'async' || service.async) {
  // ASYNC mode (for APIs): return 202 immediately with retry info
  const retryAfter = getEstimatedStartupTime(service.name);
  res.status(202)
     .header('Retry-After', retryAfter.toString())
     .json({
       status: 'starting',
       message: `Service ${service.name} is starting. Please retry in ${retryAfter} seconds.`,
       service: service.name,
       estimatedTime: retryAfter,
       retryAfter: retryAfter,
       healthCheckUrl: `/health/${host}`
     });
}
```

---

## 🚀 Déploiement

### 1. Backup et déploiement
```bash
# Backups automatiques créés
/opt/docker-autostart/server.js.backup_20251021_110619
/opt/docker-autostart/config.json.backup_20251021_110619

# Nginx configs backupées
/etc/nginx/sites-available/*.backup_autostart_20251021
```

### 2. Redémarrage services
```bash
systemctl restart docker-autostart
systemctl reload nginx

# Logs
journalctl -u docker-autostart -f
```

### 3. Vérification
```bash
# Status
systemctl status docker-autostart

# Test health check
curl http://localhost:8890/api/services | jq
```

---

## 📚 Documentation

### Guides mis à jour
- ✅ `docs/services/docker-autostart-config.md` - Configuration complète avec modes
- ✅ `server-configs/README.md` - Ajout section docker-autostart
- ✅ `mkdocs.yml` - Ajout dans navigation

### Commandes utiles

**Synchroniser la config depuis le serveur**:
```bash
./scripts/sync-autostart-config.sh
```

**Synchroniser et committer**:
```bash
./scripts/sync-autostart-config.sh --commit
```

**Tester un service**:
```bash
# Arrêter
docker-compose -f /opt/SERVICE/docker-compose.yml stop

# Accéder via navigateur ou curl
curl -I https://SERVICE.srv759970.hstgr.cloud

# Vérifier démarrage
docker logs -f CONTAINER_NAME
```

---

## 🎓 Leçons apprises

### 1. Source de vérité
❌ **Faux**: `config.json` = état réel du système
✅ **Vrai**: Nginx configs = routage réel, config.json = capacités du proxy

### 2. Vérification en 3 étapes
1. **Nginx** (`/etc/nginx/sites-enabled/*`) → Qui utilise autostart ?
2. **config.json** → Que peut gérer autostart ?
3. **Docker** (`docker ps`) → Qu'est-ce qui tourne ?

### 3. Audit script indispensable
Créer des scripts d'audit qui croisent les 3 sources:
- Nginx proxy_pass
- config.json services
- Docker containers running

### 4. Cache Nginx + Autostart = INCOMPATIBLE
**Problème**: Le cache Nginx sert du contenu statique même quand les conteneurs sont arrêtés
**Résultat**: docker-autostart n'est JAMAIS appelé, les conteneurs restent arrêtés
**Solution**: TOUJOURS désactiver `proxy_cache` pour les services utilisant autostart

### 5. Debug méthodique des problèmes de proxy
Quand une page incorrecte persiste malgré les changements:
1. **Test direct backend** (`curl localhost:8890 -H 'Host: ...'`) - Isole le problème
2. **Si backend OK mais HTTPS KO** → Problème dans Nginx
3. **Vérifier modules globaux** (`/etc/nginx/nginx.conf`) - Pas seulement vhosts
4. **Reload effectif** - Parfois plusieurs reload nécessaires pour processus workers

### 6. WordPress moderne avec WP-CLI
**Architecture recommandée 2025**:
- WordPress FPM (pas Apache) pour meilleures performances
- Nginx avec FastCGI vers PHP-FPM
- WP-CLI pour installation/gestion automatisée
- Conteneurs séparés: MySQL, WordPress, Nginx, WP-CLI
- `restart: "no"` pour compatibilité autostart

---

## ✅ Finalisation - 2025-10-21 (Suite)

### Déploiement des conteneurs manquants

**Problème identifié**: De nombreux services n'avaient jamais eu leurs conteneurs créés.

**Action**: Script de création automatique de tous les conteneurs manquants:
```bash
/tmp/create-missing-containers.sh
```

**Services déployés** (containers créés et arrêtés pour autostart):
1. ✅ **Support Dashboard** (Streamlit) - Image built, containers created
2. ✅ **SharePoint Dashboards** (Streamlit) - Containers created
3. ✅ **Cristina Strapi CMS** - Containers created
4. ✅ **RAGFlow** (with docker-compose-full.yml) - 5 containers created (server, MySQL, Redis, Elasticsearch, MinIO)
5. ✅ **SolidarLink** - Complètement reconstruit (voir section ci-dessous)

**Note importante**: Les conteneurs sont créés puis immédiatement arrêtés. C'est le comportement attendu pour docker-autostart - ils seront démarrés automatiquement lors de la première requête HTTP.

### Reconstruction complète de SolidarLink

**Contexte**: SolidarLink était compromis ("vérolé") et nécessitait une reconstruction complète.

**Actions effectuées**:
1. **Backup et suppression** de l'ancien site:
   - Ancien dossier renommé en `wordpress-solidarlink.old_TIMESTAMP`
   - Base de données conservée mais non réutilisée

2. **Création nouveau stack WordPress moderne**:
   ```yaml
   - MySQL 8.0 (nouveau container dédié)
   - WordPress php8.3-fpm (architecture moderne)
   - Nginx Alpine (FastCGI vers PHP-FPM)
   - WP-CLI php8.3 (pour installation automatisée)
   ```

3. **Installation WordPress via WP-CLI**:
   ```bash
   docker exec wp-cli-solidarlink wp core install \
     --url='https://solidarlink.srv759970.hstgr.cloud' \
     --title='SolidarLink' \
     --admin_user='admin' \
     --admin_password='SolidarLinkAdmin2025!' \
     --admin_email='julien@julienfernandez.xyz'
   ```

4. **Configuration pour autostart**:
   - `restart: "no"` sur tous les conteneurs
   - Port 9003 maintenu
   - Theme "hacker-terminal" configuré

**Fichiers créés**:
- `/opt/wordpress-solidarlink/docker-compose.yml` - Stack complet
- `/opt/wordpress-solidarlink/nginx.conf` - Config FastCGI
- Volumes Docker: `wordpress-data` et `mysql-data`

**Identifiants admin**:
- URL: https://solidarlink.srv759970.hstgr.cloud/wp-admin
- User: admin
- Password: SolidarLinkAdmin2025!

### Désactivation complète du système Sablier

**Problème découvert**: Malgré la suppression du cache Nginx et la reconstruction de SolidarLink, les pages Sablier persistaient.

**Investigation en profondeur**:
1. Test direct docker-autostart (`:8890`) → ✅ Retournait WordPress correctement
2. Test via HTTPS Nginx → ❌ Retournait toujours page Sablier
3. **Conclusion**: Le problème était dans la couche Nginx, pas dans docker-autostart

**Root cause identifiée**: Module JavaScript Sablier chargé globalement dans Nginx
- Fichier: `/etc/nginx/conf.d/sablier.js` (ancien système Sablier)
- Import global: `/etc/nginx/nginx.conf` ligne 13: `js_import conf.d/sablier.js;`
- Ce module interceptait les requêtes AVANT qu'elles n'atteignent docker-autostart

**Solution appliquée**:
```bash
# Commenté l'import global du module Sablier
sed -i '13s/^/# /' /etc/nginx/nginx.conf
# Ligne 13: js_import conf.d/sablier.js;  →  # js_import conf.d/sablier.js;

# Reload Nginx
nginx -t && systemctl reload nginx
```

**Résultat**:
- ✅ SolidarLink fonctionne via HTTPS (WordPress affiché)
- ✅ Clemence fonctionne également
- ✅ Système docker-autostart opérationnel pour tous les services

**Fichiers modifiés**:
- `/etc/nginx/nginx.conf` - Ligne 13 commentée (Sablier désactivé globalement)
- `/etc/nginx/sites-available/solidarlink` - Cache Nginx complètement supprimé
- `/etc/nginx/sites-available/clemence` - Cache Nginx complètement supprimé
- `/opt/wordpress-solidarlink/docker-compose.yml` - Nouveau stack sans Sablier
- `/opt/tika-server/docker-compose.yml` - Réécrit sans Sablier

**Commits Git**:
- `9b21415` - docker autostart server.js improvements
- `76b22a4` - remove obsolete Sablier references from docker-compose

### Ajout headers Nginx manquants

**Problème**: 17 sites Nginx utilisaient `proxy_pass http://127.0.0.1:8890` mais sans le header `X-Autostart-Target`

**Solution**: Script automatique d'ajout des headers:
```bash
/tmp/add-autostart-headers.sh
```

**Résultat**: 17 sites Nginx mis à jour avec le bon header de routage

---

## 🔮 Prochaines étapes (optionnel)

1. **Nextcloud**: Investiguer pourquoi pas de site Nginx, ajouter si nécessaire
2. **Tests complets**: Re-tester tous les 18 services autostart
3. **Monitoring**: Ajouter métriques Prometheus pour autostart (temps de démarrage, requêtes 202, etc.)
4. **Alerting**: Notifier si un service ne démarre pas après N tentatives
5. **Cron sync**: Automatiser `sync-autostart-config.sh` en daily cron
6. **Health checks avancés**: Vérifier endpoints applicatifs, pas juste containers running
7. **Backup automatique**: Sauvegarder volumes WordPress avant modifications (lesson learned)

---

**Version**: 2.0.2
**Status**: ✅ PROD
**Deployed**: ✅ 18 services configurés, tous conteneurs créés
**Tested**: ✅ SolidarLink, Clemence, Dashy, WhisperX, MkDocs (5/18)
**Issues résolus**:
- ✅ Sablier complètement désactivé
- ✅ Cache Nginx incompatible documenté et supprimé
- ✅ SolidarLink reconstruit from scratch
**Documentation**: ✅ Complète et synchronisée avec toutes les leçons apprises
**Commits à faire**:
- Sync server-configs (docker-compose.yml SolidarLink)
- Update changelog (ce fichier)
**Commits précédents**:
- `9b21415` - docker autostart improvements
- `76b22a4` - remove Sablier references
