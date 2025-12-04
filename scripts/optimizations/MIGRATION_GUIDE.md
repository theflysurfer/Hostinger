# 🚀 GUIDE DE MIGRATION - OPTIMISATIONS DOCKER P0

**Date:** 2025-11-09
**Applications:** RAG-Anything & WhisperX
**Gain estimé:** -13.27 GB (-60%)
**Temps estimé:** 2-3 heures

---

## 📋 PRÉ-REQUIS

- [ ] Accès SSH au serveur (automation@69.62.108.82)
- [ ] Backup des données existantes
- [ ] Les services peuvent être arrêtés pendant 10-15 minutes
- [ ] Token Hugging Face disponible (pour WhisperX)

---

## 🎯 PLAN DE MIGRATION

### Timeline
1. **Backup** - 15 min
2. **RAG-Anything** - 45 min
3. **WhisperX** - 45 min
4. **Tests** - 15 min
5. **Cleanup** - 10 min

**Total:** ~2h

---

## 📦 ÉTAPE 1 : BACKUP (15 min)

### 1.1 Backup des configurations actuelles

```bash
# Se connecter au serveur
ssh automation@69.62.108.82

# Créer répertoire de backup
mkdir -p ~/docker-backups/$(date +%Y%m%d)

# Backup RAG-Anything
cd /opt/rag-anything
tar -czf ~/docker-backups/$(date +%Y%m%d)/rag-anything-backup.tar.gz .

# Backup WhisperX
cd /opt/whisperx
tar -czf ~/docker-backups/$(date +%Y%m%d)/whisperx-backup.tar.gz .

# Vérifier les backups
ls -lh ~/docker-backups/$(date +%Y%m%d)/
```

### 1.2 Backup des volumes Docker

```bash
# Lister les volumes
docker volume ls | grep -E 'rag|whisperx'

# Backup volumes (optionnel mais recommandé)
docker run --rm -v whisperx_whisperx-redis-data:/data \
    -v ~/docker-backups/$(date +%Y%m%d):/backup \
    alpine tar -czf /backup/whisperx-redis-data.tar.gz /data
```

---

## 🔧 ÉTAPE 2 : RAG-ANYTHING (45 min)

### 2.1 Arrêter le service actuel

```bash
cd /opt/rag-anything

# Vérifier l'état
docker ps | grep rag-anything

# Arrêter
docker-compose down

# Vérifier l'arrêt
docker ps -a | grep rag-anything
```

### 2.2 Copier les fichiers optimisés

Depuis votre machine locale:

```bash
# Copier les fichiers optimisés
scp scripts/optimizations/rag-anything/Dockerfile.optimized \
    automation@69.62.108.82:/opt/rag-anything/

scp scripts/optimizations/rag-anything/docker-compose.optimized.yml \
    automation@69.62.108.82:/opt/rag-anything/

scp scripts/optimizations/rag-anything/Dockerfile.converter \
    automation@69.62.108.82:/opt/rag-anything/

scp scripts/optimizations/rag-anything/converter_service.py \
    automation@69.62.108.82:/opt/rag-anything/
```

Sur le serveur:

```bash
cd /opt/rag-anything

# Backup de l'ancien Dockerfile
mv Dockerfile Dockerfile.old
mv docker-compose.yml docker-compose.old.yml

# Renommer les fichiers optimisés
mv Dockerfile.optimized Dockerfile
mv docker-compose.optimized.yml docker-compose.yml
```

### 2.3 Construire la nouvelle image

```bash
cd /opt/rag-anything

# Build avec cache
docker-compose build

# Vérifier la taille
docker images | grep rag-anything
# Avant: ~12 GB
# Après: ~5 GB ✅
```

### 2.4 Démarrer le service

```bash
# Démarrer
docker-compose up -d

# Vérifier les logs
docker-compose logs -f rag-anything

# Attendre le healthcheck
watch -n 2 'docker ps | grep rag-anything'
```

### 2.5 Tester le service

