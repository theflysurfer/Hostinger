# Rocket.Chat

**URL**: https://chat.srv759970.hstgr.cloud
**Port interne**: 3002
**Statut**: ✅ Opérationnel

---

## Vue d'ensemble

Rocket.Chat est une plateforme de messagerie instantanée et collaboration d'équipe open-source, alternative à Slack et Microsoft Teams.

### Fonctionnalités principales

- **Chat en temps réel** : Channels publics/privés, messages directs
- **Visioconférence** : Intégration Jitsi Meet
- **Partage fichiers** : Upload images, documents, vidéos
- **Threads** : Conversations organisées par fils de discussion
- **Notifications** : Desktop, mobile, email
- **Apps & Intégrations** : Webhooks, bots, intégrations tierces

---

## Architecture

```
Rocket.Chat (port 3002)
    ↓
MongoDB Replica Set (rs0)
    ↓
MongoDB Oplog (pour real-time sync)
```

### Conteneur

- **rocketchat** : Application Rocket.Chat complète

---

## Configuration

### Emplacement

- **Répertoire**: `/opt/rocketchat/`
- **Uploads**: `/opt/rocketchat/uploads/`
- **Data**: `/opt/rocketchat/data/`
- **Environment**: `/opt/rocketchat/.env`

### Base de données

- **Type**: MongoDB (Replica Set rs0)
- **Host**: `mongodb-shared`
- **Database**: `rocketchat`
- **User**: `rocketchat`
- **Oplog**: Activé (requis pour real-time)

---

## Utilisation

### Accès Web

URL: https://chat.srv759970.hstgr.cloud

**Premier démarrage** :
- Créer compte administrateur lors de la première connexion
- Configurer nom de l'organisation
- Paramétrer les channels par défaut

### Clients

**Desktop** :
- [Rocket.Chat Desktop](https://github.com/RocketChat/Rocket.Chat.Electron/releases) (Windows, macOS, Linux)

**Mobile** :
- [Android](https://play.google.com/store/apps/details?id=chat.rocket.android)
- [iOS](https://apps.apple.com/app/rocket-chat/id1148741252)

---

## Intégration Jitsi Meet

Rocket.Chat est préconfiguré pour utiliser Jitsi Meet pour la visioconférence.

### Configuration

- **Jitsi Domain**: `meet.srv759970.hstgr.cloud`
- **Enable SSL**: Oui
- **URL Prefix**: `https://`

### Utilisation

Dans un channel ou message direct :
1. Cliquer sur l'icône caméra
2. Ou taper `/jitsi NomDeLaReunion`
3. Jitsi s'ouvre dans un nouvel onglet

---

## Administration

### Panneau Admin

**Accès**: Menu → Administration (icône engrenage)

**Sections importantes** :
- **Users**: Gestion utilisateurs
- **Rooms**: Channels et groupes
- **Settings**: Configuration globale
- **Integrations**: Webhooks et bots

### Commandes utiles

```bash
# Logs en temps réel
docker logs rocketchat --tail 100 -f

# Redémarrer
docker restart rocketchat

# Shell MongoDB (debug)
docker exec -it mongodb-shared mongosh rocketchat -u rocketchat -p PASSWORD

# Stats
docker stats rocketchat
```

---

## Channels

### Types de channels

- **Public Channel** : Visible par tous, n'importe qui peut rejoindre
- **Private Group** : Invitation uniquement
- **Direct Message** : Message privé 1-1

### Créer un channel

1. Cliquer sur `+` à côté de "Channels"
2. Choisir Public/Private
3. Nommer le channel (ex: `#general`, `#dev`)
4. Inviter membres

---

## Webhooks & Intégrations

### Incoming Webhooks

**Usage**: Recevoir notifications externes (GitHub, GitLab, monitoring, etc.)

**Création**:
1. Admin → Integrations → New Integration → Incoming Webhook
2. Choisir channel de destination
3. Copier Webhook URL
4. Utiliser dans service externe

**Exemple curl**:
```bash
curl -X POST https://chat.srv759970.hstgr.cloud/hooks/WEBHOOK_ID \
  -H 'Content-Type: application/json' \
  -d '{"text": "Hello from external service!"}'
```

### Outgoing Webhooks

**Usage**: Déclencher actions externes depuis Rocket.Chat

---

## Notifications

### Desktop

- Notifications natives browser/app desktop
- Configuration par channel (All messages, Mentions, Nothing)

### Mobile

- Push notifications via app mobile
- Configuration par utilisateur

### Email

- Notifications email configurables
- SMTP requis (voir configuration serveur)

---

## Sécurité

### HTTPS

- ✅ Certificat Let's Encrypt
- ✅ Renouvellement automatique
- ✅ WebSocket over HTTPS

### Authentification

- Authentification locale Rocket.Chat
- Support 2FA (TOTP)
- OAuth2 disponible (Google, GitHub, etc.)

### Permissions

- Rôles: Admin, Moderator, User, Guest
- Permissions granulaires par channel

---

## Backup

### Données à sauvegarder

1. **MongoDB database**: `rocketchat`
2. **Uploads**: `/opt/rocketchat/uploads/`
3. **Config**: `/opt/rocketchat/.env`

### Script backup

```bash
# Backup MongoDB
docker exec mongodb-shared mongodump --db=rocketchat --username=rocketchat --password=PASSWORD --out=/backup

# Backup uploads
tar czf rocketchat-uploads-$(date +%Y%m%d).tar.gz /opt/rocketchat/uploads/
```

---

## Troubleshooting

### Problème de connexion

**Symptôme**: "Cannot connect to server"

**Solution**:
```bash
# Vérifier logs
docker logs rocketchat --tail 50

# Vérifier MongoDB
docker exec mongodb-shared mongosh --eval "rs.status()"
```

### Problème Jitsi

**Symptôme**: Vidéo ne démarre pas

**Solution**:
1. Vérifier config dans Admin → Video Conference → Jitsi
2. Tester Jitsi directement: https://meet.srv759970.hstgr.cloud
3. Vérifier logs Jitsi

### Messages ne s'affichent pas

**Symptôme**: Messages en retard ou ne s'affichent pas

**Solution**: Vérifier MongoDB oplog
```bash
docker exec mongodb-shared mongosh --eval "rs.status()" | grep -A 5 oplog
```

---

## Limites et quotas

### Uploads

- **Taille max fichier**: Configurable dans Admin → File Upload
- **Stockage**: Limité par espace disque serveur

### Users

- **Nombre max**: Aucune limite technique (version Community)
- **Concurrent users**: Limité par ressources serveur

---

## Liens utiles

- **Documentation officielle**: https://docs.rocket.chat
- **API documentation**: https://developer.rocket.chat/reference/api
- **Marketplace apps**: https://rocket.chat/marketplace
- **Community**: https://open.rocket.chat

---

**Dernière mise à jour**: 2025-10-21
**Version Rocket.Chat**: Latest (Docker image officiel)
