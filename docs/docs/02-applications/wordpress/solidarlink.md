# SolidarLink - Site WordPress

**URL**: https://solidarlink.srv759970.hstgr.cloud
**Port hôte**: 9003
**Statut**: ✅ Opérationnel

---

## Vue d'ensemble

Site WordPress pour le projet SolidarLink, hébergé via Docker avec auto-start/stop.

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
wordpress-solidarlink (:9000 PHP-FPM)
    ↓
mysql-solidarlink (:3306)
```

---

## Conteneurs

| Container | Port | Status |
|-----------|------|--------|
| `wordpress-solidarlink` | 9000 | ✅ Running |
| `mysql-solidarlink` | 3306 | ✅ Running |
| `nginx-solidarlink` | 9003 | ✅ Running |
| `wp-cli-solidarlink` | - | ✅ Running |

---

## Emplacements

- **Répertoire**: `/opt/wordpress-solidarlink/`
- **Data WordPress**: `/opt/wordpress-solidarlink/wordpress/`
- **Data MySQL**: `/opt/wordpress-solidarlink/mysql/`
- **Config**: `/opt/wordpress-solidarlink/docker-compose.yml`
- **Nginx config**: `/etc/nginx/sites-available/solidarlink`

---

## Gestion

### Démarrage manuel

```bash
ssh root@69.62.108.82
cd /opt/wordpress-solidarlink
docker-compose up -d
```

### Logs

```bash
# Logs WordPress
docker logs wordpress-solidarlink -f

# Logs MySQL
docker logs mysql-solidarlink -f

# Logs Nginx
docker logs nginx-solidarlink -f
```

### Accès MySQL

```bash
docker exec -it mysql-solidarlink mysql -u solidarlink_user -p
```

### WP-CLI

```bash
# Lister les plugins
docker exec wp-cli-solidarlink wp plugin list

# Mettre à jour WordPress
docker exec wp-cli-solidarlink wp core update

# Vider le cache
docker exec wp-cli-solidarlink wp cache flush
```

---

## Configuration Auto-Start

Le site utilise docker-autostart pour démarrage à la demande :

- **Timeout inactivité**: 30 minutes
- **Mode**: Async (démarrage en arrière-plan)
- **Health check**: Vérifie MySQL + WordPress

Configuration dans `/opt/docker-autostart/config.json` :

```json
{
  "name": "SolidarLink",
  "container": "wordpress-solidarlink",
  "timeout": 1800,
  "async": true,
  "healthCheck": {
    "enabled": true,
    "containers": ["mysql-solidarlink", "wordpress-solidarlink"]
  }
}
```

---

## Accès Admin WordPress

**URL**: https://solidarlink.srv759970.hstgr.cloud/wp-admin

Identifiants dans `/opt/wordpress-solidarlink/.env`

---

## Backup

### Base de données

```bash
docker exec mysql-solidarlink mysqldump -u root -p solidarlink_db > backup_solidarlink_$(date +%Y%m%d).sql
```

### Fichiers WordPress

```bash
tar -czf backup_solidarlink_files_$(date +%Y%m%d).tar.gz /opt/wordpress-solidarlink/wordpress/
```

---

## Voir aussi

- [Guide WordPress Docker](../../guides/services/wordpress/wordpress-docker.md)
- [Docker Auto-Start Config](../automation/docker-autostart.md)
