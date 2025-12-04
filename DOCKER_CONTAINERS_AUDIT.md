# Audit Complet des Containers Docker

**Date**: 2025-12-04
**Serveur**: srv759970.hstgr.cloud
**Total Images**: 51 images (48.31GB)

---

## 📊 Vue d'Ensemble

### Top 10 Images par Taille

| Rang | Image | Taille | Type | Optimisation Possible | Priorité |
|------|-------|--------|------|----------------------|----------|
| 1 | whisperx_whisperx | 8.77GB | ML (Custom) | ✅ OUI - 4-5GB | 🔴 HAUTE |
| 2 | infiniflow/ragflow | 7.06GB | ML (Tierce) | ⚠️ LIMITÉE | 🟡 MOYENNE |
| 3 | paperflow_paperflow-worker | 6.65GB | ML (Custom) | ✅ OUI - 3-4GB | 🔴 HAUTE |
| 4 | ghcr.io/remsky/kokoro-fastapi-cpu | 5.61GB | ML (Tierce) | ⚠️ LIMITÉE | 🟡 MOYENNE |
| 5 | calcom/cal.com | 4.82GB | App (Tierce) | ❌ NON | 🟢 FAIBLE |
| 6 | jellyfin/jellyfin | 1.55GB | Media (Tierce) | ❌ NON | 🟢 FAIBLE |
| 7 | fallenbagel/jellyseerr | 1.44GB | App (Tierce) | ❌ NON | 🟢 FAIBLE |
| 8 | elasticsearch | 1.41GB | DB (Tierce) | ❌ NON | 🟢 FAIBLE |
| 9 | mongo:7 | 834MB | DB (Officielle) | ❌ NON | 🟢 FAIBLE |
| 10 | mysql:8.0 | 780MB | DB (Officielle) | ❌ NON | 🟢 FAIBLE |

