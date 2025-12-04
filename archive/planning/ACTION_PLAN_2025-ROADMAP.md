# Plan d'Action 2025 - srv759970

Roadmap stratégique pour l'infrastructure VPS.

## Vue d'ensemble

**Objectif global** : Optimiser l'utilisation des ressources, améliorer la fiabilité et faciliter la maintenance du serveur.

**Contraintes actuelles** :
- RAM : 8GB (actuellement 30% utilisée grâce à l'auto-start)
- CPU : 4 vCPU
- Stockage : ~150GB disponible
- Uptime : 195+ jours (excellente stabilité)

---

## Phase 1 : Consolidation (Immédiat - 2 semaines)

### 🎯 Objectifs
- Finaliser les services Whisper
- Standardiser la configuration
- Documenter l'existant

### Tâches

#### 1.1 WhisperX - Build et test ✅ EN COURS
```bash
# Priorité : HAUTE
# Durée : 1-2 heures
# Dépendances : HuggingFace token

cd /opt/whisperx
# Configurer .env avec HF_TOKEN
docker-compose build
docker-compose up -d
# Tester diarization
curl -F "file=@test.mp3" -F "diarize=true" https://whisperx.srv759970.hstgr.cloud/transcribe
docker-compose stop
```

**Bloqueur** : Token HuggingFace requis
**Action** : Créer compte HF → Accepter conditions pyannote → Générer token

#### 1.2 Versionning configuration serveur ⏸️
```bash
# Priorité : MOYENNE
# Durée : 2-3 heures

# Initialiser repository config
ssh root@69.62.108.82
mkdir -p /root/server-config
cd /root/server-config
git init

# Copier toutes les configs (suivre GIT_POLICY.md)
# Commit initial

# Créer cron backup hebdomadaire (optionnel)
crontab -e
# 0 2 * * 0 cd /root/server-config && git add . && git commit -m "Weekly snapshot"
```

#### 1.3 Ollama systemd socket activation ⏸️
```bash
# Priorité : BASSE (optimisation, pas urgent)
# Durée : 3-4 heures
# Bénéfice : Économie RAM supplémentaire (~1-2GB)

# Recherche et implémentation
# Voir : https://www.freedesktop.org/software/systemd/man/systemd.socket.html
```

**Risque** : Service critique pour plusieurs apps, tester prudemment

---

## Phase 2 : Optimisation (2-4 semaines)

### 🎯 Objectifs
- Réduire encore l'empreinte RAM
- Améliorer les temps de réponse
- Automatiser les backups

### Tâches

#### 2.1 Monitoring amélioré

**Action** : Dashboard centralisé de métriques auto-start

```javascript
// Ajouter dans /opt/docker-autostart/server.js
const metrics = {
  starts: {},    // Compteur démarrages par service
  stops: {},     // Compteur arrêts
  avgStartTime: {},  // Temps moyen démarrage
  lastAccess: {}
};

// Endpoint metrics
app.get('/metrics', (req, res) => {
  res.json(metrics);
});
```

**Intégration Netdata** : Exporter métriques vers Netdata

#### 2.2 Healthchecks personnalisés

**Problème** : Certains services lents à démarrer → 502 occasionnel

**Solution** : Healthchecks dans docker-compose

```yaml
# Exemple pour WhisperX
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8002/docs"]
  interval: 5s
  timeout: 3s
  retries: 3
  start_period: 30s
```

**Services concernés** :
- WhisperX (modèle lourd à charger)
- Tika (parsing engine lent au démarrage)
- Strapi (Node.js + DB connection)

#### 2.3 Backups automatiques

**Stratégie** :

1. **Bases de données** (quotidien)
   ```bash
   # Créer /root/scripts/backup-dbs.sh
   #!/bin/bash
   DATE=$(date +%Y-%m-%d)
   mkdir -p /backups/mysql/$DATE

   # WordPress Clémence
   docker exec mysql-clemence mysqldump -u root -p$MYSQL_ROOT_PASSWORD clemence_db > /backups/mysql/$DATE/clemence.sql

   # SolidarLink
   mysqldump -u root -p$MYSQL_ROOT_PASSWORD solidarlink_db > /backups/mysql/$DATE/solidarlink.sql

   # Retention 30 jours
   find /backups/mysql/ -type d -mtime +30 -exec rm -rf {} \;

   # Cron : 3h du matin tous les jours
   # 0 3 * * * /root/scripts/backup-dbs.sh
   ```

2. **Configurations** (hebdomadaire)
   ```bash
   # Déjà géré par Git si implémenté (Phase 1.2)
   # Sinon :
   rsync -av /etc/nginx/ /backups/nginx/
   rsync -av /opt/docker-autostart/ /backups/docker-autostart/
   ```

3. **Uploads** (hebdomadaire)
   ```bash
   # WordPress uploads
   tar czf /backups/uploads/clemence-$(date +%Y%m%d).tar.gz /opt/wordpress-clemence/wp-content/uploads
   tar czf /backups/uploads/solidarlink-$(date +%Y%m%d).tar.gz /var/www/solidarlink/wp-content/uploads
   ```

#### 2.4 Reverse proxy caching

**Objectif** : Réduire latence pour assets statiques

**Solution** : Nginx FastCGI cache

```nginx
# /etc/nginx/nginx.conf (http block)
fastcgi_cache_path /var/cache/nginx levels=1:2 keys_zone=WORDPRESS:100m inactive=60m;
fastcgi_cache_key "$scheme$request_method$host$request_uri";

# Dans chaque vhost WordPress
location ~ \.php$ {
    fastcgi_cache WORDPRESS;
    fastcgi_cache_valid 200 60m;
    fastcgi_cache_bypass $skip_cache;
    fastcgi_no_cache $skip_cache;
    # ... reste config PHP-FPM
}
```

**Bénéfice** : 2-3x plus rapide pour pages statiques

---

## Phase 3 : Nouveaux services (1-3 mois)

### 🎯 Objectifs
- Ajouter valeur avec nouveaux services
- Exploiter la RAM disponible
- Préparer futurs projets

### Services potentiels

#### 3.1 Redis Cache (haute priorité)

**Utilité** :
- Cache WordPress (W3 Total Cache, Redis Object Cache)
- Cache sessions Strapi
- Cache API responses (Tika, Whisper)

**Déploiement** :
```yaml
# docker-compose.yml
redis:
  image: redis:7-alpine
  container_name: redis
  restart: unless-stopped
  ports:
    - "127.0.0.1:6379:6379"
  volumes:
    - redis-data:/data
  command: redis-server --appendonly yes
  mem_limit: 256m
```

**RAM** : ~100-200MB
**Bénéfice** : 5-10x plus rapide pour données mises en cache

#### 3.2 MinIO (stockage S3-compatible)

**Utilité** :
- Offload uploads WordPress vers stockage objet
- Backups centralisés
- CDN-like pour assets statiques

**Déploiement** :
```yaml
minio:
  image: minio/minio:latest
  container_name: minio
  ports:
    - "127.0.0.1:9000:9000"
    - "127.0.0.1:9001:9001"  # Console
  volumes:
    - minio-data:/data
  environment:
    - MINIO_ROOT_USER=admin
    - MINIO_ROOT_PASSWORD=<générer>
  command: server /data --console-address ":9001"
```

**RAM** : ~200-300MB
**Storage** : Configurable (recommandé : dédier 50GB)

#### 3.3 Uptime Kuma (monitoring)

**Utilité** :
- Monitoring uptime de tous les services
- Alertes email/Slack si service down
- Dashboard public optionnel

**Déploiement** :
```yaml
uptime-kuma:
  image: louislam/uptime-kuma:1
  container_name: uptime-kuma
  ports:
    - "8504:3001"
  volumes:
    - uptime-kuma-data:/app/data
  restart: unless-stopped
```

**RAM** : ~150MB
**URL** : https://uptime.srv759970.hstgr.cloud

#### 3.4 Plausible Analytics (alternatif Google Analytics)

**Utilité** :
- Analytics respectueux vie privée
- GDPR-compliant
- Self-hosted

**Déploiement** : Complexe (PostgreSQL + ClickHouse requis)
**RAM** : ~800MB-1GB
**Priorité** : BASSE (uniquement si besoin analytics)

---

## Phase 4 : Scalabilité (3-6 mois)

### 🎯 Objectifs
- Préparer croissance traffic
- Haute disponibilité
- CI/CD automatisé

### Projets

#### 4.1 Load Balancing (si multi-VPS futur)

**Scénario** : Si un 2ème VPS est ajouté

```nginx
# /etc/nginx/nginx.conf
upstream backend_pool {
    server 69.62.108.82:8501;  # VPS 1
    server 203.0.113.45:8501;  # VPS 2 hypothétique
    least_conn;
}

server {
    location / {
        proxy_pass http://backend_pool;
    }
}
```

#### 4.2 CI/CD avec GitHub Actions

**Workflow** : Push code → Auto-deploy sur serveur

```yaml
# .github/workflows/deploy.yml
name: Deploy to VPS
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy via SSH
        uses: appleboy/ssh-action@master
        with:
          host: 69.62.108.82
          username: root
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/myapp
            git pull
            docker-compose up -d --build
```

**Services concernés** :
- WhisperX (build custom)
- API Portal (HTML updates)
- Docker-autostart (code changes)

#### 4.3 Secrets management avec Vault

**Alternative à .env éparpillés**

```bash
# Installer HashiCorp Vault
docker run -d --name=vault \
  -p 8200:8200 \
  --cap-add=IPC_LOCK \
  vault server -dev

# Stocker secrets
vault kv put secret/whisperx HF_TOKEN=hf_xxxxx

# Récupérer dans docker-compose
HF_TOKEN=$(vault kv get -field=HF_TOKEN secret/whisperx)
```

**RAM** : ~100MB
**Complexité** : Élevée
**Priorité** : BASSE (sauf si compliance requis)

---

## Phase 5 : Nettoyage et décommission (6-12 mois)

### 🎯 Objectifs
- Retirer services obsolètes
- Simplifier stack
- Libérer ressources

### Services à évaluer

#### 5.1 WordPress Multisite ⛔

**Statut** : Marqué pour décommission
**Action** :
1. Vérifier aucune dépendance active
2. Backup final complet
3. Arrêter Nginx vhost
4. Archiver `/var/www/wordpress/`
5. Supprimer après 3 mois sans incident

#### 5.2 Cristina Site (Astro)

**Statut** : Actif mais statique
**Évaluation** : Si plus mis à jour → Déplacer vers hébergement statique (Netlify, Vercel)
**Bénéfice** : Libérer Nginx config, simplifier maintenance

---

## Métriques de succès

### Phase 1 (Immédiat)
- [ ] WhisperX opérationnel avec diarization
- [ ] Configuration serveur versionnée dans Git
- [ ] 100% des services documentés

### Phase 2 (2-4 semaines)
- [ ] Healthchecks sur tous les services critiques
- [ ] Backups automatiques fonctionnels (test restore OK)
- [ ] Zéro 502 Bad Gateway pendant 30 jours
- [ ] RAM usage moyen < 35% (actuellement 30%)

### Phase 3 (1-3 mois)
- [ ] Redis déployé et utilisé par ≥2 services
- [ ] Uptime monitoring actif (SLA target: 99.5%)
- [ ] 1 nouveau service à valeur ajoutée déployé

### Phase 4 (3-6 mois)
- [ ] CI/CD configuré pour ≥1 service
- [ ] Documentation complète pour onboarding nouveau dev
- [ ] Auto-scaling proof-of-concept validé

---

## Risques et mitigation

### Risque 1 : Dépassement RAM
**Probabilité** : Faible (30% usage actuel)
**Impact** : Élevé (OOM kills, downtime)
**Mitigation** :
- Monitoring continu (Netdata alerts < 80%)
- Auto-start aggressif (idle 15 min au lieu de 30)
- Upgrade VPS si >70% soutenu (99€/mois → 149€/mois pour 16GB)

### Risque 2 : Complexité excessive
**Probabilité** : Moyenne
**Impact** : Moyen (temps maintenance ↑)
**Mitigation** :
- Principe YAGNI (You Ain't Gonna Need It)
- Évaluer ROI avant chaque nouveau service
- Décommissionner services non utilisés

### Risque 3 : Perte données (corruption, ransomware)
**Probabilité** : Faible
**Impact** : Critique
**Mitigation** :
- Backups 3-2-1 : 3 copies, 2 médias, 1 offsite
- Test restore mensuel
- Snapshots VPS Hostinger (manuel avant changements majeurs)

### Risque 4 : SSL expiration
**Probabilité** : Très faible (Certbot auto-renew)
**Impact** : Moyen (warning navigateur, perte confiance)
**Mitigation** :
- Vérifier logs Certbot : `journalctl -u certbot.timer`
- Alert si renouvellement échoue
- Fallback : Renouvellement manuel

---

## Coûts estimés

### Serveur actuel
- VPS Hostinger 8GB : ~99€/mois ✅

### Projets Phase 3
- Redis : Inclus (RAM disponible)
- MinIO : Inclus (storage disponible)
- Uptime Kuma : Inclus

**Total Phase 3 : 0€ supplémentaire**

### Projets Phase 4 (optionnel)
- 2ème VPS (si scaling) : +99€/mois
- Vault Enterprise (si compliance) : ~500€/an
- CI/CD : Gratuit (GitHub Actions free tier)

**Total Phase 4 : 0€ à +100€/mois selon besoins**

### Services externes potentiels
- Backups offsite (Backblaze B2) : ~5€/mois pour 100GB
- CDN (Cloudflare Pro) : 20$/mois (optionnel, Free tier souvent suffisant)
- Monitoring externe (UptimeRobot) : Gratuit jusqu'à 50 monitors

---

## Prochaines étapes (Semaine prochaine)

### Lundi-Mardi
1. ✅ Obtenir HuggingFace token
2. ✅ Build et tester WhisperX
3. ✅ Valider diarization fonctionne
4. ✅ Documenter résultats

### Mercredi-Jeudi
5. ⏸️ Initialiser repository `/root/server-config/`
6. ⏸️ Commit snapshot configuration actuelle
7. ⏸️ Créer script backup bases de données
8. ⏸️ Tester restore backup

### Vendredi
9. ⏸️ Évaluer besoin Ollama socket activation (ROI?)
10. ⏸️ Planifier Phase 2 en détail
11. ⏸️ Mise à jour documentation locale

---

## Conclusion

**Priorités immédiates** :
1. WhisperX opérationnel
2. Versioning configuration
3. Backups automatiques

**Vision long terme** :
- Infrastructure stable, bien documentée, facile à maintenir
- Utilisation optimale des ressources (RAM, CPU, storage)
- Prête pour croissance future sans refonte majeure

**Principe directeur** : **Simplicité > Sophistication**

Mieux vaut 5 services fiables et bien maintenus que 15 services complexes et fragiles.

---

**Dernière mise à jour** : Octobre 2025
**Prochaine révision** : Janvier 2026
