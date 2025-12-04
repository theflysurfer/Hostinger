# 🚀 Next Steps - Après Restructuration

**Date** : 2025-10-28
**Phase Actuelle** : Phase 1 ✅ Complète

---

## ✅ Phase 1 : Structure de Base (COMPLÉTÉ)

**Durée** : 2h
**Status** : ✅ Terminé

### Ce qui a été fait
- [x] Création structure `apps/` (13 catégories)
- [x] Création structure `infrastructure/` (server, nginx, ssl)
- [x] Placeholder Nginx Manager (lien vers repo externe)
- [x] Migration documentation vers `new-docs/`
- [x] Configuration MkDocs complète (`mkdocs.yml`)
- [x] Pages principales créées (index, infrastructure, applications)
- [x] Tags prod/staging définis
- [x] Rapport de migration complet
- [x] README mis à jour

---

## 🔄 Phase 2 : Compléter la Documentation (2-3h)

**Priorité** : 🟡 Moyenne
**Timing** : Cette semaine

### 2.1 Migrer documentation restante

```bash
# Copier docs existantes vers nouvelle structure
docs/services/ai/*.md → new-docs/docs/02-applications/ai-*/
docs/services/websites/*.md → new-docs/docs/02-applications/wordpress/
docs/guides/services/*.md → new-docs/docs/02-applications/
```

**Fichiers à migrer** :
- [ ] AI Services (ollama, tika, langchain) - 6 fichiers
- [ ] Bots (telegram, discord) - 2 fichiers
- [ ] CMS Sites (cristina, impro-manager, strapi) - 4 fichiers
- [ ] Collaboration (nextcloud, rocketchat, jitsi) - 3 fichiers
- [ ] Documents (paperless, invidious) - 3 fichiers
- [ ] Automation (n8n, rustdesk) - 2 fichiers
- [ ] WordPress restants (jesuishyperphagique, panneauxsolidaires) - 2 fichiers

### 2.2 Créer pages index manquantes

- [ ] `02-applications/ai-rag/index.md`
- [ ] `02-applications/ai-transcription/index.md`
- [ ] `02-applications/ai-tts/index.md`
- [ ] `02-applications/bots/index.md`
- [ ] `02-applications/cms-sites/index.md`
- [ ] `03-operations/index.md`

### 2.3 Créer guides opérations

- [ ] `03-operations/deployment.md` - Procédures de déploiement
- [ ] `03-operations/backup.md` - Stratégie de backup
- [ ] `03-operations/troubleshooting.md` - Troubleshooting général

---

## 📊 Phase 3 : Sections Dynamiques (2h)

**Priorité** : 🟢 Faible (nice to have)
**Timing** : Semaine prochaine

### 3.1 Créer scripts de génération

**Fichier** : `new-docs/scripts/update-dynamic-sections.sh`

```bash
#!/bin/bash
# Met à jour les sections dynamiques

# System Status
ssh automation@69.62.108.82 "
  echo '# System Status' > /tmp/system-status.md
  echo '' >> /tmp/system-status.md
  echo '**RAM** : ' >> /tmp/system-status.md
  free -h >> /tmp/system-status.md
  echo '' >> /tmp/system-status.md
  echo '**Disque** : ' >> /tmp/system-status.md
  df -h >> /tmp/system-status.md
" && scp automation@69.62.108.82:/tmp/system-status.md new-docs/docs/99-dynamic/system-status.md

# Containers Status
ssh automation@69.62.108.82 "docker ps --format 'table {{.Names}}\t{{.Status}}'" > new-docs/docs/99-dynamic/containers.md

# Regenerate MkDocs
cd new-docs && mkdocs build
```

### 3.2 Automatiser avec cron

```bash
# Ajouter au crontab sur serveur
*/5 * * * * /root/scripts/update-dynamic-docs.sh
```

### 3.3 Pages dynamiques à créer

- [ ] `99-dynamic/system-status.md` - RAM, CPU, Disque
- [ ] `99-dynamic/containers.md` - Docker ps
- [ ] `99-dynamic/services-health.md` - Health checks des services
- [ ] `99-dynamic/nginx-status.md` - Sites Nginx actifs

---

## 🎨 Phase 4 : Skills Claude (1-2h)

**Priorité** : 🟡 Moyenne
**Timing** : Semaine prochaine

### 4.1 Structure skills

```
.claude/skills/
├── infrastructure/
│   ├── nginx-manager.md
│   ├── databases-manager.md
│   └── server-admin.md
├── wordpress/
│   ├── clemence.md
│   ├── solidarlink.md
│   └── shared-ops.md
├── ai-transcription/
│   ├── whisperx.md
│   └── faster-whisper.md
├── dashboards/
│   └── energie-dashboard.md
└── operations/
    ├── deploy-app.md
    ├── backup-all.md
    └── health-check.md
```

### 4.2 Skills prioritaires

**Critical** :
- [ ] `operations/health-check.md` - Check santé globale
- [ ] `infrastructure/nginx-manager.md` - Gestion Nginx (deploy, rollback)
- [ ] `operations/backup-all.md` - Backup global

**Important** :
- [ ] `wordpress/clemence.md` - Gestion WordPress Clemence
- [ ] `dashboards/energie-dashboard.md` - Projet DownTo40
- [ ] `ai-transcription/whisperx.md` - Gestion WhisperX

