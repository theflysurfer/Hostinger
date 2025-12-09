# Bases de Données Partagées

**Emplacement**: `/opt/databases-shared/`
**Statut**: ✅ Opérationnel

---

## Vue d'ensemble

Infrastructure de bases de données mutualisées pour les services de collaboration et applications modernes. Trois moteurs de bases de données distincts pour différents cas d'usage.

### Composants

- **MongoDB** : Base NoSQL pour Rocket.Chat
- **PostgreSQL** : Base relationnelle pour Nextcloud, ONLYOFFICE
- **Redis** : Cache et sessions

---

## MongoDB

**Image**: `mongo:7`
**Port**: `27017` (localhost only)
**Configuration**: Replica Set (rs0)

### Utilisation

MongoDB est configuré en Replica Set pour supporter l'oplog (requis par Rocket.Chat pour le real-time).

#### Bases de données

| Database | Application | User |
|----------|-------------|------|
| `rocketchat` | Rocket.Chat | `rocketchat` |
| `nextcloud` | Nextcloud (metadata) | `nextcloud` |
| `loadbalancer` | Load Balancer (futur) | `loadbalancer` |
| `pipeline` | Pipeline Transcription (futur) | `pipeline` |

#### Connexion

```bash
# Shell MongoDB
docker exec -it mongodb-shared mongosh -u root -p PASSWORD

# Via application
mongodb://USERNAME:PASSWORD@mongodb-shared:27017/DATABASE?authSource=DATABASE
```

#### Replica Set

```bash
# Vérifier statut replica set
docker exec mongodb-shared mongosh -u root -p PASSWORD --eval "rs.status()"

# Membres du replica set
docker exec mongodb-shared mongosh -u root -p PASSWORD --eval "rs.conf()"
```

#### Backup

```bash
# Dump toutes les bases
docker exec mongodb-shared mongodump -u root -p PASSWORD --out=/backup

# Dump une base spécifique
docker exec mongodb-shared mongodump -u rocketchat -p PASSWORD --db=rocketchat --out=/backup

# Restore
docker exec mongodb-shared mongorestore -u root -p PASSWORD /backup
```

---

## PostgreSQL

**Image**: `postgres:17-alpine`
**Port**: `5432` (localhost only)

### Utilisation

PostgreSQL est utilisé pour les applications nécessitant une base relationnelle avec support transactionnel complet.

#### Bases de données

| Database | Application | User |
|----------|-------------|------|
| `nextcloud` | Nextcloud | `nextcloud` |
| `onlyoffice` | ONLYOFFICE | `onlyoffice` |
| `loadbalancer` | Load Balancer (futur) | `loadbalancer` |
| `pipeline` | Pipeline Transcription (futur) | `pipeline` |

#### Connexion

```bash
# psql shell
docker exec -it postgresql-shared psql -U postgres

# Via application
postgresql://USERNAME:PASSWORD@postgresql-shared:5432/DATABASE
```

#### Commandes utiles

```bash
# Lister bases
docker exec postgresql-shared psql -U postgres -c "\l"

# Lister tables d'une base
docker exec postgresql-shared psql -U postgres -d nextcloud -c "\dt"

# Taille des bases
docker exec postgresql-shared psql -U postgres -c "SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) FROM pg_database;"

# Vacuum
docker exec postgresql-shared psql -U postgres -d nextcloud -c "VACUUM ANALYZE;"
```

#### Backup

```bash
# Dump toutes les bases
docker exec postgresql-shared pg_dumpall -U postgres > all-databases.sql

# Dump une base spécifique
docker exec postgresql-shared pg_dump -U nextcloud nextcloud > nextcloud.sql

# Restore
cat nextcloud.sql | docker exec -i postgresql-shared psql -U nextcloud -d nextcloud
```

---

## Redis

**Image**: `redis:7-alpine`
**Port**: `6379` (localhost only)

### Utilisation

Redis est utilisé comme cache applicatif et stockage de sessions. Distinct du Redis RQ (port 6380) utilisé pour les queues de transcription.

#### Usage par application

| Application | Usage | DB |
|-------------|-------|-----|
| Nextcloud | Cache fichiers, sessions, locking | DB 0 |
| Rocket.Chat (futur) | Cache | DB 1 |
| Load Balancer (futur) | Rate limiting | DB 2 |

#### Connexion

```bash
# Redis CLI
docker exec -it redis-shared redis-cli -a PASSWORD

# Via application
redis://redis-shared:6379?password=PASSWORD&db=0
```

#### Commandes utiles

```bash
# Info général
docker exec redis-shared redis-cli -a PASSWORD INFO

# Statistiques par DB
docker exec redis-shared redis-cli -a PASSWORD INFO keyspace

# Nombre de clés
docker exec redis-shared redis-cli -a PASSWORD DBSIZE

# Vider une DB (ATTENTION!)
docker exec redis-shared redis-cli -a PASSWORD -n 0 FLUSHDB

# Monitor en temps réel
docker exec redis-shared redis-cli -a PASSWORD MONITOR
```

#### Configuration

- **maxmemory**: 512MB
- **maxmemory-policy**: `allkeys-lru` (éviction LRU si mémoire pleine)
- **Persistence**: Désactivée (cache volatile)

---

## Monitoring

### Exporters Prometheus

Trois exporters sont déployés pour collecter les métriques :

