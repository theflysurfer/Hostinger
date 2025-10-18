# 🎯 Guide API & Admin Portal - srv759970.hstgr.cloud

## 📋 Vue d'ensemble

Le **API & Admin Portal** est un portail web centralisé qui regroupe toute la documentation API (Swagger UI) et les outils d'administration/monitoring du serveur.

**URL principale** : https://portal.srv759970.hstgr.cloud

---

## 🚀 Accès au portail

### URL principale

```
https://portal.srv759970.hstgr.cloud
```

Le portail affiche une page d'accueil organisée en 3 sections :
1. **📚 API Documentation** (Swagger UI)
2. **🔧 Monitoring & Administration**
3. **🌐 Applications déployées**

---

## 📚 Documentation API (Swagger UI)

**URL unifiée** : https://portal.srv759970.hstgr.cloud/api

Le portail présente une interface Swagger UI unique qui regroupe les 3 APIs suivantes :

### Whisper API

**Description** : API de transcription speech-to-text avec faster-whisper
- OpenAPI 3.1 natif (FastAPI)
- Endpoints compatibles OpenAI
- Interface "Try it out" interactive
- **Spec source** : https://whisper.srv759970.hstgr.cloud/openapi.json

**Endpoints principaux** :
- `POST /v1/audio/transcriptions` - Transcription audio
- `POST /v1/audio/translations` - Traduction audio
- `GET /v1/models` - Liste des modèles
- `GET /health` - Health check

---

### Tika API

**Description** : API de parsing de documents (1000+ formats)
- Spec OpenAPI 3.0 créée spécifiquement
- PDF, Office, images avec OCR, archives
- Apache Tika 3.2.3
- **Spec source** : https://portal.srv759970.hstgr.cloud/api/specs/tika.yaml

**Endpoints principaux** :
- `PUT /tika` - Parser un document (extraire texte)
- `PUT /meta` - Extraire métadonnées
- `PUT /detect/stream` - Détecter type MIME
- `GET /version` - Version Tika
- `GET /parsers` - Liste des parsers disponibles
- `GET /mime-types` - Types MIME supportés

---

### Ollama API

**Description** : API LLM local (Llama, Mistral, Qwen)
- Spec OpenAPI 3.0 communautaire
- Inférence locale
- Chat, génération, embeddings
- **Spec source** : https://portal.srv759970.hstgr.cloud/api/specs/ollama.yaml

**Endpoints principaux** :
- `POST /api/generate` - Génération de texte
- `POST /api/chat` - Chat conversation
- `GET /api/tags` - Liste des modèles locaux
- `POST /api/pull` - Télécharger un modèle
- `POST /api/embeddings` - Générer embeddings

---

## 🔧 Monitoring & Administration

### Portainer

**URL** : https://portal.srv759970.hstgr.cloud/monitoring/portainer

**Description** : Interface web de gestion Docker
- Gestion des containers, images, volumes, networks
- Création et déploiement de stacks Docker Compose
- Monitoring des ressources
- Logs des containers
- Console interactive

**Port direct** : http://69.62.108.82:9000

---

### Dozzle

**URL** : https://portal.srv759970.hstgr.cloud/monitoring/dozzle

**Description** : Visualiseur de logs Docker temps réel
- Monitoring live des logs containers
- Léger (ne stocke pas les logs)
- Interface simple et rapide
- Recherche dans les logs
- Multi-container viewing

**Port direct** : http://69.62.108.82:8888

---

### Netdata

**URL** : https://portal.srv759970.hstgr.cloud/monitoring/netdata

**Description** : Monitoring système temps réel
- CPU, RAM, Disk I/O, Network
- Métriques par process
- Alertes configurables
- Graphiques interactifs
- Historique des performances

**Port direct** : http://69.62.108.82:19999

---

## 🛠️ Architecture technique

### Stack Docker

```
/opt/api-portal/
├── docker-compose.yml      # Config Swagger UI
├── index.html              # Page d'accueil du portail
└── openapi-specs/
    ├── tika.yaml          # Spec OpenAPI Tika
    └── ollama.yaml        # Spec OpenAPI Ollama
```

