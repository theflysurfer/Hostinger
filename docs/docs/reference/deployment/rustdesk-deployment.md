# Guide RustDesk - Bureau à distance auto-hébergé

**Dernière mise à jour** : 20 octobre 2025
**Serveur** : srv759970.hstgr.cloud (69.62.108.82)
**Status** : ✅ Installé et fonctionnel

---

## 🎯 Qu'est-ce que RustDesk ?

RustDesk est une alternative open-source à TeamViewer/AnyDesk permettant :
- ✅ Bureau à distance sécurisé
- ✅ Auto-hébergement complet (aucune dépendance cloud)
- ✅ Multiplateforme (Windows, Mac, Linux, Android, iOS)
- ✅ Gratuit et sans limitation
- ✅ Chiffrement de bout en bout

---

## 📦 Installation serveur

### Architecture déployée

```
/opt/rustdesk/
├── docker-compose.yml          # Configuration Docker
└── data/                       # Données persistantes
    ├── id_ed25519              # Clé privée serveur
    └── id_ed25519.pub          # Clé publique serveur
```

### Composants installés

| Service | Conteneur | Port | Rôle | RAM |
|---------|-----------|------|------|-----|
| **HBBS** | hbbs | 21115-21116 (TCP/UDP) | Signal server (enregistrement ID, NAT) | ~2 MB |
| **HBBR** | hbbr | 21117, 21119 (TCP) | Relay server (connexions peer-to-peer) | ~1 MB |
| **Web** | nginx | 80 (HTTP) | Page d'information | - |

**Total RAM** : ~3 MB (ultra léger, laissé actif 24/7)

### Ports ouverts dans le firewall

```bash
# TCP
21115 - NAT type test
21116 - ID registration & heartbeat
21117 - Relay server
21118 - WebSocket support
21119 - WebSocket support

# UDP
21116 - ID registration & heartbeat
```

---

## 🔑 Configuration client

### Informations de connexion

**Serveur ID** : `rustdesk.srv759970.hstgr.cloud`
**Port ID** : `21116` (ou laisser vide pour port par défaut)
**Serveur Relay** : `rustdesk.srv759970.hstgr.cloud`
**Port Relay** : `21117` (ou laisser vide pour port par défaut)
**Clé publique** : `Rrvoi88SE7SuwOBgzUD9vqWqPl6gpDWDXNjifrTee+c=`

### Étapes de configuration client

#### 1. Télécharger RustDesk

**Windows/Mac/Linux** : https://rustdesk.com/fr/
**Android** : Google Play Store
**iOS** : Apple App Store

#### 2. Configurer le client

1. Lancer RustDesk
2. Cliquer sur les **3 points** (menu) à côté de "Prêt"
3. Sélectionner **"Serveur ID/Relay"**
4. Remplir les champs :

```
Serveur ID : rustdesk.srv759970.hstgr.cloud
Port ID : (laisser vide ou 21116)
Serveur Relay : rustdesk.srv759970.hstgr.cloud
Port Relay : (laisser vide ou 21117)
Clé : Rrvoi88SE7SuwOBgzUD9vqWqPl6gpDWDXNjifrTee+c=
```

5. Cliquer sur **"Appliquer"**
6. Redémarrer RustDesk

#### 3. Vérifier la connexion

Le client doit afficher :
- ✅ **"Prêt"** avec un **ID unique** (ex: 123456789)
- ✅ Point vert à côté de l'ID (connecté au serveur)

---

## 🚀 Utilisation

### Contrôler un ordinateur à distance

1. **Sur l'ordinateur distant** :
   - Noter l'ID RustDesk affiché (ex: 987654321)
   - Noter le mot de passe temporaire (ou configurer un mot de passe fixe)

2. **Sur votre ordinateur** :
   - Entrer l'ID distant dans le champ "Remote ID"
   - Cliquer sur "Connect"
   - Entrer le mot de passe
   - Le bureau distant s'affiche

### Permettre à quelqu'un de se connecter à votre PC

1. Partager votre **ID RustDesk** (9 chiffres)
2. Partager le **mot de passe temporaire** affiché sous l'ID
3. L'autre personne entre votre ID et se connecte

---

## 🔧 Gestion du serveur

### Commandes Docker

```bash
# Voir les conteneurs
ssh automation@69.62.108.82 "sudo docker ps | grep rustdesk"

# Voir les logs HBBS (signal server)
ssh automation@69.62.108.82 "sudo docker logs hbbs -f"

# Voir les logs HBBR (relay server)
ssh automation@69.62.108.82 "sudo docker logs hbbr -f"

# Redémarrer les services
ssh automation@69.62.108.82 "cd /opt/rustdesk && sudo docker-compose restart"

# Arrêter les services
ssh automation@69.62.108.82 "cd /opt/rustdesk && sudo docker-compose stop"

# Démarrer les services
ssh automation@69.62.108.82 "cd /opt/rustdesk && sudo docker-compose start"

# Rebuild complet
ssh automation@69.62.108.82 "cd /opt/rustdesk && sudo docker-compose down && sudo docker-compose up -d"
```

