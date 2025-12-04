# Guide Docker Auto-Start/Stop

Système automatique de démarrage et arrêt des conteneurs Docker peu utilisés pour optimiser la RAM.

## Architecture

```
Internet (HTTPS)
    ↓
Nginx (port 443) - Basic Auth
    ↓
Node.js Proxy (port 8890) - Auto-start/stop logic
    ↓
Docker Container (port variable)
```

### Fonctionnement

1. **Requête entrante** : L'utilisateur accède à https://service.srv759970.hstgr.cloud
2. **Nginx** : Vérifie basic auth, puis proxifie vers port 8890
3. **Node.js Proxy** :
   - Vérifie si conteneurs running avec `docker ps`
   - **Si arrêtés** :
     - Mode Dynamic → Affiche page d'attente HTML (auto-refresh 3s)
     - Mode Blocking → Attend silencieusement (pour APIs)
     - Lance `docker-compose start`
   - **Si running** : Proxifie directement vers le conteneur
4. **Idle checker** (toutes les minutes) :
   - Si aucune requête depuis 15 min → `docker-compose stop`

## Compatibilité avec Dashy

### ⚠️ Conflit Dashy Status Checks

**IMPORTANT :** Dashy et docker-autostart peuvent entrer en conflit si les status checks sont activés.

**Problème :**
- Les status checks Dashy génèrent des requêtes HTTP régulières (axios/1.12.0)
- Ces requêtes réinitialisent le compteur d'inactivité
- Résultat : Les services ne s'arrêtent jamais automatiquement

**Solution :**

1. **Supprimer complètement** les status checks dans Dashy :
```bash
cd /opt/dashy
sed -i '/^[[:space:]]*statusCheck: \(true\|false\)/d' conf.yml
docker-compose restart
```

2. **Exclure Dashy** de la configuration auto-stop (le laisser toujours actif)

3. Dans `conf.yml`, **NE PAS** mettre `statusCheck: false`, mais **SUPPRIMER** la ligne :
```yaml
# ❌ INCORRECT - Ne fonctionne pas (cache localStorage navigateur)
appConfig:
  statusCheck: false

# ✅ CORRECT - Supprimer la ligne complètement
appConfig:
  # statusCheck: REMOVED
```

**Référence :** [Fix complet Dashy/Auto-Stop 24/10/2025](../../changelog/dashy-autostart-fix-2025-10-24.md)

## Installation

### Prérequis

- ✅ Node.js installé
- ✅ Docker et Docker Compose
- ✅ Nginx avec HTTPS/SSL configuré

### Fichiers du système

```
/opt/docker-autostart/
├── server.js                   # Serveur Express (proxy + auto-start)
├── config.json                 # Configuration des services
├── package.json                # Dépendances npm
└── themes/                     # Pages d'attente HTML
    ├── hacker-terminal.html
    ├── ghost.html
    ├── matrix.html
    └── shuffle.html
```

### Configuration d'un nouveau service

#### 1. Ajouter dans config.json

```json
{
  "port": 8890,
  "idleTimeout": 1800,
  "services": {
    "votreservice.srv759970.hstgr.cloud": {
      "name": "Nom Affiché",
      "composeDir": "/opt/chemin-vers-service",
      "proxyPort": 8080,
      "theme": "hacker-terminal",
      "containers": ["nom-conteneur"]
    }
  }
}
```

