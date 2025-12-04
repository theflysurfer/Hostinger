# Impro Manager

**URL**: https://impro.srv759970.hstgr.cloud
**Port interne**: 3001
**Statut**: ✅ Running (unhealthy)

---

## Vue d'ensemble

Application web de gestion pour troupes d'improvisation théâtrale. Interface moderne construite avec Next.js et base de données PostgreSQL.

### Fonctionnalités principales

- Gestion des membres de la troupe
- Planification des répétitions et spectacles
- Bibliothèque d'exercices d'improvisation
- Gestion des catégories d'impro
- Gestion des matchs et événements

---

## Architecture

```
Internet (HTTPS 443)
    ↓
Nginx (reverse proxy)
    ↓
impro-manager (:3001) - Next.js
    ↓
PostgreSQL (databases-shared:5432)
```

---

## Stack technique

- **Frontend**: Next.js 14 + React
- **Backend**: Next.js API Routes
- **Base de données**: PostgreSQL (partagée)
- **Conteneur**: Docker

---

## Emplacements

- **Répertoire**: `/opt/impro-manager/`
- **Docker Compose**: `/opt/impro-manager/docker-compose.yml`
- **Nginx config**: `/etc/nginx/sites-available/impro-manager`
- **Documentation**: `/opt/impro-manager/DEPLOYMENT_GUIDE.md`
- **PRD**: `/opt/impro-manager/PRD.md`

---

## Gestion

### Démarrage/Arrêt

```bash
ssh root@69.62.108.82
cd /opt/impro-manager
docker-compose up -d
docker-compose down
```

### Logs

```bash
# Logs en temps réel
docker logs impro-manager -f

# Dernières 100 lignes
docker logs impro-manager --tail=100
```

### Status

```bash
docker ps | grep impro-manager
docker inspect impro-manager
```

---

## Configuration

### Variables d'environnement

Fichier: `/opt/impro-manager/.env`

```env
DATABASE_URL=postgresql://user:pass@postgresql-shared:5432/impro_manager
NEXT_PUBLIC_API_URL=https://impro.srv759970.hstgr.cloud
NODE_ENV=production
PORT=3001
```

### Base de données

- **Host**: `postgresql-shared` (container)
- **Port**: 5432
- **Database**: `impro_manager`
- **User**: Voir `.env`

Accès:
```bash
docker exec -it postgresql-shared psql -U postgres -d impro_manager
```

---

## Troubleshooting

### Container unhealthy

Le container est marqué "unhealthy" mais fonctionne. Cela peut indiquer :

1. Health check trop strict
2. Temps de démarrage long
3. Problème de connexion DB

Vérifier les logs :
```bash
docker logs impro-manager --tail=50
curl -I https://impro.srv759970.hstgr.cloud
```

### Rebuild de l'image

```bash
cd /opt/impro-manager
docker-compose build --no-cache
docker-compose up -d
```

---

## Documentation complète

Documentation détaillée disponible dans le repo :

- **[DEPLOYMENT_GUIDE.md](../../impro-manager/DEPLOYMENT_GUIDE.md)** - Guide de déploiement
- **[PRD.md](../../impro-manager/PRD.md)** - Product Requirements Document
- **[ACTION_PLAN.md](../../impro-manager/ACTION_PLAN.md)** - Plan d'action développement
- **[README.md](../../impro-manager/README.md)** - Vue d'ensemble technique

---

## Backup

### Base de données

```bash
docker exec postgresql-shared pg_dump -U postgres impro_manager > backup_impro_$(date +%Y%m%d).sql
```

### Code et assets

```bash
cd /opt/impro-manager
git pull  # Si géré via git
tar -czf backup_impro_files_$(date +%Y%m%d).tar.gz /opt/impro-manager/
```

---

## Voir aussi

- [PostgreSQL Shared](../infrastructure/databases-shared.md)
- [Nginx](../../infrastructure/nginx.md)
