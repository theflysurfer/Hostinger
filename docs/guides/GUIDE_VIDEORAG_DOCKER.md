# 🐳 Guide VideoRAG Docker - Installation et Configuration

> **VideoRAG Dockerisé**: Chat with Your Videos - Version conteneurisée

**Date d'installation**: 20 Octobre 2025
**Serveur**: srv759970.hstgr.cloud (69.62.108.82)
**URL**: https://videorag.srv759970.hstgr.cloud

---

## 📋 Architecture Docker

```
┌─────────────────────────────────────┐
│         Nginx (Host)                │
│  https://videorag.srv759970...      │
└───────────┬─────────────────────────┘
            │
            ▼
┌───────────────────────────────────┐
│   Docker Container: videorag      │
│   ┌───────────────────────────┐   │
│   │  VideoRAG Backend API     │   │
│   │  Python 3.11 + Flask      │   │
│   │  Port: 5000               │   │
│   └───────────────────────────┘   │
│   ┌───────────────────────────┐   │
│   │  Models (~8GB)            │   │
│   │  - MiniCPM-V (4GB)       │   │
│   │  - Whisper (1.5GB)       │   │
│   │  - ImageBind (2.4GB)     │   │
│   └───────────────────────────┘   │
└───────────────────────────────────┘
```

---

## ✅ Installation Complète

### Composants

1. **Dockerfile** - Image Python 3.11 avec toutes les dépendances
2. **docker-compose.yml** - Orchestration du service
3. **Nginx** - Reverse proxy HTTPS
4. **Volumes Docker**:
   - `videorag-data` - Données persistantes (vidéos uploadées)
   - `videorag-cache` - Cache des modèles
5. **Modèles** - Montés en read-only depuis l'hôte

---

## 🚀 Gestion du Container

### Démarrer VideoRAG

```bash
cd /opt/videorag
docker compose up -d
```

### Voir les logs

```bash
# Logs en temps réel
docker compose logs -f

# Dernières 100 lignes
docker compose logs --tail=100

# Logs du container uniquement
docker logs videorag -f
```

### Arrêter / Redémarrer

```bash
# Arrêter
docker compose stop

# Redémarrer
docker compose restart

# Arrêter et supprimer
docker compose down

# Arrêter et supprimer avec volumes
docker compose down -v
```

### Status

```bash
# Status des containers
docker compose ps

# Détails du container
docker inspect videorag

# Ressources utilisées
docker stats videorag
```

---

## 🔧 Configuration

### Variables d'environnement

Fichier: `/opt/videorag/.env`

```env
OPENAI_API_KEY=sk-proj-...
FLASK_ENV=production
PORT=5000
```

### Modifier la clé OpenAI

```bash
# Option 1: Éditer .env
nano /opt/videorag/.env

# Option 2: Éditer docker-compose.yml
nano /opt/videorag/docker-compose.yml

# Puis redémarrer
cd /opt/videorag
docker compose restart
```

---

## 📁 Structure des Fichiers

```
/opt/videorag/
├── Dockerfile                    # Image Docker
├── docker-compose.yml           # Orchestration
├── .env                         # Variables d'environnement
├── web/
│   └── index.html              # Frontend web
├── VideoRAG-algorithm/          # Code VideoRAG (monté)
│   ├── MiniCPM-V-2_6-int4/     # Modèle (read-only)
│   ├── faster-distil-whisper/   # Modèle (read-only)
│   └── .checkpoints/            # ImageBind (read-only)
└── Vimo-desktop/
    └── python_backend/          # Backend API (monté)
```

### Volumes Docker

```bash
# Lister les volumes
docker volume ls | grep videorag

# Inspecter un volume
docker volume inspect videorag_videorag-data

# Sauvegarder les données
docker run --rm -v videorag_videorag-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/videorag-backup.tar.gz /data
```

---

## 🔄 Mise à Jour

### Mettre à jour le code

```bash
cd /opt/videorag
git pull

# Rebuild et redémarrer
docker compose build
docker compose up -d
```