**Paramètres** :
- `name` : Nom affiché sur la page d'attente
- `composeDir` : Chemin absolu vers le dossier docker-compose.yml
- `proxyPort` : Port du conteneur à proxifier
- `theme` : Page d'attente (hacker-terminal, ghost, matrix, shuffle)
- `containers` : Liste des noms de conteneurs (cf. `container_name:` dans docker-compose)
- `blocking` : (optionnel) `true` pour mode API (pas de page d'attente)

#### 2. Modifier docker-compose.yml

**Important** : Changer la restart policy :

```yaml
services:
  votreservice:
    # ...
    restart: "no"  # ← Obligatoire pour auto-start
```

Recréer les conteneurs :

```bash
cd /opt/votreservice
docker-compose down
docker-compose up -d
docker-compose stop
```

#### 3. Configurer Nginx

Exemple pour un site web (mode Dynamic) :

```nginx
server {
    listen 443 ssl http2;
    server_name votreservice.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/votreservice.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/votreservice.srv759970.hstgr.cloud/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Basic Auth (optionnel)
    include snippets/basic-auth.conf;

    location / {
        proxy_pass http://127.0.0.1:8890;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_read_timeout 300;
        client_max_body_size 100M;
    }
}

server {
    listen 80;
    server_name votreservice.srv759970.hstgr.cloud;
    return 301 https://$host$request_uri;
}
```

Pour une API (mode Blocking), ajouter `"blocking": true` dans config.json.

#### 4. Redémarrer le service

```bash
systemctl restart docker-autostart
nginx -t && systemctl reload nginx
```

## Services configurés

| Service | URL | Type | Mode | Thème | Port |
|---------|-----|------|------|-------|------|
| **SolidarLink** | solidarlink.srv759970.hstgr.cloud | WordPress | Dynamic | hacker-terminal | 9003 |
| **Tika API** | tika.srv759970.hstgr.cloud | API | Blocking | - | 9998 |
| **Clémence** | clemence.srv759970.hstgr.cloud | WordPress | Dynamic | ghost | 9002 |
| **Support Dashboard** | dashboard.srv759970.hstgr.cloud | Streamlit | Dynamic | matrix | 8501 |
| **SharePoint Dashboards** | sharepoint.srv759970.hstgr.cloud | Streamlit | Dynamic | shuffle | 8502 |
| **Cristina Admin** | admin.cristina.srv759970.hstgr.cloud | Strapi | Dynamic | ghost | 1337 |
| **Whisper API (faster-whisper)** | whisper.srv759970.hstgr.cloud | API | Blocking | - | 8001 |
| **WhisperX API (diarization)** | whisperx.srv759970.hstgr.cloud | API | Blocking | - | 8002 |

## Modes d'opération

### Mode Dynamic (Sites web)

- **Affiche une page d'attente** pendant le démarrage (~15-20s)
- Auto-refresh toutes les 3 secondes
- Thèmes disponibles : hacker-terminal, ghost, matrix, shuffle
- Utilisation : Sites web, dashboards, admin panels

### Mode Blocking (APIs)

- **Attend silencieusement** que les conteneurs démarrent
- Timeout : 30 secondes
- Pas de page d'attente (meilleur pour les API clients)
- Utilisation : APIs REST, services backend

## Commandes utiles

### Service systemd

```bash
# Statut
systemctl status docker-autostart

# Logs en temps réel
journalctl -u docker-autostart -f

# Redémarrer
systemctl restart docker-autostart

# Arrêter/Démarrer
systemctl stop docker-autostart
systemctl start docker-autostart
```

### Debug

```bash
# Vérifier la config
cat /opt/docker-autostart/config.json | jq

# Tester manuellement (arrêter systemd avant)
systemctl stop docker-autostart
cd /opt/docker-autostart && node server.js

# Vérifier conteneurs arrêtés
docker ps -a | grep -E "(support|sharepoint|cristina|tika|solidarlink|clemence|whisper)"

# Forcer arrêt des conteneurs pour test
cd /opt/votreservice && docker-compose stop
```

### Tester l'auto-start

```bash
# 1. Arrêter le conteneur
cd /opt/support-dashboard && docker-compose stop

# 2. Accéder à l'URL
curl -I https://dashboard.srv759970.hstgr.cloud

# 3. Vérifier les logs
journalctl -u docker-autostart -n 20 --no-pager
```

## Thèmes des pages d'attente

### hacker-terminal
- Fond noir avec gradient vert radial
- Texte vert phosphorescent style terminal
- Effet scanlines + CRT monitor
- Parfait pour : Sites techniques, outils dev

### ghost
- Fond sombre avec animation de fantômes flottants
- Couleurs violettes/roses
- Effet mystérieux et élégant
- Parfait pour : Sites créatifs, portfolios

### matrix
- Effet pluie de caractères Matrix
- Fond noir, caractères verts qui tombent
- Animation constante
- Parfait pour : APIs, services backend

### shuffle
- Cartes qui se mélangent avec animation
- Coloré et dynamique
- Effet ludique
- Parfait pour : Dashboards, outils analytics

## Personnalisation

### Créer un nouveau thème

1. Créer `/opt/docker-autostart/themes/montheme.html`
2. Utiliser les placeholders :
   - `{{SERVICE_NAME}}` : Remplacé par le nom du service
   - `{{DISPLAY_NAME}}` : Alias de SERVICE_NAME
3. Ajouter auto-refresh :
```html
<meta http-equiv="refresh" content="3" />
```
4. Référencer dans config.json :
```json
"theme": "montheme"
```

### Modifier le timeout d'inactivité

Éditer `/opt/docker-autostart/config.json` :

```json
{
  "idleTimeout": 3600,  // 60 minutes au lieu de 30
  // ...
}
```

Puis redémarrer :
```bash
systemctl restart docker-autostart
```

## Troubleshooting

### Problème : Page d'attente ne s'affiche pas

**Diagnostic** :
```bash
journalctl -u docker-autostart -n 50 --no-pager
```

**Solutions** :
- Vérifier que Nginx proxifie vers port 8890
- Vérifier le service tourne : `systemctl status docker-autostart`
- Vérifier config.json valide : `cat /opt/docker-autostart/config.json | jq`

### Problème : Conteneurs redémarrent automatiquement

**Cause** : Restart policy incorrecte dans docker-compose.yml

**Solution** :
```bash
cd /opt/votreservice
grep 'restart:' docker-compose.yml  # Doit afficher "no"
# Si ce n'est pas le cas :
sed -i 's/restart: unless-stopped/restart: "no"/g' docker-compose.yml
docker-compose down && docker-compose up -d && docker-compose stop
```

### Problème : Conteneurs ne démarrent pas

**Vérifier** :
```bash
# Nom des conteneurs dans config.json
cat /opt/docker-autostart/config.json | jq '.services["votreservice.srv759970.hstgr.cloud"].containers'

# Nom réel des conteneurs
docker ps -a --format '{{.Names}}' | grep votreservice
```

Les noms doivent correspondre exactement (cf. `container_name:` dans docker-compose.yml).

### Problème : Services ne s'arrêtent jamais (auto-stop ne fonctionne pas)

**Diagnostic :**
```bash
# Vérifier le trafic suspect
tail -100 /var/log/nginx/votreservice-access.log | grep axios
```

**Causes possibles :**
1. **Dashy status checks** → Voir section "Compatibilité avec Dashy" ci-dessus
2. **Monitoring externe** → Ajouter exclusion dans nginx ou auto-stop
3. **Timeout trop court** → Augmenter `idleTimeout` dans config.json
4. **Service conflictuel** → Vérifier si `nginx-auto-docker` est actif :
```bash
systemctl status nginx-auto-docker
# Si actif, le désactiver :
systemctl disable --now nginx-auto-docker
```

### Problème : 502 Bad Gateway après démarrage

**Cause** : Conteneurs pas encore prêts après `docker-compose start`

**Solution** :
- Ajouter un healthcheck dans docker-compose.yml
- Augmenter le délai d'attente dans server.js (waitForReady)
- Pour les sites lents, utiliser mode Dynamic au lieu de Blocking

## Optimisation RAM

### Avant auto-start
```
RAM utilisée : 7.1GB / 8GB (89%)
```

### Après auto-start (conteneurs arrêtés)
```
RAM utilisée : 2.4GB / 8GB (30%)
Économie : 4.7GB (66%)
```

### Services concernés
- Support Dashboard : ~300MB
- SharePoint Dashboards : ~300MB
- Cristina Admin (Strapi) : ~400MB
- Tika API : ~800MB
- SolidarLink (WordPress) : ~200MB
- Clémence (WordPress) : ~200MB
- Whisper API (faster-whisper) : ~400MB
- WhisperX API : ~500MB

**Total économisé** : ~3.1GB de RAM quand tous arrêtés

## Sécurité

### Basic Auth

Tous les services sont protégés par basic auth Nginx. Les credentials sont dans `/etc/nginx/.htpasswd`.

### Exposition des ports

Le proxy Node.js écoute uniquement sur **127.0.0.1:8890** (localhost), pas accessible depuis l'extérieur.

### Accès Docker socket

Le service systemd tourne en tant que `root` pour accéder à Docker socket (`/var/run/docker.sock`).

## Maintenance

### Backup de la configuration

```bash
# Backup config
cp /opt/docker-autostart/config.json /opt/docker-autostart/config.json.backup

# Versionner dans Git (recommandé)
cd /opt/docker-autostart
git init
git add .
git commit -m "Configuration auto-start"
```

### Mise à jour du serveur Node.js

```bash
# Éditer server.js
nano /opt/docker-autostart/server.js

# Test syntaxe
node -c /opt/docker-autostart/server.js

# Redémarrer
systemctl restart docker-autostart
```

## Limites actuelles

### Non supporté

- ❌ **Ollama** : Service systemd (pas Docker), nécessite approche différente
- ❌ **MySQL shared** : Doit rester actif (utilisé par plusieurs WordPress)
- ❌ **Portainer/Dozzle/Netdata** : Services de monitoring, doivent rester actifs

### À venir

- [ ] Support Ollama via systemd socket activation
- [ ] Healthchecks personnalisables par service
- [ ] Notifications (email/webhook) au démarrage/arrêt
- [ ] Dashboard web pour voir l'état des services
- [ ] Métriques de démarrage/arrêt (logs structurés)

## Liens utiles

- **Documentation Sablier** : https://sablierapp.dev (inspiration pour les thèmes)
- **Node.js Express** : https://expressjs.com
- **Docker Compose** : https://docs.docker.com/compose/
- **Systemd** : https://www.freedesktop.org/software/systemd/man/systemd.service.html
