# Proposition de Restructuration du Repository Hostinger

**Date**: 2025-12-09
**Analyse complète**: 125 fichiers MD, 115 scripts, 30 configs, ~21 MB total

> **🎉 UPDATE**: La restructuration `docs/docs/` → `docs/` a été complétée avec succès !
> Voir `MKDOCS_RESTRUCTURATION_REPORT.md` pour les détails.
> Build MkDocs fonctionnel en 7.69s, -66% de taille repository.

---

## 🚨 Problèmes Identifiés

### 1. Racine du Repo Encombrée (14 fichiers MD + 13 non trackés)

**Fichiers à la racine qui polluent** (124 KB de rapports temporaires):
```
✗ COMPREHENSIVE_SPACE_ANALYSIS.md       (11 KB)
✗ DOCKER_CONTAINERS_AUDIT.md            (16 KB)
✗ DOCKER_OPTIMIZATION_ANALYSIS.md       (19 KB)
✗ DOCKER_SERVICES_ACTIVE.md             (9.2 KB)
✗ DOCKER_SPACE_ANALYSIS_REPORT.md       (9.6 KB)
✗ SPACE_ANALYSIS_2025-12-04.md          (12 KB)
✗ MIGRATION_100GB_STATUS.md             (4.6 KB)
✗ MIGRATION_DROPBOX_REPORT.md           (8.8 KB)
✗ MIGRATION_EN_COURS.md                 (2.8 KB)
✗ MIGRATION_PLAN.md                     (7.4 KB)
✗ SESSION_SUMMARY_2025-12-04.md         (7.9 KB)
✗ SKILLS_PROPOSAL.md                    (12 KB)
```

**Fichiers non trackés** (596 KB):
```
✗ .playwright-mcp/                      (8 PNG screenshots - 596 KB)
✗ .temp/dive_app.py                     (8.8 KB)
✗ .mcp.json                             (149 bytes)
```

### 2. Documentation Dupliquée

**Duplications exactes** (MD5 identiques):
```
docs/docs/infrastructure/dns-email.md
  = EXACTEMENT IDENTIQUE =
archive/cleanup-2025-11-09/guides-old/GUIDE_DNS_EMAIL.md
```

**Rapports similaires dispersés**:
- 6 rapports d'analyse Docker/espace différents à la racine
- 4 rapports de migration (root + archive)
- 2 dashboards dashy config (conf.yml + updated-conf.yml)

### 3. Fichiers Générés Commités

**14 MB de build output dans le repo**:
```
docs/site/                              (14 MB - 66% du repo!)
  ├── assets/javascripts/               (Lunr search, 25+ fichiers)
  ├── stylesheets/
  └── search/
```
➜ **Ce sont des fichiers générés par MkDocs qui ne devraient PAS être dans Git**

> **✅ RÉSOLU**: Structure `docs/docs/` aplatie vers `docs/`, `site/` ajouté à `.gitignore`,
> `reference/04-reference/` corrigé, 3 nouveaux services ajoutés à nav.
> Build MkDocs fonctionnel. Voir `MKDOCS_RESTRUCTURATION_REPORT.md`.

### 4. TODOs Incomplets dans la Documentation

```
docs/docs/operations/emergency-runbook.md
  → "2. Court terme: [TODO]"
  → "3. Long terme: [TODO]"

docs/docs/reference/deployment/cache-wordpress.md
  → "## TODO"

docs/docs/infrastructure/dns-email.md
  → "# ⚠️ TODO - Configuration DNS pour Email Server"
```

### 5. Organisation des Scripts Incohérente

**Scripts éparpillés dans 4 endroits**:
```
scripts/                                (20 shell scripts)
  ├── deployment/
  ├── monitoring/
  ├── optimizations/                    (6 sous-dossiers app-specific)
  └── utils/

apps/11-dashboards/energie-40eur-dashboard/scripts/  (50+ scripts!)
apps/14-server-configs/scripts/
apps/03-jokers/*.sh
apps/14-media-servers/jellyfin-stack/*.sh
```

