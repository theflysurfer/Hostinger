# Dozzle

**URL**: https://dozzle.srv759970.hstgr.cloud
**Port interne**: 8888
**Statut**: ✅ Opérationnel ✅ **Sécurisé avec Basic Auth**

---

## Vue d'ensemble

Dozzle est une interface web légère et temps réel pour visualiser les logs Docker. Alternative moderne à `docker logs`, avec interface graphique intuitive et recherche en temps réel.

### Fonctionnalités principales

- **Logs temps réel** : Streaming live de tous les conteneurs
- **Multi-conteneurs** : Vue simultanée de plusieurs conteneurs
- **Recherche** : Filtrage et recherche dans les logs
- **Dark mode** : Interface moderne et agréable
- **Lightweight** : < 10MB, consommation RAM minimale
- **Zero configuration** : Détection automatique de tous les conteneurs

---

## Architecture

```
Dozzle (port 8888)
    ↓
Nginx (HTTPS + Basic Auth)
    ↓
/var/run/docker.sock (ro)
    ↓
Lecture logs de tous les conteneurs Docker
```

### Conteneur

- **dozzle** : Application Dozzle complète (web UI + Docker API)

---

## Configuration

### Emplacement

- **Conteneur** : `dozzle`
- **Image** : `amir20/dozzle:latest`
- **Port** : `0.0.0.0:8888` (exposé publiquement, sécurisé par Nginx)

### Volumes montés

```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock:ro
```

**Note** : Accès read-only au socket Docker pour lire les logs (pas de modifications possibles).

### Configuration Nginx

```nginx
# /etc/nginx/sites-available/dozzle
server {
    listen 443 ssl http2;
    server_name dozzle.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/dozzle.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dozzle.srv759970.hstgr.cloud/privkey.pem;

    access_log /var/log/nginx/dozzle-access.log;
    error_log /var/log/nginx/dozzle-error.log;

    location / {
        include snippets/basic-auth.conf;

        proxy_pass http://127.0.0.1:8888;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support pour streaming temps réel
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## Utilisation

### Accès Web UI

**URL** : https://dozzle.srv759970.hstgr.cloud

**Authentification** : Basic Auth (credentials configurés dans Nginx)

### Navigation principale

#### Page d'accueil

- Liste de **tous les conteneurs** Docker actifs
- Statut (running, stopped)
- Uptime
- Bouton pour accéder aux logs

#### Visualisation logs

1. Cliquer sur un conteneur
2. Logs s'affichent en temps réel (auto-scroll)
3. Utiliser la **barre de recherche** en haut pour filtrer
4. Cliquer sur **Pause** pour arrêter l'auto-scroll

#### Fonctionnalités avancées

**Multi-conteneurs** :
- Maintenir `Ctrl` (Windows/Linux) ou `Cmd` (Mac)
- Cliquer sur plusieurs conteneurs
- Les logs se mélangent chronologiquement

**Recherche** :
- Taper dans la barre de recherche
- Logs filtrés instantanément
- Expressions régulières supportées

**Download logs** :
- Bouton "Download" pour télécharger les logs au format texte

---

## Administration

### Vérifier le conteneur

```bash
# Statut
docker ps --filter name=dozzle

# Logs Dozzle lui-même
docker logs dozzle --tail 100

# Stats ressources
docker stats dozzle
```

### Redémarrer

```bash
docker restart dozzle
```

### Vérifier accès Docker socket

```bash
# Dozzle doit avoir accès au socket Docker
docker exec dozzle ls -la /var/run/docker.sock

# Output attendu: srw-rw---- 1 root docker 0 ... /var/run/docker.sock
```

---

## Sécurité

### État actuel

- ✅ HTTPS avec Let's Encrypt (certificat expire 2026-01-19)
- ✅ Basic Auth Nginx (protection par mot de passe)
- ✅ Accès Docker socket en read-only
- ✅ Pas d'accès direct au port 8888 (proxy Nginx uniquement)

### Bonnes pratiques

#### Gestion des credentials Basic Auth

```bash
# Changer le mot de passe Basic Auth
htpasswd -c /etc/nginx/.htpasswd username

