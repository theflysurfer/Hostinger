# Clémence - Site WordPress

**URL**: https://clemence.srv759970.hstgr.cloud
**Port hôte**: 9002
**Statut**: ✅ Opérationnel

---

## Vue d'ensemble

Site WordPress pour le projet Clémence (RH Diversité & Inclusion), hébergé via Docker avec auto-start/stop.

### Stack technique

- **WordPress**: Latest
- **MySQL**: 8.0
- **Nginx**: Reverse proxy
- **PHP-FPM**: 9000
- **Docker Auto-Start**: Activé

---

## Architecture

```
Internet (HTTPS 443)
    ↓
Nginx (reverse proxy)
    ↓
Docker Auto-Start API (:8890)
    ↓
wordpress-clemence (:9000 PHP-FPM)
    ↓
mysql-clemence (:3306)
```

---

## Conteneurs

| Container | Port | Status |
|-----------|------|--------|
| `wordpress-clemence` | 9000 | ✅ Running |
| `mysql-clemence` | 3306 | ✅ Running |
| `nginx-clemence` | 9002 | ✅ Running |
| `wp-cli-clemence` | - | ✅ Running |

---

## Emplacements

- **Répertoire**: `/opt/wordpress-clemence/`
- **Data WordPress**: `/opt/wordpress-clemence/wordpress/`
- **Data MySQL**: `/opt/wordpress-clemence/mysql/`
- **Config**: `/opt/wordpress-clemence/docker-compose.yml`
- **Nginx config**: `/etc/nginx/sites-available/clemence`

---

## Gestion

### Démarrage manuel

```bash
ssh root@69.62.108.82
cd /opt/wordpress-clemence
docker-compose up -d
```

### Logs

```bash
# Logs WordPress
docker logs wordpress-clemence -f

# Logs MySQL
docker logs mysql-clemence -f

# Logs Nginx
docker logs nginx-clemence -f
```

### Accès MySQL

```bash
docker exec -it mysql-clemence mysql -u clemence_user -p
```

### WP-CLI

```bash
# Lister les plugins
docker exec wp-cli-clemence wp plugin list

# Mettre à jour WordPress
docker exec wp-cli-clemence wp core update

# Vider le cache
docker exec wp-cli-clemence wp cache flush
```

---

## Configuration Email

Le site utilise Gmail SMTP pour l'envoi d'emails.

Configuration dans `wp-config.php` :

```php
define( 'WPMS_SMTP_HOST', 'smtp.gmail.com' );
define( 'WPMS_SMTP_PORT', 587 );
define( 'WPMS_SMTP_USER', 'clemsfou@gmail.com' );
```

Voir [Guide Email](../../guides/infrastructure/email-smtp.md) pour la configuration complète.

---

## Configuration Auto-Start

Le site utilise docker-autostart pour démarrage à la demande :

- **Timeout inactivité**: 30 minutes
- **Mode**: Async (démarrage en arrière-plan)
- **Health check**: Vérifie MySQL + WordPress

Configuration dans `/opt/docker-autostart/config.json` :

```json
{
  "name": "Clémence Site",
  "container": "wordpress-clemence",
  "timeout": 1800,
  "async": true,
  "healthCheck": {
    "enabled": true,
    "containers": ["mysql-clemence", "wordpress-clemence"]
  }
}
```

---

## Accès Admin WordPress

**URL**: https://clemence.srv759970.hstgr.cloud/wp-admin

Identifiants dans `/opt/wordpress-clemence/.env`

---

## Backup

### Base de données

```bash
docker exec mysql-clemence mysqldump -u root -p clemence_db > backup_clemence_$(date +%Y%m%d).sql
```

### Fichiers WordPress

```bash
tar -czf backup_clemence_files_$(date +%Y%m%d).tar.gz /opt/wordpress-clemence/wordpress/
```

---

## Voir aussi

- [Guide WordPress Docker](../../guides/services/wordpress/wordpress-docker.md)
- [Guide Email](../../guides/infrastructure/email-smtp.md)
- [Docker Auto-Start Config](../automation/docker-autostart.md)
