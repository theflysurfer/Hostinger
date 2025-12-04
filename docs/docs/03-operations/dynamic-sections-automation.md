# Automatisation Sections Dynamiques

Guide pour automatiser la mise à jour des sections dynamiques de la documentation.

---

## 📋 Vue d'Ensemble

Les sections dynamiques (`99-dynamic/`) affichent l'état temps réel du serveur :
- `server-status.md` - CPU, RAM, disque, uptime
- `services-status.md` - État des conteneurs Docker

---

## 🔄 Script de Mise à Jour

**Emplacement** : `scripts/update-dynamic-sections.sh`

### Utilisation Manuelle

```bash
# Depuis Windows (local)
cd "C:\Users\JulienFernandez\OneDrive\Coding\_référentiels de code\Hostinger"
bash scripts/update-dynamic-sections.sh

# Rebuild MkDocs
cd new-docs
mkdocs build
```

### Automatisation Locale (Windows)

**Option 1 : Task Scheduler Windows**

1. Ouvrir Task Scheduler
2. Create Basic Task :
   - Name : "Update Hostinger Docs Dynamic Sections"
   - Trigger : Daily at 8:00 AM
   - Action : Start a program
     - Program : `C:\Program Files\Git\bin\bash.exe`
     - Arguments : `-c "cd 'C:\Users\JulienFernandez\OneDrive\Coding\_référentiels de code\Hostinger' && bash scripts/update-dynamic-sections.sh"`

**Option 2 : PowerShell Script**

Créer `update-docs-daily.ps1` :

```powershell
$repoPath = "C:\Users\JulienFernandez\OneDrive\Coding\_référentiels de code\Hostinger"
cd $repoPath

# Update dynamic sections
bash scripts/update-dynamic-sections.sh

# Rebuild MkDocs
cd new-docs
mkdocs build

# Optional: Commit changes
git add docs/99-dynamic/
git commit -m "docs: auto-update dynamic sections $(Get-Date -Format 'yyyy-MM-dd')"
```

Planifier avec Task Scheduler pointant vers ce script PowerShell.

---

## 🖥️ Automatisation Serveur (Option Avancée)

Si MkDocs est déployé sur le serveur, automatiser directement là-bas.

### Script Serveur

`/opt/mkdocs/update-status.sh` :

```bash
#!/bin/bash
# Run on server to update status pages

DOCS_DIR="/opt/mkdocs/docs/99-dynamic"

# Server Status
cat > "$DOCS_DIR/server-status.md" << 'EOF'
# Server Status

**Dernière mise à jour** : $(date '+%Y-%m-%d %H:%M:%S')

## System Info
\`\`\`
$(free -h)
$(df -h)
$(uptime)
\`\`\`
EOF

# Services Status
cat > "$DOCS_DIR/services-status.md" << 'EOF'
# Services Status

\`\`\`
$(docker ps --format 'table {{.Names}}\t{{.Status}}')
\`\`\`
EOF

# Rebuild
cd /opt/mkdocs
mkdocs build
```

### Cron Job Serveur

```bash
# Edit crontab
crontab -e

# Add line for daily update at 6 AM
0 6 * * * /opt/mkdocs/update-status.sh >> /var/log/mkdocs-update.log 2>&1
```

---

## 📊 Vérification

Après mise à jour :

```bash
# Check files were updated
ls -lah new-docs/docs/99-dynamic/

# Verify content
cat new-docs/docs/99-dynamic/server-status.md
```

---

## 🎯 Fréquence Recommandée

- **Développement** : Manuel (on-demand)
- **Production** : Quotidien (6 AM serveur / 8 AM local)

---

## 📝 Notes

- Le script utilise SSH vers `root@69.62.108.82`
- Nécessite clé SSH configurée sans passphrase pour automation
- Les sections dynamiques ne sont PAS versionnées dans Git (optionnel)
- Utile surtout si doc déployée en production

---

**Créé** : 2025-10-28
**Dernière révision** : 2025-10-28
