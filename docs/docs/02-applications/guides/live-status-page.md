# Live Services Status - Documentation

## Vue d'Ensemble

Le système **Live Services Status** génère automatiquement une page de documentation listant en temps réel l'état de tous les services Docker déployés sur srv759970.

### Accès Rapide

- **📄 Page Live:** [Services Status](/SERVICES_STATUS/)
- **🎯 Dashy Portal:** [https://dashy.srv759970.hstgr.cloud](https://dashy.srv759970.hstgr.cloud)
- **📊 Grafana:** [https://monitoring.srv759970.hstgr.cloud](https://monitoring.srv759970.hstgr.cloud)

## Fonctionnalités

### 📊 Statistiques en Temps Réel

- **Total containers** - Nombre total de conteneurs Docker
- **Containers actifs** - Services en cours d'exécution
- **Containers arrêtés** - Services désactivés
- **Horodatage** - Dernière mise à jour

### 📦 Liste Complète des Services

Pour chaque service Docker:
- ✅ **Nom du container**
- ✅ **Status** (🟢 running, 🔴 stopped, 🟡 restarting)
- ✅ **Uptime** - Temps depuis le démarrage
- ✅ **Ports** - Ports exposés et mappings

### 💻 Ressources Système

- **RAM** - Utilisation et pourcentage
- **Disque** - Espace utilisé et pourcentage
- **Top Consommateurs** - 10 containers utilisant le plus de RAM

## Architecture

```
┌─────────────────────────────────────────────────────┐
│         Cron Job (toutes les 5 minutes)             │
│                                                     │
│   */5 * * * * generate-services-status-simple.sh   │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ Collecte données
                  ▼
┌─────────────────────────────────────────────────────┐
│              Docker Engine API                      │
│                                                     │
│  • docker ps -a (tous les containers)              │
│  • docker stats (ressources)                       │
│  • docker inspect (health checks)                  │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ Génération
                  ▼
┌─────────────────────────────────────────────────────┐
│         docs/SERVICES_STATUS.md                     │
│                                                     │
│  • Markdown formaté                                │
│  • Tableaux de données                             │
│  • Badges de statut                                │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ Publication
                  ▼
┌─────────────────────────────────────────────────────┐
│            MkDocs Material                          │
│                                                     │
│  https://docs.srv759970.hstgr.cloud/               │
│  SERVICES_STATUS/                                   │
└─────────────────────────────────────────────────────┘
```

## Configuration

### Script de Génération

**Emplacement:** `/root/hostinger/scripts/generate-services-status-simple.sh`

**Permissions:**
```bash
-rwxr-xr-x 1 root root 4.5K Oct 23 18:50 generate-services-status-simple.sh
```

### Cron Job

**Configuration actuelle:**
```bash
*/5 * * * * cd /root/hostinger && ./scripts/generate-services-status-simple.sh >> /var/log/services-status.log 2>&1
```

**Vérifier le cron:**
```bash
crontab -l | grep services-status
```

### Fichier de Sortie

**Emplacement:** `/root/hostinger/docs/SERVICES_STATUS.md`

**Format:** Markdown compatible MkDocs Material

## Utilisation

### Mise à Jour Manuelle

**Méthode 1 - Alias:**
```bash
update-services-status
```

**Méthode 2 - Commande complète:**
```bash
cd /root/hostinger && ./scripts/generate-services-status-simple.sh
```

### Visualisation

**1. Via MkDocs (recommandé):**
- Accéder à [https://docs.srv759970.hstgr.cloud/SERVICES_STATUS/](https://docs.srv759970.hstgr.cloud/SERVICES_STATUS/)
- Navigation: "🚀 Services Status (Live)"

**2. Via fichier brut:**
```bash
cat /root/hostinger/docs/SERVICES_STATUS.md
```

**3. Via less (pour scroll):**
```bash
less /root/hostinger/docs/SERVICES_STATUS.md
```

### Consultation des Logs

**Logs en temps réel:**
```bash
tail -f /var/log/services-status.log
```

**Dernières exécutions:**
```bash
tail -50 /var/log/services-status.log
```

**Rechercher les erreurs:**
```bash
grep -i error /var/log/services-status.log
```

## Personnalisation

### Modifier l'Intervalle de Mise à Jour

**Éditer le cron:**
```bash
crontab -e
```

**Exemples d'intervalles:**

```bash
# Toutes les minutes (très fréquent)
*/1 * * * * cd /root/hostinger && ./scripts/generate-services-status-simple.sh >> /var/log/services-status.log 2>&1

# Toutes les 10 minutes (recommandé pour réduire la charge)
*/10 * * * * cd /root/hostinger && ./scripts/generate-services-status-simple.sh >> /var/log/services-status.log 2>&1

# Toutes les 30 minutes (léger)
*/30 * * * * cd /root/hostinger && ./scripts/generate-services-status-simple.sh >> /var/log/services-status.log 2>&1

# Toutes les heures
0 * * * * cd /root/hostinger && ./scripts/generate-services-status-simple.sh >> /var/log/services-status.log 2>&1
```

### Ajouter des Catégories Personnalisées

Éditer le script pour mapper des containers à des catégories:

```bash
vim /root/hostinger/scripts/generate-services-status-simple.sh
```

### Filtrer Certains Containers

Pour exclure certains containers de la liste:

```bash
# Dans le script, modifier la ligne docker ps
docker ps -a --format '{{.Names}}|{{.Status}}|{{.Ports}}' | grep -v "unwanted-container" | sort
```

## Monitoring & Alertes

### Vérifier que le Script Fonctionne

**Test 1 - Dernière modification:**
```bash
stat /root/hostinger/docs/SERVICES_STATUS.md | grep Modify
```

**Test 2 - Exécution manuelle:**
```bash
cd /root/hostinger && ./scripts/generate-services-status-simple.sh
# Doit afficher: ✅ Services status page generated
```

**Test 3 - Vérifier le cron:**
```bash
grep CRON /var/log/syslog | grep services-status | tail -5
```

### Alertes sur Échecs

**Option 1 - Email sur erreur:**

Modifier le cron pour envoyer un email en cas d'erreur:

```bash
MAILTO=your-email@example.com
*/5 * * * * cd /root/hostinger && ./scripts/generate-services-status-simple.sh >> /var/log/services-status.log 2>&1 || echo "Services status generation failed"
```

**Option 2 - Webhook Discord/Slack:**

Ajouter à la fin du script:

```bash
# En cas d'erreur
if [ $? -ne 0 ]; then
    curl -X POST https://your-webhook-url \
        -H "Content-Type: application/json" \
        -d '{"content":"❌ Services status generation failed!"}'
fi
```

## Intégrations

### Grafana Dashboard

Créer un dashboard Grafana affichant les métriques:

1. **Panel "Total Containers"** - Nombre total de containers
2. **Panel "Services Status"** - Répartition actifs/arrêtés
3. **Panel "RAM Usage"** - Top consommateurs
4. **Panel "Generation Time"** - Temps d'exécution du script

### API REST

Exposer les données via une API:

```bash
# Convertir markdown en JSON
cat docs/SERVICES_STATUS.md | \
  python3 -c "import json; import sys; print(json.dumps({'status': 'ok'}))" \
  > /var/www/html/services-status.json
```

Accessible via: `http://srv759970.hstgr.cloud/services-status.json`

### Dashy Widget

Intégrer dans Dashy pour affichage visuel:

```yaml
# /opt/dashy/conf.yml
widgets:
  - type: iframe
    options:
      url: https://docs.srv759970.hstgr.cloud/SERVICES_STATUS/
      height: 600
```

## Dépannage

### Le Script ne S'exécute pas

**1. Vérifier les permissions:**
```bash
ls -l /root/hostinger/scripts/generate-services-status-simple.sh
chmod +x /root/hostinger/scripts/generate-services-status-simple.sh
```

**2. Vérifier le cron:**
```bash
# Service cron actif?
systemctl status cron

# Redémarrer si nécessaire
systemctl restart cron
```

**3. Vérifier les logs:**
```bash
tail -100 /var/log/services-status.log
journalctl -u cron -f
```

### Le Fichier n'est pas Généré

**1. Vérifier le répertoire:**
```bash
ls -la /root/hostinger/docs/
mkdir -p /root/hostinger/docs
```

**2. Tester Docker:**
```bash
docker ps
# Doit lister les containers
```

**3. Exécuter avec debug:**
```bash
cd /root/hostinger
bash -x ./scripts/generate-services-status-simple.sh
```

### Les Données ne Sont pas à Jour

**1. Vérifier l'horodatage:**
```bash
head -10 /root/hostinger/docs/SERVICES_STATUS.md | grep "Dernière mise à jour"
```

**2. Forcer une mise à jour:**
```bash
update-services-status
```

**3. Vérifier le cache MkDocs:**
```bash
# Rebuild MkDocs si déployé
cd /path/to/mkdocs && mkdocs build --clean
```

## Performance

### Temps d'Exécution

**Mesure:**
```bash
time ./scripts/generate-services-status-simple.sh
```

**Temps moyen:** ~2-3 secondes pour 64 containers

### Optimisations

**1. Réduire la fréquence:**
- Passer de 5 minutes à 10 minutes

**2. Cache Docker:**
```bash
# Utiliser le cache Docker stats
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}" > /tmp/docker-stats.cache
```

**3. Génération asynchrone:**
```bash
# Générer en arrière-plan
nohup ./scripts/generate-services-status-simple.sh &
```

## Sécurité

### Permissions

**Script:**
```bash
chmod 700 /root/hostinger/scripts/generate-services-status-simple.sh
chown root:root /root/hostinger/scripts/generate-services-status-simple.sh
```

**Fichier de sortie:**
```bash
chmod 644 /root/hostinger/docs/SERVICES_STATUS.md
```

### Logs

**Rotation des logs:**
```bash
# /etc/logrotate.d/services-status
/var/log/services-status.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

## Voir Aussi

- [Dashy Portal](../../../services/infrastructure/dashy-portal.md) - Dashboard visuel
- [Monitoring Stack](../../../services/infrastructure/monitoring.md) - Grafana + Prometheus
- [Dozzle](../../../services/infrastructure/dozzle.md) - Logs Docker temps réel
- [Portainer](../../../services/infrastructure/portainer.md) - Gestion Docker GUI

## Ressources

- **Script:** `/root/hostinger/scripts/generate-services-status-simple.sh`
- **Documentation:** `/root/hostinger/scripts/README.md`
- **Logs:** `/var/log/services-status.log`
- **Sortie:** `/root/hostinger/docs/SERVICES_STATUS.md`

---

**Dernière mise à jour:** 2025-10-23
**Status:** ✅ Production
**Maintenance:** Automatique via cron
