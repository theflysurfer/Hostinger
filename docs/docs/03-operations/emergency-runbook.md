# 🚨 Emergency Runbook - srv759970.hstgr.cloud

**Version:** 1.0
**Dernière mise à jour:** 2025-10-27
**Usage:** Procédures d'urgence pour incidents critiques

---

## ⚡ Incidents Critiques - Réponse Rapide

### 🔴 Niveau 1: Serveur Complètement Inaccessible

**Symptôme:** Impossible de SSH, tous les services down

#### Diagnostic (5 min)

1. **Tester connectivité réseau:**
```bash
# Depuis machine locale
ping 69.62.108.82
ping srv759970.hstgr.cloud
```

2. **Vérifier depuis Hostinger Panel:**
   - Se connecter: https://hpanel.hostinger.com
   - VPS > srv759970 > Console VNC
   - Vérifier si serveur boot ou kernel panic

#### Actions Immédiates

**Si serveur down physiquement:**
1. Hostinger Panel > VPS > Redémarrer
2. Attendre 5-10 minutes
3. Tester SSH: `ssh root@69.62.108.82`
4. Si échec répété → Contacter support Hostinger

**Si serveur accessible en VNC mais pas SSH:**
```bash
# Dans console VNC
systemctl status sshd
systemctl restart sshd
systemctl status nginx
systemctl status docker
```

---

### 🟠 Niveau 2: Serveur Accessible, Services Down

**Symptôme:** SSH OK, mais tous les services web ne répondent pas

#### Diagnostic Rapide (2 min)

```bash
ssh root@69.62.108.82

# 1. Vérifier services critiques
systemctl status nginx
systemctl status docker

# 2. Vérifier conteneurs actifs
docker ps | wc -l
# Attendu: 15-25 conteneurs

# 3. Vérifier RAM
free -h
# Si >28GB utilisés → OOM imminent

# 4. Vérifier disque
df -h
# / doit avoir >10% libre
```

#### Actions par Priorité

**Priorité 1: Nginx (Reverse Proxy)**
```bash
# Tester config
nginx -t

# Si erreur de config
cd /etc/nginx/sites-enabled
ls -la
# Désactiver dernière config modifiée
rm <fichier-problematique>
nginx -t

# Redémarrer
systemctl restart nginx
systemctl status nginx
```

**Priorité 2: Docker Daemon**
```bash
systemctl status docker

# Si inactive
systemctl start docker
sleep 10

# Vérifier
docker ps
```

**Priorité 3: Services Critiques Always-On**
```bash
# Redis Queue (dépendance transcription)
docker ps | grep rq-queue-redis
docker logs rq-queue-redis --tail 50

# Si arrêté
cd /opt/whisperx  # ou /opt/faster-whisper-queue
docker-compose up -d rq-queue-redis

# Dashy Portal
docker ps | grep dashy
cd /opt/dashy
docker-compose up -d

# MkDocs Documentation
docker ps | grep mkdocs
cd /opt/mkdocs
docker-compose up -d
```

---

### 🟡 Niveau 3: Un Service Spécifique Ne Répond Pas

**Symptôme:** Service X timeout ou erreur 502/503

#### Diagnostic Service (3 min)

```bash
# 1. Identifier le service
SERVICE_NAME="whisperx"  # Remplacer par le vrai nom

# 2. Vérifier conteneur
docker ps | grep $SERVICE_NAME
docker ps -a | grep $SERVICE_NAME  # Inclut arrêtés

# 3. Vérifier logs
docker logs $SERVICE_NAME --tail 100

# 4. Vérifier config Nginx
grep -r "$SERVICE_NAME" /etc/nginx/sites-available/
cat /etc/nginx/sites-available/$SERVICE_NAME

# 5. Tester port interne
# Trouver le port dans docker-compose.yml
cd /opt/$SERVICE_NAME
cat docker-compose.yml | grep ports
# Exemple: "8002:8000" → port interne 8002
curl -I http://127.0.0.1:8002
```

#### Actions de Résolution

**Cas 1: Conteneur arrêté (auto-start expected)**
```bash
# Vérifier si service dans auto-start
cat /opt/docker-autostart/config.json | grep -i $SERVICE_NAME

# Si oui → Attendre 30-180s après première requête
# Si non → Démarrer manuellement
cd /opt/$SERVICE_NAME
docker-compose up -d
```