# Redémarrer Nginx
systemctl reload nginx
```

#### Limiter accès par IP (optionnel)

```nginx
# Dans /etc/nginx/sites-available/dozzle
location / {
    # Autoriser uniquement certaines IPs
    allow 203.0.113.0/24;
    deny all;

    include snippets/basic-auth.conf;
    proxy_pass http://127.0.0.1:8888;
}
```

---

## Cas d'usage

### 1. Debugging en temps réel

**Scénario** : Un service Docker plante aléatoirement

**Solution** :
1. Ouvrir Dozzle
2. Sélectionner le conteneur problématique
3. Attendre le crash
4. Logs disponibles immédiatement (pas besoin de SSH)

### 2. Monitoring déploiement

**Scénario** : Déploiement d'un nouveau service

**Solution** :
1. Ouvrir Dozzle
2. Sélectionner le nouveau conteneur
3. Vérifier que le service démarre correctement
4. Identifier rapidement les erreurs de config

### 3. Support utilisateur

**Scénario** : Un utilisateur signale un problème

**Solution** :
1. Partager l'accès Dozzle (temporaire)
2. L'utilisateur peut voir les logs en temps réel
3. Pas besoin de SSH ou accès serveur

---

## Comparaison avec alternatives

| Feature | Dozzle | Portainer Logs | Loki + Grafana |
|---------|--------|----------------|----------------|
| **Temps réel** | ✅ Oui | ✅ Oui | ⚠️ Délai ~5s |
| **Multi-conteneurs** | ✅ Oui | ❌ Non | ✅ Oui |
| **Recherche** | ✅ Basique | ✅ Basique | ✅ Avancée (LogQL) |
| **Historique** | ⚠️ Limité | ⚠️ Limité | ✅ Illimité |
| **Installation** | ✅ 1 conteneur | ⚠️ Stack complète | ❌ Stack complexe |
| **Ressources** | ✅ < 10MB | ⚠️ ~100MB | ❌ > 500MB |
| **Dashboards** | ❌ Non | ❌ Non | ✅ Grafana |

**Recommandation** : Utiliser Dozzle **ET** Loki/Grafana en complémentarité :
- **Dozzle** : Debugging rapide, logs temps réel, simplicité
- **Loki/Grafana** : Historique long terme, dashboards, alerting

---

## Troubleshooting

### Problème : Page blanche ou erreur 502

**Symptôme** : Dozzle inaccessible via Nginx

**Solution** :
```bash
# Vérifier que Dozzle tourne
docker ps --filter name=dozzle

# Vérifier logs Dozzle
docker logs dozzle --tail 50

# Vérifier Nginx
nginx -t
systemctl status nginx

# Redémarrer Dozzle
docker restart dozzle
```

### Problème : Conteneurs manquants dans la liste

**Symptôme** : Certains conteneurs ne s'affichent pas dans Dozzle

**Solution** :
```bash
# Vérifier accès Docker socket
docker exec dozzle ls -la /var/run/docker.sock

# Si erreur, recréer conteneur avec bon volume
docker stop dozzle
docker rm dozzle
docker run -d --name dozzle \
  --restart unless-stopped \
  -p 0.0.0.0:8888:8080 \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  amir20/dozzle:latest
```

### Problème : Logs ne se rafraîchissent pas

**Symptôme** : Logs figés, pas de streaming temps réel

**Solution** :
1. Vérifier WebSocket fonctionne (F12 → Network → WS)
2. Vérifier configuration Nginx (`Upgrade` et `Connection` headers)
3. Rafraîchir la page (Ctrl+F5)

---

## Fonctionnalités avancées

### Variables d'environnement

Dozzle supporte plusieurs options de configuration via variables d'environnement :

```bash
docker run -d --name dozzle \
  -p 8888:8080 \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -e DOZZLE_LEVEL=info \
  -e DOZZLE_FILTER="name=app" \
  -e DOZZLE_ENABLE_ACTIONS=true \
  amir20/dozzle:latest
```

**Variables utiles** :
- `DOZZLE_LEVEL` : Niveau de logs Dozzle (`debug`, `info`, `warn`, `error`)
- `DOZZLE_FILTER` : Filtre containers (ex: `name=nginx|mysql`)
- `DOZZLE_ENABLE_ACTIONS` : Activer boutons start/stop/restart (⚠️ dangereux)

### Mode multi-host

Dozzle peut surveiller plusieurs hôtes Docker :

```bash
docker run -d --name dozzle \
  -p 8888:8080 \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -e DOZZLE_REMOTE_HOST=tcp://remote-docker:2375 \
  amir20/dozzle:latest
```

---

## Performance

### Ressources

- **CPU** : < 1% en moyenne
- **RAM** : ~8-12 MB
- **Disk** : Aucun stockage (lecture directe Docker)

### Optimisations

Dozzle est déjà ultra-optimisé. Aucune optimisation nécessaire.

---

## Intégration avec autres outils

### Lien vers Grafana

Ajouter un lien dans Dozzle vers Grafana pour une vue complète :

1. Dans Dozzle, copier le nom du conteneur
2. Ouvrir Grafana → Explore
3. Chercher dans Loki : `{container_name="nom_conteneur"}`

### Webhooks

Dozzle ne supporte pas nativement les webhooks, mais peut être couplé avec un script :

```bash
# Exemple: Alerte si erreur critique détectée
docker logs -f nom_conteneur | grep -i "ERROR" | while read line; do
  curl -X POST https://chat.srv759970.hstgr.cloud/hooks/WEBHOOK_ID \
    -d "{\"text\": \"Erreur détectée: $line\"}"
done
```

---

## Liens utiles

- **GitHub** : https://github.com/amir20/dozzle
- **Documentation** : https://dozzle.dev
- **Docker Hub** : https://hub.docker.com/r/amir20/dozzle
- **Release notes** : https://github.com/amir20/dozzle/releases

---

**Dernière mise à jour** : 2025-10-21
**Version Dozzle** : latest
**Container** : `dozzle`
**Certificat SSL** : Expire 2026-01-19
