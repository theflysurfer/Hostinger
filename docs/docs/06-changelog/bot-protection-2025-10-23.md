# 🛡️ Déploiement Protection Anti-Bots & Optimisation Auto-Start

**Date** : 23 octobre 2025
**Statut** : ✅ Déployé en production

---

## 📋 Résumé

Déploiement d'une protection nginx contre les scans automatiques de bots qui empêchaient le système docker-autostart de fonctionner correctement. Les services lourds en RAM (RAGFlow, XTTS, Paperless) ne s'arrêtaient jamais car constamment sollicités par des bots.

**Résultats attendus** :
- Réduction des requêtes de bots de ~80%
- Auto-stop fonctionnel après 15 min d'inactivité réelle
- Économie potentielle : ~10.3 GB RAM (sur 16 GB total)

---

## 🔍 Problème Identifié

### Scans de bots observés dans les logs

**1. WordPress Clémence** - Attaque xmlrpc.php :
```
34.29.224.209 (Google Cloud)
POST //xmlrpc.php HTTP/1.1
20+ requêtes en 1 seconde
Toutes les 2-3 minutes
```

**2. Nextcloud** - Scan fichiers .env :
```
44.251.145.131 (AWS)
GET /.env, /.env.local, /.env.dev, /.env.prod, etc.
20 variantes testées systématiquement
```

**3. Domaine principal** - LeakIX scanner :
```
178.128.207.138 (DigitalOcean)
User-Agent: l9scan/2.0 (LeakIX)
GET /.git/config, /.env, /.DS_Store, /config.json
Toutes les 2-3 minutes
```

### Impact sur docker-autostart

```
15:00:00 - Service arrêté (idle)
15:02:37 - Bot teste /.git/config → Service se réveille → Timer reset
15:05:12 - Bot teste /admin → Timer reset
15:07:45 - Shodan scan → Timer reset

❌ Résultat : Service ne reste JAMAIS idle assez longtemps
```

---

## ✅ Solution Déployée

### 1. Protection nginx anti-bots

**Fichier** : `/etc/nginx/snippets/bot-protection.conf`

**Bloque** :
- Fichiers cachés : `/.git`, `/.env`, `/.DS_Store`
- WordPress : `/xmlrpc.php`, `/wp-admin`, `/wp-login.php`
- Admin panels : `/phpmyadmin`, `/adminer`, `/admin`
- Fichiers config : `/config.json`, `/composer.json`, `/package.json`
- Scanners connus : LeakIX, Shodan, Censys, Nikto, sqlmap

**Déploiement** :
- ✅ 70 vhosts nginx mis à jour
- ✅ Configuration validée
- ✅ Nginx rechargé

### 2. Timeouts docker-autostart optimisés

**Avant** :
- Global : 1800s (30 min)
- Services lourds : 1800s (30 min)

**Après** :
- Global : 1800s (30 min) - inchangé
- **Services lourds : 900s (15 min)** ⚡

**Services avec timeout 15 min** :
1. RAGFlow + Elasticsearch (~6.5 GB)
2. XTTS Text-to-Speech (~2.5 GB)
3. Paperless-ngx (~1.3 GB)
4. MemVid API (~490 MB)
5. Nextcloud (~130 MB)
6. Jitsi Meet (~220 MB)
7. WordPress SolidarLink
8. WordPress Clémence
9. WordPress Je Suis Hyperphagique
10. WordPress Panneaux Solidaires

**Backup config** : `/opt/docker-autostart/config.json.backup-20251023-160503`

---

## 📊 Métriques Avant/Après

### État AVANT déploiement

```
Services "Up 2 days" (jamais arrêtés) :
- ragflow-server : 1.868 GiB
- ragflow-es-01 : 4.339 GiB
- xtts-api : 2.523 GiB
- memvid-api : 481.6 MiB
- nextcloud : 151.2 MiB

RAM : 14Gi/15Gi utilisée (93%)
Containers running : 41/64
```

### État APRÈS redémarrage serveur

```
Tous services redémarrés (Up 56 seconds)
Services démarrent à la demande
Timeout 15 min actif
Bot protection active
```

### Vérification dans 24h

Pour vérifier l'efficacité :
```bash
ssh root@69.62.108.82 "bash /opt/scripts/check-autostart-status.sh"
```

Attendu :
- Services lourds arrêtés si pas utilisés
- RAM libre : 5-10 GB
- Logs nginx : requêtes bots bloquées (403/404)

---

## 🔧 Scripts Déployés