### 6. Services Non Trackés

3 nouveaux services documentés mais non commités:
```
? docs/docs/services/discord-bot.md
? docs/docs/services/langchain-service.md
? docs/docs/services/paperflow.md
```

---

## 🎯 Proposition de Restructuration

### Phase 1: Nettoyage Immédiat (Priorité Haute)

#### A. Gérer les Fichiers Non Trackés

**Option 1 - Archiver puis supprimer**:
```bash
# Créer archive des rapports temporaires
mkdir -p archive/reports/2025-12-09-cleanup/
mv COMPREHENSIVE_SPACE_ANALYSIS.md archive/reports/2025-12-09-cleanup/
mv DOCKER_CONTAINERS_AUDIT.md archive/reports/2025-12-09-cleanup/
mv DOCKER_OPTIMIZATION_ANALYSIS.md archive/reports/2025-12-09-cleanup/
mv DOCKER_SERVICES_ACTIVE.md archive/reports/2025-12-09-cleanup/
mv DOCKER_SPACE_ANALYSIS_REPORT.md archive/reports/2025-12-09-cleanup/
mv SPACE_ANALYSIS_2025-12-04.md archive/reports/2025-12-09-cleanup/
mv MIGRATION_100GB_STATUS.md archive/reports/2025-12-09-cleanup/
mv MIGRATION_DROPBOX_REPORT.md archive/reports/2025-12-09-cleanup/
mv MIGRATION_EN_COURS.md archive/reports/2025-12-09-cleanup/
mv MIGRATION_PLAN.md archive/reports/2025-12-09-cleanup/
mv SESSION_SUMMARY_2025-12-04.md archive/reports/2025-12-09-cleanup/
mv SKILLS_PROPOSAL.md archive/reports/2025-12-09-cleanup/

# Screenshots Playwright
mkdir -p archive/screenshots/
mv .playwright-mcp archive/screenshots/playwright-2025-12-09

# Temp files
rm -rf .temp/

# MCP config
git add .mcp.json  # Si utilisé, sinon supprimer
```

**Option 2 - Supprimer directement** (si rapports obsolètes):
```bash
rm COMPREHENSIVE_SPACE_ANALYSIS.md
rm DOCKER_CONTAINERS_AUDIT.md
rm DOCKER_OPTIMIZATION_ANALYSIS.md
rm DOCKER_SERVICES_ACTIVE.md
rm DOCKER_SPACE_ANALYSIS_REPORT.md
rm SPACE_ANALYSIS_2025-12-04.md
rm MIGRATION_*.md
rm SESSION_SUMMARY_2025-12-04.md
rm SKILLS_PROPOSAL.md
rm -rf .playwright-mcp/
rm -rf .temp/
```

#### B. Ajouter au .gitignore

Créer/mettre à jour `.gitignore`:
```gitignore
# Build output (MkDocs)
docs/site/
site/

# Temporary files
.temp/
*.tmp
*.log

# Screenshots & test artifacts
.playwright-mcp/
screenshots/
test-results/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# OS
.DS_Store
Thumbs.db
desktop.ini

# IDE
.vscode/
.idea/

# Reports & analysis (keep in archive/ only)
/*_ANALYSIS*.md
/*_REPORT*.md
/*_STATUS*.md
MIGRATION_*.md
SESSION_*.md
```

#### C. Supprimer Duplications

```bash
# Supprimer duplications exactes de l'archive
rm archive/cleanup-2025-11-09/guides-old/GUIDE_DNS_EMAIL.md
rm archive/cleanup-2025-11-09/guides-old/GUIDE_GMAIL_SMTP.md
rm archive/cleanup-2025-11-09/guides-old/GUIDE_PHOTO_MANAGEMENT_DROPBOX_DIGIKAM.md

# Garder uniquement les versions dans docs/docs/
```