### Mettre à jour les dépendances Python

Modifier `Dockerfile`, puis:

```bash
cd /opt/videorag
docker compose build --no-cache
docker compose up -d
```

---

## 🐛 Troubleshooting

### Container ne démarre pas

```bash
# Voir les logs d'erreur
docker compose logs videorag

# Vérifier la config
docker compose config

# Rebuild sans cache
docker compose build --no-cache
docker compose up -d
```

### API ne répond pas

```bash
# Vérifier que le container tourne
docker compose ps

# Logs en temps réel
docker logs videorag -f

# Tester depuis l'hôte
curl http://localhost:5000/health

# Entrer dans le container
docker exec -it videorag bash
curl http://localhost:5000/health
```

### Problèmes de modèles

```bash
# Vérifier que les modèles sont bien montés
docker exec -it videorag ls -la /app/VideoRAG-algorithm/

# Vérifier les permissions
ls -la /opt/videorag/VideoRAG-algorithm/
```

### Problème d'espace disque

```bash
# Voir l'espace utilisé par Docker
docker system df

# Nettoyer les images inutilisées
docker system prune -a

# Nettoyer tout (ATTENTION!)
docker system prune -a --volumes
```

---

## 📊 Monitoring

### Ressources

```bash
# CPU et RAM en temps réel
docker stats videorag

# Voir les processus dans le container
docker top videorag
```

### Logs Nginx

```bash
# Access logs
tail -f /var/log/nginx/videorag-access.log

# Error logs
tail -f /var/log/nginx/videorag-error.log
```

### Health Check

Le container a un health check automatique:

```bash
# Status du health check
docker inspect videorag | grep -A 10 Health
```

---

## 🔐 Sécurité

### Bonnes Pratiques

1. **.env protégé**: `chmod 600 /opt/videorag/.env`
2. **Clé OpenAI**: Ne jamais commit dans git
3. **Modèles en read-only**: Montés avec `:ro`
4. **Restart policy**: `unless-stopped` pour redémarrage auto
5. **HTTPS**: Configuré avec Let's Encrypt

### Network Isolation

Le container utilise un réseau bridge dédié:

```bash
# Voir le réseau
docker network inspect videorag_videorag-network
```

---

## 🚀 Performance

### Optimisations

1. **Multi-stage build** possible pour réduire taille image
2. **Cache layers** Docker pour builds plus rapides
3. **Volumes** pour données persistantes
4. **Health check** pour monitoring automatique

### Limites de ressources

Ajouter dans `docker-compose.yml`:

```yaml
services:
  videorag:
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
        reservations:
          memory: 4G
```

---

## 📚 Commandes Utiles

```bash
# Build
docker compose build
docker compose build --no-cache

# Start/Stop
docker compose up -d
docker compose down

# Logs
docker compose logs -f
docker logs videorag -f

# Status
docker compose ps
docker stats videorag

# Shell dans le container
docker exec -it videorag bash
docker exec -it videorag python

# Restart
docker compose restart

# Pull latest
cd /opt/videorag && git pull
docker compose build && docker compose up -d
```

---

## ✅ Checklist

- [ ] Docker et docker-compose installés
- [ ] Repository cloné dans `/opt/videorag`
- [ ] Modèles téléchargés
- [ ] `.env` configuré avec clé OpenAI
- [ ] Nginx configuré
- [ ] HTTPS activé
- [ ] Container built
- [ ] Container running (`docker compose ps`)
- [ ] API répond (`curl localhost:5000/health`)
- [ ] Interface web accessible (https://videorag...)
- [ ] Logs corrects (`docker compose logs`)

---

## 🔗 Liens

- **Interface Web**: https://videorag.srv759970.hstgr.cloud
- **API Health**: https://videorag.srv759970.hstgr.cloud/api/health
- **GitHub VideoRAG**: https://github.com/HKUDS/VideoRAG
- **Docker Hub**: (si publié)

---

**Installation**: 20 Octobre 2025
**Type**: Docker Compose
**Version**: 1.0