### `/opt/scripts/deploy-bot-protection.sh`
Déploie la protection anti-bots sur tous les vhosts nginx.

**Usage** :
```bash
bash /opt/scripts/deploy-bot-protection.sh
```

### `/opt/scripts/set-autostart-timeout.sh`
Modifie les timeouts des services lourds.

**Usage** :
```bash
bash /opt/scripts/set-autostart-timeout.sh <seconds>

# Exemples :
bash /opt/scripts/set-autostart-timeout.sh 180   # 3 min (test)
bash /opt/scripts/set-autostart-timeout.sh 900   # 15 min (prod)
bash /opt/scripts/set-autostart-timeout.sh 1800  # 30 min (défaut)
```

### `/opt/scripts/check-autostart-status.sh`
Vérifie le statut et la RAM des services auto-start.

**Usage** :
```bash
bash /opt/scripts/check-autostart-status.sh
```

---

## 🧪 Tests de Validation

### 1. Vérifier le blocage des bots

```bash
# Tester depuis l'extérieur
curl https://ragflow.srv759970.hstgr.cloud/.git/config
# Attendu : 404 Not Found

curl https://clemence.srv759970.hstgr.cloud/xmlrpc.php
# Attendu : 404 Not Found

# Voir les requêtes bloquées dans les logs
ssh root@69.62.108.82 "tail -f /var/log/nginx/*error.log | grep denied"
```

### 2. Vérifier l'auto-stop

```bash
# Laisser un service idle pendant 20 minutes
# Vérifier qu'il s'arrête bien

ssh root@69.62.108.82 "docker ps | grep ragflow"
# Attendu après 15 min idle : aucun résultat
```

### 3. Vérifier la RAM disponible

```bash
ssh root@69.62.108.82 "free -h"
# Attendu : 5-10 GB disponibles si services lourds arrêtés
```

---

## 📝 Fichiers Modifiés

**Locaux (repo)** :
- `nginx-bot-protection.conf` (nouveau)
- `deploy-bot-protection.sh` (nouveau)
- `docs/BOT_PROTECTION_DEPLOYMENT.md` (nouveau)

**Serveur** :
- `/etc/nginx/snippets/bot-protection.conf` (nouveau)
- `/etc/nginx/sites-available/*` (70 vhosts modifiés)
- `/opt/docker-autostart/config.json` (timeouts 900s)
- `/opt/scripts/deploy-bot-protection.sh` (nouveau)
- `/opt/scripts/set-autostart-timeout.sh` (existant, utilisé)
- `/opt/scripts/check-autostart-status.sh` (existant, utilisé)

---

## 🔄 Rollback si Nécessaire

Si problème, restaurer la config précédente :

```bash
# Restaurer config docker-autostart
ssh root@69.62.108.82
cp /opt/docker-autostart/config.json.backup-20251023-160503 \
   /opt/docker-autostart/config.json
systemctl restart docker-autostart

# Retirer bot protection des vhosts
cd /etc/nginx/sites-available
for f in *; do
    sed -i '/bot-protection.conf/d' "$f"
done
nginx -t && systemctl reload nginx
```

---

## 📈 Monitoring Recommandé

### Dashboards Grafana

Ajouter métriques :
- Nombre de requêtes 403/404 par vhost (bots bloqués)
- RAM libre au fil du temps
- Nombre de conteneurs running

### Alertes

Configurer alerte si :
- RAM libre < 2GB pendant > 30 min
- Services lourds up > 24h consécutives

---

## 🎯 Prochaines Étapes (Optionnel)

1. **Fail2Ban pour bots agressifs**
   - Bannir IPs avec > 10 req/min sur chemins bloqués
   - Durée : 24h

2. **Rate limiting nginx**
   ```nginx
   limit_req_zone $binary_remote_addr zone=bot:10m rate=5r/m;
   limit_req zone=bot burst=10 nodelay;
   ```

3. **Augmenter limites SSH**
   ```
   # /etc/ssh/sshd_config
   MaxStartups 30:30:60
   MaxSessions 30
   ```

4. **Cloudflare Bot Management**
   - Activer "Bot Fight Mode"
   - Challenge JS pour requêtes suspectes

---

## 📚 Références

- Logs nginx : `/var/log/nginx/*-access.log`
- Config docker-autostart : `/opt/docker-autostart/config.json`
- Scripts monitoring : `/opt/scripts/`
- Documentation : `docs/services/docker-autostart-config.md`

---

**🤖 Généré avec Claude Code**
