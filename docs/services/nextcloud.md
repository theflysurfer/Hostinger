# Nextcloud

**URL**: https://nextcloud.srv759970.hstgr.cloud
**Port interne**: 8505
**Statut**: ✅ Opérationnel

---

## Vue d'ensemble

Nextcloud est une plateforme de stockage cloud et de synchronisation de fichiers self-hosted. Elle permet le partage de fichiers, la collaboration en temps réel, et l'intégration avec ONLYOFFICE pour l'édition de documents.

### Fonctionnalités principales

- **Stockage cloud** : Upload, download, synchronisation fichiers
- **Partage** : Partage interne/externe avec liens et permissions
- **Collaboration** : Co-édition documents via ONLYOFFICE
- **Calendrier & Contacts** : CalDAV/CardDAV intégré
- **Notes** : Application Notes intégrée
- **Photos** : Galerie photos avec reconnaissance faciale

---

## Architecture

```
Nextcloud (port 8505)
    ↓
PostgreSQL (databases-shared)
    ↓
Redis (cache sessions)
    ↓
ONLYOFFICE (port 8508) - Édition documents Office
```

### Conteneurs

- **nextcloud** : Application Nextcloud principale
- **nextcloud-cron** : Tâches planifiées (cleanup, preview generation)

---

## Configuration

### Emplacement

- **Répertoire**: `/opt/nextcloud/`
- **Data**: `/opt/nextcloud/data/`
- **Config**: `/opt/nextcloud/config/config.php`
- **Apps**: `/opt/nextcloud/custom_apps/`

### Base de données

- **Type**: PostgreSQL
- **Host**: `postgresql-shared`
- **Database**: `nextcloud`
- **User**: `nextcloud`

### Cache Redis

- **Host**: `redis-shared`
- **Port**: 6379
- **Usage**: Sessions, file locking, cache applicatif

---

## Utilisation

### Accès Web

URL: https://nextcloud.srv759970.hstgr.cloud

**Compte admin** :
- User: `admin`
- Password: Voir `/opt/nextcloud/.env`

### Clients de synchronisation

**Desktop** :
- [Nextcloud Desktop Client](https://nextcloud.com/install/#install-clients) (Windows, macOS, Linux)

**Mobile** :
- [Android](https://play.google.com/store/apps/details?id=com.nextcloud.client)
- [iOS](https://apps.apple.com/app/nextcloud/id1125420102)

### WebDAV

- **URL**: `https://nextcloud.srv759970.hstgr.cloud/remote.php/dav/files/USERNAME/`
- **Usage**: Monter comme lecteur réseau

---

## Intégration ONLYOFFICE

Nextcloud est configuré pour utiliser ONLYOFFICE Document Server pour l'édition collaborative de documents Office.

### Documents supportés

- **Word**: `.docx`, `.doc`
- **Excel**: `.xlsx`, `.xls`
- **PowerPoint**: `.pptx`, `.ppt`
- **PDF**: Lecture seule

### Co-édition

- Plusieurs utilisateurs peuvent éditer simultanément
- Modifications en temps réel
- Commentaires et révisions

### Configuration

L'intégration est déjà configurée :

- **Document Server URL**: `https://onlyoffice.srv759970.hstgr.cloud`
- **JWT Secret**: Configuré pour sécurité
- **App Nextcloud**: ONLYOFFICE installée et active

---

## Commandes utiles

### Via CLI (occ)

```bash
# Se connecter au conteneur
docker exec -u www-data nextcloud php occ

# Lister utilisateurs
docker exec -u www-data nextcloud php occ user:list

# Créer utilisateur
docker exec -u www-data nextcloud php occ user:add USERNAME

# Scanner fichiers
docker exec -u www-data nextcloud php occ files:scan --all

# Vérifier config
docker exec -u www-data nextcloud php occ config:list system

# Mode maintenance
docker exec -u www-data nextcloud php occ maintenance:mode --on
docker exec -u www-data nextcloud php occ maintenance:mode --off
```

### Gestion conteneurs

```bash
# Vérifier logs
docker logs nextcloud --tail 50 -f
docker logs nextcloud-cron --tail 50 -f

# Redémarrer
docker restart nextcloud nextcloud-cron

# Stats
docker stats nextcloud nextcloud-cron
```

---

## Tâches de maintenance

### Cron jobs

Le conteneur `nextcloud-cron` exécute automatiquement les tâches planifiées toutes les 5 minutes :

- Nettoyage fichiers temporaires
- Génération previews
- Mise à jour indexes
- Synchronisation calendriers

### Logs

```bash
# Logs Nextcloud
docker exec nextcloud tail -f /var/www/html/data/nextcloud.log

# Logs Nginx interne
docker logs nextcloud | grep nginx
```

---

## Troubleshooting

### Problème de connexion

**Symptôme**: Erreur "Trusted domain"

**Solution**:
```bash
docker exec -u www-data nextcloud php occ config:system:set trusted_domains 1 --value='nextcloud.srv759970.hstgr.cloud'
```

### Problème ONLYOFFICE

**Symptôme**: "Document editing service is not available"

**Solution**:
```bash
# Vérifier ONLYOFFICE
curl -I https://onlyoffice.srv759970.hstgr.cloud

# Revalider config
docker exec -u www-data nextcloud php occ config:app:get onlyoffice DocumentServerUrl
```

### Problème de performance

**Solution**: Vider cache Redis
```bash
docker exec redis-shared redis-cli -a PASSWORD FLUSHDB
docker restart nextcloud
```

---

## Sécurité

### HTTPS

- ✅ Certificat Let's Encrypt automatique
- ✅ Renouvellement automatique
- ✅ HTTP/2 activé

### Authentification

- Authentification locale Nextcloud
- Support 2FA disponible (app Two-Factor TOTP)

### Permissions

- Système de partage granulaire
- Permissions lecture/écriture/partage configurables
- Liens publics avec expiration optionnelle

---

## Backup

### Données à sauvegarder

1. **Data directory**: `/opt/nextcloud/data/`
2. **Database PostgreSQL**: `nextcloud` database
3. **Config**: `/opt/nextcloud/config/config.php`

### Script backup

```bash
# Backup data
tar czf nextcloud-data-$(date +%Y%m%d).tar.gz /opt/nextcloud/data/

# Backup database
docker exec postgresql-shared pg_dump -U nextcloud nextcloud > nextcloud-db-$(date +%Y%m%d).sql
```

---

## Liens utiles

- **Documentation officielle**: https://docs.nextcloud.com
- **Admin manual**: https://docs.nextcloud.com/server/stable/admin_manual/
- **Apps store**: https://apps.nextcloud.com
- **Community**: https://help.nextcloud.com

---

**Dernière mise à jour**: 2025-10-21
**Version Nextcloud**: Latest (Docker image officiel)