**Cas 2: Conteneur running mais ne répond pas**
```bash
cd /opt/$SERVICE_NAME

# Voir logs erreurs
docker-compose logs --tail 100

# Redémarrer
docker-compose restart

# Si échec persistant
docker-compose down
docker-compose up -d

# Vérifier healthcheck (si configuré)
docker inspect $SERVICE_NAME | grep -A 20 Health
```

**Cas 3: Erreur 502 Bad Gateway**
```bash
# Problème Nginx → backend
# 1. Vérifier port dans nginx
cat /etc/nginx/sites-available/$SERVICE_NAME | grep proxy_pass
# Exemple: proxy_pass http://127.0.0.1:8002;

# 2. Vérifier que port est ouvert
netstat -tlnp | grep 8002

# 3. Tester backend direct
curl -I http://127.0.0.1:8002

# 4. Si backend OK mais nginx KO → recharger nginx
nginx -t
systemctl reload nginx
```

---

## 📋 Checklist de Diagnostic Complet

### Phase 1: Santé Système (5 min)

```bash
# Connexion
ssh root@69.62.108.82

# 1. Ressources système
free -h
df -h
uptime
top -bn1 | head -20

# 2. Services système
systemctl status nginx
systemctl status docker
systemctl status fail2ban  # Si configuré

# 3. Conteneurs Docker
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | head -30
docker stats --no-stream | head -20

# 4. Logs système récents
journalctl -xe --since "10 minutes ago" | tail -50
```

**Seuils d'alerte:**
- RAM: >28GB/32GB → CRITIQUE
- Disque /: <10% libre → CRITIQUE
- Load average: >8.0 → ATTENTION
- Conteneurs: <10 actifs → ANORMAL

### Phase 2: Services Critiques (5 min)

```bash
# Redis Queue (transcription)
docker exec -it rq-queue-redis redis-cli ping
# Attendu: PONG

docker exec -it rq-queue-redis redis-cli
SELECT 0
LLEN transcription  # Queue WhisperX
SELECT 1
LLEN faster-whisper-transcription  # Queue Faster-Whisper
exit

# Nginx Config
nginx -t
# Attendu: test is successful

# Auto-Start Proxy
curl http://127.0.0.1:8890
# Attendu: HTML ou "Service not configured"

# Dashy Portal
curl -I https://dashy.srv759970.hstgr.cloud
# Attendu: 200 OK ou 401 (Basic Auth)

# MkDocs
curl -I https://docs.srv759970.hstgr.cloud
# Attendu: 200 OK
```

### Phase 3: Monitoring & Logs (5 min)

```bash
# Grafana (si accessible)
curl -I https://monitoring.srv759970.hstgr.cloud

# Dozzle (logs temps réel)
curl -I https://dozzle.srv759970.hstgr.cloud

# Prometheus
curl http://srv759970.hstgr.cloud:9090/-/healthy
# Attendu: Healthy

# Logs Nginx erreurs récentes
tail -100 /var/log/nginx/error.log

# Logs Nginx access par service
ls -lh /var/log/nginx/*-access.log
tail -50 /var/log/nginx/dashy-access.log
```

---

## 🔧 Procédures de Réparation Courantes

### Redémarrage Propre d'un Service Docker

```bash
SERVICE_DIR="/opt/whisperx"  # Exemple
cd $SERVICE_DIR

# 1. Voir config actuelle
docker-compose config

# 2. Arrêt propre
docker-compose down
# Attendre 5 secondes
sleep 5

# 3. Vérifier volumes/réseau nettoyés
docker volume ls | grep $(basename $SERVICE_DIR)
docker network ls | grep $(basename $SERVICE_DIR)

# 4. Redémarrage
docker-compose up -d

# 5. Vérifier logs démarrage
docker-compose logs -f --tail 50
# Ctrl+C pour quitter

# 6. Tester service
docker-compose ps
```

### Rebuild Complet d'un Service

```bash
cd /opt/<service>

# 1. Backup config si nécessaire
cp docker-compose.yml docker-compose.yml.backup-$(date +%Y%m%d-%H%M%S)

# 2. Arrêt et nettoyage
docker-compose down -v  # ATTENTION: -v supprime volumes!

# 3. Rebuild images
docker-compose build --no-cache

# 4. Redémarrage
docker-compose up -d

# 5. Vérifier
docker-compose logs -f
```

