# 📸 Guide - Gestion Photos : Dropbox + digiKam + Lychee

## 🎯 Architecture

```
[ Dropbox 600 Go (stockage maître) ]
            |
            | (rclone mount)
            v
   VPS Hostinger (srv759970)
            |
            +-- MariaDB (catalogue digiKam) :3306
            +-- Lychee (galerie web) :8080
            +-- Samba (partage réseau) :445
            |
            v
   [ PC Windows ]
       - digiKam → connexion MariaDB
       - Lecteur Z:\ → partage Samba
```

---

## 📋 Composants

### VPS Hostinger

1. **MariaDB 11.5** (port 3306)
   - Base de données `digikam` pour le catalogue central
   - Accessible depuis Windows pour digiKam

2. **Lychee** (port 8080)
   - Galerie photos web moderne
   - Lit les photos depuis `/mnt/dropbox` (read-only)
   - Base de données séparée (lychee-mariadb)

3. **Samba** (port 445)
   - Partage réseau Windows
   - Expose `/mnt/dropbox` comme `\\srv759970\photos`
   - Montable comme lecteur Z:\ sous Windows

4. **rclone**
   - Monte Dropbox sur `/mnt/dropbox`
   - Cache activé pour performances
   - Read-only (sécurité)

### PC Windows

1. **digiKam**
   - Connexion à MariaDB distant (VPS)
   - Accès aux photos via Z:\ (Samba)
   - Catalogage, tags, reconnaissance faciale

2. **Lecteur réseau Z:\**
   - Monté depuis `\\69.62.108.82\photos`
   - Accès aux photos Dropbox via Samba

---

## 🚀 Installation sur VPS

### 1. Configuration rclone pour Dropbox

```bash
ssh root@69.62.108.82

# Configuration interactive de Dropbox
rclone config

# Répondre :
# n (new remote)
# name> dropbox
# Storage> dropbox (choisir dans la liste)
# client_id> (laisser vide, appuyer sur Entrée)
# client_secret> (laisser vide)
# Follow the link to authorize... → copier l'URL et autoriser dans le navigateur
# Coller le token
# yes (pour confirmer)
# q (quit)
```

**⚠️ Important** : L'autorisation Dropbox nécessite un navigateur. Si vous êtes en SSH, utilisez :

```bash
rclone config create dropbox dropbox config_token "YOUR_TOKEN"
```

Ou configurez rclone depuis votre PC Windows puis copiez `~/.config/rclone/rclone.conf` vers le VPS.

### 2. Créer le point de montage

```bash
mkdir -p /mnt/dropbox

# Test du montage (foreground)
rclone mount dropbox:/Photos /mnt/dropbox \
  --vfs-cache-mode full \
  --dir-cache-time 72h \
  --tpslimit 12 \
  --allow-other \
  --read-only

# Si ça fonctionne, Ctrl+C puis créer le service systemd
```

### 3. Créer le service rclone systemd

```bash
cat > /etc/systemd/system/rclone-dropbox.service << 'EOF'
[Unit]
Description=RClone mount Dropbox
After=network-online.target
Wants=network-online.target

[Service]
Type=notify
ExecStartPre=/bin/mkdir -p /mnt/dropbox
ExecStart=/usr/bin/rclone mount dropbox:/Photos /mnt/dropbox \
  --config=/root/.config/rclone/rclone.conf \
  --vfs-cache-mode full \
  --vfs-cache-max-size 50G \
  --vfs-cache-max-age 168h \
  --dir-cache-time 72h \
  --poll-interval 15s \
  --tpslimit 12 \
  --allow-other \
  --read-only \
  --log-level INFO \
  --log-file /var/log/rclone-dropbox.log
ExecStop=/bin/fusermount -u /mnt/dropbox
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

# Activer le service
systemctl daemon-reload
systemctl enable rclone-dropbox
systemctl start rclone-dropbox
systemctl status rclone-dropbox
```

### 4. Démarrer les services Docker

```bash
cd /var/www/photo-management
docker-compose up -d

# Vérifier les conteneurs
docker ps
docker logs lychee
docker logs digikam-mariadb
docker logs samba
```

### 5. Configuration Nginx pour Lychee