**Container Swagger UI** :
- Image : `swaggerapi/swagger-ui:latest`
- Port : 8503
- Volume : `./openapi-specs` monté en lecture seule
- Environment variables :
  - `BASE_URL=/api` - Configure Swagger UI pour fonctionner derrière reverse proxy
  - `URLS=[...]` - Liste des specs OpenAPI à charger (Tika, Ollama, Whisper)

### Configuration Nginx

**Fichier** : `/etc/nginx/sites-available/portal`

**Routes configurées** :
- `/` → Page d'accueil statique (`/opt/api-portal/index.html`)
- `/api` → Swagger UI (port 8503)
  - Note : Pas de trailing slash pour éviter les problèmes de routing
  - Header `X-Forwarded-Prefix: /api` pour la compatibilité
- `/monitoring/portainer/` → Portainer (port 9000)
- `/monitoring/dozzle/` → Dozzle (port 8888)
- `/monitoring/netdata/` → Netdata (port 19999)

**SSL** : Certificat Let's Encrypt dédié
- Certificat : `/etc/letsencrypt/live/portal.srv759970.hstgr.cloud/`
- Renouvellement automatique

---

## 📊 Fichiers OpenAPI créés

### Tika OpenAPI Spec

**Fichier** : `/opt/api-portal/openapi-specs/tika.yaml`

Décrit tous les endpoints Tika avec :
- Paramètres de requête
- Types de contenu acceptés/retournés
- Exemples de réponses
- Tags et descriptions

**Basé sur** :
- Documentation officielle Apache Tika
- Wiki TikaJAXRS
- Analyse des endpoints natifs

### Ollama OpenAPI Spec

**Fichier** : `/opt/api-portal/openapi-specs/ollama.yaml`

Spec communautaire complète avec :
- Endpoints de génération et chat
- Gestion des modèles
- Embeddings
- Exemples pour chaque endpoint

**Basé sur** :
- Documentation officielle Ollama
- Spec communautaire GitHub

---

## 🔐 Sécurité

### Accès HTTPS

Tous les services sont accessibles via HTTPS uniquement :
- ✅ Certificat SSL Let's Encrypt
- ✅ Redirection HTTP → HTTPS automatique
- ✅ Headers X-Forwarded correctement configurés

### Authentification

