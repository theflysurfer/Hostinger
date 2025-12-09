# Scripts de Maintenance

Scripts organisés pour la maintenance du serveur Hostinger srv759970.

---

## 📂 Structure

### docker-cleanup/
Scripts pour le nettoyage et l'audit des ressources Docker.

**Scripts disponibles**:
- `docker-analyze-images.sh` - Analyse les images Docker
- `docker-audit-complete.sh` - Audit complet des conteneurs et images
- `docker-cleanup-images.sh` - Nettoyage des images inutilisées
- `docker-final-cleanup.sh` - Nettoyage final (dangling images, volumes)
- `docker-images-report.py` - Rapport détaillé des images Python

### space-analysis/
Scripts pour l'analyse et le monitoring de l'espace disque.

**Scripts disponibles**:
- `docker-monitor-space.sh` - Monitoring continu de l'espace Docker

### backup/
Scripts pour les sauvegardes serveur.

**Scripts à venir**:
- Backup configurations
- Backup databases
- Backup volumes

---

## 🚀 Usage

### Nettoyage Docker

```bash
# Audit complet des ressources
cd /path/to/scripts/maintenance/docker-cleanup
./docker-audit-complete.sh

# Nettoyage images inutilisées
./docker-cleanup-images.sh

# Nettoyage final
./docker-final-cleanup.sh
```

### Monitoring Espace

```bash
cd /path/to/scripts/maintenance/space-analysis
./docker-monitor-space.sh
```

---

## 📋 Maintenance Recommandée

### Hebdomadaire (chaque lundi)
```bash
# Audit rapide
./docker-cleanup/docker-audit-complete.sh

# Si espace < 20 GB: cleanup
./docker-cleanup/docker-cleanup-images.sh
```

### Mensuel (1er du mois)
```bash
# Nettoyage complet
./docker-cleanup/docker-final-cleanup.sh

# Rapport d'analyse
./docker-cleanup/docker-images-report.py
```

---

## 🔗 Voir Aussi

- **Hostinger Infrastructure Skills**: `~/.claude/skills/hostinger-*`
- **Operations Docs**: `docs/operations/`
- **Emergency Runbook**: `docs/operations/emergency-runbook.md`

---

**Last updated**: 2025-12-09
