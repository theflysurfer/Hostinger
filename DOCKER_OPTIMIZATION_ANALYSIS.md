# Analyse Détaillée et Optimisation des Images Docker

**Date**: 2025-12-04
**Serveur**: srv759970.hstgr.cloud

---

## 📊 Analyse Détaillée des 3 Plus Gros Consommateurs

### 1. WhisperX (8.77 GB) - PRIORITÉ HAUTE

#### Analyse Actuelle

**Image**: `whisperx_whisperx:latest` (8.77GB)
**Base**: `python:3.11-slim`
**Layers principaux**:
- Python dependencies (pip install): **7.9GB** ← GROS PROBLÈME
- System packages (ffmpeg, git, curl): 745MB
- Python base: 78.6MB
- Application code: 17.3kB

**Dépendances clés installées**:
```
torch                    2.8.0      ← GPU version (lourd!)
torchaudio               2.8.0      ← GPU version
whisperx                 3.7.4
pytorch-lightning        2.6.0
faster-whisper           1.2.1
fastapi                  0.104.1
```

**Dockerfile actuel**:
```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg git curl
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py worker.py ./
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8002"]
```

#### Problèmes Identifiés

1. **PyTorch GPU par défaut** (6-7GB)
   - Installe CUDA libs même si pas nécessaire
   - CPU-only PyTorch = ~2.5GB vs ~7GB pour GPU version

2. **Pas de multi-stage build**
   - Tous les outils de build restent dans l'image finale
   - git, curl non nécessaires au runtime

3. **Dependencies non optimisées**
   - `pytorch-lightning` peut-être superflu
   - `torch-audiomentations` si utilisé rarement

#### Recommandations d'Optimisation

**Option A: CPU-Only PyTorch** (Gain: ~4-5GB)

Si WhisperX n'utilise PAS de GPU:
```dockerfile
# Multi-stage build
FROM python:3.11-slim as builder

WORKDIR /app

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch torchaudio && \
    pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install only runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application
COPY server.py worker.py ./

EXPOSE 8002
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8002"]
```

**Taille estimée**: 3-4GB (gain de ~5GB)

**Option B: Garder GPU mais optimiser** (Gain: ~1-2GB)

Si GPU nécessaire:
```dockerfile
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04 as base

# Install Python 3.11
RUN apt-get update && apt-get install -y \
    python3.11 python3.11-dev python3-pip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Multi-stage for deps
FROM base as builder
COPY requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

FROM base
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY server.py worker.py ./
EXPOSE 8002
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8002"]
```

**Taille estimée**: 6-7GB (gain de ~2GB)

**Recommandation finale**: Option A si pas de GPU, sinon Option B

---

### 2. impro-manager (5.1 GB) - CRITIQUE DATA

#### Analyse Actuelle

**Répertoire**: `/opt/impro-manager`
**Contenu**:
```
4.1G    music/              ← FICHIERS MP3 (80% du total!)
856M    nextjs-app/
129M    node_modules/
77M     client/
1.5M    data/
772K    music_library.json
```

**Fichiers MP3 trouvés**:
- Musiques de spectacles (dossiers par date)
- Musiques d'ambiance
- Musiques entre impros
- Total: ~4.1GB de MP3

#### Problème Identifié

**Ce ne sont PAS des données Docker** mais des **assets applicatifs**!

- Application Next.js pour gestion de musiques d'improvisation
- Fichiers MP3 stockés localement dans `/opt/impro-manager/music/`
- Ces fichiers devraient être:
  - ✅ Dans un volume Docker séparé
  - ✅ Sur un CDN/S3
  - ✅ Sur le mount RClone (/mnt/rd)

#### Recommandations

**Option 1: Migrer vers /mnt/rd** (Gain: 4.1GB)