```bash
cat > /etc/nginx/sites-available/lychee << 'EOF'
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name photos.srv759970.hstgr.cloud;

    # SSL
    ssl_certificate /etc/letsencrypt/live/photos.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/photos.srv759970.hstgr.cloud/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Logs
    access_log /var/log/nginx/lychee-access.log;
    error_log /var/log/nginx/lychee-error.log;

    # Basic Auth
    include snippets/basic-auth.conf;

    # Proxy vers Lychee
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Upload de fichiers volumineux
        client_max_body_size 1G;
    }
}

# HTTP -> HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name photos.srv759970.hstgr.cloud;
    return 301 https://$host$request_uri;
}
EOF

# Obtenir certificat SSL
systemctl stop nginx
certbot certonly --standalone -d photos.srv759970.hstgr.cloud \
  --non-interactive --agree-tos --email julien.fernandez.work@gmail.com
systemctl start nginx

# Activer le site
ln -sf /etc/nginx/sites-available/lychee /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

---

## 💻 Configuration Windows

### 1. Monter le partage Samba

1. Ouvrir **Explorateur Windows**
2. Clic droit sur **Ce PC** → **Connecter un lecteur réseau**
3. Configuration :
   - **Lecteur** : `Z:`
   - **Dossier** : `\\69.62.108.82\photos`
   - **Se reconnecter à l'ouverture de session** : ✅
   - **Se connecter avec d'autres informations** : ✅
4. Identifiants :
   - **Utilisateur** : `julien`
   - **Mot de passe** : `SambaPhotos2025`

Le lecteur `Z:\` apparaît avec toutes vos photos Dropbox.

### 2. Installer et configurer digiKam

1. Télécharger **digiKam** : https://www.digikam.org/download/
2. Installer (version Windows 64-bit)
3. Au premier lancement, choisir :
   - **Base de données MySQL/MariaDB** (pas SQLite)
4. Configuration de la base de données :
   - **Type** : MySQL Internal
   - **Nom** : `digikam`
   - **Hôte** : `69.62.108.82`
   - **Port** : `3306`
   - **Utilisateur** : `dkuser`
   - **Mot de passe** : `DigiKamDB2025`
5. Test de connexion → **OK**
6. **Collections** → Ajouter `Z:\` comme collection d'images
7. digiKam va scanner et cataloguer vos photos

---

## 🔧 Utilisation

### digiKam (Windows)

- **Catalogage** : Tags, notes, géolocalisation
- **Reconnaissance faciale** : Détection automatique des personnes
- **Recherche avancée** : Par date, lieu, tag, personne
- **Édition** : Retouche non-destructive
- **Export** : Vers web, email, réseaux sociaux

### Lychee (Web)

- **URL** : https://photos.srv759970.hstgr.cloud
- **Auth** : Basic Auth (julien/DevAccess2025) puis compte Lychee
- **Import** : `php artisan lychee:sync --import_via_symlink`
- **Partage** : Albums publics/privés avec liens

### Synchronisation Lychee

```bash
ssh root@69.62.108.82
docker exec -it lychee /bin/bash
php artisan lychee:sync --import_via_symlink
```

---

## 🔐 Identifiants

### VPS

| Service | Port | User | Password |
|---------|------|------|----------|
| **MariaDB digiKam** | 3306 | dkuser | DigiKamDB2025 |
| **MariaDB Lychee** | - (interne) | lychee | LycheeDB2025 |
| **Samba** | 445 | julien | SambaPhotos2025 |
| **Lychee Web** | 8080/HTTPS | (à créer) | (à créer) |

### URLs

- **Lychee** : https://photos.srv759970.hstgr.cloud
- **Basic Auth** : julien / DevAccess2025

---

## 🛠️ Commandes utiles

### rclone

```bash
# Vérifier le montage
ls -la /mnt/dropbox
df -h /mnt/dropbox

# Voir les logs
tail -f /var/log/rclone-dropbox.log

# Redémarrer le service
systemctl restart rclone-dropbox
```

### Docker

```bash
cd /var/www/photo-management

# Voir les logs
docker-compose logs -f lychee
docker-compose logs -f digikam-mariadb

# Redémarrer un service
docker-compose restart lychee

# Tout arrêter
docker-compose down

# Tout démarrer
docker-compose up -d
```

### MariaDB

```bash
# Se connecter à la base digiKam
docker exec -it digikam-mariadb mysql -u dkuser -pDigiKamDB2025 digikam

# Backup de la base
docker exec digikam-mariadb mysqldump -u dkuser -pDigiKamDB2025 digikam > digikam-backup-$(date +%Y%m%d).sql
```

---

## 📊 Performance et cache

### rclone cache

- **Taille max** : 50 Go (`--vfs-cache-max-size 50G`)
- **Durée** : 7 jours (`--vfs-cache-max-age 168h`)
- **Localisation** : `/root/.cache/rclone/`

### Optimisations

- Cache répertoires : 72h
- Limite requêtes Dropbox : 12/s
- Poll interval : 15s (détection changements)

---

## ⚠️ Points d'attention

### Sécurité

- **MariaDB exposé** : Port 3306 ouvert sur Internet
  - Firewall recommandé : `ufw allow from VOTRE_IP to any port 3306`
  - Ou VPN (WireGuard) pour accès sécurisé
- **Samba exposé** : Port 445 ouvert
  - Mot de passe fort obligatoire
  - VPN recommandé

### Sauvegardes

- **Base digiKam** : Critique ! Contient tout le catalogage
  - Backup quotidien recommandé (cron + mysqldump)
- **Dropbox** : Stockage maître (600 Go)
  - Déjà sauvegardé par Dropbox
- **Configuration rclone** : `/root/.config/rclone/rclone.conf`
  - À sauvegarder (contient tokens d'accès)

### Limites

- **Dropbox API** : Limites de débit (d'où `--tpslimit 12`)
- **Lecture seule** : `/mnt/dropbox` en read-only (modifications uniquement via Dropbox client)
- **Latence** : Accès réseau via rclone + Samba (plus lent que local)

---

## 🔄 Workflow recommandé

1. **Ajout de photos** :
   - Déposer dans Dropbox (client Windows/Mac/Mobile)
   - rclone détecte automatiquement (poll 15s)

2. **Catalogage** :
   - digiKam scanne automatiquement `Z:\`
   - Ajouter tags, personnes, localisation

3. **Partage web** :
   - Lancer sync Lychee (`lychee:sync`)
   - Créer albums et partager liens

4. **Backup** :
   - Dropbox : automatique
   - Base digiKam : dump SQL quotidien

---

## 📚 Ressources

- **rclone docs** : https://rclone.org/docs/
- **digiKam docs** : https://docs.digikam.org/
- **Lychee docs** : https://lycheeorg.github.io/docs/
- **Dropbox API** : https://www.dropbox.com/developers/documentation

---

**Créé le** : 2025-10-16
**Localisation** : /var/www/photo-management/
**Fichiers** : docker-compose.yml, rclone-dropbox.service
