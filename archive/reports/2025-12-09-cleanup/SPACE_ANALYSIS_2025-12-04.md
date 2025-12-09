# Analyse Espace Disque - srv759970.hstgr.cloud

**Date**: 2025-12-04
**Serveur**: 69.62.108.82 (srv759970.hstgr.cloud)
**Statut**: CRITIQUE - 94% utilisé

---

## 📊 Vue d'ensemble

### Espace Disque Global

```
Filesystem: /dev/sda3
Size:       193GB
Used:       180GB (94%)
Available:  14GB (6%)
Status:     🔴 CRITIQUE
```

**Seuils**:
- ✅ Sain: < 80%
- ⚠️ Attention: 80-90%
- 🔴 **CRITIQUE: > 90%** ← État actuel

---

## 🔍 Analyse Détaillée par Catégorie

### 1. Docker (PRIORITÉ HAUTE)

#### Images Docker: 48.31 GB

**Top 10 images volumineuses**:

| Image | Taille | Usage | Action |
|-------|--------|-------|--------|
| whisperx_whisperx | 8.77GB | Active | Conserver |
| infiniflow/ragflow | 7.06GB | Active | Conserver |
| paperflow_paperflow-worker | 6.65GB | Active | Optimiser? |
| kokoro-fastapi-cpu | 5.61GB | Active | Conserver |
| calcom/cal.com | 4.82GB | Active | Conserver |
| jellyfin/jellyfin | 1.55GB | Active | Conserver |
| jellyseerr | 1.44GB | Active | Conserver |
| elasticsearch | 1.41GB | Active | Conserver |
| mongo:7 | 834MB | Active | Conserver |
| mysql:8.0 | 780MB | Active | Conserver |

**Images dangling**: 3 images (<none>:<none>)
**Espace récupérable**: ~18GB (37% des images)

**Détails docker system df**:
```
Images:     48.31GB (18GB reclaimable = 37%)
Containers: 2.8GB   (0GB reclaimable)
Volumes:    4.379GB (2.3GB reclaimable = 52%)
Build Cache: 0B
```

**Actions recommandées**:
- ✅ **SAFE**: `docker image prune -f` → ~500MB-1GB
- ⚠️ **MODERATE**: `docker image prune -a --filter "until=720h"` → ~5-10GB (images >30j)
- 🔴 **AGGRESSIVE**: `docker system prune -a --volumes` → ~20GB (DANGER: tout supprimer)

#### Volumes Docker: 4.4 GB

**Espace récupérable**: 2.3GB (52%)

**Actions recommandées**:
- ⚠️ `docker volume ls -f dangling=true` → Identifier volumes orphelins
- ⚠️ `docker volume prune -f` → Supprimer volumes dangling (~2.3GB)

#### Containers

**Containers actifs**: 51 containers
**Containers arrêtés**: 0
**Espace utilisé**: 2.8GB (tous actifs, rien à récupérer)

**Containers volumineux** (write layer):
- whisperx-worker: 1.53GB (unhealthy)
- calcom: 804MB
- rdtclient: 82MB

**Action**: Vérifier pourquoi whisperx-worker est unhealthy (potentiel data leak)

#### /var/lib/docker: Taille inconnue

**Problème**: `du -sh /var/lib/docker` timeout après 30s
**Cause possible**: Énorme quantité de fichiers (inode overhead)

**Actions recommandées**:
- Analyser par sous-répertoire:
  - `/var/lib/docker/overlay2/` (layers)
  - `/var/lib/docker/containers/` (logs)
  - `/var/lib/docker/volumes/`

---

### 2. Applications (/opt) - 8.5GB

#### Top 10 répertoires

| Répertoire | Taille | Type | Action |
|------------|--------|------|--------|
| impro-manager | 5.1GB | App | Analyser contenu |
| cristina-backend | 1.1GB | App | Analyser contenu |
| paperflow | 507MB | App | Vérifier uploads |
| whisperx | 280MB | Service | Conserver |
| backups | 212MB | Backup | Nettoyer anciens |
| coqui-tts | 210MB | Service | Conserver |
| ragflow | 205MB | Service | Conserver |
| DockerWakeUp | 77MB | Infra | Conserver |
| wordpress-clemence | 46MB | App | Conserver |
| wordpress-test-themes | 28MB | Dev | Supprimer? |

**Répertoire suspect**:
- **impro-manager (5.1GB)** - Anormalement volumineux pour une app
  - Hypothèse: uploads, cache, ou données non nettoyées
  - **Action**: Analyser `du -sh /opt/impro-manager/* | sort -rh`

**Actions recommandées**:
- ✅ **SAFE**: Supprimer `wordpress-test-themes` (28MB)
- ⚠️ **MODERATE**: Nettoyer anciens backups dans `/opt/backups/`
- 🔴 **INVESTIGATE**: Analyser impro-manager (potentiel 2-4GB récupérable)

---

### 3. Backups (/opt/backups) - 212 MB

