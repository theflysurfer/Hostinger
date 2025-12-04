# Stack Jellyfin + Real-Debrid - Média Server Automatique

Stack Docker complète pour un serveur média automatisé avec streaming Real-Debrid et sous-titres automatiques.

## 🎯 Vue d'ensemble

Cette stack contient **7 services** qui fonctionnent ensemble :

1. **Jellyfin** : Serveur média (interface type Netflix)
2. **Radarr** : Gestion automatique des films
3. **Sonarr** : Gestion automatique des séries
4. **Prowlarr** : Gestion des indexers torrent
5. **RDTClient** : Client Real-Debrid (crée des symlinks)
6. **Bazarr** : Téléchargement automatique de sous-titres
7. **Jellyseerr** : Interface de requêtes utilisateur

## 📋 Prérequis

- VPS avec Docker et Docker Compose
- Compte Real-Debrid actif (~4€/mois)
- Au moins 2 GB de RAM disponible
- 10 GB d'espace disque pour les configs

## 🚀 Installation rapide

### 1. Créer le dossier des symlinks

```bash
ssh automation@69.62.108.82

# Créer le point de montage pour Real-Debrid
sudo mkdir -p /mnt/realdebrid
sudo chown -R 1000:1000 /mnt/realdebrid
```

### 2. Copier les fichiers sur le VPS

```bash
# Depuis ton PC Windows
scp -r "C:\Users\julien\OneDrive\Coding\_référentiels de code\Hostinger\apps\14-media-servers\jellyfin-stack" automation@69.62.108.82:~/apps/14-media-servers/
```

### 3. Lancer la stack

```bash
ssh automation@69.62.108.82

cd ~/apps/14-media-servers/jellyfin-stack

# Lancer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f
```

### 4. Vérifier que tout tourne

```bash
docker-compose ps
```

Tu devrais voir les 7 services avec le statut "Up".

## ⚙️ Configuration initiale

### Étape 1 : RDTClient (Real-Debrid)

1. Ouvre http://VPS_IP:6500
2. Va dans **Settings**
3. Configure :
   - **Real-Debrid API Key** : Colle ton API key depuis https://real-debrid.com/apitoken
   - **Download Path** : `/data/downloads`
   - **Mapped Path** : `/mnt/realdebrid`
   - Coche **Use Symlinks**
4. Clique sur **Save**

### Étape 2 : Prowlarr (Indexers)

1. Ouvre http://VPS_IP:9696
2. Va dans **Settings → Indexers → Add Indexer**
3. Ajoute ces indexers :
   - **YTS** (films)
   - **EZTV** (séries)
   - **1337x** (général)
   - **ThePirateBay** (général)
   - **RARBG** (si disponible)
4. Pour chaque indexer, configure le **API Key** si nécessaire

### Étape 3 : Radarr (Films)

1. Ouvre http://VPS_IP:7878
2. **Settings → Media Management** :
   - Coche **Rename Movies**
   - Format : `{Movie Title} ({Release Year})`
3. **Settings → Download Clients → Add → qBittorrent** :
   - **Host** : `rdtclient`
   - **Port** : `6500`
   - **Category** : `radarr`
4. **Settings → Indexers → Add → Prowlarr** :
   - **Prowlarr Server** : `http://prowlarr:9696`
   - Copie l'API Key depuis Prowlarr
5. **Movies → Add Root Folder** :
   - `/data/movies`

### Étape 4 : Sonarr (Séries)

1. Ouvre http://VPS_IP:8989
2. **Settings → Media Management** :
   - Coche **Rename Episodes**
   - Format : `{Series Title} - S{season:00}E{episode:00} - {Episode Title}`
3. **Settings → Download Clients → Add → qBittorrent** :
   - **Host** : `rdtclient`
   - **Port** : `6500`
   - **Category** : `sonarr`
4. **Settings → Indexers → Add → Prowlarr** :
   - **Prowlarr Server** : `http://prowlarr:9696`
   - Copie l'API Key depuis Prowlarr
5. **Series → Add Root Folder** :
   - `/data/tvshows`

### Étape 5 : Bazarr (Sous-titres)

1. Ouvre http://VPS_IP:6767
2. **Settings → Languages** :
   - **Languages Filter** : Français, Anglais (ou autres)
   - **Default Enabled** : Oui
3. **Settings → Providers** :
   - Active **OpenSubtitles** (crée un compte sur opensubtitles.com)
   - Active **Subscene**
   - Active **Podnapisi**
4. **Settings → Sonarr** :
   - **Address** : `http://sonarr:8989`
   - Copie l'API Key depuis Sonarr
   - Teste la connexion
5. **Settings → Radarr** :
   - **Address** : `http://radarr:7878`
   - Copie l'API Key depuis Radarr
   - Teste la connexion

### Étape 6 : Jellyfin (Serveur média)

1. Ouvre http://VPS_IP:8096
2. Suis l'assistant de configuration :
   - Crée un compte admin
   - **Add Media Library → Movies** :
     - **Folder** : `/media/movies`
   - **Add Media Library → Shows** :
     - **Folder** : `/media/tvshows`
