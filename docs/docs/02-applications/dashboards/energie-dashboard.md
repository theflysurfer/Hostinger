# Energie Dashboard - Projet DownTo40

**Tags** : `production`, `dashboard`, `streamlit`, `downto40`

**Status** : 🟢 Actif en production
**URL** : https://energie.srv759970.hstgr.cloud
**Localisation** : `/opt/energie-40eur-dashboard/`

---

## Description

Dashboard Streamlit pour visualisation et analyse des prix de l'électricité dans le cadre du projet **DownTo40**.

### Fonctionnalités

- 📊 Visualisation prix électricité temps réel
- 📈 Graphiques historiques
- 🔔 Alertes seuils de prix
- 💡 Recommandations optimisation

---

## Architecture

### Stack Technique

| Composant | Technologie |
|-----------|-------------|
| **Frontend** | Streamlit |
| **Backend** | Python 3.11 |
| **Data Source** | API externe (prix électricité) |
| **Déploiement** | Docker Compose |

### Docker Compose

```yaml
services:
  energie-40eur-dashboard:
    build: .
    container_name: energie-40eur-dashboard
    restart: unless-stopped
    ports:
      - "8501:8501"
    environment:
      - API_KEY=${ELECTRICITY_API_KEY}
```

---

## Configuration Nginx

**Site** : `energie.srv759970.hstgr.cloud`

```nginx
server {
    listen 443 ssl http2;
    server_name energie.srv759970.hstgr.cloud;

    ssl_certificate /etc/letsencrypt/live/energie.srv759970.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/energie.srv759970.hstgr.cloud/privkey.pem;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Déploiement

### Initial Setup

```bash
# Depuis le serveur
cd /opt/energie-40eur-dashboard
docker-compose up -d

# Vérifier les logs
docker logs -f energie-40eur-dashboard
```

### Mise à Jour

```bash
# Pull latest code
cd /opt/energie-40eur-dashboard
git pull origin main

# Rebuild et redémarrer
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## Données et API

### Source de Données

L'application récupère les données depuis l'API publique des prix de l'électricité.

**Configuration** : Voir `/opt/energie-40eur-dashboard/.env`

```bash
ELECTRICITY_API_KEY=<clé API>
ELECTRICITY_API_URL=https://api.example.com/v1/prices
```

---

## Monitoring

### Health Check

```bash
# Vérifier que le container tourne
docker ps | grep energie-40eur-dashboard

# Tester l'accès HTTP
curl -I https://energie.srv759970.hstgr.cloud

# Logs en direct
docker logs -f energie-40eur-dashboard
```

### Métriques

- **Uptime** : Visible dans Dashy portal
- **Usage mémoire** : ~123 MB
- **CPU** : Faible (dashboard statique principalement)

---

## Troubleshooting

### Dashboard ne charge pas

```bash
# 1. Vérifier que le container tourne
docker ps | grep energie

# 2. Voir les logs
docker logs energie-40eur-dashboard --tail 50

# 3. Restart si besoin
docker restart energie-40eur-dashboard
```

### Erreur API

```bash
# Vérifier que la clé API est valide
docker exec energie-40eur-dashboard env | grep API_KEY

# Tester l'API manuellement
curl -H "Authorization: Bearer $API_KEY" https://api.example.com/v1/prices
```

---

## Backup

### Code

Le code est versionné dans un repo Git (privé ou local).

```bash
# Backup manuel
cd /opt/energie-40eur-dashboard
tar czf ~/backups/energie-dashboard-$(date +%Y%m%d).tar.gz .
```

### Configuration

```bash
# Backup du .env
cp /opt/energie-40eur-dashboard/.env ~/backups/.env.energie-dashboard-$(date +%Y%m%d)
```

---

## Liens Utiles

- **Dashboard Live** : https://energie.srv759970.hstgr.cloud
- **Dashy Portal** : https://dashy.srv759970.hstgr.cloud
- **Logs Dozzle** : https://dozzle.srv759970.hstgr.cloud (chercher `energie`)

---

## Notes Projet DownTo40

Ce dashboard est au cœur du projet **DownTo40** visant à :
- Réduire la facture d'électricité à 40€/mois
- Optimiser la consommation selon les heures creuses
- Alerter sur les pics de prix

**Priorité** : 🔴 Haute - Dashboard principal du projet

---

**Dernière mise à jour** : 2025-10-28
**Responsable** : Julien Fernandez
