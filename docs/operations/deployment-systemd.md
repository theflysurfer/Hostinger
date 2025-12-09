# 🔧 Guide des services systemd sur VPS Hostinger

Guide pour déployer et gérer des services natifs (non-Docker) sur le VPS.

---

## 📋 Quand utiliser systemd vs Docker ?

### Utiliser systemd quand :
- ✅ Service léger nécessitant accès direct au système
- ✅ Performance maximale requise (pas de virtualisation)
- ✅ Service système existant (Ollama, bases de données, etc.)
- ✅ Gestion simplifiée sans conteneurisation

### Utiliser Docker quand :
- ✅ Isolation complète nécessaire
- ✅ Portabilité entre environnements
- ✅ Application web classique
- ➡️ Voir `GUIDE_DEPLOIEMENT_VPS.md`

---

## 🎯 Services systemd actuellement déployés

| Service | Port(s) | Description | Status |
|---------|---------|-------------|--------|
| `ollama.service` | 11434 (local) | LLM inference API | ✅ En ligne |
| `nginx.service` | 80, 11435 | Reverse proxy | ✅ En ligne |

---

## 📦 Exemple : Ollama API

### Architecture

```
Client → Nginx (0.0.0.0:11435) → Ollama (127.0.0.1:11434)
```

### 1. Installation du service

```bash
# Ollama est déjà installé, mais voici la procédure générique
ssh root@69.62.108.82 "curl -fsSL https://ollama.com/install.sh | sh"
```

### 2. Configuration du service

Le service est géré par systemd : `/etc/systemd/system/ollama.service`

```bash
# Voir la configuration
ssh root@69.62.108.82 "systemctl cat ollama"
```

### 3. Gestion du service

```bash
# Démarrer
ssh root@69.62.108.82 "systemctl start ollama"

# Arrêter
ssh root@69.62.108.82 "systemctl stop ollama"

# Redémarrer
ssh root@69.62.108.82 "systemctl restart ollama"

# Statut
ssh root@69.62.108.82 "systemctl status ollama"

# Activer au démarrage
ssh root@69.62.108.82 "systemctl enable ollama"

# Logs en temps réel
ssh root@69.62.108.82 "journalctl -u ollama -f"
```

### 4. Configuration Nginx (reverse proxy)

**Fichier** : `/etc/nginx/sites-available/ollama-api`

```nginx
server {
    listen 0.0.0.0:11435;
    server_name _;

    access_log /var/log/nginx/ollama-access.log;
    error_log /var/log/nginx/ollama-error.log;

    location / {
        proxy_pass http://127.0.0.1:11434;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;

        proxy_buffering off;
        proxy_cache off;

        # CORS headers
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;
    }
}
```

**Activation** :

```bash
ssh root@69.62.108.82 "ln -s /etc/nginx/sites-available/ollama-api /etc/nginx/sites-enabled/ollama-api"
ssh root@69.62.108.82 "nginx -t && systemctl reload nginx"
```

### 5. Vérification

```bash
# Test local (sur le serveur)
ssh root@69.62.108.82 "curl http://localhost:11434/api/version"

# Test public (depuis l'extérieur)
curl http://69.62.108.82:11435/api/version

# Vérifier les ports écoutés
ssh root@69.62.108.82 "netstat -tlnp | grep -E '11434|11435'"
```

### 6. Gestion des modèles

```bash
# Lister les modèles installés
ssh root@69.62.108.82 "ollama list"

# Télécharger un nouveau modèle
ssh root@69.62.108.82 "ollama pull llama3.2:3b"

# Supprimer un modèle
ssh root@69.62.108.82 "ollama rm llama3.2:1b"

# Voir l'espace utilisé
ssh root@69.62.108.82 "du -sh /usr/share/ollama/.ollama/models"
```

---

## 🔧 Template générique : Déployer un service systemd

### Étape 1 : Créer le fichier de service

```bash
ssh root@69.62.108.82 "cat > /etc/systemd/system/mon-service.service" << 'EOF'
[Unit]
Description=Mon service personnalisé
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/mon-service
ExecStart=/usr/local/bin/mon-executable
Restart=on-failure
RestartSec=5s

Environment="PORT=8080"
Environment="LOG_LEVEL=info"

[Install]
WantedBy=multi-user.target
EOF
```

### Étape 2 : Activer et démarrer

```bash
# Recharger systemd (après modification de fichier .service)
ssh root@69.62.108.82 "systemctl daemon-reload"

# Activer au démarrage
ssh root@69.62.108.82 "systemctl enable mon-service"

# Démarrer
ssh root@69.62.108.82 "systemctl start mon-service"

# Vérifier
ssh root@69.62.108.82 "systemctl status mon-service"
```

### Étape 3 : Exposer via Nginx (si nécessaire)

```bash
ssh root@69.62.108.82 'cat > /etc/nginx/sites-available/mon-service << "HEREDOC"
server {
    listen 80;
    server_name mon-service.srv759970.hstgr.cloud;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
HEREDOC'

# Activer
ssh root@69.62.108.82 "ln -s /etc/nginx/sites-available/mon-service /etc/nginx/sites-enabled/"
ssh root@69.62.108.82 "nginx -t && systemctl reload nginx"
```

---

## 📊 Monitoring et logs

### Logs systemd

```bash
# Logs d'un service (temps réel)
ssh root@69.62.108.82 "journalctl -u ollama -f"

# Logs depuis un certain temps
ssh root@69.62.108.82 "journalctl -u ollama --since '1 hour ago'"

# Logs avec niveau de détail
ssh root@69.62.108.82 "journalctl -u ollama -p err"  # Seulement les erreurs
```