3. Scan la bibliothèque (vide pour l'instant)

### Étape 7 : Jellyseerr (Requêtes)

1. Ouvre http://VPS_IP:5055
2. **Sign in with Jellyfin** :
   - **Jellyfin URL** : `http://jellyfin:8096`
   - Connecte-toi avec ton compte Jellyfin admin
3. **Configure Services** :
   - **Radarr** :
     - **Server** : `http://radarr:7878`
     - Copie l'API Key depuis Radarr
     - **Root Folder** : `/data/movies`
     - **Quality Profile** : Any
   - **Sonarr** :
     - **Server** : `http://sonarr:8989`
     - Copie l'API Key depuis Sonarr
     - **Root Folder** : `/data/tvshows`
     - **Quality Profile** : Any
4. Termine la configuration

## 🎬 Utilisation

### Demander un film ou une série

1. Va sur http://VPS_IP:5055
2. Cherche un film ou une série
3. Clique sur **Request**
4. Attends 10-30 secondes

### Workflow automatique

```
Request → Radarr/Sonarr cherche torrent
       → RDTClient ajoute à Real-Debrid
       → Symlink créé dans /mnt/realdebrid
       → Bazarr télécharge sous-titres
       → Jellyfin détecte le nouveau média
       → Prêt à regarder !
```

## 🛠️ Commandes utiles

### Gérer la stack

```bash
# Démarrer tous les services
docker-compose up -d

# Arrêter tous les services
docker-compose down

# Redémarrer un service spécifique
docker-compose restart jellyfin

# Voir les logs
docker-compose logs -f jellyfin

# Voir l'état
docker-compose ps

# Update tous les services
docker-compose pull && docker-compose up -d
```

### Gérer individuellement

```bash
# Arrêter Jellyfin seulement
docker-compose stop jellyfin

# Redémarrer Radarr
docker-compose restart radarr

# Voir les logs de Bazarr
docker logs bazarr -f --tail 100
```

### Désactiver la stack

```bash
# Arrêter sans supprimer les configs
docker-compose stop

# Supprimer les containers (garde les configs)
docker-compose down

# Supprimer TOUT (containers + volumes)
docker-compose down -v
```

## 🌐 URLs et Ports

| Service | Port | URL | Description |
|---------|------|-----|-------------|
| Jellyfin | 8096 | http://VPS_IP:8096 | Interface principale |
| Jellyseerr | 5055 | http://VPS_IP:5055 | Faire des requêtes |
| Radarr | 7878 | http://VPS_IP:7878 | Gestion films |
| Sonarr | 8989 | http://VPS_IP:8989 | Gestion séries |
| Prowlarr | 9696 | http://VPS_IP:9696 | Gestion indexers |
| RDTClient | 6500 | http://VPS_IP:6500 | Real-Debrid |
| Bazarr | 6767 | http://VPS_IP:6767 | Sous-titres |

## 🔒 Sécuriser avec Nginx + SSL

Une fois la stack fonctionnelle, tu peux exposer Jellyfin et Jellyseerr en HTTPS :

```bash
# Créer les configs Nginx
sudo nano /etc/nginx/sites-available/jellyfin.srv759970.hstgr.cloud
sudo nano /etc/nginx/sites-available/jellyseerr.srv759970.hstgr.cloud

# Activer les sites
sudo ln -s /etc/nginx/sites-available/jellyfin.srv759970.hstgr.cloud /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/jellyseerr.srv759970.hstgr.cloud /etc/nginx/sites-enabled/

# Obtenir les certificats SSL
sudo certbot --nginx -d jellyfin.srv759970.hstgr.cloud
sudo certbot --nginx -d jellyseerr.srv759970.hstgr.cloud

# Recharger Nginx
sudo systemctl reload nginx
```

## 📊 Ressources requises

| Service | RAM | CPU | Disk |
|---------|-----|-----|------|
| Jellyfin | 512 MB | 10% | 500 MB |
| Radarr | 256 MB | 5% | 200 MB |
| Sonarr | 256 MB | 5% | 200 MB |
| Prowlarr | 128 MB | 5% | 100 MB |
| RDTClient | 128 MB | 5% | 100 MB |
| Bazarr | 128 MB | 5% | 100 MB |
| Jellyseerr | 256 MB | 5% | 200 MB |
| **TOTAL** | **~1.5 GB** | **40%** | **~1.5 GB** |

## 🐛 Troubleshooting

### Jellyfin ne voit pas les médias

```bash
# Vérifier les permissions
sudo chown -R 1000:1000 /mnt/realdebrid

# Vérifier les symlinks
ls -la /mnt/realdebrid/movies
ls -la /mnt/realdebrid/tvshows

# Rescanner Jellyfin
# Dashboard → Libraries → Scan All Libraries
```

### RDTClient ne crée pas de symlinks

1. Vérifie que **Use Symlinks** est coché dans RDTClient Settings
2. Vérifie que le **Mapped Path** est `/mnt/realdebrid`
3. Teste un download manuel dans RDTClient

### Bazarr ne trouve pas de sous-titres

1. Vérifie que tu as créé un compte OpenSubtitles
2. Active plusieurs providers (Subscene, Podnapisi)
3. Baisse le **Minimum Score** à 60%

### Services ne communiquent pas entre eux

```bash
# Vérifier le réseau Docker
docker network ls
docker network inspect jellyfin-stack_media

# Redémarrer la stack
docker-compose down && docker-compose up -d
```

## 💡 Conseils

1. **Ne pas télécharger** : Avec Real-Debrid, tout est streamé, rien n'est stocké localement
2. **Qualité** : Configure "Any" ou "1080p" comme quality profile par défaut
3. **Sous-titres** : Bazarr télécharge automatiquement, mais tu peux forcer un download manuel
4. **Multi-utilisateurs** : Chaque personne peut avoir son compte Jellyfin
5. **Apps mobiles** : Utilise Jellyfin pour Android/iOS pour regarder sur mobile

## 🎉 Terminé !

Ta stack est maintenant prête ! Tu peux :

1. Ouvrir Jellyseerr (http://VPS_IP:5055)
2. Chercher un film/série
3. Cliquer sur Request
4. Attendre 10-30 secondes
5. Ouvrir Jellyfin et regarder !

---

**Coût total** : ~4€/mois (Real-Debrid uniquement)
