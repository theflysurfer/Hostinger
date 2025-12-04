# Déploiement Kavita + Stremio - Statut

**Date** : 2025-12-02
**VPS** : Hostinger srv759970 (69.62.108.82)
**Utilisateur** : automation

## ✅ Kavita - Serveur Ebook/Comics

### Installation complétée

- **URL** : https://kavita.srv759970.hstgr.cloud
- **Port Docker** : 5001 → 5000
- **Image** : kizaing/kavita:latest
- **Status** : ✅ En ligne et fonctionnel

### Configuration

```yaml
Services:
  - Kavita (Docker)
  - Nginx (reverse proxy avec SSL)
  - rclone (sync automatique OneDrive)
  - cron (sync toutes les heures)

Chemins:
  - Config : ~/apps/14-media-servers/kavita/config
  - Library : /home/automation/calibre-library
  - Scripts : ~/scripts/sync-calibre-onedrive.sh
  - Logs : ~/logs/calibre-sync.log
```

### Certificat SSL

- **Provider** : Let's Encrypt
- **Domain** : kavita.srv759970.hstgr.cloud
- **Expiration** : 2026-03-02
- **Renouvellement** : Automatique via Certbot

### Synchronisation OneDrive

- **Source** : OneDrive:/Calibre/Calibre Library
- **Destination** : /home/automation/calibre-library
- **Fréquence** : Toutes les heures (via cron)
- **Taille bibliothèque** : ~4 GB
- **Status premier sync** : ⏳ En cours (2784 fichiers listés, 65 à transférer)

### Fichiers déployés

```
~/apps/14-media-servers/kavita/
├── docker-compose.yml
└── config/ (généré par Kavita)

~/scripts/
├── sync-calibre-onedrive.sh
└── setup-rclone-onedrive.sh

~/.config/rclone/
└── rclone.conf

/etc/nginx/sites-available/
└── kavita.srv759970.hstgr.cloud
```

### Commandes utiles

```bash
# Restart Kavita
docker restart kavita

# Voir les logs
docker logs kavita -f

# Sync manuel
bash ~/scripts/sync-calibre-onedrive.sh

# Voir logs sync
tail -f ~/logs/calibre-sync.log

# Update Kavita
cd ~/apps/14-media-servers/kavita
docker-compose pull && docker-compose up -d
```

### Prochaines étapes Kavita

1. Attendre la fin du premier sync (~10-30 min)
2. Se connecter à https://kavita.srv759970.hstgr.cloud
3. Créer un compte admin
4. Configurer la bibliothèque :
   - Nom : "Calibre Library"
   - Path : `/manga` (ou `/books`)
   - Type : Mixed (Ebooks + Comics)
5. Scanner la bibliothèque

---

## 📺 Stremio + Torrentio + Real-Debrid

### Architecture choisie

**Important** : Pas de serveur VPS nécessaire ! Stremio fonctionne comme client.

### Installation recommandée

1. **Real-Debrid** (service premium)
   - URL : https://real-debrid.com/
   - Prix : ~4€/mois ou 16€/6 mois
   - Action : Créer compte et obtenir API token

2. **Stremio Client** (application)
   - Windows/Mac : https://www.stremio.com/downloads
   - Android/iOS : Play Store / App Store
   - Linux : .deb disponible

3. **Torrentio Addon** (configuration)
   - URL config : https://torrentio.strem.fun/configure
   - Lier API token Real-Debrid
   - Providers : YTS, EZTV, RARBG, 1337x, etc.
   - Options : Exclude non-cached, Show debrid catalog

### Guide complet

Voir le fichier : `STREMIO_SETUP.md`

### Pourquoi pas de serveur VPS ?

- Stremio + Real-Debrid = streaming direct depuis Real-Debrid vers ton client
- Pas besoin de stocker les fichiers sur le VPS
- Pas besoin de serveur de streaming
- Le "serveur Stremio" est optionnel et sert uniquement au streaming local

### Avantages

- ✅ Streaming instantané (torrents pré-cachés)
- ✅ Qualité 4K/1080p
- ✅ Pas de téléchargement
- ✅ Multi-device (PC, mobile, TV)
- ✅ Pas de gestion de stockage
- ✅ ~4€/mois tout compris

---

## 📊 Ressources VPS

### Espace disque

```
Avant sync : 178G utilisés / 193G (93%)
Après sync : ~182G / 193G (94%) estimé
Espace libre : ~11G minimum
```

**Attention** : Le VPS est presque plein (93%). La bibliothèque Calibre ajoute ~4GB.

### Ports utilisés

```
80    : Nginx (HTTP redirect)
443   : Nginx (HTTPS)
5001  : Kavita (Docker)
11470 : Stremio Server (optionnel, non installé)
12470 : Stremio Streaming (optionnel, non installé)
```

---

## 🔍 Troubleshooting

### Kavita inaccessible

```bash
# Vérifier Docker
docker ps | grep kavita

# Vérifier Nginx
sudo systemctl status nginx

# Vérifier le certificat SSL
sudo certbot certificates
```

### Sync OneDrive échoue

```bash
# Tester la connexion
rclone lsd OneDrive:

# Vérifier le config
cat ~/.config/rclone/rclone.conf

# Relancer le sync
bash ~/scripts/sync-calibre-onedrive.sh
```

### Espace disque plein

```bash
# Vérifier l'espace
df -h

# Nettoyer Docker
docker system prune -a

# Nettoyer logs
sudo journalctl --vacuum-size=100M
```

---

## 📝 URLs et Accès

| Service | URL | Credentials |
|---------|-----|-------------|
| Kavita | https://kavita.srv759970.hstgr.cloud | À créer au premier accès |
| Real-Debrid | https://real-debrid.com/ | À créer |
| Torrentio Config | https://torrentio.strem.fun/configure | Pas de login |

---

## ✅ Checklist finale

### Kavita
- [x] Docker installé et configuré
- [x] Nginx configuré avec SSL
- [x] rclone configuré et testé
- [x] Premier sync lancé
- [ ] Premier sync terminé
- [ ] Compte admin créé
- [ ] Bibliothèque configurée et scannée

### Stremio
- [x] Guide d'installation créé
- [ ] Compte Real-Debrid créé
- [ ] Stremio client installé
- [ ] Torrentio addon configuré
- [ ] Testé et fonctionnel

---

## 🎯 Prochaines actions

1. **Immédiat** : Attendre la fin du sync Calibre (~5-10 min restantes)
2. **Ensuite** : Se connecter à Kavita et configurer la bibliothèque
3. **Puis** : Créer compte Real-Debrid et configurer Stremio sur ton PC/mobile

---

## 📚 Documentation

- Installation Kavita : `INSTALL_KAVITA.md`
- Configuration Stremio : `STREMIO_SETUP.md`
- Scripts : `~/scripts/` sur le VPS

---

**Dernière mise à jour** : 2025-12-02 17:15 UTC
