# Configuration Docker Auto-Start/Stop

## Vue d'ensemble

Le système d'auto-start/stop automatique est un proxy Node.js custom qui gère le démarrage/arrêt automatique des services Docker en fonction de l'activité. Il remplace l'ancien système Sablier.

**Emplacement** : `/opt/docker-autostart/`
**Port** : `8890`
**Configuration** : `/opt/docker-autostart/config.json`
**Timeout d'inactivité** : `1800` secondes (30 minutes)

---

## Services configurés

### Tableau récapitulatif

| Service | Nom | Compose Dir | Port Proxy | Mode | Thème | Conteneurs |
|---------|-----|-------------|------------|------|-------|------------|
| **solidarlink.srv759970.hstgr.cloud** | SolidarLink | `/opt/wordpress-solidarlink` | 9003 | Dynamic | hacker-terminal | nginx-solidarlink, wordpress-solidarlink |
| **tika.srv759970.hstgr.cloud** | Tika API | `/opt/tika-server` | 9998 | **Blocking** | *(none)* | tika-server |
| **clemence.srv759970.hstgr.cloud** | Clémence Site | `/opt/wordpress-clemence` | 9002 | Dynamic | ghost | wordpress-clemence, nginx-clemence |
| **dashboard.srv759970.hstgr.cloud** | Support Dashboard | `/opt/support-dashboard` | 8501 | Dynamic | matrix | support-dashboard |
| **sharepoint.srv759970.hstgr.cloud** | SharePoint Dashboards | `/opt/sharepoint-dashboards` | 8502 | Dynamic | shuffle | sharepoint-dashboards |
| **admin.cristina.srv759970.hstgr.cloud** | Cristina Admin | `/opt/cristina-backend` | 1337 | Dynamic | ghost | cristina-strapi |
| **whisper.srv759970.hstgr.cloud** | Whisper API (faster-whisper) | `/opt/whisper-faster` | 8001 | **Blocking** | *(none)* | faster-whisper |
| **whisperx.srv759970.hstgr.cloud** | WhisperX API (with diarization) | `/opt/whisperx` | 8002 | **Blocking** | *(none)* | whisperx |
| **memvid.srv759970.hstgr.cloud** | MemVid RAG API | `/opt/memvid` | 8506 | **Blocking** | *(none)* | memvid-api |
| **memvid-ui.srv759970.hstgr.cloud** | MemVid UI | `/opt/memvid` | 8507 | Dynamic | matrix | memvid-ui |
| **ragflow.srv759970.hstgr.cloud** | RAGFlow | `/opt/ragflow/docker` | 9500 | **Blocking** | cyberpunk | ragflow-server, ragflow-mysql, ragflow-es-01, ragflow-redis, ragflow-minio |
| **rag-anything.srv759970.hstgr.cloud** | RAG-Anything | `/opt/rag-anything` | 9510 | **Blocking** | synthwave | rag-anything-api |

---

## Détails des paramètres

### 1. Mode Dynamic vs Blocking

#### **Dynamic Mode** (défaut)
- **Comportement** : Affiche une page d'attente animée pendant le démarrage
- **Utilisation** : Sites web, dashboards, applications UI
- **Services** : SolidarLink, Clémence, Support Dashboard, SharePoint, Cristina, MemVid UI
- **Thèmes disponibles** :
  - `matrix` - Animation Matrix (pluie de caractères verts)
  - `ghost` - Fantômes flottants avec effets de particules
  - `hacker-terminal` - Terminal de hacking avec commandes simulées
  - `shuffle` - Cartes qui se mélangent et se révèlent
  - `cyberpunk` - Grille néon avec effet glitch
  - `synthwave` - Grille rétro années 80