**Contenu**:
```
mysql-data-prod-20251109-073431.tar.gz        15MB
wordpress-data-prod-20251109-073417.tar.gz    52MB
wordpress-clemence-config-20251109-073445.tar.gz  1KB
infrastructure/                               (répertoire)
wordpress-clemence/                           (répertoire)
```

**Total**: 67MB de fichiers + répertoires

**Politique de rétention**: Aucune actuellement définie

**Actions recommandées**:
- ✅ Définir politique de rétention (ex: 7 derniers backups)
- ✅ Implémenter rotation automatique
- ✅ Déplacer anciens backups vers stockage externe/S3
- Gain potentiel: ~50-150MB

---

### 4. Logs - 544 MB

#### /var/log

| Fichier/Répertoire | Taille | Action |
|--------------------|--------|--------|
| journal/ | 448MB | Limiter à 100MB |
| sysstat/ | 41MB | Conserver |
| nginx/ | 12MB | Rotation OK |
| rclone-music.log | 11MB | Nettoyer |
| syslog | 7.4MB | Rotation OK |
| syslog.1 | 7.1MB | Rotation OK |
| services-status.log | 2MB | Limiter |
| nginx-auto-docker.log | 1.4MB | Limiter |

**Systemd Journal**: 54.9MB (archives + actifs)

**Actions recommandées**:
- ✅ **SAFE**: `journalctl --vacuum-size=100M` → Gain ~350MB
- ✅ **SAFE**: Configurer `/etc/systemd/journald.conf`:
  ```ini
  SystemMaxUse=100M
  RuntimeMaxUse=100M
  ```
- ✅ Nettoyer `/var/log/rclone-music.log` → 11MB
- ✅ Limiter `/var/log/services-status.log` (rotation)
- Gain total: ~400MB

#### Docker Container Logs

**Problème potentiel**: Logs non limités dans containers

**Vérification**:
```bash
docker inspect --format='{{.LogPath}}' container_name
ls -lh /var/lib/docker/containers/*/container_name-json.log
```

**Actions recommandées**:
- Configurer log rotation dans `/etc/docker/daemon.json`:
  ```json
  {
    "log-driver": "json-file",
    "log-opts": {
      "max-size": "10m",
      "max-file": "3"
    }
  }
  ```

---

### 5. Fichiers Temporaires

#### /tmp

**Non analysé** (généralement nettoyé automatiquement)

**Actions recommandées**:
- ✅ Vérifier taille: `du -sh /tmp`
- ✅ Nettoyer si > 1GB: `find /tmp -type f -atime +7 -delete`

#### Caches applicatifs

**Locations potentielles**:
- `/home/automation/.cache/`
- `/root/.cache/`
- Caches npm, pip, Docker build cache

**Actions recommandées**:
- Analyser: `du -sh /home/automation/.cache /root/.cache 2>/dev/null`
- Nettoyer si nécessaire

---

### 6. Fichiers Volumineux (>500MB)

**Aucun fichier >500MB trouvé** en dehors de:
- `/mnt/rd/` (mount virtuel RClone - 12TB, n'utilise pas d'espace réel)
- Vidéos dans /mnt/rd sont des fichiers streamés, pas stockés localement

**Statut**: ✅ Pas de fichiers isolés anormalement volumineux

---

## 🎯 Plan de Récupération d'Espace

### Niveau 1: Actions SAFE (Immediate) - Gain: ~1-2GB

**Pas de risque, exécution immédiate recommandée**

1. **Nettoyer images Docker dangling** (~500MB-1GB)
   ```bash
   docker image prune -f
   ```

2. **Limiter journald** (~350MB)
   ```bash
   journalctl --vacuum-size=100M
   ```

3. **Nettoyer logs rclone** (11MB)
   ```bash
   > /var/log/rclone-music.log
   ```

4. **Supprimer wordpress-test-themes** (28MB)
   ```bash
   rm -rf /opt/wordpress-test-themes
   ```

**Total Niveau 1**: ~900MB-1.4GB récupérable

---

### Niveau 2: Actions MODERATE (Review Required) - Gain: ~10-15GB

**Requiert validation avant exécution**

1. **Nettoyer anciennes images Docker** (~5-10GB)
   ```bash
   # Images non utilisées depuis 30 jours
   docker image prune -a --filter "until=720h"
   ```

2. **Nettoyer volumes Docker orphelins** (~2.3GB)
   ```bash
   docker volume ls -f dangling=true
   docker volume prune -f
   ```

3. **Analyser et nettoyer impro-manager** (~2-4GB potentiel)
   ```bash
   du -sh /opt/impro-manager/*
   # Identifier uploads, cache, tmp
   ```

4. **Rotation backups** (~50-150MB)
   ```bash
   # Garder 7 derniers, supprimer anciens
   cd /opt/backups
   ls -t *.tar.gz | tail -n +8 | xargs rm -f
   ```

5. **Configurer log rotation Docker**
   - Éditer `/etc/docker/daemon.json`
   - Redémarrer Docker daemon

