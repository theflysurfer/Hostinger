# Glances

**URL**: https://glances.srv759970.hstgr.cloud
**Port interne**: 61208
**Statut**: ✅ Opérationnel ✅ **Sécurisé avec HTTPS + Basic Auth**

---

## Vue d'ensemble

Glances est un outil de monitoring système multiplateforme écrit en Python. Alternative légère à Netdata, offre une interface web temps réel pour surveiller CPU, RAM, disque, réseau et conteneurs Docker.

### Fonctionnalités principales

- **Monitoring système** : CPU, RAM, disque, réseau en temps réel
- **Monitoring Docker** : Tous les conteneurs avec métriques détaillées
- **Interface web** : Dashboard moderne et responsive
- **API REST** : Export des métriques au format JSON
- **Lightweight** : ~55MB RAM (vs Netdata ~200MB)
- **Limites de ressources** : Conteneur limité à 256MB RAM et 0.5 CPU

---

## Architecture

```
Glances (port 61208, limité 256MB RAM / 0.5 CPU)
    ↓
Nginx (HTTPS + Basic Auth)
    ↓
/var/run/docker.sock (ro)
    ↓
Lecture métriques système + Docker
```

### Conteneur

- **glances** : Application Glances complète (monitoring + web UI + API REST)

---

## Configuration

### Emplacement

- **Conteneur** : `glances`
- **Image** : `nicolargo/glances:latest`
- **Port** : `127.0.0.1:61208` (localhost uniquement, accessible via Nginx)

### Volumes montés

```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock:ro
```

**Note** : Accès read-only au socket Docker pour lire les métriques (pas de modifications possibles).

### Limites de ressources

```yaml
--memory=256m      # Limite RAM à 256MB
--cpus=0.5         # Limite CPU à 50%
```

**Raison** : Éviter la surcharge du serveur (leçon apprise avec Netdata qui a planté le serveur).

### Configuration Nginx

```nginx
# /etc/nginx/sites-available/glances
server {
    listen 443 ssl http2;
    server_name glances.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/glances.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/glances.srv759970.hstgr.cloud/privkey.pem;

    location / {
        include snippets/basic-auth.conf;

        proxy_pass http://127.0.0.1:61208;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_read_timeout 300;
    }
}
```

---

## Utilisation

### Accès Web UI

**URL** : https://glances.srv759970.hstgr.cloud

**Authentification** : Basic Auth (credentials configurés dans Nginx)

### Navigation principale

#### Dashboard principal

- **CPU** : Usage global et par cœur
- **RAM** : Total, utilisée, buffers, cache, swap
- **LOAD** : Load average 1m, 5m, 15m
- **NETWORK** : Bande passante RX/TX
- **DISK I/O** : Lecture/écriture par seconde
- **FILE SYSTEM** : Espace disque utilisé/disponible

#### Conteneurs Docker

- Liste de tous les conteneurs actifs
- CPU % par conteneur
- RAM usage par conteneur
- Network I/O par conteneur
- Uptime par conteneur

### API REST

Glances expose une API REST complète :

```bash
# Toutes les métriques (JSON)
curl -u user:pass https://glances.srv759970.hstgr.cloud/api/4/all

# CPU seulement
curl -u user:pass https://glances.srv759970.hstgr.cloud/api/4/cpu

# RAM seulement
curl -u user:pass https://glances.srv759970.hstgr.cloud/api/4/mem

# Docker containers
curl -u user:pass https://glances.srv759970.hstgr.cloud/api/4/docker
```

---

## Administration

### Vérifier le conteneur

```bash
# Statut
docker ps --filter name=glances

# Logs
docker logs glances --tail 100 -f

# Stats ressources (vérifier limites)
docker stats glances
```

### Redémarrer

```bash
docker restart glances
```

### Vérifier consommation ressources

```bash
# Glances devrait rester sous 256MB RAM et 1% CPU
docker stats glances --no-stream
```

---

## Sécurité

### État actuel

- ✅ HTTPS avec Let's Encrypt (certificat expire 2026-01-19)
- ✅ Basic Auth Nginx (protection par mot de passe)
- ✅ Accès Docker socket en read-only
- ✅ Port localhost uniquement (127.0.0.1:61208)
- ✅ Limites de ressources (256MB RAM, 0.5 CPU)

### Bonnes pratiques

#### Changer le mot de passe Basic Auth

```bash
htpasswd -c /etc/nginx/.htpasswd username
systemctl reload nginx
```

#### Limiter accès par IP (optionnel)

```nginx
location / {
    allow 203.0.113.0/24;  # Votre réseau
    deny all;

    include snippets/basic-auth.conf;
    proxy_pass http://127.0.0.1:61208;
}
```

---

## Cas d'usage

### 1. Monitoring rapide CPU/RAM

**Scénario** : Vérifier rapidement si le serveur est surchargé

**Solution** :
1. Ouvrir https://glances.srv759970.hstgr.cloud
2. Vue instantanée CPU, RAM, Load average
3. Identifier les processus/conteneurs consommant le plus

### 2. Identifier conteneur problématique

**Scénario** : Un conteneur consomme trop de ressources

**Solution** :
1. Section "DOCKER" dans Glances
2. Trier par CPU % ou RAM usage
3. Identifier le coupable immédiatement

