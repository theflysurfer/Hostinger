# Docker - Commandes Courantes

Référence rapide des commandes Docker et Docker Compose les plus utilisées.

## Docker - Gestion des Conteneurs

### Lister les conteneurs

```bash
# Conteneurs en cours d'exécution
docker ps

# Tous les conteneurs (y compris arrêtés)
docker ps -a

# Format personnalisé
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Logs

```bash
# Voir les logs
docker logs <container_name>

# Suivre les logs en temps réel
docker logs -f <container_name>

# 50 dernières lignes
docker logs --tail 50 <container_name>

# Avec timestamps
docker logs -t <container_name>

# Depuis une date
docker logs --since 2024-01-01 <container_name>
```

### Redémarrer / Arrêter

```bash
# Redémarrer
docker restart <container_name>

# Arrêter
docker stop <container_name>

# Arrêter avec timeout (défaut 10s)
docker stop -t 30 <container_name>

# Démarrer
docker start <container_name>

# Tuer (force)
docker kill <container_name>
```

### Exécuter des commandes

```bash
# Shell interactif
docker exec -it <container_name> bash
docker exec -it <container_name> sh  # Si bash non disponible

# Commande unique
docker exec <container_name> ls -la /app
docker exec <container_name> cat /app/config.json

# En tant qu'utilisateur spécifique
docker exec -u root <container_name> apt-get update
```

### Inspecter

```bash
# Informations complètes
docker inspect <container_name>

# IP address
docker inspect <container_name> | grep IPAddress

# Env variables
docker inspect <container_name> | grep -A 20 Env

# Ports
docker port <container_name>

# Processus
docker top <container_name>

# Stats temps réel
docker stats <container_name>
```

### Supprimer

```bash
# Supprimer conteneur arrêté
docker rm <container_name>

# Forcer suppression (même si running)
docker rm -f <container_name>

# Supprimer tous les conteneurs arrêtés
docker container prune
```

## Docker Compose

### Démarrer / Arrêter

```bash
# Démarrer tous les services
docker-compose up -d

# Démarrer service spécifique
docker-compose up -d <service_name>

# Arrêter tous les services
docker-compose down

# Arrêter et supprimer volumes
docker-compose down -v

# Arrêter sans supprimer conteneurs
docker-compose stop
```

### Logs

```bash
# Logs de tous les services
docker-compose logs

# Suivre en temps réel
docker-compose logs -f

# Service spécifique
docker-compose logs -f <service_name>

# 50 dernières lignes
docker-compose logs --tail 50
```

### Rebuild

```bash
# Reconstruire et redémarrer
docker-compose up -d --build

# Reconstruire sans cache
docker-compose build --no-cache

# Service spécifique
docker-compose build <service_name>
```

### Status

```bash
# Status des services
docker-compose ps

# Vérifier config
docker-compose config

# Valider config
docker-compose config --quiet
```

### Autres

```bash
# Redémarrer service
docker-compose restart <service_name>

# Exécuter commande
docker-compose exec <service_name> bash

# Scaler service
docker-compose up -d --scale <service_name>=3
```

## Docker - Images

```bash
# Lister images
docker images

# Pull image
docker pull <image_name>:<tag>

# Supprimer image
docker rmi <image_id>

# Supprimer images non utilisées
docker image prune -a

# Tag image
docker tag <image_id> <new_name>:<tag>
```

## Docker - Volumes

```bash
# Lister volumes
docker volume ls

# Inspecter volume
docker volume inspect <volume_name>

# Créer volume
docker volume create <volume_name>

# Supprimer volume
docker volume rm <volume_name>

# Supprimer volumes non utilisés
docker volume prune
```

## Docker - Réseaux

```bash
# Lister réseaux
docker network ls

# Inspecter réseau
docker network inspect <network_name>

# Créer réseau
docker network create <network_name>

# Connecter conteneur à réseau
docker network connect <network_name> <container_name>

# Déconnecter
docker network disconnect <network_name> <container_name>
```

## Systemctl (pour services Docker)

```bash
# Démarrer Docker daemon
systemctl start docker

# Arrêter Docker daemon
systemctl stop docker

# Redémarrer Docker daemon
systemctl restart docker

# Status Docker daemon
systemctl status docker

# Activer au démarrage
systemctl enable docker

# Logs Docker daemon
journalctl -u docker -f
```

## Nettoyage Système

```bash
# Nettoyer tout (conteneurs, images, volumes, réseaux)
docker system prune -a --volumes

# Nettoyer seulement conteneurs arrêtés
docker container prune

# Nettoyer seulement images
docker image prune -a

# Nettoyer seulement volumes
docker volume prune

# Voir utilisation disque
docker system df
```

## Exemples Pratiques srv759970

### Vérifier tous les services

```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Logs WhisperX

```bash
cd /opt/whisperx
docker-compose logs -f whisperx
docker-compose logs -f whisperx-worker
```

### Redémarrer Faster-Whisper

```bash
cd /opt/faster-whisper-queue
docker-compose restart
```

### Logs Redis partagé

```bash
docker logs -f rq-queue-redis
```

### Monitoring usage mémoire

```bash
docker stats --no-stream
```

### Nettoyer vieux conteneurs

```bash
docker container prune -f
docker image prune -a -f
```

## Voir aussi

- [Infrastructure > Docker](../../infrastructure/docker.md) - Documentation complète Docker
- [Docker Compose Snippets](compose-patterns.md) - Configurations réutilisables
- [Guides > Docker Autostart](../../guides/deployment/docker-autostart-setup.md) - Auto-démarrage services
