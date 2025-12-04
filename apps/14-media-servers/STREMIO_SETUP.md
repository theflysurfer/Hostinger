# Installation Stremio + Torrentio + Real-Debrid

## Vue d'ensemble

**Important** : Contrairement à Kavita qui nécessite un serveur, Stremio fonctionne principalement comme une application cliente. Le "serveur" Stremio est uniquement nécessaire pour le streaming local, pas pour l'utilisation avec Real-Debrid.

### Architecture recommandée

- **Stremio Client** : Application sur ton PC/Mac/Android/iOS
- **Torrentio Addon** : Addon qui agrège les sources torrent
- **Real-Debrid** : Service premium qui fournit des liens rapides et cachés

## Étape 1 : Créer un compte Real-Debrid

1. Va sur https://real-debrid.com/
2. Clique sur "Sign Up" et crée un compte
3. Souscris à un abonnement (environ 4€/mois ou 16€/6mois)
4. Une fois connecté, va dans **My Account → API Token**
5. Copie ton API token (garde-le précieusement)

## Étape 2 : Installer Stremio

### Sur Windows/Mac
1. Télécharge depuis https://www.stremio.com/downloads
2. Installe et lance l'application
3. Crée un compte Stremio ou connecte-toi

### Sur Android/iOS
1. Cherche "Stremio" dans le Play Store / App Store
2. Installe et connecte-toi avec ton compte

### Sur Linux
```bash
# Ubuntu/Debian
wget -O stremio.deb https://dl.strem.io/shell-linux/v4.4.168/stremio_4.4.168-1_amd64.deb
sudo dpkg -i stremio.deb
```

## Étape 3 : Configurer l'addon Torrentio

1. Ouvre ton navigateur et va sur https://torrentio.strem.fun/configure
2. Configure les options :

### Configuration recommandée :

**Providers** (sources de torrents) :
- ✅ YTS
- ✅ EZTV
- ✅ RARBG
- ✅ 1337x
- ✅ ThePirateBay
- ✅ KickassTorrents

**Debrid Provider** :
- Sélectionne **Real-Debrid**
- Colle ton **API Token** Real-Debrid

**Sorting** :
- **By quality then seeders** (recommandé)

**Quality** :
- ✅ 4K
- ✅ 1080p
- ✅ 720p
- ✅ 480p

**Other options** :
- ✅ **Show debrid catalog** : affiche le contenu déjà caché sur Real-Debrid
- ✅ **Exclude non-cached** : uniquement les liens instantanés
- ❌ **Don't show download to debrid** : désactivé pour voir toutes les options

3. En bas de page, clique sur **"Install"**
4. Stremio va s'ouvrir automatiquement et installer l'addon

## Étape 4 : Vérifier l'installation

1. Lance Stremio
2. Cherche un film ou une série
3. Clique dessus pour voir les sources disponibles
4. Tu devrais voir des liens marqués **[RD+] Torrentio**
5. Ces liens sont les sources premium via Real-Debrid

## Étape 5 (Optionnel) : Installer Stremio Server sur VPS

**Note** : Ceci n'est nécessaire QUE si tu veux streamer depuis le VPS vers d'autres devices. Pour une utilisation normale avec Real-Debrid, le client suffit.

Si tu veux quand même l'installer :

```bash
ssh automation@69.62.108.82

# Créer le dossier
mkdir -p ~/apps/14-media-servers/stremio

# Lancer le serveur Stremio
docker run -d \
  --name stremio-server \
  --restart unless-stopped \
  -p 11470:11470 \
  -p 12470:12470 \
  -v ~/apps/14-media-servers/stremio/config:/root/.stremio-server \
  stremio/server:latest
```

Ensuite configure Nginx si tu veux l'exposer en HTTPS (mais c'est rarement nécessaire).

## Addons recommandés supplémentaires

En plus de Torrentio, tu peux installer :

1. **OpenSubtitles** : Sous-titres automatiques
   - https://opensubtitles.strem.io/

2. **IMDB Lists** : Créer des listes de films/séries
   - https://94c8cb9f702d-imdb-list.baby-beamup.club/

3. **Trakt** : Synchroniser ce que tu regardes
   - https://trakt.tv/

## Utilisation quotidienne

1. Ouvre Stremio
2. Cherche un film/série
3. Clique sur Play
4. Choisis une source **[RD+] Torrentio**
5. Le streaming démarre instantanément (grâce à Real-Debrid)

## Avantages de cette configuration

- **Pas de téléchargement** : Streaming direct
- **Instantané** : Les torrents sont déjà cachés sur Real-Debrid
- **Qualité maximale** : 4K/1080p disponibles
- **Pas de ratio** : Pas besoin de seeder
- **Multi-device** : Fonctionne sur tous tes appareils
- **Légal pour toi** : Tu ne télécharges rien directement

## Troubleshooting

### Pas de sources [RD+]
- Vérifie que ton API token Real-Debrid est correct
- Vérifie que ton abonnement Real-Debrid est actif
- Réinstalle l'addon Torrentio

### Buffering
- Change de source (prends un lien avec plus de seeders)
- Vérifie ta connexion Internet
- Réduis la qualité (1080p au lieu de 4K)

### Addon ne s'installe pas
- Ouvre Stremio AVANT de cliquer sur "Install" sur le site Torrentio
- Vérifie que tu es connecté à ton compte Stremio

## Sources

- [Official Stremio Docker](https://github.com/Stremio/server-docker)
- [Torrentio Configuration Guide](https://www.stremioguide.com/en/addons/torrentio-real-debrid/)
- [Stremio + Real-Debrid 2025 Guide](https://troypoint.com/torrentio/)
- [Torrentio Setup Page](https://torrentio.strem.fun/configure)

## Coûts

- **Stremio** : Gratuit
- **Torrentio** : Gratuit
- **Real-Debrid** : ~4€/mois ou 16€/6 mois

Total : ~4€/mois pour un accès quasi-illimité à tous les films/séries en streaming 4K.