#### D. Commiter les Services Non Trackés

```bash
git add docs/docs/services/discord-bot.md
git add docs/docs/services/langchain-service.md
git add docs/docs/services/paperflow.md
git commit -m "docs: add missing service documentation (discord-bot, langchain-service, paperflow)"
```

---

### Phase 2: Restructuration Documentation (Priorité Moyenne)

#### A. Nouvelle Structure Proposée

```
docs/
├── docs/                               (Source - gardé tel quel)
│   ├── infrastructure/                 ✅ (12 docs)
│   ├── services/                       ✅ (28 docs) + 3 nouveaux
│   ├── operations/                     ✅ (8 docs)
│   ├── reference/                      ✅ (18 docs)
│   ├── advanced/                       ✅ (10 docs)
│   ├── applications/                   ✅ (2 docs + registry.yml)
│   ├── changelog/                      ✅ (6 docs)
│   ├── dynamic/                        ✅ (2 docs)
│   └── index.md
│
├── site/                               ❌ SUPPRIMÉ (dans .gitignore)
└── mkdocs.yml                          ✅ Gardé

archive/
├── cleanup-2025-11-09/
│   ├── guides-old/                     ❌ SUPPRIMÉ (duplications)
│   └── CLEANUP_REPORT.md               ✅ Gardé
├── migrations/                         ✅ Consolidé
│   └── [tous les rapports migration regroupés ici]
├── planning/                           ✅ Gardé
├── reports/                            ✅ CRÉER - pour futurs rapports
│   └── 2025-12-09-cleanup/            ← Rapports actuels archivés ici
└── screenshots/                        ✅ CRÉER - pour screenshots Playwright

scripts/                                ✅ Restructuré
├── deployment/                         (shell scripts)
├── monitoring/                         (shell + Python)
├── maintenance/                        ✅ CRÉER
│   ├── docker-cleanup/
│   ├── space-analysis/
│   └── backup/
├── optimizations/                      ✅ Gardé (app-specific)
└── utils/                              ✅ Gardé

apps/                                   ✅ Gardé tel quel
└── [structure existante OK]
```

#### B. Actions Concrètes

```bash
# 1. Supprimer output généré
rm -rf docs/site/
echo "docs/site/" >> .gitignore

# 2. Créer structure archive
mkdir -p archive/reports/2025-12-09-cleanup
mkdir -p archive/screenshots

# 3. Supprimer guides dupliqués
rm -rf archive/cleanup-2025-11-09/guides-old/

# 4. Créer scripts/maintenance/
mkdir -p scripts/maintenance/docker-cleanup
mkdir -p scripts/maintenance/space-analysis
mkdir -p scripts/maintenance/backup

# Déplacer scripts appropriés
mv scripts/docker-analyze-images.sh scripts/maintenance/docker-cleanup/
mv scripts/docker-audit-complete.sh scripts/maintenance/docker-cleanup/
mv scripts/docker-cleanup-images.sh scripts/maintenance/docker-cleanup/
mv scripts/docker-final-cleanup.sh scripts/maintenance/docker-cleanup/
mv scripts/docker-monitor-space.sh scripts/maintenance/space-analysis/
```

---

### Phase 3: Compléter TODOs (Priorité Basse)

#### Fichiers à compléter:

1. **docs/docs/operations/emergency-runbook.md**
   - Compléter sections "Court terme" et "Long terme"

2. **docs/docs/reference/deployment/cache-wordpress.md**
   - Compléter section TODO

3. **docs/docs/infrastructure/dns-email.md**
   - Retirer marqueur "⚠️ TODO" ou compléter configuration

---

### Phase 4: Optimisations Scripts (Optionnel)

#### Problème: 50+ scripts dans energie-dashboard