```bash
# Test health endpoint
curl -f http://localhost:9510/health

# Test upload (adapter selon votre API)
curl -X POST http://localhost:9510/upload \
    -F "file=@test.pdf"
```

---

## 🎤 ÉTAPE 3 : WHISPERX (45 min)

### 3.1 Arrêter les services actuels

```bash
cd /opt/whisperx

# Arrêter tous les services WhisperX
docker-compose down

# Vérifier
docker ps -a | grep whisperx
```

### 3.2 Copier les fichiers optimisés

Depuis votre machine locale:

```bash
scp scripts/optimizations/whisperx/Dockerfile.optimized \
    automation@69.62.108.82:/opt/whisperx/

scp scripts/optimizations/whisperx/docker-compose.optimized.yml \
    automation@69.62.108.82:/opt/whisperx/

scp scripts/optimizations/whisperx/requirements.txt \
    automation@69.62.108.82:/opt/whisperx/
```

Sur le serveur:

```bash
cd /opt/whisperx

# Backup
mv Dockerfile Dockerfile.old
mv docker-compose.yml docker-compose.old.yml

# Renommer
mv Dockerfile.optimized Dockerfile
mv docker-compose.optimized.yml docker-compose.yml
```

### 3.3 Migrer les modèles

**IMPORTANT:** Les modèles doivent maintenant être dans un volume, pas dans l'image.

```bash
cd /opt/whisperx

# Si les modèles existent déjà dans ./models/
# Ils seront automatiquement montés par le nouveau docker-compose

# Vérifier
ls -lh ./models/
```

Si les modèles n'existent PAS localement:

```bash
# Créer le répertoire
mkdir -p ./models

# Les modèles seront téléchargés au premier démarrage
# Cela prendra ~5-10 minutes
```

### 3.4 Vérifier le token Hugging Face

```bash
cd /opt/whisperx

# Vérifier le fichier .env
cat .env | grep HF_TOKEN

# Si absent, ajouter:
echo "HF_TOKEN=your_token_here" >> .env
```

### 3.5 Construire les nouvelles images

```bash
cd /opt/whisperx

# Build
docker-compose build

# Vérifier la taille
docker images | grep whisperx
# Avant: 8.77 GB (x2)
# Après: 2.5 GB ✅
```

### 3.6 Démarrer les services

```bash
# Démarrer
docker-compose up -d

# Suivre les logs
docker-compose logs -f

# ⚠️ ATTENTION: Le premier démarrage peut prendre 5-10 min
# car les modèles Hugging Face seront téléchargés dans /models
```

### 3.7 Vérifier le téléchargement des modèles

```bash
# Suivre les logs du worker
docker logs whisperx-worker -f

# Vous devriez voir:
# "Downloading models from Hugging Face..."
# "Model cached at /models/..."

# Vérifier la taille du volume
docker exec whisperx ls -lh /models/
```

### 3.8 Tester le service

```bash
# Test health endpoint
curl -f http://localhost:8002/

# Test RQ Dashboard
curl -f http://localhost:9181/

# Test transcription (adapter selon votre API)
curl -X POST http://localhost:8002/transcribe \
    -F "file=@test.mp3"
```

---

## ✅ ÉTAPE 4 : VÉRIFICATION (15 min)

### 4.1 Vérifier tous les services

```bash
# Tous les conteneurs UP
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Size}}"

# Health checks
docker ps --filter "health=healthy"
```

### 4.2 Vérifier les gains de taille

```bash
# Images avant/après
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" \
    | grep -E 'rag-anything|whisperx'

# Espace total Docker
docker system df
```

### 4.3 Tester l'intégration

```bash
# Test Telegram Bot avec WhisperX
# (envoyer un message vocal au bot)

# Vérifier les logs
docker logs telegram-voice-bot -f
```

### 4.4 Vérifier le monitoring

```bash
# Prometheus metrics (si configuré)
curl http://localhost:9090/metrics | grep whisperx

# Flower dashboard
# Ouvrir dans le navigateur: http://whisperx-dashboard.srv759970.hstgr.cloud
```

---

## 🧹 ÉTAPE 5 : CLEANUP (10 min)