| Exporter | Port | Cible |
|----------|------|-------|
| **mongodb-exporter** | 9216 | MongoDB |
| **postgres-exporter** | 9187 | PostgreSQL |
| **redis-exporter** | 9121 | Redis |

#### Métriques disponibles

**MongoDB** :
- Connexions actives
- Opérations par seconde
- Taille des bases
- Replica set status

**PostgreSQL** :
- Connexions actives
- Transactions par seconde
- Taille des bases
- Cache hit ratio

**Redis** :
- Mémoire utilisée
- Hit/miss ratio
- Commandes par seconde
- Evictions

#### Visualisation

Les métriques sont visibles dans Grafana :
- URL: https://monitoring.srv759970.hstgr.cloud
- Dashboards: "Database Monitoring"

---

## Sécurité

### Authentification

- ✅ Authentification obligatoire sur toutes les bases
- ✅ Utilisateurs dédiés par application
- ✅ Passwords stockés dans `.env` (gitignored)

### Réseau

- ✅ Ports exposés uniquement sur `127.0.0.1` (localhost)
- ✅ Réseau Docker isolé `databases-shared`
- ❌ Pas d'accès direct depuis l'extérieur

### Permissions

#### MongoDB
```javascript
// Utilisateur application
{
  user: "rocketchat",
  roles: [
    { role: "readWrite", db: "rocketchat" }
  ]
}
```

#### PostgreSQL
```sql
-- Utilisateur application
GRANT ALL ON DATABASE nextcloud TO nextcloud;
GRANT ALL ON SCHEMA public TO nextcloud;
ALTER DATABASE nextcloud OWNER TO nextcloud;
```

---

## Maintenance

### Logs

```bash
# MongoDB
docker logs mongodb-shared --tail 100 -f

# PostgreSQL
docker logs postgresql-shared --tail 100 -f

# Redis
docker logs redis-shared --tail 100 -f
```

### Redémarrage

```bash
# Redémarrer une base
docker restart mongodb-shared
docker restart postgresql-shared
docker restart redis-shared

# Redémarrer toutes les bases (ATTENTION: downtime!)
cd /opt/databases-shared && docker-compose restart
```

### Nettoyage

#### MongoDB
```bash
# Compacter base
docker exec mongodb-shared mongosh -u root -p PASSWORD --eval "db.runCommand({compact: 'collection'})"
```

#### PostgreSQL
```bash
# Vacuum
docker exec postgresql-shared psql -U postgres -d nextcloud -c "VACUUM FULL;"
```

#### Redis
```bash
# Pas de nettoyage nécessaire (éviction automatique LRU)
```

---

## Troubleshooting

### MongoDB Replica Set non initialisé

**Symptôme**: Rocket.Chat erreur "oplog not available"

**Solution**:
```bash
docker exec mongodb-shared mongosh -u root -p PASSWORD --eval "rs.initiate({_id: 'rs0', members: [{_id: 0, host: 'mongodb-shared:27017'}]})"
```

### PostgreSQL connexion refusée

**Symptôme**: Application ne peut pas se connecter

**Solution**:
```bash
# Vérifier que conteneur tourne
docker ps --filter name=postgresql-shared

# Vérifier logs
docker logs postgresql-shared --tail 50

# Vérifier healthcheck
docker inspect postgresql-shared | grep -A 10 Health
```

### Redis mémoire pleine

**Symptôme**: Erreur "OOM command not allowed"

**Solution**:
```bash
# Vérifier mémoire utilisée
docker exec redis-shared redis-cli -a PASSWORD INFO memory

# Vider cache (si acceptable)
docker exec redis-shared redis-cli -a PASSWORD FLUSHALL
```

---

## Limites et quotas

### MongoDB
- **Max connections**: 1000 (configurable)
- **Oplog size**: 990 MB (5% de mémoire)

### PostgreSQL
- **Max connections**: 100 (configurable)
- **Shared buffers**: 128 MB

### Redis
- **Max memory**: 512 MB
- **Eviction**: Automatique (LRU)

---

## Ajout d'une nouvelle base

### MongoDB

```bash
# Créer base + user
docker exec mongodb-shared mongosh -u root -p ROOT_PASSWORD --eval '
use newdb
db.createUser({
  user: "newuser",
  pwd: "newpassword",
  roles: [{role: "readWrite", db: "newdb"}]
})
'
```

### PostgreSQL

```bash
# Créer base + user
docker exec postgresql-shared psql -U postgres -c "CREATE USER newuser WITH PASSWORD 'newpassword';"
docker exec postgresql-shared psql -U postgres -c "CREATE DATABASE newdb OWNER newuser;"
docker exec postgresql-shared psql -U postgres -d newdb -c "GRANT ALL ON SCHEMA public TO newuser;"
```

---

## Backup complet

### Script automatique

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/databases/$DATE"

mkdir -p $BACKUP_DIR

# MongoDB
docker exec mongodb-shared mongodump -u root -p PASSWORD --out=$BACKUP_DIR/mongodb

# PostgreSQL
docker exec postgresql-shared pg_dumpall -U postgres > $BACKUP_DIR/postgresql-all.sql

# Redis (pas nécessaire, cache volatile)

echo "Backup completed: $BACKUP_DIR"
```

---

**Dernière mise à jour**: 2025-10-21
**Configuration**: `/opt/databases-shared/docker-compose.yml`
