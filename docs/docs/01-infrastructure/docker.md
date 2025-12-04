# Docker - Gestion des Conteneurs

## Vue d'ensemble

Tous les services de srv759970 sont déployés via Docker et Docker Compose pour assurer l'isolation, la portabilité et la facilité de gestion.

## Installation Docker

### Version installée

```bash
docker --version
# Docker version 24.0.x

docker-compose --version
# Docker Compose version 2.x
```

## Structure des Services

### Organisation des dossiers

```
/opt/
├── whisperx/                   # WhisperX avec RQ queue
├── faster-whisper-queue/       # Faster-Whisper avec RQ queue
├── monitoring/                 # Stack Grafana + Prometheus + Loki
├── dashy/                      # Dashboard services
├── mkdocs/                     # Documentation site
└── wordpress-*/                # Sites WordPress
```

## Commandes Docker Essentielles

### Gestion des conteneurs

```bash
# Lister tous les conteneurs en cours
docker ps

# Lister tous les conteneurs (y compris arrêtés)
docker ps -a

# Voir les logs d'un conteneur
docker logs <container_name>
docker logs -f <container_name>  # Mode suivi
docker logs --tail 50 <container_name>  # 50 dernières lignes

# Redémarrer un conteneur
docker restart <container_name>

# Arrêter un conteneur
docker stop <container_name>

# Supprimer un conteneur
docker rm <container_name>

# Exécuter une commande dans un conteneur
docker exec -it <container_name> bash
docker exec <container_name> <commande>
```

### Gestion avec Docker Compose

```bash
# Démarrer tous les services
docker-compose up -d

# Arrêter tous les services
docker-compose down

# Voir les logs
docker-compose logs -f

# Redémarrer un service
docker-compose restart <service_name>

# Reconstruire et redémarrer
docker-compose up -d --build

# Vérifier le statut
docker-compose ps
```

### Gestion des images

```bash
# Lister les images
docker images

# Supprimer une image
docker rmi <image_id>

# Pull une nouvelle version
docker pull <image_name>

# Nettoyer les images inutilisées
docker image prune -a
```

### Gestion des volumes

```bash
# Lister les volumes
docker volume ls

# Inspecter un volume
docker volume inspect <volume_name>

# Supprimer un volume
docker volume rm <volume_name>

# Nettoyer les volumes inutilisés
docker volume prune
```

### Gestion des réseaux

```bash
# Lister les réseaux
docker network ls

# Inspecter un réseau
docker network inspect <network_name>

# Créer un réseau
docker network create <network_name>

# Connecter un conteneur à un réseau
docker network connect <network_name> <container_name>
```

## Réseaux Docker Utilisés

### whisperx_whisperx
Réseau partagé pour tous les services de transcription:
- rq-queue-redis (Redis partagé)
- whisperx, whisperx-worker
- faster-whisper, faster-whisper-queue-api, faster-whisper-worker
- monitoring (rq-exporter)

### monitoring_monitoring
Réseau pour la stack de monitoring:
- prometheus
- grafana
- loki
- promtail

## Bonnes Pratiques

### Healthchecks

Tous les services critiques ont des healthchecks configurés:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 10s
  timeout: 5s
  retries: 3
  start_period: 30s
```

### Logs

Configuration de rotation des logs:

```yaml
logging:
  driver: json-file
  options:
    max-size: '10m'
    max-file: '3'
```

### Restart Policy

```yaml
restart: unless-stopped
```

Garantit que les conteneurs redémarrent automatiquement sauf arrêt manuel.

## Monitoring Docker

### Stats en temps réel

```bash
# Stats de tous les conteneurs
docker stats

# Stats d'un conteneur spécifique
docker stats <container_name>
```

### Inspection détaillée

```bash
# Inspecter un conteneur
docker inspect <container_name>

# Voir les processus dans un conteneur
docker top <container_name>

# Voir les ports mappés
docker port <container_name>
```

## Dépannage

### Conteneur qui redémarre en boucle

```bash
# Voir les logs
docker logs --tail 100 <container_name>

# Inspecter le statut
docker inspect <container_name> | grep -A 10 "State"

# Vérifier le healthcheck
docker inspect <container_name> | grep -A 20 "Health"
```

### Problèmes réseau

```bash
# Vérifier la connectivité entre conteneurs
docker exec <container1> ping <container2>

# Inspecter le réseau
docker network inspect <network_name>

# Voir les réseaux d'un conteneur
docker inspect <container_name> | grep -A 10 "Networks"
```

### Espace disque

```bash
# Voir l'utilisation disque de Docker
docker system df

# Nettoyer tout ce qui est inutilisé
docker system prune -a --volumes

# Nettoyer uniquement les conteneurs arrêtés
docker container prune

# Nettoyer uniquement les images
docker image prune -a
```

## Backup et Restore

### Backup d'un volume

```bash
docker run --rm \
  -v <volume_name>:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/<volume_name>-backup.tar.gz -C /data .
```

### Restore d'un volume

```bash
docker run --rm \
  -v <volume_name>:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/<volume_name>-backup.tar.gz -C /data
```

## Services Démarrés au Boot

Les conteneurs avec `restart: unless-stopped` redémarrent automatiquement au boot du serveur.

Vérifier que Docker démarre au boot:

```bash
systemctl is-enabled docker
# Devrait retourner: enabled

# Si pas activé:
systemctl enable docker
```

## Mise à Jour des Services

### Procédure standard

```bash
cd /opt/<service_name>

# Pull les nouvelles images
docker-compose pull

# Rebuild si custom Dockerfile
docker-compose build --no-cache

# Redémarrer avec nouvelles versions
docker-compose up -d

# Vérifier les logs
docker-compose logs -f
```

### Rollback si problème

```bash
# Lister les images disponibles
docker images

# Retourner à une ancienne image
docker tag <old_image_id> <image_name>:latest
docker-compose up -d
```

## Ressources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)