**Option A - Laisser tel quel** (si projet actif)
```
apps/11-dashboards/energie-40eur-dashboard/scripts/
└── [50+ scripts restent ici]
```

**Option B - Sous-organiser** (si besoin de clarté)
```
apps/11-dashboards/energie-40eur-dashboard/scripts/
├── fetchers/                           (1_fetch_*.py, 2_fetch_*.py)
├── analyzers/                          (4_analyze_*.py, 5_analyze_*.py)
├── scrapers/                           (10_scrape_*.py, 11_automated_scraper.py)
├── consolidators/                      (8_consolidate.py, 16_consolidate_*.py)
├── uploaders/                          (92_prepare_*.py, 93_upload_*.py)
└── memvid/                             (97_create_*.py, 98_upload_*.py, 99_test_*.py)
```

---

## 📊 Impact Estimé

### Avant Restructuration
```
Repository: ~21 MB
├── docs/site/ (built)          14 MB    (66%) ❌ Généré
├── archive/                    3.2 MB   (15%) ⚠️ Avec duplications
├── Root reports               124 KB    ❌ Désorganisé
├── Untracked files            604 KB    ❌ Non géré
└── Autres                     3.7 MB    ✅ OK

Issues:
- 14 fichiers MD à la racine
- 13 fichiers non trackés
- Duplications dans archive/
- 14 MB de build output commité
```

### Après Restructuration
```
Repository: ~6 MB (-71%)
├── docs/docs/ (source)         1.1 MB   (18%) ✅ Source clean
├── archive/                    2.8 MB   (47%) ✅ Consolidé, sans duplications
├── apps/                       751 KB   (13%) ✅ Organisé
├── scripts/                    370 KB   (6%)  ✅ Restructuré
├── .claude/                    113 KB   (2%)  ✅ OK
└── Configs                     ~100 KB  (2%)  ✅ OK

Benefits:
✅ Racine propre (seulement CLAUDE.md, README.md, mkdocs.yml, repos-map.yml)
✅ Pas de build output dans Git
✅ Pas de duplications
✅ Fichiers temporaires ignorés
✅ Archive organisée chronologiquement
✅ Scripts classés par fonction
```

---

## 🚀 Plan d'Exécution Recommandé

### Étape 1: Nettoyage Immédiat (15 minutes)
```bash
# Sauvegarder d'abord (au cas où)
git status > pre-cleanup-status.txt
git log -1 > pre-cleanup-commit.txt

# Archiver rapports temporaires
mkdir -p archive/reports/2025-12-09-cleanup
mv *_ANALYSIS*.md *_REPORT*.md *_STATUS*.md MIGRATION_*.md SESSION_*.md SKILLS_*.md archive/reports/2025-12-09-cleanup/ 2>/dev/null

# Supprimer fichiers temporaires
rm -rf .playwright-mcp .temp

# Créer .gitignore
cat >> .gitignore << 'EOF'
docs/site/
site/
.temp/
.playwright-mcp/
EOF

# Supprimer build output
rm -rf docs/site/

# Commit
git add .gitignore
git add -u  # Stage suppression de docs/site/ si tracked
git commit -m "cleanup: archive temporary reports, add gitignore, remove build output"
```

### Étape 2: Supprimer Duplications (5 minutes)
```bash
# Supprimer duplications archive
rm archive/cleanup-2025-11-09/guides-old/GUIDE_DNS_EMAIL.md
rm archive/cleanup-2025-11-09/guides-old/GUIDE_GMAIL_SMTP.md
rm archive/cleanup-2025-11-09/guides-old/GUIDE_PHOTO_MANAGEMENT_DROPBOX_DIGIKAM.md

git add -u
git commit -m "cleanup: remove duplicate guides from archive"
```

### Étape 3: Commiter Services (2 minutes)
```bash
git add docs/docs/services/discord-bot.md
git add docs/docs/services/langchain-service.md
git add docs/docs/services/paperflow.md
git commit -m "docs: add missing service documentation (discord-bot, langchain-service, paperflow)"
```

