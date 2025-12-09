# Guide de Déploiement VPS

## Vue d'ensemble

Guide de déploiement complet pour srv759970.hstgr.cloud, incluant la configuration initiale du serveur et le déploiement de tous les services.

## Configuration Initiale du Serveur

### 1. Connexion SSH

```bash
ssh root@srv759970.hstgr.cloud
# ou
ssh root@69.62.108.82
```

### 2. Mise à Jour du Système

```bash
apt-get update && apt-get upgrade -y
apt-get install -y curl wget git htop vim net-tools
```

### 3. Installation Docker

```bash
# Installation des dépendances
apt-get install -y ca-certificates curl gnupg lsb-release

# Ajout de la clé GPG Docker
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Configuration du dépôt
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installation
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### 4. Installation Nginx

```bash
apt-get install -y nginx
systemctl enable nginx
systemctl start nginx
```

### 5. Installation Certbot

```bash
apt-get install -y certbot python3-certbot-nginx
```

### 6. Configuration du Pare-feu

```bash
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

## Déploiement des Services

### WhisperX (Transcription avec Diarization)

```bash
mkdir -p /opt/whisperx
cd /opt/whisperx

# Créer docker-compose.yml, server.py, worker.py
# (voir documentation WhisperX)

docker-compose up -d
```

**Vérification:**
```bash
curl http://localhost:8002/
docker logs whisperx-worker -f
```

### Faster-Whisper Queue

```bash
mkdir -p /opt/faster-whisper-queue
cd /opt/faster-whisper-queue

# Créer docker-compose.yml, server.py, worker.py, Dockerfile
# (voir documentation Faster-Whisper Queue)

docker-compose up -d
```

**Vérification:**
```bash
curl http://localhost:8003/health
curl http://localhost:8003/queue/stats
```

### Monitoring Stack (Grafana + Prometheus + Loki)

```bash
mkdir -p /opt/monitoring/{prometheus,loki,promtail,grafana/provisioning/{datasources,dashboards}}
cd /opt/monitoring

# Créer docker-compose.yml et fichiers de config
# (voir documentation Monitoring)

docker-compose up -d
```

**Vérification:**
```bash
curl http://localhost:3001  # Grafana
curl http://localhost:9090  # Prometheus
curl http://localhost:3100/ready  # Loki
```

### Dashy Dashboard

```bash
mkdir -p /opt/dashy
cd /opt/dashy

# Créer docker-compose.yml et conf.yml

docker-compose up -d
```

### Dozzle (Docker Logs Viewer)

```bash
docker run -d \
  --name dozzle \
  --restart unless-stopped \
  -p 8888:8080 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  amir20/dozzle:latest
```

### MkDocs Documentation

```bash
mkdir -p /opt/mkdocs/docs
cd /opt/mkdocs

# Créer mkdocs.yml, Dockerfile, docker-compose.yml
# Copier les fichiers de documentation

docker-compose up -d
```

## Configuration SSL/Nginx

### Créer les Certificats

```bash
# Monitoring
certbot certonly --nginx -d monitoring.srv759970.hstgr.cloud --non-interactive --agree-tos -m julien@julienfernandez.xyz

# WhisperX
certbot certonly --nginx -d whisperx.srv759970.hstgr.cloud --non-interactive --agree-tos -m julien@julienfernandez.xyz

# Dozzle
certbot certonly --nginx -d dozzle.srv759970.hstgr.cloud --non-interactive --agree-tos -m julien@julienfernandez.xyz

# Faster-Whisper
certbot certonly --nginx -d faster-whisper.srv759970.hstgr.cloud --non-interactive --agree-tos -m julien@julienfernandez.xyz
```

### Créer les Configurations Nginx

Pour chaque service, créer un fichier dans `/etc/nginx/sites-available/` et activer:

```bash
ln -sf /etc/nginx/sites-available/<service> /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### Configuration Basic Auth

```bash
# Créer le fichier de mots de passe
htpasswd -c /etc/nginx/.htpasswd admin

# Créer le snippet
cat > /etc/nginx/snippets/basic-auth.conf << EOF
auth_basic "Restricted Access";
auth_basic_user_file /etc/nginx/.htpasswd;
EOF
```

## Vérification Post-Déploiement

### Services Docker

```bash
# Tous les conteneurs en cours
docker ps

# Vérifier les logs
docker-compose logs -f
```

### Services HTTPS

```bash
# Monitoring
curl -I https://monitoring.srv759970.hstgr.cloud

# WhisperX
curl https://whisperx.srv759970.hstgr.cloud/

# Dozzle
curl -I https://dozzle.srv759970.hstgr.cloud

# Dashy
curl -I https://dashy.srv759970.hstgr.cloud
```

### Certificats SSL

```bash
certbot certificates
```

## Maintenance

### Mises à Jour

```bash
# Système
apt-get update && apt-get upgrade -y

# Images Docker
cd /opt/<service>
docker-compose pull
docker-compose up -d --build
```

### Backup

```bash
# Volumes Docker
docker run --rm -v <volume_name>:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz -C /data .

# Configurations Nginx
tar czf nginx-configs-$(date +%Y%m%d).tar.gz /etc/nginx/sites-available/
```

### Logs

```bash
# Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Docker
docker logs -f <container_name>

# Système
tail -f /var/log/syslog
```

## Troubleshooting

### Service ne démarre pas

```bash
# Voir les logs
docker logs <container_name> --tail 50

# Inspecter le conteneur
docker inspect <container_name>

# Vérifier le réseau
docker network inspect <network_name>
```

### Erreur 502 Nginx

```bash
# Vérifier que le service écoute
netstat -tlnp | grep <port>

# Logs Nginx
tail -50 /var/log/nginx/error.log

# Redémarrer le service
docker-compose restart
```

### Certificat SSL expiré

```bash
# Renouveler
certbot renew

# Recharger Nginx
systemctl reload nginx
```

## Structure Finale

```
/opt/
├── whisperx/
│   ├── docker-compose.yml
│   ├── server.py
│   └── worker.py
├── faster-whisper-queue/
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── server.py
│   ├── worker.py
│   └── requirements.txt
├── monitoring/
│   ├── docker-compose.yml
│   ├── prometheus/
│   ├── loki/
│   ├── promtail/
│   └── grafana/
├── dashy/
│   ├── docker-compose.yml
│   └── conf.yml
└── mkdocs/
    ├── docker-compose.yml
    ├── Dockerfile
    ├── mkdocs.yml
    └── docs/
```

```
/etc/nginx/
├── sites-available/
│   ├── monitoring
│   ├── whisperx-api
│   ├── dozzle
│   ├── dashy
│   └── faster-whisper-queue
├── sites-enabled/  (symlinks)
└── snippets/
    └── basic-auth.conf
```

## Ressources

- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Ubuntu Server Guide](https://ubuntu.com/server/docs)
