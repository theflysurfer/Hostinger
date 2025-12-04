# Proposition de Skills pour Hostinger VPS

**Date**: 2025-12-04
**Basé sur**: Analyse espace disque et audit Docker containers

---

## 📊 Analyse des Skills Existantes

### Skills Actuelles dans le Repo

**Repo Hostinger** (`.claude/skills/`):
1. `docker-hostinger/` - Management Docker général (EXISTANT)
2. `docker-hostinger-optimizer/` - Optimisation containers (SKELETON uniquement)
3. `ssh-fix-hostinger/` - Fix SSH permissions Windows (COMPLET)

**Marketplace** (`~/.claude/skills/` via junction):
1. `hostinger-ssh` - SSH operations
2. `hostinger-docker` - Docker management
3. `hostinger-nginx` - Nginx configuration
4. `hostinger-database` - Database operations
5. `hostinger-maintenance` - Maintenance générale

### Best Practices Claude Skills (Recherche 2025)

**Sources consultées**:
- [Agent Skills - Claude Code Docs](https://docs.claude.com/en/docs/claude-code/skills)
- [Skill authoring best practices - Claude Docs](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [Building Skills for Claude Code | Claude](https://www.claude.com/blog/building-skills-for-claude-code)

**Principes clés identifiés**:

1. **Description efficace** (~100 tokens lors du scan):
   - Inclure le "quoi" ET le "quand"
   - Triggers spécifiques pour auto-invocation
   - Contexte d'utilisation clair

2. **Progressive disclosure**:
   - Metadata: ~100 tokens (scan)
   - Full skill: <5k tokens (activation)
   - Resources: chargés à la demande

3. **Structure focalisée**:
   - Une skill = un workflow
   - Plusieurs skills focused > une skill large
   - Composition > complexité

4. **Contenus recommandés**:
   - Examples inputs/outputs
   - Scripts exécutables
   - References/documentation
   - Clear safety checks

---

## 🆕 Nouvelle Skill Créée: `hostinger-space-reclaim`

### Pourquoi Cette Skill?

**Problème identifié**:
- Serveur fréquemment à 94% d'utilisation disque
- Pas de procédure standardisée de cleanup
- Risques si cleanup manuel sans analyse
- Besoin de niveaux de risque (safe/moderate/advanced)

**Workflow couvert**:
1. Analyse complète espace disque
2. Cleanup safe (automatique)
3. Cleanup modéré (avec approval)
4. Actions avancées (expert)
5. Scripts bash prêts à l'emploi

### Structure de la Skill

```
hostinger-space-reclaim/
├── SKILL.md                    # 2800 tokens - Core skill
├── scripts/
│   ├── analyze-space.sh        # Analyse complète
│   ├── safe-cleanup.sh         # Actions safe automatiques
│   └── migrate-impro-music.sh  # Migration 4.1GB vers RClone
└── references/
    └── cleanup-levels.md       # Risk levels, decision tree, rollback
```

### Triggers d'Auto-Invocation

La skill s'active sur:
- "disk space"
- "cleanup"
- "reclaim space"
- "free up space"
- "running out of space"
- "90% disk usage"

### Niveaux de Cleanup

**Level 1: SAFE** (1-1.5GB, auto-execute):
- Prune dangling images
- Vacuum journal
- Truncate logs safe

**Level 2: MODERATE** (12-21GB, ask user):
- Prune old images >30d
- Prune unused volumes
- Migrate impro-manager music (4.1GB)

**Level 3: ADVANCED** (8-50GB, expert):
- Rebuild Docker images
- System prune --all
- Manual overlay2 cleanup

### Scripts Fournis

**`analyze-space.sh`** (130 lines):
- Disk usage global
- Docker system df
- Top 20 directories
- Logs analysis
- Dangling resources
- Recommendations basées sur seuils

**`safe-cleanup.sh`** (100 lines):
- Zero-risk actions
- Before/after measurements
- Verification checks
- Summary report

**`migrate-impro-music.sh`** (120 lines):
- Pre-flight checks (RClone mount, writable, etc.)
- Backup creation
- Migration avec symlink
- Health check application
- Rollback instructions

### Integration avec Skills Existantes

**Références croisées**:
- `hostinger-docker` → Pour operations Docker de base
- `hostinger-docker-optimizer` → Pour rebuild images (Level 3)
- `hostinger-maintenance` → Pour maintenance régulière

**Complémentarité**:
- `space-reclaim` = Réactif (espace critique)
- `maintenance` = Proactif (préventif)
- `docker` = Operations générales
- `docker-optimizer` = Optimisation technique

---

## 🔄 Skill à Compléter: `hostinger-docker-optimizer`

### État Actuel

**Fichier existant**: `.claude/skills/docker-hostinger-optimizer/SKILL.md`
**Statut**: SKELETON (28 lines, pas de détails)
**Contenu**: Description générique seulement

### Proposition de Complétion

Basé sur `DOCKER_OPTIMIZATION_ANALYSIS.md` et `DOCKER_CONTAINERS_AUDIT.md`:

**Ajouter**:
1. **Workflows spécifiques par type d'app**:
   - Python/ML (CPU PyTorch, multi-stage)
   - Node.js/Next.js (alpine, production deps)
   - FastAPI/Flask (slim base, venv copy)

2. **Dockerfiles optimisés prêts à l'emploi**:
   - `templates/python-ml-cpu.dockerfile`
   - `templates/python-fastapi.dockerfile`
   - `templates/nodejs-nextjs.dockerfile`

3. **Analyse automatique d'images**:
   - Script `analyze-image.sh` (layers, size, PyTorch check)
   - Recommendations basées sur findings
   - Estimation de gain

4. **Procédures de rebuild sécurisées**:
   - Backup image actuelle
   - Build avec tests
   - Rollback si échec
   - Validation post-deploy

5. **Best practices 2025**:
   - Multi-stage builds (50-90% réduction)
   - CPU-only ML libs (-60% pour PyTorch)
   - Alpine vs slim bases
   - Micro-distros (Wolfi, Chainguard)

### Résultats Attendus

**Images optimisables identifiées**:
- whisperx: 8.77GB → 3-4GB (4-5GB gain)
- paperflow-worker: 6.65GB → 2.5-3GB (3-4GB gain)
- kokoro-tts: 5.61GB (tierce, issue GitHub suggérée)

**Total gain potentiel**: 8-12GB d'images

---

## 📊 Comparaison Skills Proposées vs Existantes

| Aspect | Skills Existantes | Nouvelles Skills |
|--------|------------------|------------------|
| **Focus** | Operations générales | Problèmes spécifiques |
| **Granularité** | Large (docker, nginx, ssh) | Fine (space, optimization) |
| **Scripts** | Quelques exemples | Prêts à exécuter |
| **Risk levels** | Non définis | Clairement séparés |
| **Progressive disclosure** | Basique | Structurée (metadata → full → resources) |
| **Auto-invoke triggers** | Génériques | Spécifiques au contexte |
| **Examples** | Limités | Inputs/outputs inclus |
| **Rollback** | Non documenté | Procédures complètes |

---

## 🎯 Recommandations d'Implémentation

### Phase 1: Immédiat

**1. Déployer `hostinger-space-reclaim`** (PRÊT)
```bash
# Skill déjà créée dans Marketplace
cd "C:\Users\julien\OneDrive\Coding\_Projets de code\2025.11 Claude Code MarketPlace"
git add skills/hostinger-space-reclaim/
git commit -m "feat: add hostinger-space-reclaim skill"
git push

# Sync to global
# Skills via junction déjà actifs globalement
```

**Test**: "Analyze disk space on srv759970" → Devrait auto-invoke la skill

**2. Exécuter cleanup safe** (si espace critique)
```bash
# Via la skill nouvellement créée
ssh automation@69.62.108.82 'bash -s' < scripts/safe-cleanup.sh
```

**Gain attendu**: 1-1.5GB immédiatement

### Phase 2: Cette Semaine

**3. Compléter `docker-hostinger-optimizer`**

Ajouter:
- Templates Dockerfile optimisés
- Script analyze-image.sh
- Workflow rebuild sécurisé
- Documentation best practices 2025

**4. Créer skill `hostinger-docker-audit`** (optionnel)

Pour audits récurrents:
- Scan toutes images >1GB
- Check PyTorch CPU vs GPU
- Dangling resources
- Rapport avec recommendations

### Phase 3: Long Terme

**5. Hook pre-deployment** (optionnel)

Créer `.claude/hooks/pre-deployment.sh`:
```bash
#!/bin/bash
# Check disk space before deploying
USAGE=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$USAGE" -gt 85 ]; then
  echo "⚠️  WARNING: Disk usage high ($USAGE%). Consider cleanup first."
  echo "Run: hostinger-space-reclaim skill"
  exit 1
fi
```

**6. Monitoring integration**

Ajouter alertes Grafana:
- Disk >85% → Warning
- Disk >90% → Critical (invoke space-reclaim auto)
- Dangling images >5 → Info

---

## 📝 Documentation Standards Appliqués

### SKILL.md Structure (Best Practices)

```yaml
---
name: skill-name
description: What it does + when to use (specific triggers)
---

# Skill Title

Brief introduction (1-2 sentences)

## When to Use
- Specific triggers that auto-invoke
- Contexts where skill is relevant

## Workflow Overview
Progressive disclosure - start simple

## Key Actions
Grouped by risk/complexity level

## Scripts
Executable, tested scripts

## References
Deep-dive documentation

## Related Skills
Cross-references

## Safety/Rollback
Always included for operations
```

### Script Headers Template

```bash
#!/bin/bash
# Clear description of what script does
# Gain expected (if cleanup)
# Risk level (safe/moderate/advanced)
# Usage: ssh server 'bash -s' < script.sh

set -e  # Exit on error

# Pre-flight checks
# Main operations
# Verification
# Summary report
```

---

## 🔗 Ressources

### Documentation Consultée

**Claude Skills**:
- [Agent Skills - Claude Code Docs](https://docs.claude.com/en/docs/claude-code/skills)
- [Skill authoring best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [How to create custom Skills | Claude Help Center](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)
- [Building Skills for Claude Code | Claude](https://www.claude.com/blog/building-skills-for-claude-code)

**Docker Optimization**:
- [Best practices | Docker Docs](https://docs.docker.com/build/building/best-practices/)
- [Collabnix - 90% Image Reduction](https://collabnix.com/how-i-reduced-a-docker-image-size-by-90-a-step-by-step-journey/)
- [Wayfair Case Study - 50% Reduction](https://www.aboutwayfair.com/case-study-how-we-decreased-the-size-of-our-python-docker-images-by-over-50)

### Fichiers Créés

**Marketplace**:
```
skills/hostinger-space-reclaim/
├── SKILL.md                    (2.8k tokens)
├── scripts/
│   ├── analyze-space.sh        (130 lines)
│   ├── safe-cleanup.sh         (100 lines)
│   └── migrate-impro-music.sh  (120 lines)
└── references/
    └── cleanup-levels.md       (250 lines)
```

**Hostinger Repo**:
```
SPACE_ANALYSIS_2025-12-04.md           (Analyse complète)
DOCKER_OPTIMIZATION_ANALYSIS.md        (Best practices + templates)
DOCKER_CONTAINERS_AUDIT.md             (Audit 51 images)
SKILLS_PROPOSAL.md                     (Ce document)
```

---

## ✅ Checklist de Déploiement

### Skill hostinger-space-reclaim

- [x] SKILL.md créé avec frontmatter YAML
- [x] Description avec triggers spécifiques
- [x] Progressive disclosure (analyse → safe → moderate → advanced)
- [x] Scripts bash testables créés
- [x] Références détaillées (risk levels, rollback)
- [x] Cross-references vers autres skills
- [x] Safety checks documentés
- [ ] Scripts testés sur srv759970
- [ ] Commité dans Marketplace repo
- [ ] Testé l'auto-invocation

### Skill hostinger-docker-optimizer

- [ ] Compléter SKILL.md (actuellement skeleton)
- [ ] Ajouter templates Dockerfile
- [ ] Créer analyze-image.sh
- [ ] Workflow rebuild sécurisé
- [ ] Documentation best practices 2025
- [ ] Tests sur images cibles (whisperx, paperflow)

---

## 🚀 Next Steps Immédiats

**1. Tester space-reclaim skill**
```bash
# Test auto-invoke
"Can you analyze disk space on srv759970?"

# Devrait invoquer hostinger-space-reclaim automatiquement
```

**2. Exécuter cleanup safe** (si >90% disk)
```bash
ssh automation@69.62.108.82 'bash -s' < ~/.claude/skills/hostinger-space-reclaim/scripts/safe-cleanup.sh
```

**3. Proposer moderate cleanup** (si user approuve)
```bash
# Migrate impro-manager music
ssh automation@69.62.108.82 'bash -s' < ~/.claude/skills/hostinger-space-reclaim/scripts/migrate-impro-music.sh
```

**Gain total attendu**: 5-6GB (safe + migrate)

---

**Document créé**: 2025-12-04
**Basé sur**: 3 rapports d'analyse + best practices Claude 2025
**Prochaine étape**: Commiter skills + tester auto-invocation
