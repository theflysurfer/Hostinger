# Portainer

**URL**: https://portainer.srv759970.hstgr.cloud
**Ports**: 127.0.0.1:9000 (HTTP local), 127.0.0.1:9443 (HTTPS local)
**Statut**: ✅ Opérationnel ✅ **Sécurisé via Nginx**
**Identifiants**: admin / Po85593734!?

---

## Vue d'ensemble

Portainer est une interface web de gestion complète pour Docker et Kubernetes. Alternative graphique au CLI Docker, permet de gérer conteneurs, images, volumes, réseaux et stacks via interface intuitive.

### Fonctionnalités principales

- **Gestion conteneurs** : Start, stop, restart, logs, console, stats
- **Gestion images** : Pull, build, push, suppression
- **Gestion volumes** : Création, suppression, navigation fichiers
- **Gestion réseaux** : Création, attachement conteneurs
- **Docker Compose** : Déploiement stacks via interface web
- **Gestion utilisateurs** : Multi-utilisateurs avec RBAC
- **Templates** : Catalogue d'applications pré-configurées

---

## Architecture

```
Portainer (ports 9000/9443)
    ↓
/var/run/docker.sock (rw)
    ↓
Contrôle COMPLET Docker Engine
    ↓
Tous conteneurs, images, volumes, networks
```

### Conteneur

- **portainer** : Application Portainer CE (Community Edition) complète

---

## Configuration

### Emplacement

- **Data** : Docker volume `portainer_data` → `/data` dans le conteneur
- **Image** : `portainer/portainer-ce:latest`

### Volumes montés

```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock  # RW (lecture + écriture!)
  - portainer_data:/data  # Configuration et base de données
```

**⚠️ ATTENTION** : Contrairement à Dozzle, Portainer a accès **RW** (read-write) au socket Docker = **contrôle total** sur le serveur.

### Ports réseau

- **9000** : HTTP Web UI ⚠️ **Exposé sur 0.0.0.0 (PUBLIC)**
- **9443** : HTTPS Web UI (si configuré)
- **8000** : Tunnel pour agents Portainer (remote Docker hosts)

**⚠️ PROBLÈME DE SÉCURITÉ CRITIQUE** : Port 9000 exposé publiquement sans authentification Nginx.

---

## Utilisation

### Accès

**URL** : https://portainer.srv759970.hstgr.cloud

**Identifiants** :
- Username: `admin`
- Password: `Po85593734!?`

**Note** : L'environnement Docker local "srv759970" est déjà configuré et connecté

### Navigation principale

#### Tableau de bord

- **Dashboard** : Vue d'ensemble (conteneurs actifs, images, volumes)
- **Containers** : Liste de tous les conteneurs
- **Images** : Liste de toutes les images Docker
- **Volumes** : Liste de tous les volumes
- **Networks** : Liste de tous les réseaux
- **Stacks** : Stacks Docker Compose déployées

#### Gestion conteneurs

**Actions disponibles** :
- **Start/Stop/Restart** : Contrôler le cycle de vie
- **Logs** : Visualiser logs (comme Dozzle)
- **Stats** : CPU, RAM, réseau, disque en temps réel
- **Console** : Shell interactif dans le conteneur
- **Inspect** : Configuration JSON complète
- **Duplicate** : Créer un clone du conteneur

**Accéder à un conteneur** :
1. Cliquer sur le nom du conteneur
2. Utiliser les boutons d'action en haut
3. Onglets : Logs, Inspect, Stats, Console

#### Déployer une stack Docker Compose

1. **Stacks** → **Add stack**
2. Donner un nom (ex: `my-app`)
3. Coller le contenu du `docker-compose.yml`
4. Cliquer **Deploy the stack**

Portainer crée automatiquement tous les conteneurs définis.

#### Browser de volumes

**Fonctionnalité unique** : Naviguer dans les fichiers d'un volume Docker !

1. **Volumes** → Sélectionner un volume
2. **Browse** → Voir l'arborescence des fichiers
3. Possibilité de télécharger/uploader des fichiers

---

## Administration

### Vérifier le conteneur

```bash
# Statut
docker ps --filter name=portainer

# Logs
docker logs portainer --tail 100

# Stats
docker stats portainer
```

### Redémarrer

```bash
docker restart portainer
```

### Backup de la configuration

```bash
# Backup volume portainer_data
docker run --rm \
  -v portainer_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/portainer-backup-$(date +%Y%m%d).tar.gz /data

# Restore
docker run --rm \
  -v portainer_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/portainer-backup-YYYYMMDD.tar.gz -C /
```

---

## Sécurité ✅

### Configuration actuelle

- ✅ Ports exposés uniquement en localhost (`127.0.0.1:9000`, `127.0.0.1:9443`)
- ✅ HTTPS via Nginx reverse proxy avec certificat Let's Encrypt
- ✅ Cache désactivé pour éviter problèmes d'initialisation
- ⚠️ API accessible sans basic-auth (requis pour détection admin)
- ⚠️ Accès **RW** au socket Docker = **CONTRÔLE TOTAL DU SERVEUR**

