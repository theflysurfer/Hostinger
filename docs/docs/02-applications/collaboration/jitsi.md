# Jitsi Meet

**URL**: https://meet.srv759970.hstgr.cloud
**Ports**: 8510 (HTTP), 8511 (HTTPS), 10000/UDP (Media)
**Statut**: ✅ Opérationnel

---

## Vue d'ensemble

Jitsi Meet est une solution de visioconférence open-source sécurisée, sans inscription requise. Compatible avec tous les navigateurs modernes.

### Fonctionnalités principales

- **Visioconférence** : Audio/vidéo HD jusqu'à 75 participants
- **Partage d'écran** : Partage fenêtre ou écran complet
- **Chat textuel** : Chat en parallèle de la vidéo
- **Enregistrement** : Enregistrement local (navigateur)
- **Streaming** : Live streaming YouTube possible
- **Sans inscription** : Créer/rejoindre une réunion instantanément

---

## Architecture

Jitsi Meet est composé de 4 conteneurs Docker :

```
jitsi-web (Frontend)
    ↓
jitsi-prosody (XMPP server)
    ↓
jitsi-jicofo (Conference focus)
    ↓
jitsi-jvb (Video bridge - WebRTC)
```

### Conteneurs

- **jitsi-web** : Interface web (port 8510)
- **jitsi-prosody** : Serveur XMPP pour signaling
- **jitsi-jicofo** : Coordonnateur de conférences
- **jitsi-jvb** : Bridge vidéo WebRTC (port 10000/UDP)

---

## Configuration

### Emplacement

- **Répertoire**: `/opt/jitsi/`
- **Config**: `/opt/jitsi/.env`
- **Data prosody**: `/opt/jitsi/prosody/config/`
- **Data jicofo**: `/opt/jitsi/jicofo/`
- **Data jvb**: `/opt/jitsi/jvb/`

### Paramètres clés

- **PUBLIC_URL**: `https://meet.srv759970.hstgr.cloud`
- **ENABLE_AUTH**: `0` (authentification désactivée)
- **ENABLE_GUESTS**: `1` (accès guest activé)
- **TZ**: `Europe/Paris`

### Ports réseau

- **8510** : HTTP (interne, proxy Nginx)
- **8511** : HTTPS (interne, proxy Nginx)
- **10000/UDP** : WebRTC media (exposé publiquement)

**⚠️ Important**: Le port 10000/UDP DOIT être ouvert dans le firewall pour le média WebRTC.

---

## Utilisation

### Créer une réunion

1. Aller sur https://meet.srv759970.hstgr.cloud
2. Entrer un nom de réunion (ex: `reunion-equipe-2025`)
3. Cliquer "Go" ou appuyer sur Entrée
4. Autoriser micro/caméra dans le navigateur
5. Partager le lien avec les participants

### Rejoindre une réunion

- **URL directe**: `https://meet.srv759970.hstgr.cloud/NomDeLaReunion`
- **Depuis Rocket.Chat**: Commande `/jitsi NomDeLaReunion`

### Fonctionnalités durant l'appel

- **Micro/Caméra**: Boutons en bas pour activer/désactiver
- **Partage d'écran**: Bouton "Share screen"
- **Chat**: Icône bulle de dialogue
- **Lever la main**: Icône main levée
- **Paramètres**: Icône engrenage (qualité vidéo, devices)
- **Quitter**: Raccrocher (icône téléphone rouge)

---

## Intégration Rocket.Chat

Jitsi Meet est préconfiguré pour fonctionner avec Rocket.Chat.

### Dans Rocket.Chat

**Configuration Admin**:
1. Admin → Video Conference → Jitsi
2. Domain: `meet.srv759970.hstgr.cloud`
3. Enable SSL: `true`
4. URL Prefix: `https://`

**Utilisation**:
- Cliquer sur l'icône caméra dans un channel/DM
- Ou taper `/jitsi NomReunion`

---

## Administration

### Vérifier les conteneurs

```bash
# Statut
docker ps --filter name=jitsi-

# Logs
docker logs jitsi-web --tail 50
docker logs jitsi-prosody --tail 50
docker logs jitsi-jicofo --tail 50
docker logs jitsi-jvb --tail 50

# Stats
docker stats jitsi-web jitsi-prosody jitsi-jicofo jitsi-jvb
```

