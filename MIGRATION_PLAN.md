# Plan de Migration Documentation

**Date**: 2025-12-04
**Status**: En cours
**Site Live**: https://docs.srv759970.hstgr.cloud/ ⚠️ ATTENTION - modifications impactent production

---

## 🎯 Objectifs

1. ✅ Migrer services techniques vers `services/`
2. ✅ Consolider applications vers `applications/registry.yml`
3. ✅ Fixer liens cassés dans mkdocs.yml
4. ✅ Maintenir compatibilité site live
5. ✅ Nettoyer ancienne structure

---

## 📊 État Actuel

### Fichiers déjà migrés ✅

| Fichier | Source | Destination | Status |
|---------|--------|-------------|--------|
| whisperx.md | 02-applications/ai-transcription/ | services/ | ✅ Migré et supprimé |
| tika.md | 02-applications/ai-services/ | services/ | ✅ Migré et supprimé |
| ragflow.md | 02-applications/ai-rag/ | services/ | ✅ Migré et supprimé |

### Liens cassés dans mkdocs.yml ❌

**10 fichiers manquants** dans section "Services Techniques":
- `services/faster-whisper.md` (existe: `02-applications/ai-transcription/`)
- `services/ollama.md` (existe: `02-applications/ai-services/`)
- `services/rag-anything.md` (n'existe pas - à créer ou retirer)
- `services/memvid.md` (n'existe pas - à créer ou retirer)
- `services/monitoring-stack.md` (existe: `02-applications/monitoring/`)
- `services/dashy.md` (existe: `02-applications/monitoring/`)
- `services/docker-autostart.md` (n'existe pas - référence operation)
- `services/nextcloud.md` (existe: `02-applications/collaboration/`)
- `services/jitsi.md` (existe: `02-applications/collaboration/`)
- `services/rocketchat.md` (existe: `02-applications/collaboration/`)

---

## 📋 Plan de Migration

### Phase 1: Fixer liens cassés urgents (PRIORITAIRE)

**Option A: Pointer vers ancienne structure** (rapide, temporaire)
- Modifier mkdocs.yml pour pointer vers 02-applications/
- Site continue de fonctionner immédiatement
- Migration progressive ensuite

**Option B: Migrer fichiers maintenant** (propre, définitif)
- Déplacer 7 fichiers vers services/
- Retirer 3 liens inexistants
- Rebuild + redeploy site

**Recommandation**: Option B - migrer maintenant car peu de fichiers

### Phase 2: Migration services techniques

#### Services AI/ML à migrer

```bash
# Fichiers existants à déplacer
mv 02-applications/ai-services/ollama.md → services/ollama.md
mv 02-applications/ai-transcription/faster-whisper.md → services/faster-whisper.md
mv 02-applications/ai-tts/neutts.md → services/neutts.md (optionnel)
mv 02-applications/ai-tts/xtts.md → services/xtts.md (optionnel)
```

#### Services Monitoring à migrer

```bash
mv 02-applications/monitoring/monitoring-stack.md → services/monitoring-stack.md
mv 02-applications/monitoring/dashy.md → services/dashy.md
mv 02-applications/monitoring/dozzle.md → services/dozzle.md (optionnel)
mv 02-applications/monitoring/glances.md → services/glances.md (optionnel)
mv 02-applications/monitoring/portainer.md → services/portainer.md (optionnel)
```

#### Services Collaboration à migrer

```bash
mv 02-applications/collaboration/nextcloud.md → services/nextcloud.md
mv 02-applications/collaboration/jitsi.md → services/jitsi.md
mv 02-applications/collaboration/rocketchat.md → services/rocketchat.md
```

#### Liens inexistants à traiter

**services/rag-anything.md** - N'existe pas
- Action: Retirer du mkdocs.yml OU créer stub

**services/memvid.md** - N'existe pas
- Action: Créer doc (service existe sur srv759970)

**services/docker-autostart.md** - N'existe pas
- Action: Pointer vers `03-operations/docker-autostart.md`

### Phase 3: Consolidation applications

#### Applications WordPress → registry.yml

- `02-applications/wordpress/clemence.md` → Metadata dans registry
- `02-applications/wordpress/solidarlink.md` → Metadata dans registry

**Action**: Ces docs restent ou migrent vers repos projets

#### Applications CMS/Sites → registry.yml

- `02-applications/cms-sites/cristina-site.md` → Metadata dans registry
- `02-applications/cms-sites/impro-manager.md` → Metadata dans registry

#### Applications Dashboards → registry.yml

- `02-applications/dashboards/energie-dashboard.md` → Metadata dans registry

#### Guides de déploiement

**02-applications/guides/** (29 fichiers)
- Option 1: Déplacer vers `reference/deployment/`
- Option 2: Déplacer vers `operations/deployment/`
- Option 3: Garder dans applications mais renommer

**Recommandation**: Migrer vers `reference/deployment/` car guides techniques réutilisables

### Phase 4: Nettoyage

Après migration complète:
```bash
# Supprimer répertoires vides
rmdir 02-applications/ai-services/
rmdir 02-applications/ai-transcription/
rmdir 02-applications/ai-rag/
rmdir 02-applications/monitoring/
rmdir 02-applications/collaboration/

# Renommer si nécessaire
# 01-infrastructure/ → infrastructure/ (si souhaité)
# 03-operations/ → operations/ (si souhaité)
# etc.
```

---

## ⚠️ Considérations Critiques

### Site Live en Production

- ✅ Toute modification doit être testée localement (`mkdocs serve`)
- ✅ Rebuild requis après migration (`mkdocs build`)
- ✅ Redeploy sur VPS nécessaire
- ❌ Ne JAMAIS casser liens existants sans redirect

### Stratégie de Migration

**Approche recommandée**: Migration par batch
1. **Batch 1**: Fixer 10 liens cassés urgents (today)
2. **Batch 2**: Migrer remaining AI/ML services
3. **Batch 3**: Migrer monitoring services
4. **Batch 4**: Migrer collaboration services
5. **Batch 5**: Consolidation applications + guides
6. **Batch 6**: Nettoyage final

**Entre chaque batch**:
- Commit + push
- Test local
- Rebuild site
- Deploy
- Vérifier site live

---

## 📝 Checklist Exécution

### Batch 1: Fixer liens cassés (URGENT)

- [ ] Migrer `02-applications/ai-transcription/faster-whisper.md` → `services/`
- [ ] Migrer `02-applications/ai-services/ollama.md` → `services/`
- [ ] Migrer `02-applications/monitoring/monitoring-stack.md` → `services/`
- [ ] Migrer `02-applications/monitoring/dashy.md` → `services/`
- [ ] Migrer `02-applications/collaboration/nextcloud.md` → `services/`
- [ ] Migrer `02-applications/collaboration/jitsi.md` → `services/`
- [ ] Migrer `02-applications/collaboration/rocketchat.md` → `services/`
- [ ] Créer `services/memvid.md` (nouveau)
- [ ] Retirer `services/rag-anything.md` du mkdocs.yml (n'existe pas)
- [ ] Corriger `services/docker-autostart.md` → pointer vers operations
- [ ] Test local: `mkdocs serve`
- [ ] Commit + push
- [ ] Rebuild: `mkdocs build`
- [ ] Deploy sur VPS
- [ ] Vérifier site live

### Batch 2-6: À planifier après Batch 1

---

## 🔧 Commandes Utiles

```bash
# Test local
cd /path/to/Hostinger
mkdocs serve

# Build
mkdocs build

# Vérifier liens cassés
find docs/docs -name "*.md" -exec grep -l "02-applications" {} \;

# Compter fichiers par répertoire
find docs/docs/02-applications -name "*.md" | wc -l
```

---

## 📅 Timeline Estimée

- **Batch 1** (urgent): 30-45 min
- **Batch 2-4**: 1-2h total
- **Batch 5**: 2-3h (guides nombreux)
- **Batch 6**: 30 min

**Total**: ~5h de travail étalé sur plusieurs jours

---

## ✅ Validation Post-Migration

- [ ] Site accessible: https://docs.srv759970.hstgr.cloud/
- [ ] Aucun lien cassé (404)
- [ ] Navigation cohérente
- [ ] Search fonctionne
- [ ] Anciens URLs redirigent (si nécessaire)
- [ ] Ancienne structure nettoyée
- [ ] Git history propre
- [ ] README mis à jour

---

**Next Step**: Exécuter Batch 1 pour fixer liens cassés urgents
