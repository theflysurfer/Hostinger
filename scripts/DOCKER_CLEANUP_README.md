# Scripts de Gestion des Images Docker

Scripts pour analyser, surveiller et nettoyer les images Docker sur le serveur.

## Vue d'ensemble

Ces scripts permettent de gérer efficacement l'espace disque utilisé par Docker en identifiant et nettoyant les images inutilisées.

### Problème identifié

Sur le serveur `69.62.108.82`, nous avons détecté :
- **33 images "dangling"** (sans tag `<none>:<none>`)
- **~42 GB d'espace gaspillé** par des anciennes images inutilisées
- Plusieurs grosses images de 6-7 GB chacune (probablement des builds de paperflow, memvid, whisperx)

## Scripts disponibles

### 1. `docker-analyze-images.sh` - Analyse détaillée

Analyse complète de toutes les images Docker et génère un rapport.

```bash
ssh hostinger-automation "./docker-analyze-images.sh"
```

**Fonctionnalités :**
- Affiche un résumé de l'utilisation de l'espace Docker
- Liste toutes les images dangling (sans tag)
- Identifie les images non utilisées par aucun conteneur
- Groupe les images par projet
- Affiche le top 10 des plus grosses images
- Calcule l'espace récupérable

**Sortie exemple :**
```
=========================================
  Analyse des Images Docker
=========================================

[1/6] Résumé de l'utilisation de l'espace Docker
...
Images dangling: 33
Espace total occupé: ~42 GB
```

---

### 2. `docker-cleanup-images.sh` - Nettoyage sécurisé

Nettoie les images Docker avec plusieurs modes de sécurité.

```bash
# Mode safe (par défaut) - Nettoie uniquement les images dangling
ssh hostinger-automation "./docker-cleanup-images.sh"
ssh hostinger-automation "./docker-cleanup-images.sh safe"

# Mode unused - Nettoie toutes les images inutilisées
ssh hostinger-automation "./docker-cleanup-images.sh unused"

# Mode aggressive - Nettoyage complet (images, conteneurs, volumes, cache)
ssh hostinger-automation "./docker-cleanup-images.sh aggressive"

# Simulation (dry-run) - Affiche ce qui serait supprimé
ssh hostinger-automation "./docker-cleanup-images.sh dry-run"
```

**Modes disponibles :**

| Mode | Description | Sécurité | Espace récupéré |
|------|-------------|----------|-----------------|
| `safe` | Images dangling uniquement | ✅ Très sûr | ~42 GB |
| `unused` | Toutes les images inutilisées | ⚠️ Modéré | Variable |
| `aggressive` | Images + conteneurs + volumes + cache | ❌ Risqué | Maximum |
| `dry-run` | Simulation sans suppression | ✅ Aucun risque | 0 GB |

**Recommandations :**
- Commencez toujours par `dry-run` pour voir ce qui serait supprimé
- Utilisez `safe` pour un nettoyage régulier (recommandé chaque semaine)
- `unused` uniquement si vous êtes sûr des images à garder
- `aggressive` uniquement en cas d'urgence d'espace disque

---

### 3. `docker-monitor-space.sh` - Surveillance continue

Surveille l'utilisation de l'espace Docker et génère des alertes.

```bash
ssh hostinger-automation "./docker-monitor-space.sh"
```

**Fonctionnalités :**
- Surveille l'espace disque utilisé par Docker
- Génère des alertes si l'espace dépasse :
  - **Seuil WARNING :** 50 GB
  - **Seuil CRITICAL :** 100 GB
- Enregistre l'historique dans `/var/log/docker-monitoring/docker-space.log`
- Affiche l'évolution dans le temps
- Propose des actions correctives

**Automatisation (optionnel) :**

Pour surveiller automatiquement chaque jour :

```bash
# Sur le serveur, ajouter à crontab
crontab -e

# Ajouter cette ligne pour exécuter chaque jour à 9h
0 9 * * * /home/automation/docker-monitor-space.sh >> /var/log/docker-monitoring/monitor.log 2>&1
```

---

### 4. `docker-images-report.py` - Rapport détaillé (Python)

Génère un rapport détaillé au format texte ou JSON.

```bash
# Rapport texte
ssh hostinger-automation "python3 ./docker-images-report.py"

# Rapport JSON
ssh hostinger-automation "python3 ./docker-images-report.py --json" > docker-report.json

# Aide
ssh hostinger-automation "python3 ./docker-images-report.py --help"
```

**Fonctionnalités :**
- Analyse détaillée avec calculs précis
- Export JSON pour intégration avec d'autres outils
- Statistiques par projet
- Identification des images orphelines
- Top 10 des plus grosses images

**Exemple de rapport JSON :**
```json
{
  "timestamp": "2025-11-09T07:00:00",
  "statistics": {
    "total_images": 106,
    "dangling_count": 33,
    "unused_count": 15,
    "total_size_gb": 85.5,
    "dangling_size_gb": 42.3
  },
  "dangling_images": [...],
  "unused_images": [...]
}
```

---

## Installation sur le serveur

