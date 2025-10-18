# Politique Git pour srv759970

Stratégie de versioning et gestion du code pour l'ensemble du serveur VPS.

## Philosophie générale

**Principe** : Version control UNIQUEMENT pour la configuration et l'infrastructure, PAS pour les contenus utilisateurs.

### Ce qui DOIT être versionné ✅

- Configuration système (`/etc/nginx/`, `/etc/systemd/`, configs serveur)
- Scripts d'infrastructure (`/opt/docker-autostart/`, scripts de déploiement)
- Code source des applications custom
- Fichiers docker-compose.yml et Dockerfiles
- Documentation locale (ce repository)

### Ce qui NE DOIT PAS être versionné ❌

- Bases de données (`*.sql`, `/var/lib/mysql/`)
- Uploads WordPress (`wp-content/uploads/`)
- Caches et fichiers temporaires
- Secrets et credentials (`.env`, tokens, passwords)
- Fichiers volumineux (images, vidéos, backups)
- Contenus créés par les utilisateurs finaux

## Architecture des repositories

### Repository 1 : Documentation locale (existant)

**Emplacement** : `C:\Users\JulienFernandez\OneDrive\Coding\_référentiels de code\Hostinger\`

**Contenu** :
- ✅ Tous les GUIDE_*.md
- ✅ README.md, INSTRUCTIONS_LLM.md
- ✅ Scripts batch (deploy.bat, update.bat, manage.bat)
- ✅ Documentation Sablier (référence)
- ✅ portal-index.html (backup local)

**Synchro** : Manuel (OneDrive + backup vers serveur si besoin)

**Git** :
```bash
# Déjà configuré
cd "C:\Users\JulienFernandez\OneDrive\Coding\_référentiels de code\Hostinger"
git status
```

### Repository 2 : Configuration serveur (à créer)

**Emplacement serveur** : `/root/server-config/`

**Contenu** :
```
/root/server-config/
├── nginx/
│   ├── sites-available/
│   │   ├── portal
│   │   ├── whisper-faster
│   │   ├── whisperx
│   │   ├── tika
│   │   ├── dashboard
│   │   └── ...
│   └── snippets/
│       └── basic-auth.conf
├── systemd/
│   └── docker-autostart.service
├── docker-autostart/
│   ├── server.js
│   ├── config.json
│   ├── package.json
│   └── themes/
│       ├── hacker-terminal.html
│       ├── ghost.html
│       ├── matrix.html
│       └── shuffle.html
├── scripts/
│   └── (utilitaires serveur)
└── README.md
```

**Initialisation** :
```bash
ssh root@69.62.108.82

# Créer repository
mkdir -p /root/server-config
cd /root/server-config

# Init git
git init
git config user.name "Julien Fernandez"
git config user.email "julien.fernandez.work@gmail.com"

# Créer structure
mkdir -p nginx/sites-available nginx/snippets systemd scripts

# Copier configs actuelles
cp /etc/nginx/sites-available/portal nginx/sites-available/
cp /etc/nginx/sites-available/whisper-faster nginx/sites-available/
cp /etc/nginx/sites-available/whisperx nginx/sites-available/
cp /etc/nginx/sites-available/tika nginx/sites-available/
# ... autres sites

cp /etc/nginx/snippets/basic-auth.conf nginx/snippets/
cp /etc/systemd/system/docker-autostart.service systemd/

# Copier docker-autostart (SANS node_modules)
cp -r /opt/docker-autostart/ ./
rm -rf docker-autostart/node_modules

# Créer .gitignore
cat > .gitignore << 'EOF'
node_modules/
*.log
.env
*.backup
*.swp
EOF

# Premier commit
git add .
git commit -m "Initial commit: server configuration snapshot