---

## 📦 Phase 5 : Synchronisation Apps (3-4h)

**Priorité** : 🟡 Moyenne
**Timing** : Dans 2 semaines

### 5.1 Créer script sync global

**Fichier** : `scripts/sync-all-from-server.sh`

```bash
#!/bin/bash
# Sync toutes les apps depuis /opt/

APPS=(
  "wordpress-clemence"
  "energie-40eur-dashboard"
  "whisperx"
  "ragflow"
  # ... (45 apps)
)

for app in "${APPS[@]}"; do
  echo "Syncing $app..."

  # Trouver la catégorie
  CATEGORY=$(find apps -name "$app" -type d -printf '%h\n' | head -1)

  if [ -z "$CATEGORY" ]; then
    echo "  ⚠️ Category not found for $app"
    continue
  fi

  # Sync docker-compose.yml
  scp automation@69.62.108.82:/opt/$app/docker-compose.yml $CATEGORY/$app/config/ 2>/dev/null

  # Sync .env (example only)
  scp automation@69.62.108.82:/opt/$app/.env $CATEGORY/$app/config/.env.example 2>/dev/null

  echo "  ✅ Synced to $CATEGORY/$app/"
done
```

### 5.2 Apps prioritaires à synchroniser

**Critical** (faire en premier) :
- [ ] energie-40eur-dashboard (DownTo40 🔴)
- [ ] wordpress-clemence
- [ ] databases-shared
- [ ] docker-autostart

**Important** :
- [ ] whisperx
- [ ] ragflow
- [ ] dashy
- [ ] memvid

**Faible priorité** :
- [ ] Autres apps (24 restantes)

---

## 🚀 Phase 6 : Déploiement MkDocs (1h)

**Priorité** : 🟡 Moyenne
**Timing** : Après Phase 2

### 6.1 Build et test local

```bash
cd new-docs
mkdocs serve
# Ouvrir http://localhost:8000
# Vérifier navigation complète
```

### 6.2 Déployer sur serveur

```bash
# Build
cd new-docs
mkdocs build

# Upload vers serveur
rsync -avz --delete site/ automation@69.62.108.82:/opt/mkdocs/site/

# Restart MkDocs container
ssh automation@69.62.108.82 "cd /opt/mkdocs && docker-compose restart"
```

### 6.3 Configurer Nginx

**Site** : `docs.srv759970.hstgr.cloud`

```nginx
server {
    listen 443 ssl http2;
    server_name docs.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/docs.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/docs.srv759970.hstgr.cloud/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔧 Phase 7 : Migration Nginx Manager (OPTIONNEL)

**Priorité** : 🟢 Faible
**Timing** : Quand repo Nginx Manager stabilisé

### 7.1 Critères de migration

Migrer Nginx Manager uniquement si :
- [x] Repo Nginx Manager n'a plus d'activité quotidienne
- [ ] Toutes les fonctionnalités sont stables
- [ ] Documentation complète
- [ ] Tests validés

### 7.2 Plan de migration

1. Copier contenu de `2025.10 Nginx Manager/` vers `infrastructure/nginx/`
2. Adapter chemins dans scripts
3. Tester tous les scripts
4. Mettre à jour documentation MkDocs
5. Archiver ancien repo

---

## 📋 Checklist Globale

### Structure
- [x] Apps (13 catégories)
- [x] Infrastructure (server, nginx, ssl)
- [x] Documentation MkDocs (structure)
- [ ] Skills Claude
- [ ] Scripts sync

### Documentation
- [x] Pages principales (10+)
- [ ] Pages secondaires (30+)
- [ ] Sections dynamiques (3)
- [ ] Guides opérations (3)

### Automatisation
- [ ] Scripts update sections dynamiques
- [ ] Cron auto-update
- [ ] Scripts sync apps

### Déploiement
- [ ] Build MkDocs local validé
- [ ] Déploiement serveur
- [ ] Site docs.srv759970.hstgr.cloud actif

---

## 🎯 Priorités Recommandées

### Cette Semaine
1. **Phase 2** - Compléter migration documentation (2-3h)
2. **Phase 4** - Créer skills Claude critiques (1h)

### Semaine Prochaine
3. **Phase 3** - Scripts sections dynamiques (2h)
4. **Phase 6** - Déployer MkDocs (1h)

### Dans 2 Semaines
5. **Phase 5** - Sync apps prioritaires (2h)

### Plus Tard (si besoin)
6. **Phase 7** - Migration Nginx Manager (optionnel)

---

## ✅ Quick Wins

**Actions rapides pour valider la nouvelle structure** :

1. **Tester MkDocs local** (5 min)
```bash
cd new-docs && mkdocs serve
```

2. **Créer 1 skill Claude** (15 min)
```bash
# Créer .claude/skills/operations/health-check.md
```

3. **Sync 1 app critique** (10 min)
```bash
# Sync energie-dashboard depuis serveur
scp automation@69.62.108.82:/opt/energie-40eur-dashboard/docker-compose.yml apps/11-dashboards/energie-40eur-dashboard/config/
```

---

**Status** : 🟢 Phase 1 Terminée - Prêt pour Phase 2
**Prochaine revue** : 2025-11-01
