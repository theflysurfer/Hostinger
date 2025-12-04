# 🤖 Instructions pour LLM - Déploiement VPS Hostinger

> **Principe DRY** : Ce document ne duplique PAS la documentation technique. Il référence les guides appropriés et ajoute uniquement les workflows spécifiques aux LLM.

---

## 📚 Documentation disponible

| Fichier | Quand le lire |
|---------|---------------|
| `GUIDE_DEPLOIEMENT_VPS.md` | Déploiement d'applications **Docker** (Streamlit, Flask, React, etc.) |
| `GUIDE_SERVICES_SYSTEMD.md` | Déploiement de services **systemd** (Ollama, PostgreSQL, etc.) |
| `../infrastructure/nginx.md` | Configuration **Nginx** (sites statiques, reverse proxy, troubleshooting) |
| `GUIDE_WORDPRESS_DOCKER.md` | Migration **WordPress** vers Docker (PHP-FPM, MySQL, permissions, proxy) |
| `GUIDE_ASTRO.md` | Déploiement sites **Astro** (SSG, build statique, résolution 404) |
| `GUIDE_STRAPI.md` | Déploiement **Strapi CMS** (Docker Node 22, bugs Vite, mode production) |
| `README.md` | Vue d'ensemble et scripts disponibles |

---

## 🎯 Workflow autonome pour LLM

### Étape 0 : Identifier le type de déploiement

```
Question à poser : "Docker ou service natif ?"

→ Application web (Streamlit, Flask, React, etc.)
  ➜ Lire GUIDE_DEPLOIEMENT_VPS.md

→ Service système (Ollama, base de données, etc.)
  ➜ Lire GUIDE_SERVICES_SYSTEMD.md

→ Pas sûr ?
  ➜ Demander à l'utilisateur
```

### Étape 1 : Vérifier les prérequis

```bash
# TOUJOURS vérifier SSH avant de commencer
ssh root@69.62.108.82 "whoami && hostname"
# Attendu: root\nsrv759970
```

Si échec → Informer l'utilisateur que la clé SSH n'est pas configurée.

### Étape 2 : Lire le guide approprié

**NE PAS dupliquer les instructions du guide.**
Lire le fichier et suivre les étapes exactement.

### Étape 3 : Créer une checklist (si tâche complexe)

**Règle** : Si la tâche nécessite **plus de 3 étapes**, utiliser l'outil TodoWrite.

Exemple :
```
- [ ] Vérifier connexion SSH
- [ ] Choisir port disponible
- [ ] Créer structure /opt/mon-app
- [ ] Transférer fichiers
- [ ] Build Docker
- [ ] Vérifier logs
```

### Étape 4 : Exécuter et vérifier

**Important** :
- Vérifier chaque commande avant l'exécution
- Ne JAMAIS deviner les paramètres manquants
- Lire les logs en cas d'erreur

### Étape 5 : Informer l'utilisateur

Format de rapport :
```
✅ Déploiement réussi !

Application : mon-app
URL : http://69.62.108.82:8502
Statut : En ligne

Commandes utiles :
- Logs : ssh root@69.62.108.82 "docker logs mon-app"
- Redémarrer : ssh root@69.62.108.82 "docker restart mon-app"
```

---

## 🚨 Règles strictes

### ❌ NE JAMAIS

1. **Deviner des valeurs** : Si l'utilisateur ne spécifie pas un port, demander
2. **Dupliquer la doc** : Référencer les guides au lieu de recopier
3. **Ignorer les erreurs** : Toujours lire les logs en cas d'échec
4. **Modifier sans vérifier** : Toujours tester avec `nginx -t`, `docker-compose config`, etc.
5. **Committer des secrets** : Vérifier `.env`, `*.key` avant tout transfert

### ✅ TOUJOURS

1. **Vérifier SSH** en premier
2. **Lire le guide approprié** (Docker vs systemd)
3. **Créer une checklist** si >3 étapes
4. **Vérifier les logs** après déploiement
5. **Donner l'URL finale** à l'utilisateur

---

## 🔍 Décision rapide : Docker ou systemd ?

```
┌─────────────────────────────────────┐
│ C'est une application web ?         │
│ (Streamlit, Flask, React, etc.)     │
└───────────┬─────────────────────────┘
            │
        OUI │ NON
            │
            ▼
    ┌───────────────┐      ┌──────────────────┐
    │ DOCKER        │      │ Service système? │
    │               │      │ (Ollama, DB...)  │
    └───────────────┘      └────────┬─────────┘
            │                       │
            │                   OUI │ NON
            │                       │
            ▼                       ▼
    GUIDE_DEPLOIEMENT_VPS    GUIDE_SERVICES_SYSTEMD
```

---

## 📋 Templates de communication

### Demander confirmation

```
J'ai identifié que vous souhaitez déployer [TYPE_APP].
Je vais utiliser [DOCKER/SYSTEMD] et le port [PORT].

Souhaitez-vous que je procède ?
```

### Rapport de succès

```
✅ [APP_NAME] déployé avec succès !

📍 URL : http://69.62.108.82:[PORT]
📦 Type : [Docker/Systemd]
📊 Status : En ligne

🔧 Commandes utiles :
- Logs : [COMMANDE]
- Redémarrer : [COMMANDE]
- Arrêter : [COMMANDE]
```

### Rapport d'erreur

```
❌ Échec du déploiement de [APP_NAME]

Erreur : [ERREUR_PRINCIPALE]

Logs :
[EXTRAIT_LOGS]

Actions suggérées :
1. [ACTION_1]
2. [ACTION_2]
```

