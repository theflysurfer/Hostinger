# 🤖 Guide Ollama - API ML/AI sur VPS

> **Guide complet pour Ollama sur VPS Hostinger avec Nginx reverse proxy et SSL**

---

## 📋 Vue d'ensemble

**Ollama** : Framework pour exécuter des LLMs (Large Language Models) localement
**Utilisation** : API REST pour générer du texte, chat, embeddings
**Avantage** : Modèles locaux, pas de dépendance cloud, gratuit
**Déploiement** : Service systemd + Nginx reverse proxy avec HTTPS

---

## 🏗️ Architecture

```
Client (HTTPS)
    ↓
Nginx (443) - ollama.srv759970.hstgr.cloud
    ↓ reverse proxy
Ollama Service (localhost:11434)
    ↓
Modèles LLMs locaux
```

**Configuration actuelle** :
- **Service** : `ollama.service` (systemd)
- **Port local** : 11434 (127.0.0.1 uniquement)
- **URL publique** : https://ollama.srv759970.hstgr.cloud
- **SSL** : Let's Encrypt
- **Modèles installés** : 4 (qwen2.5:14b, qwen2.5vl:7b, mistral:7b, llama3.2:1b)

---

## ✅ État actuel du service

### Vérifier le service

```bash
# Statut du service
ssh root@69.62.108.82 "systemctl status ollama"

# Vérifier si Ollama écoute
ssh root@69.62.108.82 "netstat -tulpn | grep 11434"
# Résultat attendu : tcp 0 0 127.0.0.1:11434 0.0.0.0:* LISTEN

# Tester localement
ssh root@69.62.108.82 "curl -s http://localhost:11434/api/tags | jq '.models | length'"
# Résultat attendu : nombre de modèles (ex: 4)
```

### Modèles disponibles

```bash
# Lister les modèles installés
ssh root@69.62.108.82 "curl -s http://localhost:11434/api/tags | jq -r '.models[] | .name'"
```

**Modèles actuels** :
- `qwen2.5:14b` - Modèle chinois multilingue (14B paramètres)
- `qwen2.5vl:7b` - Vision + Language (7B paramètres)
- `mistral:7b` - Modèle français/anglais performant
- `llama3.2:1b` - Modèle léger et rapide (1B paramètres)

---

## 🔧 Configuration Nginx avec SSL

### Configuration actuelle

**Fichier** : `/etc/nginx/sites-available/ollama-https`

```nginx
# HTTP -> HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name ollama.srv759970.hstgr.cloud;
    return 301 https://$host$request_uri;
}

# HTTPS
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ollama.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/ollama.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ollama.srv759970.hstgr.cloud/privkey.pem;

    access_log /var/log/nginx/ollama-access.log;
    error_log /var/log/nginx/ollama-error.log;

    location / {
        proxy_pass http://127.0.0.1:11434;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts augmentés pour génération de texte
        proxy_read_timeout 600s;
        proxy_connect_timeout 75s;

        # Désactiver buffering pour streaming
        proxy_buffering off;
        proxy_cache off;

        # CORS headers
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS, DELETE, PUT" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

### Points clés de la configuration

1. **Timeouts augmentés** : `proxy_read_timeout 600s` pour permettre la génération de longues réponses
2. **Buffering désactivé** : `proxy_buffering off` pour le streaming de tokens
3. **CORS activé** : Permet les appels depuis n'importe quel domaine
4. **HTTP/2** : `http2` pour meilleures performances
5. **Security headers** : Protection XSS, clickjacking, etc.

---

## 🚀 Déploiement initial (si besoin)

### Étape 1 : Installer Ollama

```bash
# Installation
ssh root@69.62.108.82 "curl -fsSL https://ollama.com/install.sh | sh"

# Vérifier l'installation
ssh root@69.62.108.82 "ollama --version"
```

### Étape 2 : Configurer le service systemd

```bash
# Vérifier la config du service
ssh root@69.62.108.82 "systemctl cat ollama.service"
```

**Config standard** : `/etc/systemd/system/ollama.service`

```ini
[Unit]
Description=Ollama Service
After=network.target

[Service]
ExecStart=/usr/local/bin/ollama serve
User=root
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### Étape 3 : Démarrer le service

```bash
# Démarrer et activer au boot
ssh root@69.62.108.82 "systemctl enable --now ollama"

# Vérifier
ssh root@69.62.108.82 "systemctl status ollama"
```