### Nettoyage Docker (Espace Disque)

```bash
# Voir espace utilisé
docker system df

# Nettoyer images inutilisées
docker image prune -a
# Attention: Supprime toutes images non utilisées!

# Nettoyer volumes orphelins
docker volume prune

# Nettoyer conteneurs arrêtés
docker container prune

# Nettoyer réseaux inutilisés
docker network prune

# Nettoyage complet (DANGEREUX!)
# docker system prune -a --volumes
# ⚠️ Ne faire que si disque critique <5%
```

### Redémarrage Nginx Sécurisé

```bash
# 1. Backup config actuelle
tar -czf /root/backups/nginx-$(date +%Y%m%d-%H%M%S).tar.gz /etc/nginx/

# 2. Tester config
nginx -t

# 3. Si OK → reload (sans interruption)
systemctl reload nginx

# 4. Si erreur → rollback
cd /etc/nginx/sites-enabled
rm <fichier-problematique>
nginx -t
systemctl reload nginx

# 5. Vérifier
systemctl status nginx
curl -I https://dashy.srv759970.hstgr.cloud
```

---

## 🔥 Scénarios d'Urgence Spécifiques

### OOM (Out of Memory) - RAM >30GB

**Symptôme:** Services crashent aléatoirement, système lent

```bash
# 1. Identifier gros consommateurs
docker stats --no-stream | sort -k4 -h | tail -10

# 2. Arrêter services non-critiques
cd /opt/nextcloud && docker-compose down
cd /opt/jitsi && docker-compose down
cd /opt/ragflow/docker && docker-compose down
cd /opt/paperless && docker-compose down

# 3. Vérifier RAM libérée
free -h

# 4. Si encore critique, arrêter plus
cd /opt/whisperx && docker-compose down
cd /opt/faster-whisper-queue && docker-compose down

# 5. Investigation après stabilisation
dmesg | grep -i "out of memory"
journalctl -xe | grep -i oom
```

### Disque Plein - / >95%

**Symptôme:** Services ne démarrent pas, erreurs "No space left"

```bash
# 1. Identifier gros dossiers
du -h --max-depth=2 /opt | sort -h | tail -20
du -h --max-depth=2 /var | sort -h | tail -20

# 2. Logs Docker (souvent gros)
du -sh /var/lib/docker/containers/*
docker system df

# 3. Nettoyer logs
journalctl --vacuum-size=500M
find /var/log -name "*.log" -mtime +30 -delete
docker system prune -a

# 4. Volumes Docker
docker volume ls
docker volume prune
```

### Redis Queue Bloquée

**Symptôme:** Jobs WhisperX/Faster-Whisper ne se traitent pas

```bash
# 1. Inspecter queues
docker exec -it rq-queue-redis redis-cli

SELECT 0  # WhisperX
LLEN transcription
LRANGE transcription 0 5  # Voir jobs

SELECT 1  # Faster-Whisper
LLEN faster-whisper-transcription
LRANGE faster-whisper-transcription 0 5

# 2. Voir workers actifs
docker ps | grep worker

# 3. Redémarrer workers
cd /opt/whisperx
docker-compose restart whisperx-worker

cd /opt/faster-whisper-queue
docker-compose restart faster-whisper-worker

# 4. Si queue corrompue (DERNIER RECOURS!)
SELECT 0
DEL transcription  # ⚠️ PERD TOUS LES JOBS!
exit
```

### Certificat SSL Expiré

**Symptôme:** Erreur SSL dans navigateur

```bash
# 1. Vérifier expiration
certbot certificates

# 2. Renouveler
certbot renew

# 3. Si erreur, forcer renouveau
certbot renew --force-renewal

# 4. Recharger Nginx
nginx -t
systemctl reload nginx

# 5. Tester
curl -I https://dashy.srv759970.hstgr.cloud
```

---

## 📞 Contacts & Escalade

### Informations Serveur

- **Hébergeur:** Hostinger
- **Panel:** https://hpanel.hostinger.com
- **Support:** https://www.hostinger.com/contact
- **IP:** 69.62.108.82
- **Hostname:** srv759970.hstgr.cloud