### 5.1 Supprimer les anciennes images

```bash
# Lister les anciennes images
docker images | grep -E 'rag-anything|whisperx' | grep -v latest

# Supprimer les images dangling
docker image prune -f

# Optionnel: Supprimer les anciennes images spécifiques
docker rmi <OLD_IMAGE_ID>
```

### 5.2 Nettoyer les backups (optionnel)

```bash
# Garder les backups pendant 30 jours
# Supprimer manuellement après validation complète

# Lister les backups
ls -lh ~/docker-backups/
```

### 5.3 Vérifier l'espace récupéré

```bash
# Espace Docker avant/après
docker system df

# Espace disque global
df -h
```

**Résultat attendu:**
```
Images:   48.59 GB → 35.32 GB (-13.27 GB) ✅
```

---

## 🚨 ROLLBACK EN CAS DE PROBLÈME

### Si RAG-Anything ne fonctionne pas:

```bash
cd /opt/rag-anything

# Arrêter
docker-compose down

# Restaurer l'ancienne config
mv Dockerfile.old Dockerfile
mv docker-compose.old.yml docker-compose.yml

# Rebuild et démarrer
docker-compose up -d --build
```

### Si WhisperX ne fonctionne pas:

```bash
cd /opt/whisperx

# Arrêter
docker-compose down

# Restaurer
mv Dockerfile.old Dockerfile
mv docker-compose.old.yml docker-compose.yml

# Rebuild
docker-compose up -d --build
```

### Restaurer depuis backup complet:

```bash
# Arrêter les services
cd /opt/rag-anything && docker-compose down
cd /opt/whisperx && docker-compose down

# Restaurer
cd /opt
rm -rf rag-anything whisperx

tar -xzf ~/docker-backups/YYYYMMDD/rag-anything-backup.tar.gz -C /opt/
tar -xzf ~/docker-backups/YYYYMMDD/whisperx-backup.tar.gz -C /opt/

# Redémarrer
cd /opt/rag-anything && docker-compose up -d
cd /opt/whisperx && docker-compose up -d
```

---

## 📊 RÉSULTATS ATTENDUS

### Gains de taille

| Service | Avant | Après | Gain |
|---------|-------|-------|------|
| RAG-Anything | 12 GB | 5 GB | -7 GB (-58%) |
| WhisperX (x2) | 17.54 GB | 5 GB | -12.54 GB (-71%) |
| **TOTAL** | **29.54 GB** | **10 GB** | **-19.54 GB (-66%)** |

### Gains de performance

- **Build time:** -50% en moyenne
- **Démarrage:** -30% plus rapide
- **RAM:** -6 GB au démarrage

### Gains de sécurité

- **User non-root:** ✅ (était ❌)
- **Multi-stage builds:** ✅ (était ❌)
- **Secrets management:** ✅ Amélioré
- **Score sécurité:** 25/100 → 78/100

---

## 📝 CHECKLIST FINALE

- [ ] Backup effectué
- [ ] RAG-Anything déployé et testé
- [ ] WhisperX déployé et testé
- [ ] Modèles téléchargés et cachés
- [ ] Tous les health checks verts
- [ ] Tests d'intégration passés
- [ ] Anciennes images supprimées
- [ ] Monitoring opérationnel
- [ ] Documentation mise à jour
- [ ] Équipe informée

---

## 🆘 SUPPORT

En cas de problème:

1. **Vérifier les logs:** `docker-compose logs -f`
2. **Health checks:** `docker ps --filter "health=unhealthy"`
3. **Rollback:** Suivre la procédure ci-dessus
4. **Contact:** Créer un ticket avec les logs

---

## 📚 RÉFÉRENCES

- Rapport d'audit complet: `scripts/DOCKER_AUDIT_REPORT.md`
- Dockerfiles optimisés: `scripts/optimizations/`
- Best practices Docker 2025: Voir rapport d'audit

---

**Bonne migration !** 🚀

N'oubliez pas de documenter tout problème rencontré pour améliorer ce guide.