### Étape 4 : Installer des modèles

```bash
# Installer un modèle (exemple : llama3.2:1b)
ssh root@69.62.108.82 "ollama pull llama3.2:1b"

# Lister les modèles
ssh root@69.62.108.82 "ollama list"
```

**Modèles recommandés** :
- `llama3.2:1b` - Léger et rapide (1.3GB)
- `mistral:7b` - Bon compromis qualité/taille (4.1GB)
- `qwen2.5:14b` - Très performant mais lourd (9GB)

### Étape 5 : Configurer SSL avec Certbot

```bash
# 1. Arrêter Nginx
ssh root@69.62.108.82 "systemctl stop nginx"

# 2. Obtenir le certificat SSL
ssh root@69.62.108.82 "certbot certonly --standalone -d ollama.srv759970.hstgr.cloud --non-interactive --agree-tos --email contact@srv759970.hstgr.cloud"

# 3. Créer la config Nginx (voir section ci-dessus)
# 4. Activer et redémarrer
ssh root@69.62.108.82 "ln -s /etc/nginx/sites-available/ollama-https /etc/nginx/sites-enabled/"
ssh root@69.62.108.82 "nginx -t && systemctl start nginx"
```

---

## 🧪 Tester l'API

### Endpoints disponibles

#### 1. Lister les modèles

```bash
curl https://ollama.srv759970.hstgr.cloud/api/tags
```

**Réponse** :
```json
{
  "models": [
    {
      "name": "llama3.2:1b",
      "modified_at": "2025-10-10T11:28:35Z",
      "size": 1300000000
    }
  ]
}
```

#### 2. Générer du texte

```bash
curl -X POST https://ollama.srv759970.hstgr.cloud/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:1b",
    "prompt": "Pourquoi le ciel est bleu?",
    "stream": false
  }'
```

**Réponse** :
```json
{
  "model": "llama3.2:1b",
  "response": "Le ciel apparaît bleu car...",
  "done": true
}
```

#### 3. Chat (conversation)

```bash
curl -X POST https://ollama.srv759970.hstgr.cloud/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral:7b",
    "messages": [
      {"role": "user", "content": "Bonjour, qui es-tu?"}
    ],
    "stream": false
  }'
```

#### 4. Embeddings (vecteurs)

```bash
curl -X POST https://ollama.srv759970.hstgr.cloud/api/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:1b",
    "prompt": "Hello world"
  }'
```

### Mode streaming

Pour recevoir les tokens au fur et à mesure :

```bash
curl -X POST https://ollama.srv759970.hstgr.cloud/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:1b",
    "prompt": "Écris une histoire courte",
    "stream": true
  }'
```

**Résultat** : Flux de JSON (un par ligne)

---

## 🔧 Gestion des modèles

### Installer un nouveau modèle

```bash
# Depuis le VPS
ssh root@69.62.108.82 "ollama pull [model-name]"

# Exemples
ssh root@69.62.108.82 "ollama pull llama3.2:1b"
ssh root@69.62.108.82 "ollama pull mistral:7b"
ssh root@69.62.108.82 "ollama pull qwen2.5:14b"
```

### Supprimer un modèle

```bash
ssh root@69.62.108.82 "ollama rm [model-name]"

# Exemple
ssh root@69.62.108.82 "ollama rm llama3.2:1b"
```

### Voir l'espace disque utilisé

```bash
# Taille totale des modèles
ssh root@69.62.108.82 "du -sh ~/.ollama/models/"

# Détail par modèle
ssh root@69.62.108.82 "ollama list"
```

---

## 🐛 Troubleshooting

### Problème 1 : Service ne démarre pas

```bash
# Voir les logs
ssh root@69.62.108.82 "journalctl -u ollama -n 50 --no-pager"

# Redémarrer le service
ssh root@69.62.108.82 "systemctl restart ollama"
```

### Problème 2 : Nginx retourne 502 Bad Gateway

**Cause** : Ollama n'est pas démarré ou n'écoute pas sur 11434

**Solution** :
```bash
# Vérifier le service
ssh root@69.62.108.82 "systemctl status ollama"

# Vérifier le port
ssh root@69.62.108.82 "netstat -tulpn | grep 11434"

# Redémarrer si nécessaire
ssh root@69.62.108.82 "systemctl restart ollama"
```