### Credentials Critiques

**Localisation:** (À compléter par Julien)
- Root SSH: Clé SSH
- Hostinger Panel: (email + password)
- Nginx Basic Auth: `julien:DevAccess2025` (fichier `/etc/nginx/.htpasswd`)

### Escalade

**Niveau 1: Self-Service (0-30 min)**
- Utiliser ce runbook
- Consulter logs
- Redémarrer services

**Niveau 2: Documentation (30 min - 2h)**
- [Nginx Troubleshooting](guides/infrastructure/nginx-troubleshooting.md)
- [Docker Commands](reference/docker/commands.md)
- [Changelog](changelog/) pour modifications récentes

**Niveau 3: Support Hostinger (2h+)**
- Panel Hostinger > Support Ticket
- Console VNC si SSH impossible
- Backup restoration si corruption

---

## 📊 Monitoring & Prévention

### Métriques à Surveiller

**Quotidien:**
- RAM usage: `free -h` (alerte >25GB)
- Disque: `df -h` (alerte >85%)
- Conteneurs actifs: `docker ps | wc -l` (alerte <10)

**Hebdomadaire:**
- Logs Nginx: `tail -500 /var/log/nginx/error.log`
- Updates système: `apt list --upgradable`
- Certificats SSL: `certbot certificates`

**Mensuel:**
- Backup vérification
- Nettoyage Docker: `docker system prune`
- Review auto-start logs

### Dashboards de Monitoring

1. **Grafana:** https://monitoring.srv759970.hstgr.cloud
   - CPU, RAM, Disque
   - Métriques Redis Queue
   - Logs agrégés (Loki)

2. **Dozzle:** https://dozzle.srv759970.hstgr.cloud
   - Logs Docker temps réel
   - Tous conteneurs

3. **Status Pages (Auto-générées):**
   - [SERVER_STATUS.md](SERVER_STATUS.md)
   - [SERVICES_STATUS.md](SERVICES_STATUS.md)

---

## 🔄 Procédures de Maintenance Préventive

### Mise à Jour Mensuelle

```bash
# 1. Backup complet
/root/scripts/backup-full.sh  # Si existe

# 2. Updates système
apt update
apt list --upgradable
apt upgrade -y

# 3. Reboot si kernel update
shutdown -r now

# 4. Après reboot, vérifier services
systemctl status docker nginx
docker ps | wc -l

# 5. Updates Docker images
cd /opt/dashy && docker-compose pull && docker-compose up -d
cd /opt/mkdocs && docker-compose pull && docker-compose up -d
# Répéter pour services critiques
```

### Nettoyage Trimestriel

```bash
# Logs anciens
journalctl --vacuum-time=60d
find /var/log -name "*.log" -mtime +90 -delete

# Docker cleanup
docker system prune -a --volumes
# ⚠️ Valider avant!

# Backups anciens
find /root/backups -mtime +180 -delete
```

---

## 📝 Post-Mortem Template

Après chaque incident, documenter:

```markdown
# Incident YYYY-MM-DD - [Titre]

## Chronologie
- HH:MM - Détection
- HH:MM - Diagnostic
- HH:MM - Action X
- HH:MM - Résolution

## Cause Racine
[Description]

## Impact
- Services affectés: [Liste]
- Durée: X minutes
- Users impactés: [Estimation]

## Actions Correctives
1. Immédiate: [Fait]
2. Court terme: [TODO]
3. Long terme: [TODO]

## Prévention Future
[Mesures à mettre en place]
```

Sauvegarder dans: `docs/incidents/YYYY-MM-DD-<titre>.md`

---

## ✅ Checklist Après Résolution

- [ ] Tous les services critiques UP
- [ ] Nginx reload sans erreur
- [ ] Docker containers count normal (15-25)
- [ ] RAM < 25GB
- [ ] Disque < 80%
- [ ] Dashy accessible
- [ ] MkDocs accessible
- [ ] Monitoring fonctionnel
- [ ] Logs vérifiés (pas d'erreurs)
- [ ] Post-mortem documenté (si incident majeur)
- [ ] Mise à jour `changelog/` si modification config

---

**Ce runbook est un document vivant. L'améliorer après chaque incident!**

*Dernière révision: 2025-10-27*