### Récupérer la clé publique

```bash
# Afficher la clé publique serveur
ssh automation@69.62.108.82 "sudo cat /opt/rustdesk/data/id_ed25519.pub"
```

**Résultat** : `Rrvoi88SE7SuwOBgzUD9vqWqPl6gpDWDXNjifrTee+c=`

### Vérifier le statut

```bash
# Tester les ports
ssh automation@69.62.108.82 "sudo netstat -tulpn | grep -E '(21115|21116|21117|21118|21119)'"

# Vérifier le firewall
ssh automation@69.62.108.82 "sudo ufw status | grep 211"
```

---

## 🛡️ Sécurité

### Recommandations

1. **Mot de passe fort** : Configurer un mot de passe permanent dans RustDesk (ne pas utiliser le mot de passe temporaire)
2. **Clé publique** : Ne jamais partager la clé privée (`id_ed25519`), seulement la clé publique
3. **Firewall** : Les ports sont ouverts uniquement pour RustDesk (21115-21119)
4. **Chiffrement** : Toutes les connexions sont chiffrées de bout en bout
5. **Logs** : Les connexions sont loggées dans Docker logs

### Audit des connexions

```bash
# Voir les connexions récentes
ssh automation@69.62.108.82 "sudo docker logs hbbs --tail 100 | grep -i 'peer'"

# Voir les erreurs
ssh automation@69.62.108.82 "sudo docker logs hbbs --tail 100 | grep -i 'error'"
```

---

## 🔄 Mise à jour

### Mettre à jour les images Docker

```bash
# 1. Pull les nouvelles images
ssh automation@69.62.108.82 "cd /opt/rustdesk && sudo docker-compose pull"

# 2. Recréer les conteneurs
ssh automation@69.62.108.82 "cd /opt/rustdesk && sudo docker-compose up -d"

# 3. Nettoyer les anciennes images
ssh automation@69.62.108.82 "sudo docker image prune -f"
```

### Pourquoi RustDesk n'utilise PAS l'auto-stop ?

