# Kavita - Universal Ebook/Comic/Manga Server

**Status**: 🟢 Production
**URL**: https://kavita.srv759970.hstgr.cloud
**Port**: 5000

## Description

Kavita est un serveur média universel pour :
- 📚 **Ebooks** (EPUB, PDF, MOBI, AZW3)
- 🎨 **Comics** (CBZ, CBR, CB7)
- 📖 **Manga**
- 📄 **Documents**

## Architecture

```
/home/automation/
├── apps/14-media-servers/kavita/
│   ├── docker-compose.yml
│   ├── config/           # Configuration Kavita
│   └── README.md
└── calibre-library/      # Bibliothèque Calibre syncée depuis OneDrive
    ├── metadata.db
    └── [Auteurs]/
        └── [Livres]/
```

## Prérequis

1. **rclone configuré** pour sync OneDrive
2. **Bibliothèque Calibre** dans `/home/automation/calibre-library`
3. **Nginx reverse proxy** configuré

## Installation

### 1. Se connecter au VPS

```bash
ssh automation@69.62.108.82
```

### 2. Créer la structure

```bash
mkdir -p ~/apps/14-media-servers/kavita
cd ~/apps/14-media-servers/kavita
```

### 3. Déployer les fichiers

Copier `docker-compose.yml` depuis le dépôt local.

### 4. Créer le réseau Docker

```bash
docker network create web 2>/dev/null || true
```

### 5. Lancer Kavita

```bash
docker-compose up -d
```

### 6. Vérifier les logs

```bash
docker logs kavita --tail 50 -f
```

## Configuration Nginx

Fichier : `/etc/nginx/sites-available/kavita.srv759970.hstgr.cloud`

```nginx
server {
    listen 80;
    server_name kavita.srv759970.hstgr.cloud;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name kavita.srv759970.hstgr.cloud;

    # SSL Configuration (géré par Certbot)
    ssl_certificate /etc/letsencrypt/live/kavita.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/kavita.srv759970.hstgr.cloud/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Proxy to Kavita
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Access logs
    access_log /var/log/nginx/kavita-access.log;
    error_log /var/log/nginx/kavita-error.log;
}
```

## Première Configuration

1. **Accéder à Kavita** : https://kavita.srv759970.hstgr.cloud
2. **Créer un compte admin** (premier utilisateur)
3. **Ajouter une bibliothèque** :
   - Name: "Calibre Library"
   - Folder: `/manga` (ou `/books`)
   - Type: Mixed (Ebooks + Comics)
4. **Scanner la bibliothèque**

## Sync OneDrive

Voir le script de sync dans `scripts/sync-calibre-onedrive.sh`

## Maintenance

### Restart

```bash
docker restart kavita
```

### Update

```bash
cd ~/apps/14-media-servers/kavita
docker-compose pull
docker-compose up -d
```

### Logs

```bash
docker logs kavita --tail 100 -f
```

### Rescan Library

Depuis l'interface web : Settings → Libraries → Scan All

## Troubleshooting

### Port déjà utilisé

```bash
sudo lsof -i :5000
```

### Permissions

```bash
sudo chown -R 1000:1000 /home/automation/calibre-library
```

### Kavita ne voit pas les fichiers

Vérifier les montages :
```bash
docker exec kavita ls /manga
```

## Accès Mobile

Kavita a des apps mobiles :
- **iOS** : Pas d'app officielle, utiliser le web
- **Android** : Tachiyomi avec extension Kavita

## Features

- ✅ Lecture en ligne (EPUB, PDF)
- ✅ Gestion collections/séries
- ✅ Suivi progression
- ✅ Multi-utilisateurs
- ✅ OPDS feed (pour apps externes)
- ✅ API REST

## URLs Utiles

- **Web UI** : https://kavita.srv759970.hstgr.cloud
- **API Docs** : https://kavita.srv759970.hstgr.cloud/api/swagger
- **OPDS** : https://kavita.srv759970.hstgr.cloud/api/opds/

## Notes

- La bibliothèque Calibre est en **lecture seule** pour Kavita
- Utiliser Calibre pour gérer les métadonnées
- Kavita scanne automatiquement les changements