**Total Top 10**: 39.24GB (81% de l'espace images)

### Images par Catégorie

| Catégorie | Nombre | Taille Totale | Optimisables |
|-----------|--------|---------------|--------------|
| ML/AI (Custom) | 3 | 15.42GB | 2 images (~9GB gain) |
| ML/AI (Tierce) | 2 | 12.67GB | Limité (~1-2GB gain) |
| Databases | 6 | 3.13GB | Non |
| Applications | 8 | 9.15GB | Non (tierces) |
| Media/Streaming | 2 | 2.99GB | Non |
| Infrastructure | 30 | 5.95GB | Déjà optimisées |

---

## 🔍 Audit Détaillé - Images Optimisables

### 1. paperflow_paperflow-worker (6.65 GB) - PRIORITÉ HAUTE

#### Analyse Technique

**Dockerfile actuel**:
```dockerfile
FROM python:3.11-slim
# COPY venv entire = 6.5GB!
COPY --chown=paperflow:paperflow dir:xxx in /opt/venv
```

**Layers principaux**:
- Python venv (COPY): **6.5GB** ← ÉNORME!
- Python build dependencies: 42MB
- System packages (libmagic, curl): 24MB
- Application code: 174kB

**Dépendances installées**:
```
torch                    2.6.0     ← GPU version
torchvision              0.21.0
pandas                   2.3.3
numpy                    2.2.3
celery                   5.5.0
```

**requirements.txt analyse**:
```python
# Comments in requirements suggest CPU version intended:
# "Install torch CPU version manually with:
#  pip install torch==2.6.0+cpu --index-url https://download.pytorch.org/whl/cpu"

# But actual installation is GPU version (2.6GB+)
torch==2.6.0  # ← No CPU index specified = GPU install
sentence-transformers==5.1.2
```

#### Problèmes Identifiés

1. **PyTorch GPU installé au lieu de CPU**
   - GPU version: ~2.6GB
   - CPU version: ~600MB
   - **Gain potentiel**: 2GB

2. **Venv entier copié en un bloc** (6.5GB)
   - Pas de multi-stage build
   - Tous les fichiers de développement inclus
   - Build dependencies non nettoyées

3. **Base image peut être optimisée**
   - Utilise `python:3.11-slim` (correct)
   - Mais installe gcc/g++ qui restent dans l'image

#### Recommandations d'Optimisation

**Option A: Multi-stage + CPU PyTorch** (Gain: ~3-4GB)

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libmagic1 && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies with CPU PyTorch
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 curl && \
    rm -rf /var/lib/apt/lists/*

# Create user
RUN groupadd -r paperflow && useradd -r -g paperflow paperflow && \
    mkdir -p /app /dropbox/paperflow/data /opt/paperflow/data /cache/huggingface && \
    chown -R paperflow:paperflow /app /dropbox /opt/paperflow /cache

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application
COPY --chown=paperflow:paperflow app/ ./

USER paperflow
ENV HF_HOME=/cache/huggingface
ENV TRANSFORMERS_CACHE=/cache/huggingface

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Taille estimée**: 2.5-3GB (vs 6.65GB actuel)
**Gain**: ~3-4GB (55-60%)

**Option B: Si GPU nécessaire, optimiser quand même** (Gain: ~1-2GB)

Si Celery tasks utilisent vraiment GPU:
- Garder PyTorch GPU
- Mais utiliser multi-stage pour nettoyer build deps
- Supprimer test/docs des packages

**Taille estimée**: 4.5-5GB
**Gain**: ~1.5-2GB (25-30%)

#### Actions Recommandées

1. **Vérifier usage GPU**:
   ```bash
   docker exec paperflow-worker python -c "
   import torch
   print(f'CUDA available: {torch.cuda.is_available()}')
   print(f'Using device: {torch.device(\"cuda\" if torch.cuda.is_available() else \"cpu\")}')
   "
   ```

2. **Si CPU only**: Appliquer Option A

3. **Tester en dev**:
   ```bash
   cd /opt/paperflow/backend
   docker build -t paperflow-worker:optimized -f Dockerfile.optimized .
   docker run --rm paperflow-worker:optimized python -c "import torch; print(torch.__version__)"
   ```

4. **Déployer si tests OK**

---

### 2. kokoro-fastapi-cpu (5.61 GB) - Image Tierce

#### Analyse Technique

**Image**: `ghcr.io/remsky/kokoro-fastapi-cpu:latest` (5.61GB)
**Source**: GitHub Container Registry (tierce)

**Layers principaux**:
- Python venv (uv sync): **2.89GB** ← Dependencies
- Rust toolchain: **1.23GB** ← Build tools qui restent!
- System packages (espeak, ffmpeg, git): 952MB
- Model download: 328MB
- Application: 35.4MB

**Problèmes Identifiés**:

1. **Rust toolchain dans image finale** (1.23GB)
   - Installé avec `curl https://sh.rustup.rs`
   - Sert uniquement pour build dependencies
   - Devrait être dans build stage uniquement

2. **Git installé au runtime** (pas nécessaire)
   - Utilisé pour clone deps au build
   - Peut être retiré de l'image finale

3. **uv venv copié entièrement** (2.89GB)
   - Peut contenir dev dependencies
   - Pas de cleanup après installation

#### Recommandations

**Option A: Contacter maintainer** (Recommandé)

Image tierce GitHub, pas de contrôle direct:
- Créer issue sur repo GitHub
- Suggérer multi-stage build
- Proposer PR si repo accepte contributions

**Gain potentiel**: ~2-3GB (50% de réduction possible)

**Option B: Fork et optimiser** (Si critique)

Si vraiment besoin:
```dockerfile
# Build stage
FROM python:3.10-slim as builder
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
RUN uv sync --extra cpu

# Runtime stage
FROM python:3.10-slim
RUN apt-get update && apt-get install -y espeak-ng ffmpeg
COPY --from=builder /app/.venv /app/.venv
# ... rest without rust/git
```

**Effort**: Élevé (maintenance du fork)
**Recommandation**: Option A (issue GitHub) ou accepter la taille

---

### 3. ragflow (7.06 GB) - Déjà "slim"

#### Analyse Technique

**Image**: `infiniflow/ragflow:v0.21.0-slim` (7.06GB)
**Note**: Déjà version "slim" officielle

**Layers principaux**:
- Application dist: 153MB (web frontend)
- RAG libraries: ~6.9GB (embeddings, ML models)

**Status**: ✅ Déjà optimisée par l'éditeur

#### Recommandations

**Aucune optimisation recommandée**:
- Déjà version "slim" officielle
- Image tierce complexe (RAG stack complet)
- Maintenance du fork trop coûteuse

**Alternative**: Si espace critique, considérer:
- Désactiver modules non utilisés via config
- Utiliser version "lite" si disponible dans futures releases
- Migrer vers solution plus légère (ex: LangChain custom)

---

## 🎯 Images Tierces - Accepter la Taille

### Cal.com (4.82 GB)

**Status**: ❌ Ne PAS optimiser
**Raisons**:
- Image officielle complexe (monorepo Node.js)
- Mises à jour fréquentes
- Maintenance fork = overhead élevé
- Gain potentiel limité (~2GB max)

### Jellyfin (1.55 GB)

**Status**: ❌ Ne PAS optimiser
**Breakdown**:
- Server binaries: 177MB
- Web interface: 57MB
- FFmpeg transcoding: ~1.2GB (nécessaire)

**Raisons**: Media server nécessite codecs/transcoders lourds

### Jellyseerr (1.44 GB)

**Status**: ❌ Ne PAS optimiser
**Raisons**: App tierce complexe, gain marginal

### Elasticsearch (1.41 GB)

**Status**: ❌ Ne PAS optimiser
**Breakdown**:
- Elasticsearch runtime: 1.32GB (Java app)
- Base Ubuntu: 72.8MB

**Raisons**:
- Image officielle Elastic
- Java app naturellement volumineuse
- Version déjà optimisée par Elastic

---

## 📋 Images Déjà Optimales

Ces images sont déjà bien optimisées et ne nécessitent pas d'action:

| Image | Taille | Raison |
|-------|--------|--------|
| downto40_streamlit | 778MB | Streamlit + deps ML (raisonnable) |
| grafana/grafana | 733MB | Dashboard complexe (optimal) |
| mysql:8.0 | 780MB | DB officielle (standard) |
| mongo:7 | 834MB | DB officielle (standard) |
| postgres:17-alpine | 278MB | Alpine = déjà optimisé |
| redis:7-alpine | 41MB | Alpine = excellent |
| nginx:alpine | 52.8MB | Alpine = excellent |

---

## 🚨 Images Dangling à Supprimer

**3 images <none>:<none>** détectées:

| Image ID | Taille | Action |
|----------|--------|--------|
| a9895585639c | 246MB | Supprimer (dangling mkdocs build) |
| c9b5e1cce49f | 225MB | Supprimer (dangling langchain build) |
| 2acb7da3552b | 278MB | Supprimer (dangling postgres) |

**Total récupérable**: ~749MB

**Commande**:
```bash
docker image prune -f
```

---

## 📊 Résumé des Gains Possibles

### Optimisations Réalistes

| Action | Complexité | Risque | Gain | ROI |
|--------|-----------|--------|------|-----|
| Paperflow CPU PyTorch | Moyenne | Moyen | 3-4GB | ⭐⭐⭐ Excellent |
| Paperflow multi-stage | Moyenne | Moyen | 1-2GB | ⭐⭐⭐ Bon |
| WhisperX CPU PyTorch | Moyenne | Moyen | 4-5GB | ⭐⭐⭐ Excellent |
| Kokoro issue GitHub | Faible | Nul | 0GB court terme | ⭐⭐ Moyen (futur) |
| Kokoro fork custom | Élevée | Élevé | 2-3GB | ⭐ Faible (maintenance) |
| Prune dangling images | Faible | Nul | 0.7GB | ⭐⭐⭐ Excellent |
| **TOTAL RÉALISTE** | | | **8-12GB** | |

### Optimisations NON Recommandées

| Image | Raison d'éviter | Gain potentiel |
|-------|----------------|----------------|
| Cal.com | Maintenance complexe | ~2GB |
| Jellyfin | Codecs nécessaires | ~0.3GB |
| RAGFlow | Déjà slim | ~0.5GB |
| Elasticsearch | Image officielle optimale | ~0.2GB |

---

## 🎯 Plan d'Action Recommandé

### Phase 1: Quick Wins (Cette Semaine)

**1. Prune dangling images** (Gain: 0.7GB)
```bash
ssh srv759970
docker image prune -f
docker system df
```
**Risque**: Aucun
**Temps**: 2 minutes

**2. Optimiser paperflow-worker** (Gain: 3-4GB)

Étapes:
```bash
# Vérifier GPU usage
ssh srv759970
docker exec paperflow-worker python -c "import torch; print(torch.cuda.is_available())"

# Si False (CPU only):
cd /opt/paperflow/backend
cp Dockerfile Dockerfile.backup
# Créer Dockerfile.optimized (voir template ci-dessus)
nano Dockerfile.optimized

# Build test
docker build -t paperflow-worker:optimized -f Dockerfile.optimized .

# Test fonctionnel
docker run --rm -p 8888:8000 paperflow-worker:optimized

# Si OK, déployer
docker-compose stop paperflow-worker
docker tag paperflow_paperflow-worker:latest paperflow_paperflow-worker:backup
docker tag paperflow-worker:optimized paperflow_paperflow-worker:latest
docker-compose up -d paperflow-worker

# Vérifier logs
docker logs -f paperflow-worker
```

**Risque**: Moyen (rollback possible)
**Temps**: 1-2 heures

**3. Optimiser WhisperX** (Gain: 4-5GB)

Voir DOCKER_OPTIMIZATION_ANALYSIS.md pour détails complets.

**Total Phase 1**: 8-10GB récupérés

---

### Phase 2: Actions Long Terme (Ce Mois)

**4. Issue GitHub pour Kokoro**

Créer issue sur repo GitHub:
```markdown
Title: Multi-stage build to reduce image size by 50%

Current image size: 5.61GB
- Rust toolchain: 1.23GB (only needed at build time)
- Git: included but not needed at runtime
- Potential size: ~2.5-3GB with multi-stage build

Would you accept a PR implementing multi-stage build?
```

**5. Veille sur RAGFlow updates**

Surveiller releases pour version plus légère:
- Subscribe to GitHub releases
- Check changelog pour "lite" ou "slim" versions

**6. Documentation standards**

Créer `docs/reference/docker/image-optimization-standards.md`:
- Checklist pour nouvelles images
- Templates Dockerfile optimisés
- Processus de review

---

## 🔧 Scripts Utilitaires

### 1. Audit automatique des images

```bash
#!/bin/bash
# audit-docker-images.sh

echo "=== Docker Images Audit ==="
echo ""
echo "Images >1GB:"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | \
  awk 'NR==1 || /GB$/ && $3+0 >= 1'

echo ""
echo "Dangling images:"
docker images -f "dangling=true" --format "table {{.ID}}\t{{.Size}}"

echo ""
echo "Total space:"
docker system df

echo ""
echo "Reclaimable space:"
docker system df -v | grep "Reclaimable"
```

### 2. Check PyTorch installation type

```bash
#!/bin/bash
# check-pytorch-type.sh

CONTAINER=$1
if [ -z "$CONTAINER" ]; then
  echo "Usage: $0 <container-name>"
  exit 1
fi

echo "Checking PyTorch in $CONTAINER..."
docker exec $CONTAINER python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'CUDA version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}')

# Check if CPU-only
import sys
cuda_available = torch.cuda.is_available()
if cuda_available:
    print('✗ GPU version installed (large)')
    sys.exit(1)
else:
    print('✓ CPU-only version (optimized)')
    sys.exit(0)
"

if [ $? -eq 0 ]; then
  echo "✓ Already optimized"
else
  echo "⚠ Can be optimized with CPU-only PyTorch"
fi
```

### 3. Backup avant rebuild

```bash
#!/bin/bash
# backup-image.sh

IMAGE=$1
if [ -z "$IMAGE" ]; then
  echo "Usage: $0 <image-name>"
  exit 1
fi

BACKUP_TAG="$IMAGE:backup-$(date +%Y%m%d-%H%M%S)"

echo "Creating backup: $BACKUP_TAG"
docker tag $IMAGE $BACKUP_TAG

echo "Backup created. To restore:"
echo "  docker tag $BACKUP_TAG $IMAGE"
```

---

## 📈 Métriques de Succès

### Objectifs

**Court terme** (1 semaine):
- [ ] Réduire usage images de 48GB à 40GB (-8GB, -17%)
- [ ] Optimiser 2 images custom (paperflow + whisperx)
- [ ] Prune dangling images

**Moyen terme** (1 mois):
- [ ] Standards d'optimisation documentés
- [ ] Process de review pour nouvelles images
- [ ] Monitoring taille images (alertes >5GB)

**Long terme** (3 mois):
- [ ] Toutes images custom optimisées
- [ ] CI/CD avec checks de taille
- [ ] Templates Dockerfile réutilisables

### KPIs

- **Taille moyenne image custom**: Cible <2GB
- **Ratio optimisation**: 80% images custom optimisées
- **Temps de build**: Ne pas dépasser +20% avec multi-stage
- **Dangling images**: 0 (cleanup automatique hebdo)

---

## ✅ Conclusion

### Synthèse

**51 images analysées** (48.31GB total):
- ✅ **2 images optimisables** avec fort ROI (paperflow + whisperx)
- ⚠️ **1 image tierce** avec optimisation possible (kokoro)
- ❌ **7 images tierces** à accepter telles quelles
- 🗑️ **3 images dangling** à supprimer

**Gain réaliste total**: 8-12GB (17-25% de réduction)

### Priorités

1. **HAUTE**: Paperflow + WhisperX (8-9GB de gain)
2. **MOYENNE**: Dangling cleanup (0.7GB)
3. **FAIBLE**: Kokoro (issue GitHub, gain futur potentiel)

### Recommandation Finale

**Exécuter Phase 1 cette semaine**:
1. Prune dangling (facile, sans risque)
2. Optimiser paperflow (bon ROI)
3. Optimiser whisperx (voir DOCKER_OPTIMIZATION_ANALYSIS.md)

**Résultat attendu**: Récupérer 8-10GB d'espace images Docker

---

**Rapport généré**: 2025-12-04
**Prochaine révision**: Après Phase 1 (semaine prochaine)
**Maintenu par**: Infrastructure team