Le serveur a déjà un mount RClone de 1PB (`/mnt/rd`):
```bash
# Migrer musiques vers RClone
mv /opt/impro-manager/music /mnt/rd/impro-manager-music

# Créer symlink
ln -s /mnt/rd/impro-manager-music /opt/impro-manager/music

# Mettre à jour docker-compose.yml
volumes:
  - /mnt/rd/impro-manager-music:/app/music:ro
```

**Gain**: 4.1GB sur disque local (immédiat)

**Option 2: Volume Docker séparé** (Bonne pratique)

```yaml
# docker-compose.yml
services:
  impro-manager:
    volumes:
      - impro-music-data:/app/music

volumes:
  impro-music-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /mnt/rd/impro-manager-music
```

**Option 3: Nettoyer anciennes musiques** (Conservateur)

```bash
# Identifier musiques non utilisées depuis 6 mois
find /opt/impro-manager/music -type f -name "*.mp3" -mtime +180

# Archiver si nécessaire
tar czf /opt/backups/impro-music-archive-$(date +%F).tar.gz \
  /opt/impro-manager/music/old-files/
```

**Recommandation finale**: Option 1 (migration vers RClone)

---

### 3. Cal.com (4.82 GB)

#### Analyse Actuelle

**Image**: `calcom/cal.com:v4.7.8` (4.82GB)
**Base**: Node.js 18.20.5
**Layers principaux**:
- Application files (COPY /calcom ./): **3.73GB** ← Tout l'app
- Node.js runtime: 154MB
- Yarn: 5.34MB

**Structure**:
- Image officielle Cal.com
- Contient tout le monorepo (node_modules + .next + source)

#### Problèmes Identifiés

1. **Image officielle non optimisée**
   - Contient probablement dev dependencies
   - Pas de multi-stage visible

2. **Monorepo complet copié**
   - 3.73GB de fichiers copiés en un seul layer
   - Probablement beaucoup de node_modules inutiles

#### Recommandations

**Option A: Utiliser image slim si disponible**

Vérifier si Cal.com propose une version slim:
```bash
docker pull calcom/cal.com:v4.7.8-slim
```

**Option B: Builder une image custom** (Avancé)

Si vraiment besoin d'optimiser:
```dockerfile
# Build stage
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Runtime stage
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./
CMD ["npm", "start"]
```

**Taille estimée**: 2-3GB (gain ~2GB)

**Option C: Accepter la taille** (Pragmatique)

Cal.com est une app tierce complexe:
- Maintenir image custom = overhead maintenance
- Gain potentiel limité (2GB max)
- Mises à jour plus complexes

**Recommandation finale**: Option C (accepter) - Le jeu n'en vaut pas la chandelle

---

## 🎯 Best Practices Docker 2025 (Recherche Internet)

### Multi-Stage Builds

**Réduction attendue**: 50-90% selon cas

**Pattern recommandé**:
```dockerfile
# Stage 1: Build
FROM python:3.11-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y gcc g++
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
CMD ["python", "app.py"]
```