### 3. Vérifier espace disque

**Scénario** : Le serveur manque d'espace disque

**Solution** :
1. Section "FILE SYSTEM" dans Glances
2. Voir tous les points de montage
3. Identifier les partitions pleines

---

## Comparaison avec alternatives

| Feature | Glances | Netdata | Portainer Stats | Grafana |
|---------|---------|---------|-----------------|---------|
| **Temps réel** | ✅ 1s | ✅ 1s | ✅ 2s | ⚠️ 5-15s |
| **Ressources** | ✅ ~55MB | ❌ ~200MB+ | ✅ ~100MB | ⚠️ ~200MB |
| **Docker support** | ✅ Oui | ✅ Oui | ✅ Oui | ⚠️ Via cAdvisor |
| **API REST** | ✅ Oui | ✅ Oui | ⚠️ Limitée | ✅ Oui |
| **Interface** | ✅ Simple | ✅ Complète | ⚠️ Par conteneur | ✅ Dashboards |
| **Stabilité (59 conteneurs)** | ✅ Stable | ❌ **Plantage serveur** | ✅ Stable | ✅ Stable |
| **Configuration** | ✅ Zero config | ✅ Zero config | ✅ Zero config | ❌ Complexe |

**Recommandation** : Utiliser Glances **ET** Grafana en complémentarité :
- **Glances** : Monitoring rapide, debug temps réel
- **Grafana** : Dashboards personnalisés, historique, alerting

---

## Troubleshooting

### Problème : Page blanche ou erreur 502

**Symptôme** : Glances inaccessible via Nginx

**Solution** :
```bash
# Vérifier que Glances tourne
docker ps --filter name=glances

# Vérifier logs Glances
docker logs glances --tail 50

# Vérifier Nginx
nginx -t
systemctl status nginx

# Redémarrer Glances
docker restart glances
```

### Problème : Glances consomme trop de ressources

**Symptôme** : CPU > 10% ou RAM > 256MB

**Solution** :
```bash
# Vérifier stats
docker stats glances --no-stream

# Si limite dépassée, réduire les limites
docker stop glances
docker rm glances

# Recréer avec limites plus strictes
docker run -d \
  --name glances \
  --restart unless-stopped \
  -p 127.0.0.1:61208:61208 \
  -e GLANCES_OPT='-w' \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  --pid host \
  --memory=128m \
  --cpus=0.25 \
  nicolargo/glances:latest
```

### Problème : Métriques Docker manquantes

**Symptôme** : Section "DOCKER" vide

**Solution** :
```bash
# Vérifier accès Docker socket
docker exec glances ls -la /var/run/docker.sock

# Si erreur, recréer avec bon volume
docker stop glances
docker rm glances
# Recréer (voir commande d'installation)
```

---

## Performance

### Ressources

- **CPU** : ~0.77% en moyenne
- **RAM** : ~55MB (limite 256MB)
- **Disk I/O** : Minimal (lecture /proc et /sys)

### Optimisations

Glances est déjà très optimisé. Si nécessaire :

```bash
# Désactiver certains plugins via variables d'environnement
docker run -d \
  --name glances \
  -e GLANCES_OPT='-w --disable-plugin network' \
  ...
```

---

## Intégration avec autres outils

### Export vers Prometheus

Glances peut exporter des métriques Prometheus :

```bash
# Activer export Prometheus
docker run -d \
  --name glances \
  -e GLANCES_OPT='-w --export prometheus' \
  ...
```

Puis dans Prometheus :
```yaml
scrape_configs:
  - job_name: 'glances'
    static_configs:
      - targets: ['glances:61208']
```

### Lien vers Grafana

Utiliser le datasource Prometheus avec les métriques Glances exportées.

---

## Variables d'environnement

Glances supporte de nombreuses options :

```bash
GLANCES_OPT='-w'                    # Mode web uniquement
GLANCES_OPT='-w --disable-docker'   # Désactiver monitoring Docker
GLANCES_OPT='-w --time 2'           # Rafraîchissement toutes les 2s
```

---

## Historique

### Pourquoi Glances au lieu de Netdata ?

**Incident du 2025-10-21** :
- Netdata a été installé sur srv759970 (59 conteneurs actifs)
- Netdata a provoqué un **effondrement complet des performances**
- Serveur complètement inaccessible (tous les services en timeout)
- **Reboot forcé nécessaire** pour restaurer le service
- Netdata incompatible avec un grand nombre de conteneurs

**Solution** : Glances avec limites de ressources strictes
- Limité à 256MB RAM et 0.5 CPU
- Testé stable avec 59 conteneurs
- Consommation réelle : ~55MB RAM, <1% CPU

---

## Liens utiles

- **GitHub** : https://github.com/nicolargo/glances
- **Documentation** : https://glances.readthedocs.io
- **Docker Hub** : https://hub.docker.com/r/nicolargo/glances
- **API Documentation** : https://glances.readthedocs.io/en/latest/api.html

---

**Dernière mise à jour** : 2025-10-21
**Version Glances** : latest
**Container** : `glances`
**Certificat SSL** : Expire 2026-01-19
**Consommation** : ~55MB RAM, <1% CPU