**Configuration Nginx en place** (`/etc/nginx/sites-available/portainer`) :

```nginx
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name portainer.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/portainer.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/portainer.srv759970.hstgr.cloud/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    access_log /var/log/nginx/portainer-access.log;
    error_log /var/log/nginx/portainer-error.log;

    # API SANS basic auth (nécessaire pour vérification admin)
    location /api/ {
        proxy_no_cache 1;
        proxy_cache_bypass 1;
        add_header Cache-Control "no-store" always;

        proxy_pass http://127.0.0.1:9000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Interface web AVEC basic auth
    location / {
        auth_basic "Portainer Access";
        auth_basic_user_file /etc/nginx/.htpasswd;

        proxy_no_cache 1;
        proxy_cache_bypass 1;
        add_header Cache-Control "no-store" always;

        proxy_pass http://127.0.0.1:9000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

server {
    listen 80;
    listen [::]:80;
    server_name portainer.srv759970.hstgr.cloud;
    return 301 https://$host$request_uri;
}
```

**⚠️ Note importante** : L'API (`/api/`) doit être accessible SANS basic-auth, sinon le JavaScript de Portainer ne peut pas vérifier l'existence de l'admin via `/api/users/admin/check` et redirige en boucle vers la page d'initialisation.

#### Option 2 : Limiter accès par IP

```nginx
location / {
    # Autoriser uniquement certaines IPs
    allow 203.0.113.0/24;  # Votre réseau
    deny all;

    include snippets/basic-auth.conf;
    proxy_pass http://127.0.0.1:9000;
}
```

#### Option 3 : Configurer HTTPS natif Portainer

Portainer peut gérer ses propres certificats SSL :

```bash
# Générer certificat (ou utiliser Let's Encrypt)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /opt/portainer/portainer.key \
  -out /opt/portainer/portainer.crt

# Redémarrer avec SSL
docker stop portainer
docker rm portainer
docker run -d \
  --name portainer \
  --restart unless-stopped \
  -p 0.0.0.0:9443:9443 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  -v /opt/portainer/portainer.crt:/certs/portainer.crt \
  -v /opt/portainer/portainer.key:/certs/portainer.key \
  portainer/portainer-ce:latest \
  --sslcert /certs/portainer.crt \
  --sslkey /certs/portainer.key
```

Accès : https://srv759970.hstgr.cloud:9443

---

## Gestion utilisateurs

### Créer utilisateurs supplémentaires

1. **Settings** → **Users** → **Add user**
2. Remplir :
   - Username
   - Password
   - Role : `Administrator` ou `User`
3. **Create user**

### Rôles disponibles

- **Administrator** : Contrôle total
- **User** : Accès limité (lecture seule ou permissions spécifiques)
- **Helpdesk** : Vue limitée pour support

### Authentification externe

Portainer supporte :
- **OAuth 2.0** : Google, GitHub, Azure AD
- **LDAP/AD** : Active Directory
- **Internal** : Base de données locale

**Configuration OAuth** :
1. **Settings** → **Authentication**
2. Choisir provider (ex: GitHub)
3. Entrer Client ID et Client Secret
4. Activer

---

## Templates d'applications

Portainer inclut un catalogue d'applications prêtes à déployer :

**Accès** : **App Templates**

**Applications disponibles** :
- **Nginx** : Serveur web
- **MySQL/PostgreSQL** : Bases de données
- **Redis/Memcached** : Caching
- **WordPress** : CMS
- **GitLab** : Git repository
- Et bien d'autres...

**Déployer depuis template** :
1. **App Templates**
2. Choisir application
3. Configurer variables (ports, passwords)
4. **Deploy the container**

---

## Stacks Docker Compose

### Déployer une stack

**Exemple** : Déployer WordPress + MySQL

1. **Stacks** → **Add stack**
2. Nom : `wordpress-stack`
3. Contenu :

```yaml
version: '3.8'
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password123
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wpuser
      MYSQL_PASSWORD: wppass
    volumes:
      - db_data:/var/lib/mysql

  wordpress:
    image: wordpress:latest
    ports:
      - "8080:80"
    environment:
      WORDPRESS_DB_HOST: db:3306
      WORDPRESS_DB_USER: wpuser
      WORDPRESS_DB_PASSWORD: wppass
      WORDPRESS_DB_NAME: wordpress
    depends_on:
      - db

volumes:
  db_data:
```

4. **Deploy the stack**

### Gérer une stack existante

- **Update** : Modifier le compose et redéployer
- **Stop** : Arrêter tous les conteneurs de la stack
- **Remove** : Supprimer la stack complète

---

## Monitoring et stats

### Vue d'ensemble serveur

**Dashboard** → Section "Host"
- CPU usage
- Memory usage
- Disk usage

### Stats par conteneur