### Problème 3 : Timeout sur génération

**Cause** : Timeout Nginx trop court

**Solution** : Augmenter `proxy_read_timeout` dans la config Nginx

```nginx
proxy_read_timeout 600s;  # 10 minutes
```

### Problème 4 : Modèle ne charge pas (out of memory)

**Symptômes** : Erreur "failed to load model"

**Solution** : Utiliser un modèle plus petit ou augmenter la RAM du VPS

```bash
# Vérifier la RAM disponible
ssh root@69.62.108.82 "free -h"

# Utiliser un modèle plus léger
ssh root@69.62.108.82 "ollama pull llama3.2:1b"  # Au lieu de qwen2.5:14b
```

---

## 📊 Monitoring et logs

### Logs du service

```bash
# Logs en temps réel
ssh root@69.62.108.82 "journalctl -u ollama -f"

# Dernières 100 lignes
ssh root@69.62.108.82 "journalctl -u ollama -n 100 --no-pager"

# Logs depuis une date
ssh root@69.62.108.82 "journalctl -u ollama --since '2025-10-15 10:00:00'"
```

### Logs Nginx

```bash
# Access logs
ssh root@69.62.108.82 "tail -f /var/log/nginx/ollama-access.log"

# Error logs
ssh root@69.62.108.82 "tail -f /var/log/nginx/ollama-error.log"
```

### Statistiques d'utilisation

```bash
# Voir l'utilisation CPU/RAM
ssh root@69.62.108.82 "top -b -n 1 | grep ollama"

# Voir les processus Ollama
ssh root@69.62.108.82 "ps aux | grep ollama"
```

---

## 🔐 Sécurité

### Considérations importantes

1. **Pas d'authentification native** : Ollama n'a pas d'auth built-in
2. **CORS ouvert** : Config actuelle permet tous les origins
3. **Rate limiting** : Pas de limite de requêtes

### Ajouter une authentification (optionnel)

#### Option 1 : Basic Auth Nginx

```nginx
location / {
    auth_basic "Ollama API";
    auth_basic_user_file /etc/nginx/.htpasswd;

    proxy_pass http://127.0.0.1:11434;
    # ... reste de la config
}
```

```bash
# Créer le fichier de mots de passe
ssh root@69.62.108.82 "apt install -y apache2-utils"
ssh root@69.62.108.82 "htpasswd -c /etc/nginx/.htpasswd admin"
```

#### Option 2 : API Key via header

```nginx
location / {
    if ($http_x_api_key != "votre-secret-key") {
        return 403;
    }

    proxy_pass http://127.0.0.1:11434;
    # ... reste de la config
}
```

**Utilisation** :
```bash
curl -H "X-API-Key: votre-secret-key" https://ollama.srv759970.hstgr.cloud/api/tags
```

---

## 📚 Ressources

- **Ollama Documentation** : https://github.com/ollama/ollama
- **API Reference** : https://github.com/ollama/ollama/blob/main/docs/api.md
- **Modèles disponibles** : https://ollama.com/library
- **Guide Nginx** : [GUIDE_NGINX.md](./GUIDE_NGINX.md)

---

## 📝 Checklist déploiement Ollama

- [ ] Ollama installé (`curl -fsSL https://ollama.com/install.sh | sh`)
- [ ] Service systemd actif (`systemctl enable --now ollama`)
- [ ] Au moins un modèle installé (`ollama pull llama3.2:1b`)
- [ ] Service écoute sur 11434 (`netstat -tulpn | grep 11434`)
- [ ] Certificat SSL obtenu (Certbot standalone)
- [ ] Config Nginx créée avec timeouts augmentés
- [ ] Config Nginx testée (`nginx -t`)
- [ ] Site activé (symlink dans `sites-enabled/`)
- [ ] Nginx rechargé (`systemctl reload nginx`)
- [ ] API accessible via HTTPS
- [ ] Test génération de texte réussi

---

**Dernière mise à jour** : Octobre 2025
**Version** : 1.0
**Status** : ✅ Opérationnel sur srv759970.hstgr.cloud
**URL publique** : https://ollama.srv759970.hstgr.cloud
**Modèles installés** : 4 (qwen2.5:14b, qwen2.5vl:7b, mistral:7b, llama3.2:1b)