---

## 🎓 Exemples de décision

### Exemple 1 : L'utilisateur demande "Déploie une API FastAPI"

```
1. Identifier : Application web → Docker
2. Lire : GUIDE_DEPLOIEMENT_VPS.md
3. Chercher : Section "Template Flask/FastAPI"
4. Appliquer : Suivre les 6 étapes du workflow
5. Vérifier : curl http://69.62.108.82:[PORT]
6. Informer : Rapport de succès
```

### Exemple 2 : L'utilisateur demande "Installe PostgreSQL"

```
1. Identifier : Base de données → Systemd (ou Docker selon préférence)
2. Demander : "Préférez-vous Docker ou installation native ?"
3. Selon réponse :
   - Docker → GUIDE_DEPLOIEMENT_VPS.md
   - Native → GUIDE_SERVICES_SYSTEMD.md (suivre template Ollama)
```

### Exemple 3 : L'utilisateur demande "Ajoute un dashboard Streamlit"

```
1. Identifier : Streamlit → Docker
2. Lire : GUIDE_DEPLOIEMENT_VPS.md
3. Chercher : Section "Template Streamlit"
4. Port : Vérifier ports disponibles (8502+)
5. Appliquer : Workflow complet
6. Nginx : Optionnel (demander à l'utilisateur)
```

---

## 🛠️ Cas particuliers

### Cas 1 : Le port suggéré est déjà utilisé

```bash
# Vérifier les ports utilisés
ssh root@69.62.108.82 "docker ps --format '{{.Names}}: {{.Ports}}'"
ssh root@69.62.108.82 "netstat -tlnp | grep -E '850[0-9]'"

# Proposer le prochain port libre
```

### Cas 2 : L'utilisateur veut un sous-domaine

```
1. Déployer l'app normalement (IP:PORT)
2. Demander le nom de sous-domaine souhaité
3. Créer config Nginx (voir GUIDE_DEPLOIEMENT_VPS.md section "Ajouter un nouveau site")
4. Informer que le DNS doit pointer vers 69.62.108.82
```

### Cas 3 : Mise à jour d'une application existante

```
1. Identifier l'app : ssh root@69.62.108.82 "ls /opt/"
2. Type : Docker ou systemd ?
   - Docker : cd /opt/[app] && docker-compose down && ...
   - Systemd : systemctl restart [service]
3. Lire le guide approprié section "Mise à jour"
```

### Cas 4 : Migration WordPress vers Docker

```
1. Lire : GUIDE_WORDPRESS_DOCKER.md
2. Suivre EXACTEMENT le workflow (9 étapes critiques)
3. Points d'attention :
   - ⚠️ Backup COMPLET (db + wp-content + wp-config.php)
   - ⚠️ user: "33:33" dans docker-compose.yml
   - ⚠️ DB_HOST = mysql-clemence:3306 (pas localhost!)
   - ⚠️ Fix reverse proxy HTTPS dans wp-config.php
   - ⚠️ URLs (siteurl et home) en HTTPS identiques
4. Vérifier : HTTP 200, plugins/themes OK, admin accessible
```

---

## 🔐 Sécurité - Checklist

Avant tout transfert de fichiers :

- [ ] Vérifier `.gitignore` contient `.env`, `*.key`, `*.pem`
- [ ] Pas de secrets hardcodés dans le code
- [ ] Variables sensibles dans fichier `.env` (non transféré)
- [ ] Permissions correctes (pas de 777)

---

## 📊 Monitoring automatique

Après chaque déploiement, suggérer à l'utilisateur :

```bash
# Voir les ressources
ssh root@69.62.108.82 "docker stats --no-stream"  # Si Docker
ssh root@69.62.108.82 "systemctl status [service]"  # Si systemd

# Voir les logs
ssh root@69.62.108.82 "docker logs [container] --tail=20"  # Docker
ssh root@69.62.108.82 "journalctl -u [service] -n 20"  # Systemd
```

---

## 🎯 Résumé des actions LLM

| Situation | Action LLM |
|-----------|------------|
| Demande de déploiement | Identifier type → Lire guide → Créer checklist → Exécuter → Vérifier → Informer |
| Erreur rencontrée | Lire logs → Diagnostiquer → Proposer solutions OU demander aide |
| Mise à jour | Identifier app → Lire guide section "Mise à jour" → Exécuter → Vérifier |
| Question utilisateur | Référencer section appropriée du guide (ne pas dupliquer) |
| Paramètre manquant | Demander à l'utilisateur (ne JAMAIS deviner) |

---

## 📞 Informations serveur (référence rapide)

**SSH** : `ssh root@69.62.108.82`
**IP** : `69.62.108.82`
**Hostname** : `srv759970.hstgr.cloud`
**OS** : Ubuntu 24.04.2 LTS

**Chemins importants** :
- Applications : `/opt/`
- Nginx configs : `/etc/nginx/sites-available/`
- Systemd services : `/etc/systemd/system/`

**Vérifications rapides** :
```bash
# Apps Docker
ssh root@69.62.108.82 "docker ps"

# Services systemd
ssh root@69.62.108.82 "systemctl list-units --type=service --state=running | grep -v '@'"

# Ports utilisés
ssh root@69.62.108.82 "netstat -tlnp"
```

---

**Dernière mise à jour** : Octobre 2025
**Principe** : DRY - Ne dupliquez pas, référencez !