**Sources**:
- [Docker Best Practices](https://docs.docker.com/build/building/best-practices/)
- [LogRocket - Multi-stage builds](https://blog.logrocket.com/reduce-docker-image-sizes-using-multi-stage-builds/)
- [Spacelift - Docker Multistage Builds](https://spacelift.io/blog/docker-multistage-builds)

### Python ML Images Optimization

**Techniques clés 2025**:

1. **Use slim/alpine base** (-32% à -85%)
   ```dockerfile
   FROM python:3.11-slim  # vs python:3.11
   FROM python:3.11-alpine  # encore plus petit
   ```

2. **CPU-only PyTorch** (-60% pour torch)
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cpu
   ```

3. **No cache + cleanup** (-10-20%)
   ```dockerfile
   RUN pip install --no-cache-dir -r requirements.txt && \
       rm -rf /root/.cache /tmp/*
   ```

4. **Remove unnecessary files** (-5-10%)
   ```dockerfile
   RUN find /usr/local -depth \
       \( -type d -a \( -name test -o -name tests \) \) \
       -o \( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
       -exec rm -rf '{}' +
   ```

**Cas réel documenté**: 3.09GB → 280MB (90% de réduction)

**Sources**:
- [Stack Overflow - Reduce Python Docker size](https://stackoverflow.com/questions/78105348/how-to-reduce-python-docker-image-size)
- [Collabnix - Docker Image Reduction Journey](https://collabnix.com/how-i-reduced-a-docker-image-size-by-90-a-step-by-step-journey/)
- [Wayfair Case Study - 50% reduction](https://www.aboutwayfair.com/case-study-how-we-decreased-the-size-of-our-python-docker-images-by-over-50)

### Node.js Images

**Techniques clés**:

1. **Alpine base** (-60%)
   ```dockerfile
   FROM node:18-alpine  # 40MB vs 180MB for slim
   ```

2. **Production deps only**
   ```dockerfile
   RUN npm ci --only=production
   ```

3. **Multi-stage with build artifacts**
   ```dockerfile
   COPY --from=builder /app/.next ./
   COPY --from=builder /app/node_modules ./node_modules
   ```

### Security Benefits (2025)

**Nouveau en 2025**: Micro-distros sécurisées
- Wolfi
- Chainguard Images

**Avantages**:
- Smaller attack surface
- Fewer CVEs
- Faster security patches

**Sources**:
- [Medium - Docker Best Practices 2025](https://saraswathilakshman.medium.com/optimise-your-docker-images-for-speed-and-security-best-practices-for-2025-e888f6dc131f)
- [Markaicode - Multi-Stage Build Tricks 2025](https://markaicode.com/reducing-docker-image-sizes-multistage-builds-2025/)

---

## 📋 Plan d'Action Recommandé

### Phase 1: Quick Wins (Cette Semaine)

**1. Migrer impro-manager music vers RClone** (Gain: 4.1GB)

```bash
# Backup
tar czf /opt/backups/impro-music-backup-$(date +%F).tar.gz \
  /opt/impro-manager/music

# Migrate
mv /opt/impro-manager/music /mnt/rd/impro-manager-music
ln -s /mnt/rd/impro-manager-music /opt/impro-manager/music

# Test app still works
curl https://impro-manager.srv759970.hstgr.cloud/health

# Update docker-compose if needed
```

**Risque**: Faible (symlink transparent pour l'app)
**Gain immédiat**: 4.1GB

**2. Optimiser WhisperX avec CPU-only PyTorch** (Gain: 4-5GB)

**Pré-requis**: Vérifier si GPU utilisé
```bash
# Check if GPU used
docker exec whisperx nvidia-smi 2>/dev/null || echo "No GPU"

# Check device in code
docker exec whisperx grep -r "cuda\|gpu" /app/
```

Si pas de GPU:
```bash
cd /opt/whisperx
# Backup Dockerfile
cp Dockerfile Dockerfile.backup

# Apply optimization (voir Dockerfile Option A ci-dessus)
nano Dockerfile

# Rebuild
docker-compose build --no-cache
docker-compose up -d

# Test
curl -u julien:DevAccess2025 https://whisperx.srv759970.hstgr.cloud/health
```

**Risque**: Moyen (nécessite rebuild et test)
**Gain estimé**: 4-5GB

**Total Phase 1**: ~8-9GB récupérés

---

### Phase 2: Optimisations Modérées (Ce Mois)

**3. Audit autres images Python/ML**

Images à vérifier:
- `paperflow_paperflow-worker:latest` (6.65GB)
- `kokoro-fastapi-cpu:latest` (5.61GB)
- `infiniflow/ragflow:v0.21.0-slim` (7.06GB - déjà slim?)

Pour chaque:
```bash
docker history <image> --no-trunc
docker exec <container> pip list | grep torch
```

**4. Standardiser Dockerfiles du projet**

Créer templates:
- `Dockerfile.python-ml.template` (avec multi-stage + CPU PyTorch)
- `Dockerfile.nodejs.template` (avec alpine + multi-stage)
- `Dockerfile.fastapi.template` (slim + optimized)

**5. Nettoyer nextjs-app dans impro-manager** (Gain: 500MB)

```bash
# Vérifier si build files nécessaires
cd /opt/impro-manager/nextjs-app
du -sh node_modules .next

# Si app compilée et déployée ailleurs, supprimer
rm -rf nextjs-app/node_modules
```

---

### Phase 3: Projet Long Terme (Prochain Trimestre)

**6. Implémenter CI/CD pour images optimisées**

- GitHub Actions pour build automatique
- Tests de taille (alerter si image >2GB)
- Scan sécurité (Trivy/Grype)

**7. Migration vers registre privé**

- Registry Docker local ou DockerHub privé
- Images optimisées versionnées
- Pull uniquement images approuvées

**8. Documentation standards**

Créer guide: `docs/reference/docker/image-optimization.md`
- Checklist optimisation
- Templates Dockerfile
- Benchmarks de taille

---

## 📊 Tableau Récapitulatif des Gains

| Action | Complexité | Risque | Gain (GB) | Priorité |
|--------|-----------|--------|-----------|----------|
| Migrer impro music → RClone | Faible | Faible | 4.1 | ✅ HAUTE |
| WhisperX CPU-only PyTorch | Moyenne | Moyen | 4-5 | ✅ HAUTE |
| Optimiser paperflow-worker | Moyenne | Moyen | 2-3 | ⚠️ Moyenne |
| Optimiser kokoro-tts | Moyenne | Moyen | 2-3 | ⚠️ Moyenne |
| Nettoyer nextjs-app build | Faible | Faible | 0.5 | ⚠️ Moyenne |
| Rebuild ragflow (si custom) | Haute | Élevé | 1-2 | 🔴 Faible |
| Rebuild calcom (custom) | Haute | Élevé | 2 | 🔴 Éviter |

**Total récupérable réaliste**: 13-18GB (phases 1+2)

---

## ⚠️ Précautions Critiques

### Avant de Rebuilder une Image

1. **Backup du service**
   ```bash
   docker commit <container> <image>:backup-$(date +%F)
   ```

2. **Test en environnement isolé**
   ```bash
   docker run --rm -p 8888:8002 <new-image> test-command
   ```

3. **Plan de rollback**
   - Garder ancienne image 7 jours
   - Script de rollback prêt
   - Backup configuration

### GPU vs CPU

**Vérifier AVANT d'installer CPU-only**:
```bash
# Check NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# Check container GPU access
docker inspect <container> | grep -i nvidia

# Check code usage
grep -r "\.cuda()\|\.to('cuda')\|device='cuda'" /opt/whisperx/
```

Si GPU utilisé → Garder version GPU!

### Node Modules

**Ne JAMAIS supprimer node_modules si app en cours d'exécution**
- Arrêter container d'abord
- Backup avant suppression
- Vérifier avec `docker exec <container> node -v`

---

## 🛠️ Scripts Utilitaires

### 1. Analyse taille images
```bash
#!/bin/bash
# analyze-docker-images.sh

echo "Top 10 Docker Images by Size"
docker images --format "{{.Repository}}:{{.Tag}}\t{{.Size}}" | sort -k2 -rh | head -10

echo -e "\nImages potentiellement optimisables (>2GB):"
docker images --format "{{.Repository}}:{{.Tag}}\t{{.Size}}" | awk '$2 ~ /GB$/ && $2+0 > 2 {print}'
```

### 2. Check CPU vs GPU PyTorch
```bash
#!/bin/bash
# check-pytorch-gpu.sh

CONTAINER=$1
if [ -z "$CONTAINER" ]; then
  echo "Usage: $0 <container-name>"
  exit 1
fi

echo "Checking PyTorch installation in $CONTAINER..."
docker exec $CONTAINER python3 -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU count: {torch.cuda.device_count()}')
else:
    print('CPU-only installation')
"
```

### 3. Migration impro-manager music
```bash
#!/bin/bash
# migrate-impro-music.sh

set -e

BACKUP_DIR="/opt/backups"
SOURCE="/opt/impro-manager/music"
DEST="/mnt/rd/impro-manager-music"

echo "Creating backup..."
tar czf $BACKUP_DIR/impro-music-backup-$(date +%F).tar.gz $SOURCE

echo "Moving music to RClone mount..."
mv $SOURCE $DEST

echo "Creating symlink..."
ln -s $DEST $SOURCE

echo "Verifying..."
ls -lah /opt/impro-manager/ | grep music

echo "Testing app..."
curl -f https://impro-manager.srv759970.hstgr.cloud/health || echo "App health check failed!"

echo "Done! Gained $(du -sh $DEST | cut -f1) on local disk"
```

---

## 📚 Ressources et Sources

### Documentation Officielle Docker
- [Best Practices | Docker Docs](https://docs.docker.com/build/building/best-practices/)
- [Multi-stage | Docker Docs](https://docs.docker.com/build/building/multi-stage/)

### Multi-Stage Builds
- [LogRocket - Reduce Docker Image Sizes](https://blog.logrocket.com/reduce-docker-image-sizes-using-multi-stage-builds/)
- [Spacelift - Docker Multistage Builds](https://spacelift.io/blog/docker-multistage-builds)
- [iximiuz Labs - Multi-Stage Builds](https://labs.iximiuz.com/tutorials/docker-multi-stage-builds)
- [Nick Janetakis - Shrink Images by 50%](https://nickjanetakis.com/blog/shrink-your-docker-images-by-50-percent-with-multi-stage-builds)

### Python/ML Optimization
- [Stack Overflow - Reduce Python Docker size](https://stackoverflow.com/questions/78105348/how-to-reduce-python-docker-image-size)
- [Collabnix - 90% Size Reduction Journey](https://collabnix.com/how-i-reduced-a-docker-image-size-by-90-a-step-by-step-journey/)
- [Wayfair Case Study - 50% Reduction](https://www.aboutwayfair.com/case-study-how-we-decreased-the-size-of-our-python-docker-images-by-over-50)
- [Medium - Minimizing Python Docker Images](https://rodneyosodo.medium.com/minimizing-python-docker-images-cf99f4468d39)
- [Divio - Optimizing Docker Images Python](https://www.divio.com/blog/optimizing-docker-images-python/)

### 2025 Best Practices
- [Medium - Docker Best Practices 2025](https://saraswathilakshman.medium.com/optimise-your-docker-images-for-speed-and-security-best-practices-for-2025-e888f6dc131f)
- [Markaicode - Multi-Stage Build Tricks 2025](https://markaicode.com/reducing-docker-image-sizes-multistage-builds-2025/)
- [Better Stack - Docker Build Best Practices](https://betterstack.com/community/guides/scaling-docker/docker-build-best-practices/)

---

## ✅ Conclusion

### Résumé Exécutif

**Problème**: 48.31GB d'images Docker, dont 3 images consomment 18.6GB

**Solutions identifiées**:
1. **impro-manager**: 4.1GB de musiques MP3 à migrer vers RClone (FACILE)
2. **WhisperX**: 8.77GB à réduire à 3-4GB avec CPU PyTorch (MOYEN)
3. **Cal.com**: 4.82GB, accepter ou rebuilder custom (COMPLEXE)

**Gain réaliste**: 8-13GB (Phases 1+2)

**Recommandation prioritaire**:
1. Migrer impro-manager music (gain immédiat 4.1GB, risque faible)
2. Optimiser WhisperX si pas de GPU (gain 4-5GB, risque moyen)
3. Appliquer best practices 2025 aux futures images

### Next Steps

1. **Cette semaine**: Exécuter Phase 1 (impro-manager + WhisperX)
2. **Ce mois**: Auditer autres images ML (paperflow, kokoro)
3. **Long terme**: Standards d'optimisation + CI/CD

**Rapport généré**: 2025-12-04
**Maintenu par**: Infrastructure team