**Containers** → Cliquer sur un conteneur → **Stats**
- CPU % en temps réel
- Memory usage (MB)
- Network I/O (rx/tx)
- Block I/O (read/write)

**Graphiques temps réel** (rafraîchissement 2s).

---

## Troubleshooting

### Problème : Cannot connect to Docker

**Symptôme** : Portainer affiche "Cannot connect to the Docker daemon"

**Solution** :
```bash
# Vérifier accès Docker socket
docker exec portainer ls -la /var/run/docker.sock

# Si erreur, recréer conteneur
docker stop portainer
docker rm portainer
docker run -d --name portainer \
  --restart unless-stopped \
  -p 9000:9000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest
```

### Problème : Mot de passe admin oublié

**Solution** : Réinitialiser via CLI

```bash
docker stop portainer
docker run --rm \
  -v portainer_data:/data \
  portainer/portainer-ce:latest \
  --admin-password-file /tmp/portainer_password

# Mot de passe par défaut: admin/admin
# Changer immédiatement après connexion
```

### Problème : Stack ne démarre pas

**Symptôme** : Erreur lors du déploiement d'une stack

**Solutions** :
1. Vérifier syntaxe YAML (indentation correcte)
2. Vérifier logs : **Stack** → **Logs**
3. Vérifier ports disponibles (pas de conflit)
4. Vérifier variables d'environnement définies

---

## Comparaison avec alternatives

| Feature | Portainer | Dozzle | Rancher | Kubernetes Dashboard |
|---------|-----------|--------|---------|----------------------|
| **Docker support** | ✅ Complet | ⚠️ Logs only | ✅ Complet | ❌ K8s only |
| **K8s support** | ✅ Oui | ❌ Non | ✅ Oui | ✅ Oui |
| **Stacks** | ✅ Oui | ❌ Non | ✅ Oui | ✅ Helm |
| **Templates** | ✅ Catalogue | ❌ Non | ✅ Catalogue | ⚠️ Limité |
| **RBAC** | ✅ Complet | ❌ Non | ✅ Complet | ✅ Complet |
| **Ressources** | ⚠️ ~100MB | ✅ ~10MB | ❌ > 1GB | ⚠️ ~200MB |
| **Complexité** | ✅ Simple | ✅ Simple | ❌ Complexe | ⚠️ Moyenne |

**Recommandation** :
- **Portainer** : Gestion complète Docker, simplicité
- **Dozzle** : Logs temps réel uniquement
- **Rancher** : Multi-cluster K8s enterprise
- **CLI Docker** : Maximum de contrôle et performance

---

## Fonctionnalités avancées

### Portainer Agent (multi-hosts)

Gérer plusieurs serveurs Docker depuis une seule interface :

**Sur le serveur distant** :
```bash
docker run -d \
  --name portainer-agent \
  --restart unless-stopped \
  -p 9001:9001 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /var/lib/docker/volumes:/var/lib/docker/volumes \
  portainer/agent:latest
```

**Dans Portainer** :
1. **Environments** → **Add environment**
2. Choisir "Agent"
3. URL: `remote-server:9001`
4. **Connect**

### Webhooks

Déclencher redéploiement stack via webhook :

1. **Stack** → Sélectionner stack → **Webhooks**
2. **Create a webhook**
3. Copier URL
4. Utiliser dans CI/CD :

```bash
# Exemple GitHub Actions
curl -X POST https://portainer.srv759970.hstgr.cloud/api/webhooks/WEBHOOK_ID
```

### Edge Computing

Portainer Edge permet de gérer des devices IoT/edge derrière NAT (pas d'IP publique requise).

---

## Liens utiles

- **Documentation officielle** : https://docs.portainer.io
- **GitHub** : https://github.com/portainer/portainer
- **Community Edition** : https://www.portainer.io/products/community-edition
- **Templates repository** : https://github.com/portainer/templates
- **Docker Hub** : https://hub.docker.com/r/portainer/portainer-ce

---

## Notes de déploiement

### Problèmes rencontrés et solutions

**Problème : Redirection infinie vers `/#!/init/admin`**
- **Cause** : Le basic-auth Nginx bloquait l'endpoint `/api/users/admin/check`, empêchant Portainer de détecter que l'admin existait
- **Solution** : Exclure `/api/` du basic-auth dans la configuration Nginx

**Problème : Formulaire de création d'admin ne fonctionne pas**
- **Cause** : Bug JavaScript de Portainer v2.33.2 avec les caractères spéciaux dans le mot de passe
- **Solution** : Créer l'admin via API avec Python au lieu du formulaire web

**Problème : Cache navigateur persistant**
- **Cause** : Nginx et navigateur cachent la page d'initialisation
- **Solution** : Désactiver le cache avec headers `Cache-Control: no-store` et `proxy_no_cache 1`

---

**Dernière mise à jour** : 2025-10-23
**Version Portainer** : CE (Community Edition) 2.33.2
**Container** : `portainer`
**Environnement Docker** : srv759970 (configuré automatiquement)