**Total Niveau 2**: ~10-15GB récupérable

---

### Niveau 3: Actions AGGRESSIVE (Expert Only) - Gain: ~20-30GB

**⚠️ DANGER: Peut casser des services**

1. **Prune complet Docker system** (~20GB)
   ```bash
   docker system prune -a --volumes
   ```
   **DANGER**: Supprime TOUTES les images non utilisées + volumes

2. **Rebuild images volumineuses**
   - whisperx (8.77GB) → Optimiser layers?
   - paperflow-worker (6.65GB) → Optimiser layers?
   - ragflow (7.06GB) → Version plus légère?

3. **Nettoyer /var/lib/docker/overlay2** manuellement
   **DANGER**: Peut corrompre containers

**Total Niveau 3**: ~20-30GB récupérable (RISQUÉ)

---

## 🚨 Problèmes Identifiés

### 1. Containers Unhealthy

**whisperx-worker**: Unhealthy + 1.53GB write layer
- Possible memory leak ou data accumulation
- **Action**: Investiguer logs, redémarrer si nécessaire

**paperflow-flower**: Unhealthy
- Service de monitoring Celery
- **Action**: Vérifier configuration

### 2. Espace Critique

**14GB disponibles** sur 193GB (6%)
- Risque: Services peuvent crasher si disque plein
- Urgence: **HAUTE**

### 3. Pas de Politique de Maintenance

**Manque**:
- Log rotation automatique
- Backup retention policy
- Image cleanup scheduled
- Monitoring espace disque

---

## 📋 Recommandations Stratégiques

### Court Terme (Cette Semaine)

1. **Exécuter Niveau 1** (SAFE) → +1-2GB immédiatement
2. **Analyser impro-manager** → Identifier source 5.1GB
3. **Configurer journald limits** → Prévenir future accumulation
4. **Review volumes Docker** → Identifier volumes inutiles

### Moyen Terme (Ce Mois)

1. **Implémenter backup rotation** → Script automatique
2. **Configurer Docker log rotation** → Prévenir log bloat
3. **Optimiser images volumineuses** → Multi-stage builds
4. **Créer monitoring disk space** → Alertes <20GB

### Long Terme (Prochain Trimestre)

1. **Évaluer upgrade stockage VPS** → Si récurrent
2. **Migrer backups vers S3/externe** → Libérer espace local
3. **Implémenter skill hostinger-space-reclaim** → Automation
4. **Documentation runbook maintenance** → Procédures claires

---

## 🛠️ Skill à Créer: hostinger-space-reclaim

### Structure Proposée

```yaml
name: hostinger-space-reclaim
description: Automated space reclamation procedures for srv759970
triggers:
  - "disk space"
  - "cleanup"
  - "reclaim space"
  - "free up space"

workflows:
  analyze:
    - Check disk usage
    - Docker system df
    - Top directories
    - Generate report

  safe-cleanup:
    - Prune dangling images
    - Vacuum journald
    - Clean known logs
    - Remove test files

  moderate-cleanup:
    - Prune old images (30d)
    - Prune dangling volumes
    - Rotate backups (keep 7)
    - Analyze app directories

  emergency:
    - All safe + moderate actions
    - Interactive prompts for aggressive
    - Safety confirmations
```

### Scripts Nécessaires

1. **analyze-space.sh** - Analyse complète
2. **safe-cleanup.sh** - Actions niveau 1
3. **moderate-cleanup.sh** - Actions niveau 2 (avec confirmations)
4. **emergency-cleanup.sh** - Wizard interactif
5. **monitor-space.sh** - Cron pour alertes

---

## 📊 Résumé Exécutif

### État Actuel
- **Espace utilisé**: 94% (180GB/193GB)
- **Disponible**: 14GB
- **Statut**: 🔴 CRITIQUE

### Espace Récupérable Estimé

| Niveau | Actions | Gain | Risque | Recommandation |
|--------|---------|------|--------|----------------|
| SAFE | Images dangling + logs + test files | 1-2GB | Aucun | ✅ Exécuter maintenant |
| MODERATE | Old images + volumes + backups + apps | 10-15GB | Faible | ⚠️ Review puis exécuter |
| AGGRESSIVE | System prune + rebuilds | 20-30GB | Élevé | 🔴 Éviter sauf urgence |

### Priorités Immédiates

1. ✅ **Exécuter Niveau 1** → Gain rapide sans risque
2. 🔍 **Analyser impro-manager** → Plus gros consommateur (5.1GB)
3. ⚙️ **Configurer log rotation** → Prévenir accumulation future
4. 📊 **Implémenter monitoring** → Alertes proactives

### Objectif Post-Cleanup

**Cible**: <80% utilisation (38GB libres)
**Réaliste avec Niveau 1+2**: ~70-75% (45-50GB libres)

---

**Rapport généré**: 2025-12-04
**Prochain review recommandé**: Après exécution Niveau 1+2
**Maintenance préventive**: Mensuelle