### 1. Copier les scripts sur le serveur

```bash
# Depuis votre machine locale
scp scripts/docker-*.sh hostinger-automation:~/
scp scripts/docker-images-report.py hostinger-automation:~/
```

### 2. Rendre les scripts exécutables

```bash
ssh hostinger-automation "chmod +x docker-*.sh docker-images-report.py"
```

### 3. Créer le répertoire de logs

```bash
ssh hostinger-automation "sudo mkdir -p /var/log/docker-monitoring && sudo chown automation:automation /var/log/docker-monitoring"
```

---

## Workflow recommandé

### Nettoyage hebdomadaire (recommandé)

```bash
# 1. Analyser l'état actuel
ssh hostinger-automation "./docker-analyze-images.sh"

# 2. Simulation du nettoyage
ssh hostinger-automation "./docker-cleanup-images.sh dry-run"

# 3. Nettoyage sûr des images dangling
ssh hostinger-automation "./docker-cleanup-images.sh safe"

# 4. Vérifier le résultat
ssh hostinger-automation "docker system df"
```

### En cas d'urgence (espace critique)

```bash
# 1. Vérifier l'état
ssh hostinger-automation "./docker-monitor-space.sh"

# 2. Nettoyage progressif
ssh hostinger-automation "./docker-cleanup-images.sh safe"
ssh hostinger-automation "./docker-cleanup-images.sh unused"

# 3. Si toujours critique
ssh hostinger-automation "./docker-cleanup-images.sh aggressive"
```

---

## Exemples d'utilisation

### Exemple 1 : Analyse initiale

```bash
$ ssh hostinger-automation "./docker-analyze-images.sh"

=========================================
  Analyse des Images Docker
=========================================

[2/6] Images dangling (sans tag - <none>:<none>)
=========================================
Nombre d'images dangling: 33

Espace total occupé par les images dangling: 42000.00 MB
```

### Exemple 2 : Nettoyage sûr

```bash
$ ssh hostinger-automation "./docker-cleanup-images.sh safe"

=========================================
  Nettoyage des Images Docker
=========================================

Mode: SAFE - Nettoyage des images dangling uniquement
=========================================
Images dangling à supprimer: 33

Voulez-vous supprimer ces images dangling ? (y/N): y
Suppression des images dangling...
Deleted Images:
untagged: sha256:0571cc7a53b5...
untagged: sha256:7359c137a167...
...

Total reclaimed space: 42.3 GB
```

---

## Précautions importantes

### ⚠️ Avant de nettoyer

1. **Vérifiez les conteneurs actifs** : `docker ps -a`
2. **Faites une sauvegarde des données importantes** si nécessaire
3. **Testez en mode dry-run** avant tout nettoyage
4. **Documentez les images que vous voulez garder**

### ⚠️ Images à NE PAS supprimer

Certaines images peuvent sembler inutilisées mais sont nécessaires :
- Images de base (alpine, ubuntu, python, node, etc.)
- Images utilisées par des conteneurs temporaires
- Images nécessaires aux rebuilds

### ⚠️ Mode aggressive

Le mode `aggressive` supprime :
- ❌ **Toutes** les images non utilisées
- ❌ **Tous** les conteneurs arrêtés
- ❌ **Tous** les volumes orphelins
- ❌ **Tout** le cache de build

**N'utilisez ce mode que si vous savez ce que vous faites !**

---

## Automatisation recommandée

### Surveillance quotidienne

```bash
# Ajouter au crontab du serveur
0 9 * * * /home/automation/docker-monitor-space.sh
```

### Nettoyage hebdomadaire automatique

```bash
# Tous les dimanches à 3h du matin
0 3 * * 0 /home/automation/docker-cleanup-images.sh safe
```

### Rapport mensuel

```bash
# Premier jour du mois à 8h
0 8 1 * * /home/automation/docker-images-report.py --json > /var/log/docker-monitoring/monthly-report-$(date +\%Y-\%m).json
```

---

## Dépannage

### Problème : Permission denied

```bash
# Assurez-vous que l'utilisateur automation peut utiliser Docker
sudo usermod -aG docker automation
```

### Problème : Les scripts ne s'exécutent pas

```bash
# Vérifier les permissions
ls -la docker-*.sh
chmod +x docker-*.sh
```

### Problème : Python script ne fonctionne pas

```bash
# Vérifier Python 3
python3 --version

# Installer les dépendances si nécessaire
pip3 install --user subprocess json
```

---

## Métriques de succès

Après nettoyage des 33 images dangling, vous devriez récupérer :
- ✅ **~42 GB d'espace disque**
- ✅ Réduction du nombre d'images de ~106 à ~73
- ✅ Amélioration des performances Docker

---

## Support et documentation

- Guide Docker officiel : https://docs.docker.com/config/pruning/
- Documentation interne : `new-docs/docs/03-operations/`
- Issues : Créer un ticket dans le projet

---

**Dernière mise à jour :** 2025-11-09
**Auteur :** Claude Code
**Serveur cible :** hostinger-automation (69.62.108.82)