- Nginx configs for all services
- Docker auto-start system
- Systemd service files"
```

### Repository 3 : Applications custom (optionnel)

**Services concernés** :
- `/opt/whisperx/` (WhisperX custom build)
- `/opt/api-portal/` (Portal HTML)

**Si besoin de versioning par app** :
```bash
# Exemple pour whisperx
cd /opt/whisperx
git init
git add Dockerfile server.py docker-compose.yml
git commit -m "Initial WhisperX service"
```

## Stratégie de branches

### Pour la documentation locale

**main** : Documentation à jour, validée
**dev** : Modifications en cours (optionnel si solo)

### Pour la configuration serveur

**main** : Configuration stable en production
**backup-YYYY-MM-DD** : Snapshots avant changements majeurs

```bash
# Avant changement majeur
git checkout -b backup-2025-10-18
git checkout main
```

## Workflow de modification

### 1. Modification d'une config Nginx

```bash
# 1. Éditer sur le serveur
nano /etc/nginx/sites-available/whisperx

# 2. Tester
nginx -t

# 3. Appliquer
systemctl reload nginx

# 4. Mettre à jour le repo
cd /root/server-config
cp /etc/nginx/sites-available/whisperx nginx/sites-available/
git add nginx/sites-available/whisperx
git commit -m "Update whisperx nginx config: increase upload limit to 1GB"
```

### 2. Modification du système auto-start

```bash
# 1. Éditer
nano /opt/docker-autostart/config.json

# 2. Restart service
systemctl restart docker-autostart

# 3. Vérifier logs
journalctl -u docker-autostart -n 20

# 4. Si OK, commit
cd /root/server-config
cp /opt/docker-autostart/config.json docker-autostart/
git add docker-autostart/config.json
git commit -m "Add new service to auto-start: example-app"
```

### 3. Mise à jour documentation locale

```bash
# Depuis Windows
cd "C:\Users\JulienFernandez\OneDrive\Coding\_référentiels de code\Hostinger"

# Modifier docs
notepad GUIDE_WHISPER_SERVICES.md

# Commit
git add GUIDE_WHISPER_SERVICES.md
git commit -m "Add WhisperX deployment guide"
git push
```

## Backups vs Git

### Git pour : ✅

- **Versions du code** : Historique des modifications, rollback facile
- **Configuration** : Fichiers texte <100KB
- **Collaboration** : Partage avec autres devs (futur)
- **Documentation** : Guides, README, instructions

### Backups traditionnels pour : 💾

- **Bases de données** : Dumps SQL automatiques (cron)
- **Uploads** : Fichiers volumineux (rsync, Duplicati, AWS S3)
- **Secrets** : Vaults (Bitwarden, 1Password), PAS dans Git
- **State complet** : Snapshots VPS Hostinger

## Commandes utiles

### Documentation locale

```bash
# Statut
git status

# Voir historique
git log --oneline

# Comparer changements
git diff

# Annuler changements non commités
git checkout -- GUIDE_DEPLOIEMENT_VPS.md

# Revenir à un commit précédent (DANGEREUX)
git revert <commit-hash>
```

### Configuration serveur

```bash
# Snapshot avant changement majeur
cd /root/server-config
git checkout -b backup-$(date +%Y-%m-%d)
git checkout main

# Comparer avec version en production
diff /etc/nginx/sites-available/portal nginx/sites-available/portal