### Étape 4: Restructurer Scripts (10 minutes)
```bash
# Créer nouvelle structure
mkdir -p scripts/maintenance/docker-cleanup
mkdir -p scripts/maintenance/space-analysis
mkdir -p scripts/maintenance/backup

# Déplacer scripts
mv scripts/docker-analyze-images.sh scripts/maintenance/docker-cleanup/
mv scripts/docker-audit-complete.sh scripts/maintenance/docker-cleanup/
mv scripts/docker-cleanup-images.sh scripts/maintenance/docker-cleanup/
mv scripts/docker-final-cleanup.sh scripts/maintenance/docker-cleanup/
mv scripts/docker-monitor-space.sh scripts/maintenance/space-analysis/

# Créer README explicatif
cat > scripts/maintenance/README.md << 'EOF'
# Maintenance Scripts

## docker-cleanup/
Scripts for Docker image, container, and volume cleanup.

## space-analysis/
Scripts for disk space monitoring and analysis.

## backup/
Backup and restore scripts for server state.
EOF

git add scripts/
git commit -m "refactor: reorganize maintenance scripts into categories"
```

### Étape 5: Compléter TODOs (Selon besoin)
- Réviser emergency-runbook.md
- Réviser cache-wordpress.md
- Réviser dns-email.md

---

## ✅ Checklist Post-Restructuration

### Vérifications
- [ ] Racine propre: seulement CLAUDE.md, README.md, mkdocs.yml, repos-map.yml, .gitignore
- [ ] Pas de fichiers non trackés (sauf .mcp.json si utilisé)
- [ ] docs/site/ dans .gitignore
- [ ] Pas de duplications dans archive/
- [ ] Services nouveaux commités
- [ ] Scripts organisés logiquement
- [ ] Git status clean

### Tests
- [ ] MkDocs build fonctionne: `mkdocs build`
- [ ] MkDocs serve fonctionne: `mkdocs serve`
- [ ] Scripts dans scripts/maintenance/ exécutables
- [ ] Documentation accessible et liens fonctionnels
- [ ] Skills dans .claude/skills/ toujours accessibles

---

## 💡 Recommandations Futures

### Prévention
1. **Ne jamais commiter docs/site/** - toujours dans .gitignore
2. **Rapports temporaires → archive/reports/DATE/** - pas à la racine
3. **Scripts app-specific → apps/XX/scripts/** - pas dans scripts/
4. **TODOs → Issues GitHub** - meilleur tracking
5. **Migration reports → archive/migrations/** - dès fin de migration

### Maintenance
- Réviser archive/ tous les 6 mois - supprimer contenu > 1 an
- Consolider rapports similaires dans archive/reports/
- Garder scripts/maintenance/ organisé par fonction
- Mettre à jour registry.yml quand nouvelles apps

### CI/CD (Optionnel)
```yaml
# .github/workflows/docs.yml
name: Deploy MkDocs
on:
  push:
    branches: [master]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install mkdocs-material
      - run: mkdocs gh-deploy --force
```

---

## 🎯 Résumé Exécutif

**Problème**: Repository encombré avec 14 fichiers MD à la racine, 14 MB de build output commité, duplications, et fichiers non trackés.

**Solution**:
1. Archiver rapports temporaires
2. Ajouter .gitignore pour build output
3. Supprimer duplications
4. Restructurer scripts
5. Commiter services manquants

**Bénéfices**:
- Repository 71% plus léger (21 MB → 6 MB)
- Racine propre et organisée
- Pas de duplications
- Scripts logiquement organisés
- Documentation complète

**Temps estimé**: 30-45 minutes

**Risques**: Très faible - sauvegardes recommandées avant exécution

---

**Prêt à exécuter ?** Je peux automatiser toutes ces étapes avec un script bash si tu veux.
