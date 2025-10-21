# Configuration Basic Auth Nginx

Mise en place de l'authentification HTTP Basic avec Nginx.

## Installation htpasswd

```bash
# Ubuntu/Debian
apt-get install apache2-utils

# CentOS/RHEL
yum install httpd-tools
```

## Créer Fichier .htpasswd

### Créer nouveau fichier

```bash
htpasswd -c /etc/nginx/.htpasswd admin
```

**Attention**: Le flag `-c` écrase le fichier existant.

### Ajouter utilisateur à fichier existant

```bash
htpasswd /etc/nginx/.htpasswd newuser
```

### Supprimer un utilisateur

```bash
htpasswd -D /etc/nginx/.htpasswd username
```

## Configuration Nginx

### Activer sur tout le serveur

```nginx
server {
    listen 443 ssl http2;
    server_name example.srv759970.hstgr.cloud;

    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;

    location / {
        proxy_pass http://localhost:8080;
    }
}
```

### Activer sur un location spécifique

```nginx
server {
    listen 443 ssl http2;
    server_name example.srv759970.hstgr.cloud;

    location / {
        proxy_pass http://localhost:8080;
    }

    location /admin {
        auth_basic "Admin Area";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://localhost:8080/admin;
    }
}
```

### Désactiver pour un sous-path

```nginx
location / {
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:8080;
}

location /public {
    auth_basic off;  # Désactive l'auth pour ce path
    proxy_pass http://localhost:8080/public;
}
```

## Snippet Réutilisable

Créer `/etc/nginx/snippets/basic-auth.conf`:

```nginx
auth_basic "Restricted Access - srv759970";
auth_basic_user_file /etc/nginx/.htpasswd;
```

Utiliser dans les server blocks:

```nginx
server {
    listen 443 ssl http2;
    server_name example.srv759970.hstgr.cloud;

    include snippets/basic-auth.conf;

    location / {
        proxy_pass http://localhost:8080;
    }
}
```

## Permissions

```bash
# Sécuriser le fichier .htpasswd
chmod 640 /etc/nginx/.htpasswd
chown root:www-data /etc/nginx/.htpasswd
```

## Vérifier le Fichier

```bash
cat /etc/nginx/.htpasswd
# admin:$apr1$xyz...
```

Format: `username:encrypted_password`

## Générer Mot de Passe Sans Interaction

```bash
# Utiliser openssl pour générer le hash
htpasswd -nb admin "MyPassword123" >> /etc/nginx/.htpasswd
```

## Tester l'Authentification

```bash
# Sans credentials → 401
curl https://example.srv759970.hstgr.cloud

# Avec credentials → 200
curl -u admin:password https://example.srv759970.hstgr.cloud
```

## Services Protégés sur srv759970

- **Grafana**: https://monitoring.srv759970.hstgr.cloud
- **RQ Dashboard**: https://whisperx-dashboard.srv759970.hstgr.cloud
- **Dozzle**: https://dozzle.srv759970.hstgr.cloud

## Troubleshooting

### 401 Unauthorized même avec bon mot de passe

```bash
# Vérifier permissions fichier
ls -la /etc/nginx/.htpasswd

# Vérifier logs Nginx
tail -f /var/log/nginx/error.log
```

### Pas de prompt d'authentification

```bash
# Vérifier syntaxe Nginx
nginx -t

# Recharger Nginx
systemctl reload nginx
```

## Voir aussi

- [Infrastructure > Security](../../infrastructure/security.md) - Vue d'ensemble sécurité
- [Infrastructure > Nginx](../../infrastructure/nginx.md) - Configuration Nginx globale