**Décision technique** : RustDesk reste actif 24/7 (pas d'auto-stop comme les autres services)

**Raisons** :
1. **Ultra léger** : ~3 MB de RAM total (négligeable)
2. **Disponibilité critique** : Bureau à distance = besoin urgent, pas de temps d'attente
3. **Incompatibilité technique** : Utilise des ports TCP/UDP directs (pas de proxy HTTP possible)
4. **Nature du protocole** : Les clients se connectent directement aux ports 21116/21117

**Comparaison** :
- WordPress : 200-300 MB → Auto-stop activé
- Strapi : 400 MB → Auto-stop activé
- RustDesk : 3 MB → **Toujours actif** (restart: unless-stopped)

---

## 🆘 Troubleshooting

### Le client affiche "Non connecté"

**Cause** : Le client ne peut pas joindre le serveur HBBS

**Solutions** :
```bash
# 1. Vérifier que les conteneurs tournent
ssh automation@69.62.108.82 "sudo docker ps | grep rustdesk"

# 2. Vérifier les logs
ssh automation@69.62.108.82 "sudo docker logs hbbs --tail 50"

# 3. Tester la connectivité depuis le client
ping rustdesk.srv759970.hstgr.cloud
telnet rustdesk.srv759970.hstgr.cloud 21116
```

### Impossible de se connecter à un peer

**Cause** : Le serveur relay (HBBR) ne fonctionne pas ou les ports sont bloqués

**Solutions** :
```bash
# 1. Vérifier HBBR
ssh automation@69.62.108.82 "sudo docker logs hbbr --tail 50"

# 2. Vérifier les ports relay
ssh automation@69.62.108.82 "sudo netstat -tulpn | grep 21117"

# 3. Tester depuis le client
telnet rustdesk.srv759970.hstgr.cloud 21117
```

### Erreur "Invalid key"

**Cause** : La clé publique configurée dans le client ne correspond pas à celle du serveur

**Solution** :
```bash
# Récupérer la bonne clé publique
ssh automation@69.62.108.82 "sudo cat /opt/rustdesk/data/id_ed25519.pub"

# La copier dans le client RustDesk (paramètres Serveur ID/Relay)
```

### Conteneurs ne démarrent pas

```bash
# Voir les erreurs
ssh automation@69.62.108.82 "cd /opt/rustdesk && sudo docker-compose logs"

# Rebuild from scratch
ssh automation@69.62.108.82 "cd /opt/rustdesk && sudo docker-compose down -v && sudo docker-compose up -d"
```

---

## 📊 Monitoring

### Métriques importantes

```bash
# Nombre de clients connectés
ssh automation@69.62.108.82 "sudo docker logs hbbs --tail 1000 | grep -c 'peer online'"

# Utilisation mémoire
ssh automation@69.62.108.82 "sudo docker stats --no-stream | grep rustdesk"

# Utilisation disque
ssh automation@69.62.108.82 "sudo du -sh /opt/rustdesk/data"
```

---

## 🌐 Accès web

**URL** : https://rustdesk.srv759970.hstgr.cloud
**SSL** : Certificat Let's Encrypt (expire le 18 janvier 2026)
**Protection** : Basic Auth (credentials Nginx)

La page affiche :
- Statut du serveur
- Ports de connexion
- Clé publique
- Instructions de configuration

### Renouvellement automatique SSL

Le certificat SSL est automatiquement renouvelé par Certbot tous les 90 jours.

**Vérifier le renouvellement** :
```bash
ssh automation@69.62.108.82 "sudo certbot certificates | grep -A 6 rustdesk"
```

**Forcer un renouvellement** (si besoin) :
```bash
ssh automation@69.62.108.82 "sudo certbot renew --cert-name rustdesk.srv759970.hstgr.cloud"
```

---

## 📝 Configuration avancée

### Changer le port de connexion

Éditer `/opt/rustdesk/docker-compose.yml` :

```yaml
services:
  hbbs:
    ports:
      - "21115:21115"      # Changer 21115 par le port souhaité
      - "21116:21116"      # Changer 21116 par le port souhaité
      - "21116:21116/udp"  # Changer 21116 par le port souhaité
```

Puis redémarrer :
```bash
ssh automation@69.62.108.82 "cd /opt/rustdesk && sudo docker-compose down && sudo docker-compose up -d"
```

### Activer les logs détaillés

```yaml
services:
  hbbs:
    command: hbbs -r rustdesk.srv759970.hstgr.cloud:21117 -v
  hbbr:
    command: hbbr -v
```

### Configuration du relay personnalisé

Le relay est configuré dans le command HBBS :
```yaml
command: hbbs -r rustdesk.srv759970.hstgr.cloud:21117
```

Cela indique aux clients où trouver le serveur relay.

---

## 🔗 Liens utiles

- **Site officiel** : https://rustdesk.com/fr/
- **Documentation** : https://rustdesk.com/docs/
- **GitHub** : https://github.com/rustdesk/rustdesk-server
- **Docker Hub** : https://hub.docker.com/r/rustdesk/rustdesk-server

---

## 📞 Support

### Logs du serveur

```bash
# Logs HBBS (signal)
ssh automation@69.62.108.82 "sudo docker logs hbbs -f"

# Logs HBBR (relay)
ssh automation@69.62.108.82 "sudo docker logs hbbr -f"

# Logs Nginx (page web)
ssh automation@69.62.108.82 "sudo tail -f /var/log/nginx/access.log | grep rustdesk"
```

### Contacts

**Serveur** : srv759970.hstgr.cloud (69.62.108.82)
**Accès SSH** : `ssh automation@69.62.108.82`
**Panel Hostinger** : https://hpanel.hostinger.com/

---

## 📋 Checklist déploiement

- [x] Serveur RustDesk installé (hbbs + hbbr)
- [x] Ports firewall ouverts (21115-21119)
- [x] Conteneurs Docker démarrés
- [x] Clé publique générée
- [x] Configuration Nginx créée
- [x] Page web d'information accessible
- [ ] Client Windows configuré et testé
- [ ] Client Mac configuré et testé
- [ ] Client Linux configuré et testé
- [ ] Connexion peer-to-peer testée
- [ ] Logs vérifiés (pas d'erreur)

---

## 🎓 Exemples d'utilisation

### Cas 1 : Support technique à distance

1. L'utilisateur lance RustDesk et communique son ID (ex: 123456789)
2. Le technicien entre cet ID dans son RustDesk
3. L'utilisateur partage le mot de passe temporaire
4. Le technicien prend le contrôle du PC

### Cas 2 : Accès à son PC de bureau depuis chez soi

1. Configurer RustDesk sur le PC de bureau avec un mot de passe permanent
2. Noter l'ID RustDesk
3. Installer RustDesk sur le PC personnel avec la même config serveur
4. Se connecter à tout moment avec l'ID et le mot de passe

### Cas 3 : Accès mobile au PC

1. Installer RustDesk sur smartphone (Android/iOS)
2. Configurer le serveur avec les mêmes paramètres
3. Entrer l'ID du PC
4. Contrôler le PC depuis le téléphone

---

**Version** : 1.0
**Auteur** : Claude Code + Julien
**Status** : Production
**Prochaine revue** : Après tests utilisateurs
