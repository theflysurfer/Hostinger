# Installation Kavita + rclone OneDrive Sync

Guide complet pour installer Kavita avec synchronisation automatique depuis OneDrive.

## 🎯 Vue d'ensemble

1. **rclone** : Synchronise la bibliothèque Calibre depuis OneDrive
2. **Kavita** : Serveur ebook/comics accessible via web
3. **Nginx** : Reverse proxy avec SSL
4. **Cron** : Sync automatique toutes les heures

## 📋 Prérequis

- VPS Hostinger avec Ubuntu 24.04
- Compte OneDrive avec bibliothèque Calibre
- Accès SSH au VPS
- Docker et docker-compose installés

## 🚀 Installation Étape par Étape

### Étape 1 : Configurer rclone sur Windows

Sur ton PC Windows :

```powershell
# Installer rclone (si pas déjà installé)
winget install Rclone.Rclone

# Configurer OneDrive
rclone config

# Suivre les instructions :
# n) New remote
# name> onedrive
# Storage> microsoft onedrive (choisir le numéro)
# client_id> (laisser vide)
# client_secret> (laisser vide)
# region> 1 (Microsoft Cloud Global)
# Edit advanced config? n
# Use web browser? y (va ouvrir le navigateur)
```

Authentifie-toi dans le navigateur.

### Étape 2 : Copier la config rclone sur le VPS

**Méthode A - Via SCP (recommandé)** :

```powershell
# Sur Windows, copier le fichier de config
scp C:\Users\julien\.config\rclone\rclone.conf automation@69.62.108.82:~/.config/rclone/
```

**Méthode B - Copier-coller** :

```powershell
# Sur Windows, afficher la config
rclone config show

# Copier toute la section [onedrive]
```

Puis sur le VPS :

```bash
ssh automation@69.62.108.82

mkdir -p ~/.config/rclone
nano ~/.config/rclone/rclone.conf
# Coller la config, sauvegarder (Ctrl+O, Ctrl+X)
```

### Étape 3 : Installer rclone sur le VPS

```bash
ssh automation@69.62.108.82

# Installer rclone
curl https://rclone.org/install.sh | sudo bash

# Vérifier l'installation
rclone version

# Tester la connexion OneDrive
rclone lsd onedrive:

# Vérifier le dossier Calibre
rclone lsd "onedrive:Calibre/Calibre Library"
```

### Étape 4 : Copier les scripts sur le VPS

Depuis ton PC, copier les fichiers :

```bash
# Créer la structure
ssh automation@69.62.108.82 "mkdir -p ~/apps/14-media-servers/kavita ~/scripts ~/logs"

# Copier docker-compose.yml
scp "C:\Users\julien\OneDrive\Coding\_référentiels de code\Hostinger\apps\14-media-servers\kavita\docker-compose.yml" automation@69.62.108.82:~/apps/14-media-servers/kavita/

# Copier les scripts
scp "C:\Users\julien\OneDrive\Coding\_référentiels de code\Hostinger\scripts\sync-calibre-onedrive.sh" automation@69.62.108.82:~/scripts/

scp "C:\Users\julien\OneDrive\Coding\_référentiels de code\Hostinger\scripts\setup-rclone-onedrive.sh" automation@69.62.108.82:~/scripts/

# Rendre les scripts exécutables
ssh automation@69.62.108.82 "chmod +x ~/scripts/*.sh"
```

### Étape 5 : Premier sync de la bibliothèque

```bash
ssh automation@69.62.108.82

# Lancer le script de setup
bash ~/scripts/setup-rclone-onedrive.sh

# Ou sync manuel direct
bash ~/scripts/sync-calibre-onedrive.sh
```

**Attention** : Le premier sync peut prendre 10-30 minutes selon la taille de ta bibliothèque (~3-4 GB).

### Étape 6 : Installer Kavita

```bash
# Se connecter au VPS
ssh automation@69.62.108.82

# Aller dans le dossier Kavita
cd ~/apps/14-media-servers/kavita

# Créer le réseau Docker
docker network create web 2>/dev/null || true

# Lancer Kavita
docker-compose up -d

# Vérifier les logs
docker logs kavita --tail 50 -f
```

### Étape 7 : Configurer Nginx

```bash
# Copier la config Nginx
sudo cp ~/infrastructure/nginx/configs/sites-available/kavita.srv759970.hstgr.cloud /etc/nginx/sites-available/

# Créer le lien symbolique
sudo ln -s /etc/nginx/sites-available/kavita.srv759970.hstgr.cloud /etc/nginx/sites-enabled/

# Obtenir certificat SSL
sudo certbot --nginx -d kavita.srv759970.hstgr.cloud

# Tester la config
sudo nginx -t

# Recharger Nginx
sudo systemctl reload nginx
```

### Étape 8 : Configuration initiale Kavita

1. Ouvre https://kavita.srv759970.hstgr.cloud
2. Crée un compte admin
3. Va dans **Settings → Libraries → Add Library**
4. Configure :
   - **Name** : "Calibre Library"
   - **Folder Paths** : `/manga` (ou `/books`)
   - **Type** : Mixed (Ebooks + Comics)
   - **Scan** : Enable
5. Clique sur **Scan Library Now**

## 🔄 Synchronisation Automatique

Le script `sync-calibre-onedrive.sh` est configuré pour tourner automatiquement toutes les heures via cron.

Vérifier le cron :

```bash
crontab -l
```

Devrait afficher :

```
0 * * * * /home/automation/scripts/sync-calibre-onedrive.sh >> /home/automation/logs/calibre-sync-cron.log 2>&1
```

## 🛠️ Commandes Utiles

### Sync manuel

```bash
bash ~/scripts/sync-calibre-onedrive.sh
```

### Voir les logs

```bash
tail -f ~/logs/calibre-sync.log
tail -f ~/logs/calibre-sync-cron.log
```

### Restart Kavita

```bash
docker restart kavita
```

### Update Kavita

```bash
cd ~/apps/14-media-servers/kavita
docker-compose pull
docker-compose up -d
```

### Vérifier l'espace disque

```bash
du -sh /home/automation/calibre-library
df -h
```

### Rescan bibliothèque

Depuis l'interface web : **Settings → Libraries → Scan All**

## 🔍 Troubleshooting

### rclone : "Failed to ls"

```bash
# Retester l'auth
rclone config reconnect onedrive:
```

### Kavita ne voit pas les fichiers

```bash
# Vérifier les permissions
sudo chown -R 1000:1000 /home/automation/calibre-library

# Vérifier les montages Docker
docker exec kavita ls /manga
```

### Sync trop lent

Éditer `sync-calibre-onedrive.sh` :
- Augmenter `--transfers` (ex: 8)
- Augmenter `--checkers` (ex: 16)

### Port 5000 déjà utilisé

```bash
sudo lsof -i :5000
# Changer le port dans docker-compose.yml
```

## 📊 Statistiques

Après installation, tu devrais avoir :

- **Bibliothèque Calibre** : ~3-4 GB sur le VPS
- **Kavita** : ~200 MB (image Docker)
- **Sync** : toutes les heures automatiquement
- **Accès** : https://kavita.srv759970.hstgr.cloud

## 🎉 Terminé !

Ta bibliothèque Calibre est maintenant accessible depuis n'importe où via Kavita !

**URLs** :
- Web UI : https://kavita.srv759970.hstgr.cloud
- API : https://kavita.srv759970.hstgr.cloud/api/swagger
- OPDS : https://kavita.srv759970.hstgr.cloud/api/opds/

**Prochaines étapes** :
- [ ] Installer Stremio + Torrentio
- [ ] Configurer Real-Debrid
