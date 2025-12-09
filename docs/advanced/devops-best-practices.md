# 🔄 Bonnes Pratiques Dev/Prod - Gestion des Versions et Environnements

> **Guide complet** pour gérer proprement les environnements de développement, staging et production, et toujours savoir quelle version tourne où.

---

## 📌 Table des matières

1. [Le Problème](#-le-problème)
2. [Solutions Progressives](#-solutions-progressives)
3. [Architecture Recommandée](#-architecture-recommandée)
4. [Exemples Concrets](#-exemples-concrets)
5. [Scripts Automatisés](#-scripts-automatisés)
6. [Checklist de Déploiement](#-checklist-de-déploiement)

---

## ❓ Le Problème

Lorsque vous développez une application et la déployez sur un serveur, vous vous posez rapidement ces questions :

- **Quelle version tourne en production ?**
- **Est-ce que mon local est synchronisé avec la prod ?**
- **Quand ai-je fait ce déploiement ?**
- **Quelles fonctionnalités sont en dev mais pas encore en prod ?**
- **Comment revenir à une version stable en cas de problème ?**

Sans système de gestion des versions, c'est le chaos : bugs mystérieux, déploiements hasardeux, impossibilité de rollback...

---

## 🎯 Solutions Progressives

### Niveau 1 : Git Commits (Minimum vital)

**Ce que c'est** : Chaque modification du code est enregistrée avec un identifiant unique (hash).

**Exemple** :
```bash
git commit -m "feat: Dashboard avec CSS Elyse Energy"
# Crée un commit avec hash: 764c119
```

**Savoir quelle version est en prod** :
```bash
# Local
git log -1 --oneline
# 764c119 feat: Dashboard avec CSS Elyse Energy

# Production
ssh root@69.62.108.82 "cd /opt/support-dashboard && git log -1 --oneline"
# 764c119 feat: Dashboard avec CSS Elyse Energy
```

**✅ Avantages** : Simple, gratuit, déjà en place
**❌ Inconvénients** : Hash illisible, pas de notion de version "stable"

---

### Niveau 2 : Git Tags (Recommandé)

**Ce que c'est** : Des "étiquettes" lisibles pour marquer les versions importantes.

**Exemple** :
```bash
# Après un déploiement réussi
git tag -a v1.0.0 -m "Version initiale du dashboard"
git push origin v1.0.0

# Lister tous les tags
git tag
# v1.0.0
# v1.0.1
# v1.1.0

# Voir le dernier tag
git describe --tags
# v1.1.0
```

**Convention de nommage** (Semantic Versioning) :
```
vMAJEUR.MINEUR.PATCH

v1.0.0 → v1.0.1  (patch : bugfix)
v1.0.1 → v1.1.0  (mineur : nouvelle fonctionnalité)
v1.1.0 → v2.0.0  (majeur : changement incompatible)
```

**Déployer une version spécifique** :
```bash
# Checkout sur un tag
git checkout v1.0.0

# Déployer cette version précise
scripts/deploy_prod.bat
```

**✅ Avantages** : Lisible, permet de revenir facilement à une version
**❌ Inconvénients** : Nécessite de penser à créer les tags

---

### Niveau 3 : Fichier VERSION (Simple et efficace)

**Ce que c'est** : Un fichier texte contenant la version courante.

**Créer le fichier** :
```bash
# À la racine du projet
echo "1.0.0" > VERSION.txt
git add VERSION.txt
git commit -m "chore: Add VERSION file"
```

**L'afficher dans l'application** :

```python
# dashboard/app.py (Streamlit)
with open('VERSION.txt') as f:
    VERSION = f.read().strip()

st.caption(f"Dashboard v{VERSION} - Dernière mise à jour: {datetime.now()}")
```

```python
# app.py (Flask)
with open('VERSION.txt') as f:
    VERSION = f.read().strip()

@app.route('/version')
def version():
    return {'version': VERSION, 'commit': get_git_hash()}
```

**Comparer local vs prod** :
```bash
# Local
cat VERSION.txt
# 1.0.0

# Production
ssh root@69.62.108.82 "docker exec support-dashboard cat /app/VERSION.txt"
# 1.0.0
```

**Workflow de mise à jour** :
```bash
# 1. Modifier le code
# 2. Incrémenter la version
echo "1.0.1" > VERSION.txt

# 3. Commit
git add .
git commit -m "fix: Correction timezone"

# 4. Tag
git tag -a v1.0.1 -m "Hotfix timezone"

# 5. Déployer
scripts/deploy_prod.bat
```

**✅ Avantages** : Visible dans l'app, facile à automatiser
**❌ Inconvénients** : Faut penser à le mettre à jour

---

### Niveau 4 : Branches Git (Professionnel)

**Structure recommandée** :
```
master (ou main)     → Production (toujours stable)
├── develop          → Développement (features en cours)
├── staging          → Pré-production (tests avant deploy)
├── feature/xyz      → Nouvelles fonctionnalités
└── hotfix/bug-123   → Correctifs urgents
```

**Workflow Git Flow** :

```bash
# 1. Développer une nouvelle feature
git checkout -b feature/nouveaux-kpis develop

# ... coder ...

git commit -m "feat: Ajout KPIs temps réel"

# 2. Merger dans develop
git checkout develop
git merge feature/nouveaux-kpis

# 3. Tester en local
streamlit run dashboard/app.py

# 4. Créer une release candidate
git checkout -b release/1.1.0 develop
echo "1.1.0" > VERSION.txt
git commit -m "chore: Bump version to 1.1.0"

# 5. Merger dans master
git checkout master
git merge release/1.1.0
git tag -a v1.1.0 -m "Release 1.1.0: Nouveaux KPIs"

# 6. Déployer en prod
scripts/deploy_prod.bat

# 7. Merger master dans develop
git checkout develop
git merge master
```

**Hotfix urgent en prod** :
```bash
# 1. Partir de master
git checkout -b hotfix/timezone-bug master

# 2. Corriger
# ... fix ...
echo "1.0.1" > VERSION.txt
git commit -m "fix: Correction timezone"

# 3. Merger dans master ET develop
git checkout master
git merge hotfix/timezone-bug
git tag -a v1.0.1 -m "Hotfix: timezone"

git checkout develop
git merge hotfix/timezone-bug

# 4. Déployer
scripts/deploy_prod.bat
```

**✅ Avantages** : Isolation des features, prod toujours stable
**❌ Inconvénients** : Plus complexe, nécessite discipline

---

### Niveau 5 : Variables d'Environnement (Distinguer Dev/Prod)

**Ce que c'est** : Configurer l'application différemment selon l'environnement.

**Dans le code** :
```python
# dashboard/app.py
import os

ENV = os.getenv('ENVIRONMENT', 'development')
VERSION = open('VERSION.txt').read().strip()

# Configuration selon environnement
if ENV == 'production':
    st.set_page_config(
        page_title="[PROD] Dashboard Support IT",
        page_icon="🚀"
    )
    DEBUG = False
    DATABASE_PATH = '/app/data/tickets.db'
else:
    st.set_page_config(
        page_title="[DEV] Dashboard Support IT",
        page_icon="🛠️"
    )
    DEBUG = True
    DATABASE_PATH = 'data/tickets.db'

# Afficher dans le footer
st.caption(f"Env: {ENV} | Version: {VERSION}")
```

**Dans docker-compose.yml** :
```yaml
version: '3.8'

services:
  dashboard:
    build: .
    container_name: support-dashboard
    ports:
      - "8501:8501"
    volumes:
      - ./data/tickets.db:/app/data/tickets.db
    restart: unless-stopped
    environment:
      - ENVIRONMENT=production
      - VERSION=1.0.0
      - DEPLOYED_AT=2025-10-10T08:45:00Z
      - TZ=Europe/Paris
```

**Fichier .env (local)** :
```bash
# .env
ENVIRONMENT=development
DEBUG=true
DATABASE_PATH=data/tickets.db
```

**Fichier .env.prod (production)** :
```bash
# .env.prod
ENVIRONMENT=production
DEBUG=false
DATABASE_PATH=/app/data/tickets.db
```

**✅ Avantages** : Configuration centralisée, facile à changer
**❌ Inconvénients** : Attention à ne pas committer les secrets

---

### Niveau 6 : Page de Status (Monitoring)

**Créer une page dédiée** :

```python
# dashboard/pages/status.py
import streamlit as st
import subprocess
import os
from datetime import datetime

st.title("📊 System Status & Version Info")

# Version
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📦 Version")

    # Lire VERSION.txt
    with open('../VERSION.txt') as f:
        version = f.read().strip()
    st.metric("Version", version)

    # Git commit
    try:
        git_hash = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD']
        ).decode().strip()
        st.metric("Git Commit", git_hash)
    except:
        st.metric("Git Commit", "N/A")

    # Git branch
    try:
        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
        ).decode().strip()
        st.metric("Branch", branch)
    except:
        st.metric("Branch", "N/A")

with col2:
    st.subheader("🌍 Environment")

    env = os.getenv('ENVIRONMENT', 'development')
    st.metric("Environment", env)

    deployed_at = os.getenv('DEPLOYED_AT', 'N/A')
    st.metric("Deployed At", deployed_at)

    tz = os.getenv('TZ', 'UTC')
    st.metric("Timezone", tz)

with col3:
    st.subheader("🐳 Docker")

    # Docker image ID
    try:
        image_id = subprocess.check_output(
            ['docker', 'inspect', '--format={{.Image}}', 'support-dashboard']
        ).decode().strip()[:12]
        st.metric("Image ID", image_id)
    except:
        st.metric("Image ID", "N/A")

    # Container uptime
    try:
        uptime = subprocess.check_output(
            ['docker', 'inspect', '--format={{.State.StartedAt}}', 'support-dashboard']
        ).decode().strip()
        st.metric("Started At", uptime[:19])
    except:
        st.metric("Started At", "N/A")

# Changelog
st.markdown("---")
st.subheader("📝 Recent Changes")

try:
    changelog = subprocess.check_output(
        ['git', 'log', '--pretty=format:%h - %s (%cr)', '-10']
    ).decode()
    st.code(changelog, language='text')
except:
    st.info("Git log not available")
```

**Accès** :
- Local: `http://localhost:8501/status`
- Prod: `http://69.62.108.82:8501/status`

---

## 🏗️ Architecture Recommandée

### Structure de Projet Complète

```
mon-projet/
├── .git/                       # Git repository
├── .gitignore                  # Fichiers à ignorer
├── VERSION.txt                 # Version actuelle
├── CHANGELOG.md                # Historique des versions
├── README.md                   # Documentation
├── requirements.txt            # Dépendances Python
├── Dockerfile                  # Build Docker
├── docker-compose.yml          # Orchestration
├── .env.example                # Template variables d'env
│
├── dashboard/                  # Code source
│   ├── app.py
│   └── pages/
│       └── status.py           # Page de status
│
├── data/                       # Données (gitignore)
│   └── tickets.db
│
├── scripts/                    # Scripts d'automatisation
│   ├── deploy_prod.bat         # Déploiement production
│   ├── deploy_staging.bat      # Déploiement staging
│   ├── compare_versions.bat    # Compare local vs prod
│   ├── bump_version.py         # Incrémenter version
│   └── rollback.bat            # Revenir à version précédente
│
└── docs/                       # Documentation
    ├── DEPLOY.md
    └── CHANGELOG.md
```

---

## 🎓 Exemples Concrets

### Exemple 1 : Dashboard Support IT (Streamlit)

**Contexte** : Application Streamlit d'analyse de tickets support, déployée sur VPS Hostinger.

**Structure actuelle** :
```
2025.10 Analyse tickets support/
├── VERSION.txt                     # ⚠️ À créer
├── dashboard/
│   └── app.py                      # Avec CSS Elyse Energy
├── data/
│   └── tickets.db                  # BDD SQLite
├── scripts/
│   ├── deploy_prod.bat             # ✅ Existe
│   ├── manage_dashboard.bat        # ✅ Existe
│   ├── sync_db_to_prod.bat         # ✅ Existe
│   └── compare_versions.bat        # ⚠️ À créer
├── Dockerfile                      # ✅ Existe
└── docker-compose.yml              # ✅ Existe
```

**Workflow de mise à jour** :

```bash
# 1. Développement local
cd "C:\Users\JulienFernandez\OneDrive\Coding\_Projets de code\2025.10 Analyse tickets support"

# Modifier le code...
# Tester : streamlit run dashboard/app.py

# 2. Vérifier les différences avec prod
scripts\compare_versions.bat

# 3. Incrémenter la version
python scripts/bump_version.py --patch  # 1.0.0 → 1.0.1

# 4. Commit et tag
git add .
git commit -m "fix: Correction filtres temporels"
git tag -a v1.0.1 -m "Hotfix: filtres temporels"

# 5. Déployer
scripts\deploy_prod.bat

# 6. Vérifier
scripts\compare_versions.bat
# ✓ Local et Prod sont synchronisés (v1.0.1)
```

**Exemple de VERSION.txt** :
```
1.0.1
```

**Affichage dans le dashboard** :
```python
# dashboard/app.py (ajout)
with open('VERSION.txt') as f:
    VERSION = f.read().strip()

ENV = os.getenv('ENVIRONMENT', 'development')

# Dans le footer
st.markdown("---")
st.caption(f"Dashboard v{VERSION} | Env: {ENV} | Commit: {get_git_hash()[:7]} | Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
```

---

### Exemple 2 : API FastAPI

**Contexte** : API REST pour gérer des budgets.

**Structure** :
```
api-budgets/
├── VERSION.txt                 # 1.2.0
├── app/
│   ├── main.py
│   ├── routers/
│   └── models/
├── scripts/
│   ├── deploy_prod.sh
│   └── compare_versions.sh
├── Dockerfile
└── docker-compose.yml
```

**Endpoint de version** :
```python
# app/main.py
from fastapi import FastAPI
import os
import subprocess

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API Budgets"}

@app.get("/health")
def health_check():
    """Endpoint de santé pour monitoring."""
    with open('VERSION.txt') as f:
        version = f.read().strip()

    try:
        git_hash = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD']
        ).decode().strip()
    except:
        git_hash = 'N/A'

    return {
        "status": "ok",
        "version": version,
        "environment": os.getenv('ENVIRONMENT', 'development'),
        "commit": git_hash
    }
```

**Test** :
```bash
# Local
curl http://localhost:8000/health
# {"status":"ok","version":"1.2.0","environment":"development","commit":"a3f2b1c"}

# Production
curl http://69.62.108.82:8502/health
# {"status":"ok","version":"1.2.0","environment":"production","commit":"a3f2b1c"}
```

---

### Exemple 3 : Application Multi-Environnements

**Contexte** : Application avec dev, staging, et prod.

**Structure de branches** :
```
master       → Production (v1.2.0)
├── staging  → Pre-prod (v1.3.0-rc1)
└── develop  → Dev (v1.3.0-alpha)
```

**docker-compose.yml par environnement** :

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
    volumes:
      - .:/app  # Hot reload

# docker-compose.staging.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8502:8501"
    environment:
      - ENVIRONMENT=staging
      - DEBUG=true
    restart: unless-stopped

# docker-compose.prod.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**Scripts de déploiement** :

```bash
# scripts/deploy_staging.bat
docker-compose -f docker-compose.staging.yml up -d

# scripts/deploy_prod.bat
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🤖 Scripts Automatisés

### Script 1 : `compare_versions.bat`

**But** : Comparer les versions local vs production.

```batch
@echo off
REM ========================================
REM Compare Local vs Production
REM ========================================

setlocal

set VPS_HOST=root@69.62.108.82
set VPS_PATH=/opt/support-dashboard
set APP_NAME=support-dashboard

echo.
echo ========================================
echo   Comparaison Local vs Production
echo ========================================
echo.

REM Version locale
echo [LOCAL]
echo Version:
type VERSION.txt 2>nul || echo "Pas de VERSION.txt"
echo.
echo Dernier commit:
git log -1 --oneline 2>nul || echo "Pas de Git"
echo.
echo Branch:
git rev-parse --abbrev-ref HEAD 2>nul || echo "Pas de Git"
echo.

REM Version production
echo [PRODUCTION]
echo Version:
ssh %VPS_HOST% "docker exec %APP_NAME% cat /app/VERSION.txt 2>/dev/null || echo 'Pas de VERSION.txt'"
echo.
echo Dernier commit:
ssh %VPS_HOST% "cd %VPS_PATH% && git log -1 --oneline 2>/dev/null || echo 'Pas de Git'"
echo.

REM Différences
echo [DIFFERENCE]
git log --oneline HEAD..origin/master 2>nul
if %errorlevel% equ 0 (
    echo.
    echo ✓ Local et Prod sont synchronises
) else (
    echo.
    echo ⚠ Vous avez des commits non deployes
    git log --oneline origin/master..HEAD 2>nul
)
echo.

pause
exit /b 0
```

**Utilisation** :
```bash
scripts\compare_versions.bat
```

**Output** :
```
========================================
  Comparaison Local vs Production
========================================

[LOCAL]
Version:
1.0.1

Dernier commit:
764c119 feat: Dashboard avec CSS Elyse Energy

Branch:
master

[PRODUCTION]
Version:
1.0.0

Dernier commit:
9054631 feat: Architecture complète

[DIFFERENCE]
⚠ Vous avez des commits non deployes
764c119 feat: Dashboard avec CSS Elyse Energy
```

---

### Script 2 : `bump_version.py`

**But** : Incrémenter automatiquement la version.

```python
#!/usr/bin/env python3
"""
Script pour incrémenter la version (Semantic Versioning).

Usage:
    python bump_version.py --major   # 1.0.0 → 2.0.0
    python bump_version.py --minor   # 1.0.0 → 1.1.0
    python bump_version.py --patch   # 1.0.0 → 1.0.1
"""

import argparse
import re
from pathlib import Path

def read_version():
    """Lit la version actuelle depuis VERSION.txt"""
    version_file = Path('VERSION.txt')
    if not version_file.exists():
        return '0.0.0'
    return version_file.read_text().strip()

def write_version(version):
    """Écrit la nouvelle version dans VERSION.txt"""
    Path('VERSION.txt').write_text(version + '\n')

def bump(version, level):
    """Incrémente la version selon le niveau (major, minor, patch)"""
    major, minor, patch = map(int, version.split('.'))

    if level == 'major':
        return f"{major + 1}.0.0"
    elif level == 'minor':
        return f"{major}.{minor + 1}.0"
    elif level == 'patch':
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Niveau inconnu: {level}")

def main():
    parser = argparse.ArgumentParser(description='Bump version')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--major', action='store_true', help='Bump major version')
    group.add_argument('--minor', action='store_true', help='Bump minor version')
    group.add_argument('--patch', action='store_true', help='Bump patch version')

    args = parser.parse_args()

    current_version = read_version()
    print(f"Version actuelle: {current_version}")

    if args.major:
        level = 'major'
    elif args.minor:
        level = 'minor'
    else:
        level = 'patch'

    new_version = bump(current_version, level)
    write_version(new_version)

    print(f"Nouvelle version: {new_version}")
    print(f"✓ VERSION.txt mis à jour")

if __name__ == '__main__':
    main()
```

**Utilisation** :
```bash
# Bugfix
python scripts/bump_version.py --patch
# Version actuelle: 1.0.0
# Nouvelle version: 1.0.1
# ✓ VERSION.txt mis à jour

# Nouvelle feature
python scripts/bump_version.py --minor
# Version actuelle: 1.0.1
# Nouvelle version: 1.1.0
# ✓ VERSION.txt mis à jour

# Breaking change
python scripts/bump_version.py --major
# Version actuelle: 1.1.0
# Nouvelle version: 2.0.0
# ✓ VERSION.txt mis à jour
```

---

### Script 3 : `rollback.bat`

**But** : Revenir à la version précédente en production.

```batch
@echo off
REM ========================================
REM Rollback à la version précédente
REM ========================================

setlocal

set VPS_HOST=root@69.62.108.82
set VPS_PATH=/opt/support-dashboard

echo.
echo ========================================
echo   ROLLBACK VERSION
echo ========================================
echo.

REM Lister les 5 derniers tags
echo Versions disponibles:
git tag --sort=-creatordate | head -5

echo.
set /p TAG="Choisir la version à restaurer (ex: v1.0.0): "

if "%TAG%"=="" (
    echo [!] Aucune version choisie
    pause
    exit /b 1
)

REM Vérifier que le tag existe
git rev-parse %TAG% >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Tag %TAG% introuvable
    pause
    exit /b 1
)

echo.
echo [!] ATTENTION: Rollback vers %TAG%
set /p CONFIRM="Confirmer ? (tapez OUI): "

if /i not "%CONFIRM%"=="OUI" (
    echo Rollback annulé
    pause
    exit /b 0
)

echo.
echo [1/5] Checkout sur %TAG%...
git checkout %TAG%
echo [+] Checkout OK

echo.
echo [2/5] Transfert vers production...
scp -r * %VPS_HOST%:%VPS_PATH%/
echo [+] Transfert OK

echo.
echo [3/5] Rebuild Docker...
ssh %VPS_HOST% "cd %VPS_PATH% && docker-compose build --no-cache"
echo [+] Build OK

echo.
echo [4/5] Redémarrage...
ssh %VPS_HOST% "cd %VPS_PATH% && docker-compose down && docker-compose up -d"
echo [+] Redémarrage OK

echo.
echo [5/5] Vérification...
timeout /t 5 /nobreak >nul
ssh %VPS_HOST% "docker logs support-dashboard --tail=10"

echo.
echo ========================================
echo   ROLLBACK TERMINE
echo ========================================
echo.
echo Version en production: %TAG%
echo URL: http://69.62.108.82:8501
echo.

pause
exit /b 0
```

**Utilisation** :
```bash
scripts\rollback.bat
# Versions disponibles:
# v1.0.1
# v1.0.0
# v0.9.5
#
# Choisir la version à restaurer: v1.0.0
# [!] ATTENTION: Rollback vers v1.0.0
# Confirmer ? (tapez OUI): OUI
#
# [1/5] Checkout sur v1.0.0...
# ...
```

---

## ✅ Checklist de Déploiement

Avant chaque déploiement, vérifiez :

### Phase 1 : Préparation

- [ ] Code testé localement sans erreur
- [ ] Tests unitaires passent (si vous en avez)
- [ ] Pas de `print()` / `console.log()` de debug
- [ ] Variables d'environnement mises à jour
- [ ] `.gitignore` à jour (pas de secrets commitées)
- [ ] `requirements.txt` / `package.json` à jour

### Phase 2 : Versioning

- [ ] `VERSION.txt` incrémenté (`bump_version.py`)
- [ ] Commit créé avec message clair
- [ ] Tag Git créé (`git tag -a v1.x.x`)
- [ ] `CHANGELOG.md` mis à jour

### Phase 3 : Comparaison

- [ ] `compare_versions.bat` exécuté
- [ ] Différences local/prod identifiées
- [ ] Backup de la version prod actuelle

### Phase 4 : Déploiement

- [ ] `deploy_prod.bat` exécuté
- [ ] Build Docker réussi
- [ ] Conteneur démarré sans erreur
- [ ] Logs vérifiés (20 dernières lignes)
- [ ] Application accessible via URL

### Phase 5 : Vérification Post-Déploiement

- [ ] Page d'accueil charge correctement
- [ ] Fonctionnalités critiques testées
- [ ] Pas d'erreur dans les logs Docker
- [ ] Pas d'erreur dans les logs Nginx
- [ ] Temps de réponse acceptable
- [ ] Version correcte affichée (`/status`)

### Phase 6 : Documentation

- [ ] Version en prod notée dans `README.md`
- [ ] Date de déploiement notée
- [ ] Utilisateurs prévenus (si changements majeurs)
- [ ] Rollback plan préparé (juste au cas où)

---

## 🚨 Plan de Rollback

En cas de problème après déploiement :

### Étape 1 : Diagnostic rapide (2 min)

```bash
# Vérifier les logs
ssh root@69.62.108.82 "docker logs support-dashboard --tail=50"

# Vérifier le status du conteneur
ssh root@69.62.108.82 "docker ps | grep support-dashboard"

# Tester l'URL
curl -I http://69.62.108.82:8501
```

### Étape 2 : Décision (1 min)

**Si erreur mineure** : Correctif rapide
```bash
# Fix rapide
git add .
git commit -m "hotfix: Quick fix"
scripts\deploy_prod.bat
```

**Si erreur majeure** : Rollback immédiat
```bash
scripts\rollback.bat
# Choisir la dernière version stable
```

### Étape 3 : Post-Mortem (après coup)

- Identifier la cause racine
- Ajouter des tests pour éviter la régression
- Documenter l'incident
- Améliorer le processus de déploiement

---

## 📊 Dashboard de Versions (Bonus)

**Page Streamlit pour comparer les environnements** :

```python
# dashboard/pages/versions.py
import streamlit as st
import subprocess
import requests

st.title("🔄 Version Comparison Dashboard")

col1, col2 = st.columns(2)

def get_version_info(env_name, url):
    """Récupère les infos de version d'un environnement."""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        data = response.json()
        return data
    except:
        return {"status": "error", "version": "N/A"}

with col1:
    st.subheader("🏠 Local (Development)")

    # Version locale
    with open('../VERSION.txt') as f:
        local_version = f.read().strip()
    st.metric("Version", local_version)

    # Git info
    try:
        git_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode().strip()
        st.metric("Commit", git_hash)

        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode().strip()
        st.metric("Branch", branch)
    except:
        pass

with col2:
    st.subheader("🚀 Production")

    # Version prod
    prod_info = get_version_info("production", "http://69.62.108.82:8501")

    st.metric("Version", prod_info.get('version', 'N/A'))
    st.metric("Commit", prod_info.get('commit', 'N/A'))
    st.metric("Status", prod_info.get('status', 'error'))

# Comparaison
st.markdown("---")
st.subheader("📊 Comparison")

if local_version == prod_info.get('version'):
    st.success("✅ Local et Production sont synchronisés")
else:
    st.warning(f"⚠️ Versions différentes: {local_version} (local) vs {prod_info.get('version')} (prod)")

    # Afficher les commits non déployés
    try:
        commits = subprocess.check_output(
            ['git', 'log', '--oneline', '--no-merges', f"v{prod_info.get('version')}..HEAD"]
        ).decode()

        if commits:
            st.markdown("**Commits non déployés:**")
            st.code(commits, language='text')
    except:
        pass
```

---

## 📚 Ressources Utiles

### Documentation

- **Semantic Versioning** : https://semver.org/
- **Git Flow** : https://nvie.com/posts/a-successful-git-branching-model/
- **Conventional Commits** : https://www.conventionalcommits.org/
- **Docker Best Practices** : https://docs.docker.com/develop/dev-best-practices/

### Outils

- **bump2version** : Automatiser l'incrémentation de version
- **commitizen** : Standardiser les messages de commit
- **semantic-release** : Automatiser releases et changelogs
- **Sentry** : Monitoring d'erreurs en production

---

## 🎯 Récapitulatif

| Niveau | Solution | Complexité | Bénéfice |
|--------|----------|------------|----------|
| 1 | Git Commits | ⭐ Facile | Historique basique |
| 2 | Git Tags | ⭐⭐ Facile | Versions lisibles |
| 3 | Fichier VERSION | ⭐⭐ Facile | Visible dans l'app |
| 4 | Branches Git | ⭐⭐⭐ Moyen | Isolation features |
| 5 | Variables Env | ⭐⭐ Facile | Config par env |
| 6 | Page Status | ⭐⭐⭐ Moyen | Monitoring visuel |

**Recommandation minimale** : Niveau 1 + 2 + 3 (Commits + Tags + VERSION.txt)
**Recommandation professionnelle** : Tous les niveaux

---

## 🤝 Workflow Recommandé (Quick Start)

```bash
# 1. Créer VERSION.txt (une seule fois)
echo "1.0.0" > VERSION.txt
git add VERSION.txt
git commit -m "chore: Add VERSION file"

# 2. Développer
# ... coder ...

# 3. Avant de déployer
python scripts/bump_version.py --patch    # Incrémenter version
git add .
git commit -m "fix: Correction bug XYZ"
git tag -a v1.0.1 -m "Hotfix: bug XYZ"

# 4. Comparer
scripts\compare_versions.bat

# 5. Déployer
scripts\deploy_prod.bat

# 6. Vérifier
scripts\compare_versions.bat
# ✓ Local et Prod synchronisés
```

---

**Dernière mise à jour** : Octobre 2025
**Version du guide** : 1.0
**Exemples basés sur** : Dashboard Support IT (Streamlit)

**Prochaines étapes recommandées** :
1. Créer `VERSION.txt` dans vos projets
2. Créer `scripts/compare_versions.bat`
3. Créer `scripts/bump_version.py`
4. Ajouter page `/status` dans vos apps
5. Documenter votre workflow dans `README.md`