**Status actuel** :
- ⚠️ Portail public (pas d'auth)
- ⚠️ Swagger UI public
- ✅ Portainer : Nécessite login/password

**Recommandation** : Ajouter authentification Basic Auth Nginx si exposition publique prolongée.

---

## 🚀 Utilisation

### Tester une API depuis Swagger UI

1. Aller sur https://portal.srv759970.hstgr.cloud
2. Cliquer sur une carte API (toutes pointent vers `/api`)
3. L'interface Swagger UI s'ouvre avec les 3 APIs disponibles
4. Choisir l'API dans le menu déroulant en haut (Whisper API, Tika API, ou Ollama API)
5. Sélectionner un endpoint dans la liste
6. Cliquer sur "Try it out"
7. Remplir les paramètres
8. Cliquer sur "Execute"
9. Voir la réponse en dessous

**Note** : Les 3 cartes API sur la page d'accueil pointent vers la même URL (`/api`) car Swagger UI présente toutes les APIs dans une seule interface avec un sélecteur.

### Exemple : Parser un PDF avec Tika via Swagger

1. Aller sur https://portal.srv759970.hstgr.cloud/api
2. Sélectionner "Tika API" dans le menu déroulant en haut
3. Sélectionner l'endpoint `PUT /tika`
4. Cliquer "Try it out"
5. Choisir un fichier PDF
6. Sélectionner Accept: `text/plain`
7. Cliquer "Execute"
8. Le texte extrait s'affiche dans la réponse

### Gérer un container avec Portainer

1. Aller sur `/monitoring/portainer`
2. Se connecter (si première fois, créer admin)
3. Cliquer sur "Containers"
4. Sélectionner un container
5. Actions disponibles : Start, Stop, Restart, Logs, Stats, Console

### Voir les logs en temps réel avec Dozzle

1. Aller sur `/monitoring/dozzle`
2. La liste des containers s'affiche
3. Cliquer sur un container pour voir ses logs
4. Recherche disponible dans la barre en haut
5. Auto-scroll pour suivre les nouveaux logs

---

## 🔧 Gestion du portail

### Voir les logs du portail

```bash
ssh root@69.62.108.82 "tail -f /var/log/nginx/portal-access.log"
ssh root@69.62.108.82 "tail -f /var/log/nginx/portal-error.log"
```

### Redémarrer Swagger UI

```bash
ssh root@69.62.108.82 "cd /opt/api-portal && docker-compose restart"
```

### Mettre à jour une spec OpenAPI

```bash
# Éditer le fichier
ssh root@69.62.108.82 "nano /opt/api-portal/openapi-specs/tika.yaml"

# Pas besoin de redémarrer, Swagger UI recharge automatiquement
```

### Ajouter une nouvelle API au portail

1. **Créer le fichier OpenAPI** :
```bash
ssh root@69.62.108.82 "nano /opt/api-portal/openapi-specs/nouvelle-api.yaml"
```

2. **Mettre à jour docker-compose.yml** :
```yaml
environment:
  - URLS=[
      {"url":"specs/tika.yaml","name":"Tika API"},
      {"url":"specs/ollama.yaml","name":"Ollama API"},
      {"url":"specs/nouvelle-api.yaml","name":"Nouvelle API"}
    ]
```

3. **Redémarrer** :
```bash
ssh root@69.62.108.82 "cd /opt/api-portal && docker-compose up -d"
```

4. **Mettre à jour index.html** avec la nouvelle carte

---

## 📊 Statistiques d'utilisation

### Vérifier les accès au portail

```bash
# Nombre de visiteurs aujourd'hui
ssh root@69.62.108.82 "grep $(date +%d/%b/%Y) /var/log/nginx/portal-access.log | wc -l"

# Top 10 des endpoints les plus utilisés
ssh root@69.62.108.82 "awk '{print \$7}' /var/log/nginx/portal-access.log | sort | uniq -c | sort -rn | head -10"

# Top IPs
ssh root@69.62.108.82 "awk '{print \$1}' /var/log/nginx/portal-access.log | sort | uniq -c | sort -rn | head -10"
```

---

## ⚠️ Troubleshooting

### Le portail ne s'affiche pas

```bash
# Vérifier Nginx
ssh root@69.62.108.82 "systemctl status nginx"
ssh root@69.62.108.82 "nginx -t"

# Vérifier les logs
ssh root@69.62.108.82 "tail -50 /var/log/nginx/portal-error.log"
```

### Swagger UI ne charge pas

```bash
# Vérifier le container
ssh root@69.62.108.82 "docker ps | grep swagger-ui"

# Voir les logs
ssh root@69.62.108.82 "docker logs swagger-ui --tail=50"

# Redémarrer
ssh root@69.62.108.82 "cd /opt/api-portal && docker-compose restart"
```

### Un service de monitoring est inaccessible

```bash
# Vérifier que le container tourne
ssh root@69.62.108.82 "docker ps | grep -E 'portainer|dozzle|netdata'"

# Tester l'accès local
ssh root@69.62.108.82 "curl -I http://localhost:9000"  # Portainer
ssh root@69.62.108.82 "curl -I http://localhost:8888"  # Dozzle
ssh root@69.62.108.82 "curl -I http://localhost:19999" # Netdata

# Voir config Nginx
ssh root@69.62.108.82 "cat /etc/nginx/sites-available/portal"
```

### Erreur 404 sur /api (Swagger UI)

**Symptôme** : Erreur "404 Not Found" quand on accède à `/api/whisper`, `/api/tika`, ou `/api/ollama`

**Cause** : Problème de configuration de BASE_URL dans Swagger UI ou routing Nginx incorrect

**Solutions** :

1. **Vérifier la configuration docker-compose.yml** :
```bash
ssh root@69.62.108.82 "cat /opt/api-portal/docker-compose.yml"
```

Doit contenir :
```yaml
environment:
  - BASE_URL=/api
  - URLS=[{\"url\":\"specs/tika.yaml\",\"name\":\"Tika API\"}...]
```

2. **Vérifier la configuration Nginx** :
```bash
ssh root@69.62.108.82 "cat /etc/nginx/sites-available/portal | grep -A 10 'location /api'"
```

Doit être :
```nginx
location /api {  # PAS de trailing slash
    proxy_pass http://localhost:8503;  # PAS de trailing slash
    ...
}
```

3. **Redémarrer les services** :
```bash
ssh root@69.62.108.82 "cd /opt/api-portal && docker-compose restart"
ssh root@69.62.108.82 "systemctl reload nginx"
```

4. **Tester** :
```bash
ssh root@69.62.108.82 "curl -I https://portal.srv759970.hstgr.cloud/api/"
ssh root@69.62.108.82 "curl -I https://portal.srv759970.hstgr.cloud/api/specs/tika.yaml"
```

---

### Whisper API CORS Error dans Swagger UI

**Symptôme** : "Failed to load API definition" avec erreur CORS dans Swagger UI pour Whisper API

**Cause** : Whisper API (whisper.srv759970.hstgr.cloud) ne permet pas les requêtes cross-origin depuis portal.srv759970.hstgr.cloud

**Solution** : Ajouter les headers CORS à la configuration Nginx de Whisper

```bash
# Éditer la config Whisper
ssh root@69.62.108.82 "nano /etc/nginx/sites-available/whisper"
```

Ajouter dans le `location /` block :
```nginx
# CORS headers for Swagger UI access from portal.srv759970.hstgr.cloud
add_header 'Access-Control-Allow-Origin' 'https://portal.srv759970.hstgr.cloud' always;
add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;

# Handle preflight requests
if ($request_method = 'OPTIONS') {
    return 204;
}
```

Recharger Nginx :
```bash
ssh root@69.62.108.82 "nginx -t && systemctl reload nginx"
```

---

### Dozzle affiche une page blanche

**Symptôme** : Page blanche lorsqu'on accède à `/monitoring/dozzle`

**Cause** : Dozzle ne sait pas qu'il fonctionne derrière un reverse proxy avec un subpath

**Solution** : Recréer le container Dozzle avec le paramètre `DOZZLE_BASE`

```bash
# Arrêter et supprimer le container actuel
ssh root@69.62.108.82 "docker stop dozzle && docker rm dozzle"

# Recréer avec base path
ssh root@69.62.108.82 "docker run -d --name dozzle --restart unless-stopped \
  -p 8888:8080 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e DOZZLE_BASE=/monitoring/dozzle \
  amir20/dozzle:latest"
```

Mettre à jour la configuration Nginx pour forward le path complet :
```nginx
location /monitoring/dozzle {  # Sans trailing slash
    proxy_pass http://localhost:8888;  # Sans trailing slash
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

Recharger Nginx :
```bash
ssh root@69.62.108.82 "systemctl reload nginx"
```

---

### Portainer redirige vers /timeout.html avec 404

**Symptôme** : Erreur 404 sur `/timeout.html` lors de l'accès à Portainer via `/monitoring/portainer/`

**Cause** : Portainer redirige vers `/timeout.html` mais Nginx ne transforme pas la redirection en `/monitoring/portainer/timeout.html`

**Solution** : Ajouter `proxy_redirect` dans la configuration Nginx de Portainer

```nginx
location /monitoring/portainer/ {
    proxy_pass http://localhost:9000/;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    # Fix Portainer redirects to work with subpath
    proxy_redirect / /monitoring/portainer/;
}
```

Recharger Nginx :
```bash
ssh root@69.62.108.82 "nginx -t && systemctl reload nginx"
```

---

## 📝 Checklist de déploiement

- [x] Container Swagger UI déployé (port 8503) → Migré vers fichiers statiques
- [x] Specs OpenAPI créées (Tika, Ollama)
- [x] Page d'accueil HTML créée
- [x] Configuration Nginx créée
- [x] Certificat SSL obtenu
- [x] Redirection HTTP → HTTPS configurée
- [x] Routes vers services de monitoring configurées
- [x] Headers CORS configurés pour Whisper API
- [x] Dozzle configuré avec DOZZLE_BASE
- [x] Portainer configuré avec proxy_redirect
- [x] Tests d'accès réussis pour tous les services
- [x] Documentation créée et mise à jour

---

## 🔗 Liens utiles

- **Portail** : https://portal.srv759970.hstgr.cloud
- **Swagger UI docs** : https://swagger.io/tools/swagger-ui/
- **OpenAPI Spec** : https://swagger.io/specification/
- **Portainer docs** : https://docs.portainer.io/
- **Dozzle docs** : https://dozzle.dev/
- **Netdata docs** : https://learn.netdata.cloud/

---

**Dernière mise à jour** : Octobre 2025
**Version** : 1.0
**Status** : ✅ En production
**Certificat SSL** : Expire le 13 janvier 2026
