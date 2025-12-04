# Infrastructure - Vue d'Ensemble

**Serveur** : srv759970.hstgr.cloud (69.62.108.82)
**OS** : Ubuntu 24.04.2 LTS
**RAM** : 15 GB
**Disque** : 193 GB

---

## Composants Infrastructure

### 🖥️ [Serveur](server.md)
- Configuration système
- Utilisateurs (compte `automation`)
- SSH et sécurité
- Fail2ban
- Cron jobs

### 🌐 [Nginx Manager](nginx.md)
- Reverse proxy pour 30+ sites
- SSL/TLS (Let's Encrypt)
- Rate limiting et sécurité
- Bot protection
- Backup/rollback automatique

### 🗄️ [Bases de Données](databases.md)
- **PostgreSQL** partagé (MemVid, Nextcloud)
- **Redis** partagé (WhisperX, MemVid, Telegram Bot)
- **MongoDB** partagé (inutilisé actuellement)

### 🐳 [Docker Architecture](docker.md)
- 36 conteneurs actifs
- 19 stacks Docker Compose
- Réseaux partagés
- Volumes persistants
- Auto-start system

### 🔒 [Sécurité](security.md)
- Fail2ban (3 jails WordPress)
- Authentification Basic Auth
- SSL/TLS hardening
- Rate limiting
- Audit réguliers

---

## Statistiques

| Métrique | Valeur |
|----------|--------|
| **Conteneurs actifs** | 36 / 64 |
| **RAM utilisée** | ~12 GB / 15 GB |
| **Disque utilisé** | 77 GB / 193 GB (40%) |
| **Sites Nginx** | 30+ configurés |
| **Certificats SSL** | 30+ actifs |

---

## Services Critiques

### SPOF (Single Point of Failure)

**⚠️ Si down, impact multiple services :**

1. **redis-shared** → 4+ services affectés
2. **postgresql-shared** → 2 services affectés
3. **nginx** → Tous les sites down
4. **databases-shared** → Arrêt de nombreux services

**Recommandation** : Monitoring actif + alertes

---

## Quick Commands

```bash
# Se connecter au serveur
ssh automation@69.62.108.82

# État système
free -h                  # RAM
df -h                    # Disque
docker ps                # Conteneurs

# Services critiques
sudo systemctl status nginx
sudo systemctl status docker
docker ps | grep -E "redis|postgres"

# Logs
sudo journalctl -u nginx -n 50
docker logs <container> --tail 50
```

---

## Liens Rapides

- **[Nginx Manager](nginx.md)** - Gestion configs Nginx
- **[Databases](databases.md)** - Bases de données partagées
- **[Sécurité](security.md)** - Audit et hardening
- **[Docker](docker.md)** - Architecture conteneurs

---

**Dernière mise à jour** : 2025-10-28
