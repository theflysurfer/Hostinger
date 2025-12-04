# Bases de Données Partagées

**Stack** : databases-shared
**Localisation** : `/opt/databases-shared/`
**Status** : 🟢 Actif

---

## Vue d'Ensemble

Infrastructure de bases de données mutualisées pour optimiser les ressources.

### Services Inclus

| Service | Image | RAM | Port | Usage |
|---------|-------|-----|------|-------|
| **postgresql-shared** | postgres:17-alpine | ~31 MB | 5432 | MemVid, Nextcloud |
| **redis-shared** | redis:7-alpine | ~7 MB | 6379 | MemVid, WhisperX, Telegram Bot |
| **mongodb-shared** | mongo:7 | ~101 MB | 27017 | (Actuellement inutilisé) |

### Monitoring

| Exporter | Port | Monitore |
|----------|------|----------|
| **postgres-exporter** | 9187 | Métriques PostgreSQL → Prometheus |
| **redis-exporter** | 9121 | Métriques Redis → Prometheus |

---

## PostgreSQL Partagé

### Bases de Données Actives

```bash
# Lister les bases
docker exec postgresql-shared psql -U postgres -c '\l'

# Voir les connexions actives
docker exec postgresql-shared psql -U postgres -c "SELECT datname, usename, client_addr FROM pg_stat_activity WHERE state = 'active';"
```

### Services Utilisant PostgreSQL

1. **memvid-api** - Base de données MemVid
2. **nextcloud** - Données Nextcloud (si actif)

### Configuration

**Credentials** : Voir `/opt/databases-shared/.env`

```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<voir .env>
POSTGRES_DB=postgres
```

---

## Redis Partagé

### Databases Redis (DB0-DB15)

| DB | Service | Usage |
|----|---------|-------|
| **DB 0** | WhisperX | Queue RQ pour transcription |
| **DB 1** | Faster-Whisper | Queue RQ pour transcription |
| **DB 2** | MemVid | Cache + queue worker |
| **DB 3** | Telegram Bot | Cache sessions |

### Commandes Utiles

```bash
# Voir les clés par DB
docker exec redis-shared redis-cli -n 0 KEYS '*'  # DB 0 (WhisperX)
docker exec redis-shared redis-cli -n 1 KEYS '*'  # DB 1 (Faster-Whisper)

# Voir les connexions actives
docker exec redis-shared redis-cli CLIENT LIST

# Info mémoire
docker exec redis-shared redis-cli INFO memory
```

---

## MongoDB Partagé

**Status** : 🔴 Arrêté (aucun service actif ne l'utilise)

### Actions Possibles

1. **Supprimer si inutilisé**
```bash
cd /opt/databases-shared
docker-compose stop mongodb-shared
docker-compose rm -f mongodb-shared
docker volume rm databases-shared_mongo-data
```

2. **Ou réactiver si besoin futur**
```bash
docker-compose up -d mongodb-shared
```

---

## Backup Strategy

### PostgreSQL Backup

```bash
# Backup d'une base spécifique
docker exec postgresql-shared pg_dump -U postgres memvid_db > backup-memvid-$(date +%Y%m%d).sql

# Backup de toutes les bases
docker exec postgresql-shared pg_dumpall -U postgres > backup-all-postgres-$(date +%Y%m%d).sql
```

### Redis Backup

```bash
# Redis persiste automatiquement dans /data
# Backup du fichier RDB
docker cp postgresql-shared:/data/dump.rdb backup-redis-$(date +%Y%m%d).rdb
```

---

## Volumes

```bash
databases-shared_postgres-data    # PostgreSQL data (actuellement vide)
databases-shared_redis-data       # Redis persistence
databases-shared_mongo-data       # MongoDB data (inutilisé)
```

---

## Monitoring

### Métriques Prometheus

Les exporters exposent des métriques pour Grafana :

**PostgreSQL Exporter** : `http://localhost:9187/metrics`
- Connexions actives
- Transactions/sec
- Taille des bases
- Query performance

**Redis Exporter** : `http://localhost:9121/metrics`
- Mémoire utilisée
- Hit rate cache
- Connexions actives
- Commandes/sec

---

## Dépendances Critiques

**⚠️ ATTENTION** : Ces services sont des **SPOF (Single Point of Failure)**

### Si PostgreSQL down
- ❌ MemVid API non fonctionnel
- ❌ Nextcloud non accessible (si actif)

### Si Redis down
- ❌ WhisperX workers arrêtés
- ❌ Faster-Whisper workers arrêtés
- ❌ MemVid worker arrêté
- ❌ Telegram Bot déconnecté

**Recommandation** : Monitoring actif + alertes si down

---

## Troubleshooting

### PostgreSQL ne démarre pas

```bash
# Voir les logs
docker logs postgresql-shared --tail 50

# Vérifier les permissions
docker exec postgresql-shared ls -la /var/lib/postgresql/data

# Restart
docker restart postgresql-shared
```

### Redis out of memory

```bash
# Voir la mémoire utilisée
docker exec redis-shared redis-cli INFO memory

# Flush une DB si besoin
docker exec redis-shared redis-cli -n 2 FLUSHDB

# Augmenter maxmemory dans docker-compose.yml
# redis-cli CONFIG SET maxmemory 512mb
```

---

## Configuration Docker Compose

**Fichier** : `/opt/databases-shared/docker-compose.yml`

```yaml
services:
  postgresql-shared:
    image: postgres:17-alpine
    container_name: postgresql-shared
    restart: unless-stopped
    ports:
      - "127.0.0.1:5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    networks:
      - databases-shared

  redis-shared:
    image: redis:7-alpine
    container_name: redis-shared
    restart: unless-stopped
    ports:
      - "127.0.0.1:6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - databases-shared

  # ... (autres services)
```

---

**Dernière mise à jour** : 2025-10-28
**Documentation complète** : Voir `docs/services/infrastructure/databases-shared.md`
