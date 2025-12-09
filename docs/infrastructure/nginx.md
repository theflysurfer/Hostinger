# Nginx Manager

**⚠️ Note** : La configuration Nginx est gérée dans un repo externe actif.

---

## Repo Principal

📁 **Localisation** : `C:\Users\JulienFernandez\OneDrive\Coding\_Projets de code\2025.10 Nginx Manager`

Le Nginx Manager est un système complet de gestion sécurisée avec :
- ✅ Backup automatique avant toute modification
- ✅ Tests de configuration avant reload
- ✅ Rollback en un clic
- ✅ Health checks automatiques
- ✅ Versioning Git des configurations

---

## Status Sécurité

**Audit complété le 2025-10-28**

| Métrique | Valeur |
|----------|--------|
| **Sites sécurisés** | 4/4 WordPress (100%) |
| **Score moyen** | 85% (+39% d'amélioration) |
| **Fail2ban jails** | 3 actifs (wordpress-auth, wordpress-hard, wordpress-xmlrpc) |

### Protections Actives
- ✅ Brute Force - Rate limiting + Fail2ban
- ✅ XML-RPC DDoS - Bloqué
- ✅ XSS - Content Security Policy
- ✅ Clickjacking - X-Frame-Options
- ✅ PHP Backdoor - Exécution bloquée dans /uploads/
- ✅ SSL - TLS 1.2/1.3 + OCSP Stapling

---

## Quick Commands

```bash
# Aller au repo Nginx Manager
cd "C:\Users\JulienFernandez\OneDrive\Coding\_Projets de code\2025.10 Nginx Manager"

# Health check
./scripts/health-check.sh

# Backup avant modification
./scripts/nginx-backup.sh mon-site

# Déployer une config (avec backup + tests automatiques)
./scripts/nginx-deploy.sh configs/sites-available/mon-site mon-site

# Rollback si problème
./scripts/nginx-rollback.sh --list mon-site
./scripts/nginx-rollback.sh mon-site 20251028-082230
```

---

## Sites Configurés

### WordPress (4 sites)
- **clemence-multidomains** - clemencefouquet.fr + alias
- **jesuishyperphagique** - jesuishyperphagique.srv759970.hstgr.cloud
- **panneauxsolidaires** - panneauxsolidaires.srv759970.hstgr.cloud
- **solidarlink** - solidarlink.srv759970.hstgr.cloud

### Services (30+ sites)
Tous les services du serveur ont une config Nginx :
- AI Services (WhisperX, RAGFlow, MemVid, etc.)
- Dashboards (Dashy, Grafana, etc.)
- Infrastructure (Portainer, Dozzle, etc.)

---

## Snippets Réutilisables

Les snippets Nginx sont dans `configs/snippets/` :

| Snippet | Usage |
|---------|-------|
| `basic-auth.conf` | Authentification HTTP Basic |
| `bot-protection.conf` | Protection contre les bots malveillants |
| `bot-protection-wordpress.conf` | Protection adaptée WordPress (autorise wp-admin) |

---

## Documentation Complète

Voir le repo Nginx Manager pour :
- **QUICKSTART.md** - Guide de démarrage rapide
- **README.md** - Documentation complète
- **docs/WORDPRESS_SECURITY.md** - Guide sécurité WordPress
- **docs/SECURITY_FINAL_REPORT.md** - Rapport d'audit détaillé
- **docs/GIT_WORKFLOW.md** - Workflow Git pour configs

---

## Intégration Future

Ce contenu sera migré ici dans `infrastructure/nginx/` une fois le repo stabilisé.

**Status actuel** : 🟡 Repo externe actif - Voir lien ci-dessus

---

**Dernière mise à jour** : 2025-10-28