### Logs Nginx (pour services proxifiés)

```bash
# Logs d'accès spécifiques
ssh root@69.62.108.82 "tail -f /var/log/nginx/ollama-access.log"

# Logs d'erreur spécifiques
ssh root@69.62.108.82 "tail -f /var/log/nginx/ollama-error.log"
```

### Ressources système

```bash
# Utilisation CPU/RAM d'un service
ssh root@69.62.108.82 "systemctl status ollama | grep -E 'Memory|CPU'"

# Processus en cours
ssh root@69.62.108.82 "ps aux | grep ollama"
```

---

## 🔄 Mise à jour d'un service

### Exemple : Mettre à jour Ollama

```bash
# 1. Arrêter le service
ssh root@69.62.108.82 "systemctl stop ollama"

# 2. Mettre à jour (méthode dépend du service)
ssh root@69.62.108.82 "curl -fsSL https://ollama.com/install.sh | sh"

# 3. Redémarrer
ssh root@69.62.108.82 "systemctl start ollama"

# 4. Vérifier
ssh root@69.62.108.82 "systemctl status ollama"
ssh root@69.62.108.82 "ollama --version"
```

---

## 🛡️ Sécurité

### Bonnes pratiques

#### 1. Ne pas exposer directement les services

❌ **Mauvais** : Service écoute sur 0.0.0.0
```bash
# Service accessible directement depuis Internet
ExecStart=/usr/bin/mon-app --host 0.0.0.0 --port 8080
```

✅ **Bon** : Service écoute sur localhost, Nginx fait le proxy
```bash
# Service local uniquement
ExecStart=/usr/bin/mon-app --host 127.0.0.1 --port 8080

# Nginx expose publiquement avec contrôles
```

#### 2. Limiter les permissions

```bash
# Ne pas lancer en root si pas nécessaire
[Service]
User=www-data
Group=www-data
```

#### 3. Restreindre l'accès réseau (optionnel)

```nginx
# Dans Nginx : limiter par IP
location / {
    allow 192.168.1.0/24;  # Votre réseau
    deny all;

    proxy_pass http://localhost:8080;
}
```

---

## 🔍 Troubleshooting

### Le service ne démarre pas

```bash
# 1. Voir les logs détaillés
ssh root@69.62.108.82 "journalctl -u mon-service -n 50"

# 2. Vérifier la syntaxe du fichier .service
ssh root@69.62.108.82 "systemd-analyze verify /etc/systemd/system/mon-service.service"

# 3. Vérifier que l'exécutable existe
ssh root@69.62.108.82 "ls -la /usr/local/bin/mon-executable"

# 4. Tester manuellement
ssh root@69.62.108.82 "/usr/local/bin/mon-executable"
```

### Le service redémarre en boucle

```bash
# Voir pourquoi il crash
ssh root@69.62.108.82 "journalctl -u mon-service | tail -100"

# Désactiver le restart automatique temporairement
ssh root@69.62.108.82 "systemctl edit --full mon-service"
# Puis commenter la ligne : Restart=on-failure
```

### Port déjà utilisé

```bash
# Trouver qui utilise le port
ssh root@69.62.108.82 "lsof -i :8080"
ssh root@69.62.108.82 "netstat -tlnp | grep 8080"
```

### Nginx ne forward pas correctement

```bash
# Test de la config
ssh root@69.62.108.82 "nginx -t"

# Vérifier que le service backend répond
ssh root@69.62.108.82 "curl http://localhost:8080"

# Voir les erreurs Nginx
ssh root@69.62.108.82 "tail -50 /var/log/nginx/error.log"
```

---

## 📋 Checklist de déploiement

Avant de déployer un nouveau service systemd :

- [ ] Exécutable testé manuellement
- [ ] Fichier `.service` créé dans `/etc/systemd/system/`
- [ ] `systemctl daemon-reload` exécuté
- [ ] Service activé avec `systemctl enable`
- [ ] Service démarré avec `systemctl start`
- [ ] Logs vérifiés (pas d'erreur)
- [ ] Service accessible en local (curl localhost:PORT)
- [ ] (Optionnel) Configuration Nginx créée
- [ ] (Optionnel) Nginx rechargé
- [ ] (Optionnel) Service accessible publiquement

---

## 🎓 Comparaison systemd vs Docker

| Aspect | systemd | Docker |
|--------|---------|--------|
| **Isolation** | Faible | Forte |
| **Performance** | Native | Légère overhead |
| **Portabilité** | Dépend de l'OS | Indépendant de l'OS |
| **Complexité** | Simple | Moyenne |
| **Gestion** | systemctl | docker-compose |
| **Logs** | journalctl | docker logs |
| **Mise à jour** | Manuelle | Rebuild image |
| **Cas d'usage** | Services système | Applications web |

---

## 📞 Informations

**Serveur** : srv759970.hstgr.cloud (69.62.108.82)
**OS** : Ubuntu 24.04.2 LTS
**Services actifs** : ollama, nginx

**Commandes rapides** :
```bash
# Lister tous les services
ssh root@69.62.108.82 "systemctl list-units --type=service --state=running"

# Voir les services qui ont failed
ssh root@69.62.108.82 "systemctl --failed"
```

---

**Dernière mise à jour** : Octobre 2025
**Services déployés** : 1 (Ollama)
