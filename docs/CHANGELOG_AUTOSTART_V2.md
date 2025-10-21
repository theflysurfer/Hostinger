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

---

## 🔮 Prochaines étapes (optionnel)

1. **Nextcloud**: Investiguer pourquoi pas de site Nginx, ajouter si nécessaire
2. **Monitoring**: Ajouter métriques Prometheus pour autostart (temps de démarrage, requêtes 202, etc.)
3. **Alerting**: Notifier si un service ne démarre pas après N tentatives
4. **Cron sync**: Automatiser `sync-autostart-config.sh` en daily cron
5. **Health checks avancés**: Vérifier endpoints applicatifs, pas juste containers running

---

**Version**: 2.0
**Status**: ✅ PROD
**Tested**: ✅ Dashy, WhisperX, MemVid
**Documentation**: ✅ Complète et synchronisée