#### **Blocking Mode** (`"blocking": true`)
- **Comportement** : Démarre le service AVANT de répondre à la requête (pas de page d'attente)
- **Utilisation** : APIs qui doivent répondre immédiatement
- **Services** : Tika API, Whisper API, WhisperX API, MemVid API, RAGFlow, RAG-Anything
- **Avantage** : Le client reçoit directement la réponse API (pas d'HTML intermédiaire)

---

### 2. Paramètres de configuration

#### `port` (global)
```json
"port": 8890
```
Port d'écoute du proxy auto-start. Nginx redirige vers ce port pour tous les services configurés.

#### `idleTimeout` (global)
```json
"idleTimeout": 1800
```
Durée d'inactivité (en secondes) avant arrêt automatique du service. Par défaut : **30 minutes**.

#### `composeDir` (par service)
Répertoire contenant le `docker-compose.yml` du service.

#### `composeFile` (optionnel)
Nom du fichier compose si différent de `docker-compose.yml`. Exemple : RAGFlow utilise `docker-compose-full.yml`.

#### `proxyPort` (par service)
Port du service Docker vers lequel le proxy redirige après démarrage.

#### `containers` (par service)
Liste des conteneurs Docker à surveiller pour détecter l'état du service.

---

## Configuration Nginx

Chaque service configuré utilise un bloc `upstream` et `proxy_pass` dans Nginx :

```nginx
upstream docker-autostart-solidarlink {
    server 127.0.0.1:8890;
}

server {
    listen 443 ssl http2;
    server_name solidarlink.srv759970.hstgr.cloud;

    location / {
        proxy_pass http://docker-autostart-solidarlink;
        proxy_set_header Host $host;
        proxy_set_header X-Autostart-Target "solidarlink.srv759970.hstgr.cloud";
    }
}
```

Le header `X-Autostart-Target` permet au proxy d'identifier quel service démarrer.

---

## Commandes de gestion

### Vérifier l'état du proxy
```bash
systemctl status docker-autostart
```

### Redémarrer le proxy
```bash
systemctl restart docker-autostart
```

### Consulter les logs
```bash
journalctl -u docker-autostart -f
```

### Modifier la configuration
```bash
nano /opt/docker-autostart/config.json
systemctl restart docker-autostart
```

### Tester un service
```bash
curl -I https://dashboard.srv759970.hstgr.cloud
# Le service démarre automatiquement
```

---

## Synchronisation dynamique

Ce document peut être mis à jour automatiquement depuis la configuration serveur.

### Script de mise à jour

Utiliser le script `scripts/sync-autostart-config.sh` pour synchroniser :

```bash
./scripts/sync-autostart-config.sh
```

Ce script :
1. Récupère `/opt/docker-autostart/config.json` depuis le serveur
2. Génère automatiquement le tableau récapitulatif
3. Met à jour cette documentation
4. Commit les changements si nécessaire

---

## Architecture technique

```
Internet → Nginx (443) → docker-autostart (8890) → Service Docker (port spécifique)
                ↓
           X-Autostart-Target header
                ↓
        1. Check service status
        2. Start containers if stopped
        3. Wait for healthcheck
        4. Proxy request to service
```

### Flux Dynamic Mode
1. Requête arrive sur Nginx
2. Nginx redirige vers docker-autostart:8890
3. Proxy détecte service arrêté
4. **Renvoie immédiatement page d'attente HTML avec thème**
5. JavaScript dans la page poll `/status` toutes les 2 secondes
6. Démarre les conteneurs Docker en arrière-plan
7. Quand healthcheck OK → JavaScript redirige vers le service

### Flux Blocking Mode
1. Requête arrive sur Nginx
2. Nginx redirige vers docker-autostart:8890
3. Proxy détecte service arrêté
4. **Démarre les conteneurs et ATTEND le healthcheck**
5. Une fois prêt → Proxy la requête vers le service
6. Client reçoit directement la réponse API

---

## Références

- **Guide complet** : [GUIDE_DOCKER_AUTOSTART.md](../guides/GUIDE_DOCKER_AUTOSTART.md)
- **Code source** : `/opt/docker-autostart/index.js`
- **Systemd service** : `/etc/systemd/system/docker-autostart.service`
- **Inventory complet** : [server-configs/INVENTORY.md](../../server-configs/INVENTORY.md)

---

**Dernière synchronisation** : 2025-10-21
**Config serveur** : `/opt/docker-autostart/config.json`