# Restaurer une config depuis git
cp nginx/sites-available/portal /etc/nginx/sites-available/
nginx -t && systemctl reload nginx
```

## Politique de secrets

### ❌ JAMAIS dans Git

- Passwords (`MYSQL_ROOT_PASSWORD`, `ADMIN_PASSWORD`)
- API keys (HuggingFace `HF_TOKEN`, OpenAI keys)
- Basic auth credentials (`/etc/nginx/.htpasswd`)
- Certificats SSL privés (`/etc/letsencrypt/live/*/*.pem`)

### ✅ Gestion sécurisée

1. **Fichiers .env** : Stockés uniquement sur le serveur
   ```bash
   # Exemple /opt/whisperx/.env
   HF_TOKEN=hf_xxxxxxxxxxxxx
   ```

2. **Backup chiffré** : Si backup des secrets nécessaire
   ```bash
   # Créer archive chiffrée
   tar czf - /opt/whisperx/.env | gpg -c > secrets-backup.tar.gz.gpg
   ```

3. **Documentation** : Référencer OÙ sont les secrets, PAS leur valeur
   ```markdown
   # Guide WhisperX
   HF_TOKEN requis dans `/opt/whisperx/.env`
   Obtenir le token sur https://huggingface.co/settings/tokens
   ```

## Remote repository (optionnel futur)

Si besoin de backup externe ou collaboration :

### Option 1 : GitHub privé

```bash
cd /root/server-config
git remote add origin https://github.com/username/srv759970-config.git
git push -u origin main
```

⚠️ **ATTENTION** : Vérifier .gitignore AVANT push initial !

### Option 2 : GitLab self-hosted

Plus de contrôle, hébergé sur le VPS ou autre serveur.

### Option 3 : Pas de remote

Git local uniquement = snapshot versionné sur le serveur. Simple et efficace.

## Fréquence de commit

### Configuration serveur

- **Avant tout changement majeur** : Snapshot branch
- **Après validation** : Commit avec message descriptif
- **Minimum** : 1 commit/semaine si modifications

### Documentation locale

- **Après création guide** : Commit immédiat
- **Après mise à jour significative** : Commit
- **Typos/petites corrections** : Batch commits OK

## Messages de commit

### Format recommandé

```
<type>: <description courte>

<détails optionnels>
```

**Types** :
- `feat:` Nouvelle fonctionnalité/service
- `fix:` Correction bug/config
- `docs:` Mise à jour documentation
- `config:` Changement configuration
- `refactor:` Réorganisation sans changement fonctionnel

### Exemples

```bash
# Bon ✅
git commit -m "feat: add WhisperX service with diarization support

- Create /opt/whisperx/ with custom Dockerfile
- Add whisperx.srv759970.hstgr.cloud nginx config
- Update docker-autostart config.json with new service"

git commit -m "fix: increase whisperx upload limit to 1GB

client_max_body_size changed from 500M to 1G in nginx config"

git commit -m "docs: add comprehensive WhisperX deployment guide"

# Mauvais ❌
git commit -m "update"
git commit -m "fix stuff"
git commit -m "wip"
```

## Audit et nettoyage

### Vérifier taille repo

```bash
cd /root/server-config
du -sh .git
```

Si >100MB → Probablement fichier binaire/lourd committé par erreur.

### Nettoyer historique (DANGEREUX)

```bash
# Supprimer gros fichier de l'historique
git filter-branch --tree-filter 'rm -f path/to/large/file' HEAD
```

⚠️ **Utiliser uniquement en dernier recours** !

## Checklist déploiement

Avant de commiter une nouvelle configuration :

- [ ] Testé en local/staging si possible
- [ ] Nginx config testée (`nginx -t`)
- [ ] Service redémarré et logs vérifiés
- [ ] Aucun secret dans les fichiers
- [ ] .gitignore à jour
- [ ] Message de commit descriptif
- [ ] Documentation mise à jour si besoin

## Liens utiles

- **Git Basics** : https://git-scm.com/book/fr/v2
- **Gitignore templates** : https://github.com/github/gitignore
- **Conventional Commits** : https://www.conventionalcommits.org/fr/

## État actuel

### Documentation locale ✅

- **Repository** : `C:\Users\JulienFernandez\OneDrive\Coding\_référentiels de code\Hostinger\`
- **Statut** : Géré avec Git
- **Remote** : Aucun (OneDrive sync uniquement)
- **Dernière mise à jour** : Octobre 2025

### Configuration serveur ⏸️

- **Repository** : À créer (`/root/server-config/`)
- **Statut** : Non versionné actuellement
- **Action** : Initialiser selon ce guide

### Applications custom ⏸️

- **WhisperX** : Non versionné
- **API Portal** : Non versionné
- **Docker-autostart** : Non versionné indépendamment
- **Action** : Décider si versioning individuel nécessaire
