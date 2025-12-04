# 🔍 Guide Apache Tika Server - Document Parsing API

## 📋 Vue d'ensemble

**Apache Tika** est un serveur de parsing de documents qui extrait du texte et des métadonnées depuis plus de 1000+ formats de fichiers (PDF, Office, HTML, images avec OCR, etc.).

**Version déployée** : Apache Tika 3.2.3 (latest-full avec Tesseract OCR)
**Type** : Docker container
**Port** : 9998
**API** : REST (HTTP)

---

## 📊 Informations du déploiement

| Propriété | Valeur |
|-----------|--------|
| **Serveur** | srv759970.hstgr.cloud (69.62.108.82) |
| **Chemin** | `/opt/tika-server/` |
| **Container** | `tika-server` |
| **Image Docker** | `apache/tika:latest-full` |
| **Port interne** | 9998 |
| **Port externe** | 9998 |
| **Auto-restart** | Oui (`unless-stopped`) |
| **Healthcheck** | Activé (30s interval) |

---

## 🚀 Accès et utilisation

### URL d'accès

**Production (HTTPS)** :
```bash
https://tika.srv759970.hstgr.cloud
```

**Local (sur le serveur)** :
```bash
http://localhost:9998
```

**Direct (non recommandé)** :
```bash
http://69.62.108.82:9998
```

**Recommandation** : Utilisez toujours l'URL HTTPS pour un accès sécurisé depuis l'extérieur.

---

## 🔧 Utilisation de l'API

### 1. Vérifier que le serveur fonctionne

```bash
curl -X GET https://tika.srv759970.hstgr.cloud/tika
```

**Réponse attendue** :
```
This is Tika Server (Apache Tika 3.2.3). Please PUT
```

### 2. Obtenir la version

```bash
curl -X GET https://tika.srv759970.hstgr.cloud/version
```

**Réponse** :
```
Apache Tika 3.2.3
```

### 3. Parser un document (extraire le texte)

```bash
curl -X PUT --data-binary @document.pdf \
  https://tika.srv759970.hstgr.cloud/tika \
  --header "Accept: text/plain"
```

**Formats supportés** :
- PDF
- Microsoft Office (Word, Excel, PowerPoint)
- OpenOffice/LibreOffice
- HTML, XML
- Images (avec OCR Tesseract) : PNG, JPG, TIFF
- Archives : ZIP, TAR, GZIP
- Et 1000+ autres formats

### 4. Extraire les métadonnées

```bash
curl -X PUT --data-binary @document.pdf \
  https://tika.srv759970.hstgr.cloud/meta \
  --header "Accept: application/json"
```

**Retourne** : Métadonnées JSON (auteur, date création, titre, format, etc.)

### 5. Détecter le type MIME d'un fichier

```bash
curl -X PUT --data-binary @unknown-file \
  https://tika.srv759970.hstgr.cloud/detect/stream
```

---

## 📚 Endpoints principaux

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/tika` | GET | Informations serveur |
| `/tika` | PUT | Extraire texte d'un document |
| `/meta` | PUT | Extraire métadonnées JSON |
| `/detect/stream` | PUT | Détecter type MIME |
| `/version` | GET | Version Apache Tika |
| `/tika/form` | POST | Upload multipart form |
| `/rmeta` | PUT | Métadonnées récursives (archives) |

**Documentation complète** : https://cwiki.apache.org/confluence/display/TIKA/TikaServer

---

## 🐳 Gestion du container

### Voir les logs

```bash
ssh root@69.62.108.82 "docker logs tika-server --tail=50 -f"
```

### Redémarrer le serveur

```bash
ssh root@69.62.108.82 "cd /opt/tika-server && docker-compose restart"
```

### Arrêter le serveur

```bash
ssh root@69.62.108.82 "cd /opt/tika-server && docker-compose down"
```

### Démarrer le serveur

```bash
ssh root@69.62.108.82 "cd /opt/tika-server && docker-compose up -d"
```

### Mettre à jour vers la dernière version

```bash
ssh root@69.62.108.82 "cd /opt/tika-server && docker-compose pull && docker-compose up -d"
```

### Vérifier l'état du container

```bash
ssh root@69.62.108.82 "docker ps | grep tika"
```

### Vérifier le healthcheck

```bash
ssh root@69.62.108.82 "docker inspect tika-server | grep -A 10 Health"
```

---

## 🌐 Configuration Nginx (optionnel - accès HTTPS public)

Pour exposer Tika via HTTPS avec un sous-domaine :

### Créer la configuration Nginx

```bash
ssh root@69.62.108.82 "cat > /etc/nginx/sites-available/tika" <<'EOF'
server {
    listen 80;
    server_name tika.srv759970.hstgr.cloud;

    location / {
        proxy_pass http://localhost:9998;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Augmenter timeout pour gros documents
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;

        # Augmenter taille max upload
        client_max_body_size 100M;
    }
}
EOF
```

### Activer le site

```bash
ssh root@69.62.108.82 "ln -s /etc/nginx/sites-available/tika /etc/nginx/sites-enabled/"
ssh root@69.62.108.82 "nginx -t && systemctl reload nginx"
```

### Obtenir un certificat SSL (Let's Encrypt)

```bash
ssh root@69.62.108.82 "certbot --nginx -d tika.srv759970.hstgr.cloud"
```

**URL finale** : `https://tika.srv759970.hstgr.cloud`