### Redémarrer

```bash
# Tous les conteneurs
docker restart jitsi-web jitsi-prosody jitsi-jicofo jitsi-jvb

# Un seul
docker restart jitsi-jvb
```

---

## Sécurité

### HTTPS

- ✅ Certificat Let's Encrypt
- ✅ Renouvellement automatique (expire 2026-01-19)
- ✅ HTTP/2 activé
- ✅ WebSocket over HTTPS

### Authentification

**Mode actuel**: Guest access (pas d'authentification)

**Pour activer l'auth** (optionnel):
```bash
# Dans /opt/jitsi/.env
ENABLE_AUTH=1
ENABLE_GUESTS=0

# Redémarrer
docker restart jitsi-prosody jitsi-web
```

### Chiffrement

- ✅ Signaling chiffré (HTTPS/WSS)
- ✅ Media chiffré (DTLS-SRTP)
- ✅ End-to-end encryption disponible (E2EE)

---

## Limites et quotas

### Participants

- **Recommandé**: Jusqu'à 35 participants avec vidéo
- **Maximum testé**: 75 participants (audio only recommandé au-delà de 35)

### Bande passante

- **Par participant**: ~2-4 Mbps (vidéo HD)
- **Total serveur**: Limité par bande passante réseau serveur

### Qualité vidéo

- **SD**: 180p, 360p
- **HD**: 720p (par défaut)
- **Full HD**: 1080p (optionnel, consomme plus)

---

## Troubleshooting

### Pas de vidéo/audio

**Symptôme**: Participant ne voit/entend rien

**Solutions**:
1. Vérifier permissions navigateur (micro/caméra)
2. Vérifier port 10000/UDP ouvert dans firewall
3. Tester connection: https://meet.srv759970.hstgr.cloud avec 2 onglets

### Erreur "Room not found"

**Symptôme**: Erreur au chargement de la salle

**Solution**:
```bash
# Vérifier Prosody
docker logs jitsi-prosody --tail 50

# Redémarrer Prosody
docker restart jitsi-prosody
```

### Problème de qualité (lag, freeze)

**Solutions**:
1. Réduire qualité vidéo dans paramètres
2. Désactiver caméra (audio only)
3. Vérifier logs JVB:
```bash
docker logs jitsi-jvb --tail 100 | grep ERROR
```

### Erreur 502 Bad Gateway

**Solution**:
```bash
# Vérifier que tous les conteneurs tournent
docker ps --filter name=jitsi-

# Redémarrer jitsi-web
docker restart jitsi-web
```

---

## Optimisations

### Qualité adaptative

Jitsi ajuste automatiquement la qualité selon:
- Bande passante disponible
- Nombre de participants
- Capacité CPU du serveur

### Simulcast

Activé par défaut - Chaque participant envoie plusieurs qualités, le serveur sélectionne la meilleure selon réception.

---

## Comparaison avec alternatives

| Feature | Jitsi Meet | Zoom | Google Meet |
|---------|------------|------|-------------|
| **Self-hosted** | ✅ Oui | ❌ Non | ❌ Non |
| **Open Source** | ✅ Oui | ❌ Non | ❌ Non |
| **Sans compte** | ✅ Oui | ❌ Non | ⚠️ Limité |
| **Chiffrement E2E** | ✅ Oui | ✅ Oui | ❌ Non |
| **Participants max** | 75+ | 100-1000 | 100-250 |
| **Enregistrement** | ⚠️ Local | ✅ Cloud | ✅ Cloud |
| **Coût** | ✅ Gratuit | 💰 Payant | 💰 Payant |

---

## Liens utiles

- **Documentation officielle**: https://jitsi.github.io/handbook/
- **FAQ**: https://jitsi.github.io/handbook/docs/faq
- **Dev guide**: https://jitsi.github.io/handbook/docs/devops-guide/
- **Community**: https://community.jitsi.org

---

**Dernière mise à jour**: 2025-10-21
**Version Jitsi**: unstable (latest Docker images)