**✅ Statut** : Configuré et opérationnel

---

## 💡 Exemples d'utilisation

### Exemple Python

```python
import requests

# Parser un PDF
with open('document.pdf', 'rb') as f:
    response = requests.put(
        'https://tika.srv759970.hstgr.cloud/tika',
        data=f,
        headers={'Accept': 'text/plain'}
    )
    text = response.text
    print(text)

# Extraire métadonnées
with open('document.pdf', 'rb') as f:
    response = requests.put(
        'https://tika.srv759970.hstgr.cloud/meta',
        data=f,
        headers={'Accept': 'application/json'}
    )
    metadata = response.json()
    print(metadata)
```

### Exemple JavaScript (Node.js)

```javascript
const fs = require('fs');
const axios = require('axios');

// Parser un document
const fileBuffer = fs.readFileSync('document.pdf');

axios.put('https://tika.srv759970.hstgr.cloud/tika', fileBuffer, {
    headers: {
        'Accept': 'text/plain'
    }
})
.then(response => {
    console.log(response.data);
})
.catch(error => {
    console.error('Error:', error);
});
```

### Exemple cURL (batch de fichiers)

```bash
# Parser tous les PDFs d'un dossier
for file in *.pdf; do
    echo "Processing: $file"
    curl -X PUT --data-binary @"$file" \
        https://tika.srv759970.hstgr.cloud/tika \
        --header "Accept: text/plain" \
        > "${file%.pdf}.txt"
done
```

---

## ⚠️ Limites et recommandations

### Limites actuelles

- **Taille max documents** : Limitée par RAM disponible (~2GB recommandé par document)
- **Timeout** : 2 minutes par défaut (configurable)
- **Concurrent requests** : Limité par CPU/RAM serveur

### Bonnes pratiques

1. **Documents volumineux** : Traiter par batch ou augmenter timeout
2. **Sécurité** : Ne pas exposer directement sur Internet sans authentification
3. **Performance** : Pour volumes élevés, considérer un cluster Tika
4. **OCR** : Ralentit le traitement, désactiver si pas nécessaire

### Optimisation pour production

```yaml
# docker-compose.yml avec configuration optimisée
version: '3.8'
services:
  tika:
    image: apache/tika:latest-full
    container_name: tika-server
    ports:
      - "9998:9998"
    restart: unless-stopped
    environment:
      - TZ=Europe/Paris
      - TIKA_CONFIG=/tika-config.xml  # Config personnalisée
    volumes:
      - ./tika-config.xml:/tika-config.xml:ro
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
```

---

## 🔍 Troubleshooting

### Le serveur ne démarre pas

```bash
# Vérifier les logs
ssh root@69.62.108.82 "docker logs tika-server"

# Vérifier que le port n'est pas utilisé
ssh root@69.62.108.82 "netstat -tlnp | grep 9998"

# Rebuild from scratch
ssh root@69.62.108.82 "cd /opt/tika-server && docker-compose down && docker-compose pull && docker-compose up -d"
```

### Erreur "Out of Memory"

```bash
# Augmenter la RAM allouée au container
# Modifier docker-compose.yml :
deploy:
  resources:
    limits:
      memory: 4G
```

### Timeout sur gros documents

```bash
# Augmenter le timeout dans la requête
curl -X PUT --data-binary @large.pdf \
    --max-time 600 \
    http://69.62.108.82:9998/tika
```

### Problème OCR (images)

```bash
# Vérifier que Tesseract est bien inclus (version full)
ssh root@69.62.108.82 "docker exec tika-server tesseract --version"
```

---

## 📊 Monitoring et maintenance

### Vérifier l'utilisation des ressources

```bash
ssh root@69.62.108.82 "docker stats tika-server --no-stream"
```

### Logs de parsing

```bash
ssh root@69.62.108.82 "docker logs tika-server --since 1h"
```

### Espace disque

```bash
ssh root@69.62.108.82 "docker system df"
```

---

## 🔗 Ressources utiles

- **Documentation officielle** : https://tika.apache.org/
- **API REST docs** : https://cwiki.apache.org/confluence/display/TIKA/TikaServer
- **Docker Hub** : https://hub.docker.com/r/apache/tika
- **GitHub** : https://github.com/apache/tika
- **Formats supportés** : https://tika.apache.org/2.6.0/formats.html

---

## 📝 Configuration actuelle (docker-compose.yml)

```yaml
version: '3.8'

services:
  tika:
    image: apache/tika:latest-full
    container_name: tika-server
    ports:
      - "9998:9998"
    restart: unless-stopped
    environment:
      - TZ=Europe/Paris
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9998/tika"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

## ✅ Checklist de déploiement

- [x] Container Docker créé et démarré
- [x] API accessible sur port 9998
- [x] Healthcheck configuré et opérationnel
- [x] Tests de parsing réussis
- [x] Logs vérifiés (pas d'erreur)
- [x] Nginx reverse proxy configuré
- [x] Certificat SSL installé (Let's Encrypt)
- [x] HTTPS fonctionnel sur https://tika.srv759970.hstgr.cloud
- [ ] (Optionnel) Authentification ajoutée

---

**Dernière mise à jour** : Octobre 2025
**Version Apache Tika** : 3.2.3
**Status** : ✅ En production
**Contact serveur** : root@69.62.108.82
