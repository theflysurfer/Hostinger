# Configuration Email - Guide Complet

Guide complet pour la configuration de l'envoi d'emails depuis le serveur srv759970.hstgr.cloud.

---

## Vue d'ensemble

Ce guide couvre 3 scenarios d'envoi d'emails :

1. **SMTP Relay externe** (SendGrid/Mailgun) - Pour applications Docker
2. **Gmail SMTP** - Pour WordPress
3. **Postfix local** - Pour notifications système

---

## Option 1 : SMTP Relay externe (Recommandé pour APIs)

### Services disponibles

1. **SMTP Relay externe** (recommandé)
   - SendGrid (100 emails/jour gratuit)
   - Mailgun
   - Amazon SES
   - SMTP2GO

### Configuration avec SendGrid

#### 1. Créer un compte SendGrid

1. Aller sur [sendgrid.com](https://sendgrid.com)
2. Créer un compte gratuit (100 emails/jour)
3. Créer une API Key dans Settings > API Keys

#### 2. Configuration Docker

```yaml
# Dans docker-compose.yml
environment:
  - SMTP_HOST=smtp.sendgrid.net
  - SMTP_PORT=587
  - SMTP_USER=apikey
  - SMTP_PASSWORD=<your_sendgrid_api_key>
  - SMTP_FROM=noreply@srv759970.hstgr.cloud
```

#### 3. Test d'envoi

```python
import smtplib
from email.mime.text import MIMEText

msg = MIMEText("Test email from srv759970")
msg['Subject'] = 'Test'
msg['From'] = 'noreply@srv759970.hstgr.cloud'
msg['To'] = 'julien@julienfernandez.xyz'

with smtplib.SMTP('smtp.sendgrid.net', 587) as server:
    server.starttls()
    server.login('apikey', 'YOUR_API_KEY')
    server.send_message(msg)
```

### Alertes Grafana par Email

#### Configuration dans Grafana

1. Aller dans Alerting > Contact points
2. Créer un nouveau contact point:
   - Type: Email
   - Addresses: julien@julienfernandez.xyz
   - SMTP Host: smtp.sendgrid.net:587
   - Username: apikey
   - Password: <api_key>
   - From: grafana@srv759970.hstgr.cloud

#### Exemple d'alerte

```yaml
# Alert: Jobs Failed
expr: rate(rq_jobs{status="failed"}[5m]) > 0.1
for: 5m
labels:
  severity: warning
annotations:
  summary: "Taux élevé d'échecs jobs WhisperX"
  description: "{{ $value }} jobs/min échouent"
```

---

## Option 2 : Gmail SMTP (Pour WordPress)

### Prérequis

1. Un compte Gmail (ex: `clemsfou@gmail.com`)
2. Validation en 2 étapes activée sur le compte Gmail
3. Un mot de passe d'application Gmail

### Étape 1 : Créer un mot de passe d'application Gmail

#### 1.1 Activer la validation en 2 étapes (si pas déjà fait)

1. Aller sur https://myaccount.google.com/security
2. Dans "Connexion à Google", cliquer sur **Validation en 2 étapes**
3. Suivre les instructions pour activer

#### 1.2 Générer un mot de passe d'application

1. Aller sur https://myaccount.google.com/apppasswords
2. Se connecter si demandé
3. Dans "Sélectionner une application", choisir **Autre (nom personnalisé)**
4. Entrer : `WordPress srv759970`
5. Cliquer sur **Générer**
6. **COPIER** le mot de passe de 16 caractères (format: `xxxx xxxx xxxx xxxx`)
7. ⚠️ **IMPORTANT** : Garder ce mot de passe, il ne sera affiché qu'une fois !

### Étape 2 : Configuration WordPress

#### Via SSH (Recommandé)

```bash
ssh root@69.62.108.82

# Éditer wp-config.php
nano /var/www/wordpress/wp-config.php
```

**Ajouter cette section** :

```php
// WP Mail SMTP configuration for Gmail
define( 'WPMS_ON', true );
define( 'WPMS_MAIL_FROM', 'clemsfou@gmail.com' );
define( 'WPMS_MAIL_FROM_NAME', 'Clémence - RH Diversité & Inclusion' );
define( 'WPMS_MAILER', 'smtp' );
define( 'WPMS_SMTP_HOST', 'smtp.gmail.com' );
define( 'WPMS_SMTP_PORT', 587 );
define( 'WPMS_SSL', 'tls' );
define( 'WPMS_SMTP_AUTH', true );
define( 'WPMS_SMTP_USER', 'clemsfou@gmail.com' );
define( 'WPMS_SMTP_PASS', 'VOTRE_MOT_DE_PASSE_APPLICATION' );  // ⚠️ Remplacer
define( 'WPMS_SMTP_AUTOTLS', true );
```

### Étape 3 : Test d'envoi

#### Via WordPress Admin

1. Dans WP Mail SMTP → **Email Test**
2. Entrer une adresse email de test
3. Cliquer sur **Send Email**
4. Vérifier la réception

#### Via SSH

```bash
ssh root@69.62.108.82
wp --path=/var/www/wordpress eval 'wp_mail("test@example.com", "Test Gmail SMTP", "Test OK");' --allow-root
```

### Limites Gmail

#### Quotas d'envoi

- **Comptes Gmail gratuits** : 500 emails/jour
- **Google Workspace** : 2000 emails/jour

Si dépassement → compte bloqué temporairement (24h).

---

## Option 3 : Postfix Local (Pour système)

### Installation

```bash
apt-get install -y postfix mailutils opendkim opendkim-tools
```

### Configuration de base

```bash
# /etc/postfix/main.cf
myhostname = srv759970.hstgr.cloud
mydomain = srv759970.hstgr.cloud
myorigin = $mydomain
inet_interfaces = localhost
inet_protocols = ipv4
mydestination = $myhostname, localhost.$mydomain, localhost
relayhost =
```

### Restart

```bash
systemctl restart postfix
```

### Test

```bash
echo "Test email body" | mail -s "Test Subject" julien@julienfernandez.xyz
```

---

## Configuration DNS pour délivrabilité

Pour améliorer la délivrabilité avec Postfix, configurer les enregistrements DNS.

### 1. Accéder au panneau DNS Hostinger

1. Aller sur https://hpanel.hostinger.com/
2. Sélectionner le VPS `srv759970.hstgr.cloud`
3. Cliquer sur **DNS Zone** ou **DNS Management**

### 2. Ajouter les enregistrements DNS

#### Enregistrement SPF

**Type** : `TXT`
**Nom/Host** : `@` ou `srv759970.hstgr.cloud`
**Valeur/Value** :
```
v=spf1 ip4:69.62.108.82 include:sendgrid.net a mx ~all
```
**TTL** : 3600

#### Enregistrement DKIM

**Type** : `TXT`
**Nom/Host** : `mail._domainkey`
**Valeur/Value** :
```
v=DKIM1; h=sha256; k=rsa; p=<votre_cle_publique_dkim>
```
**TTL** : 3600

Générer la clé DKIM :
```bash
ssh root@69.62.108.82
mkdir -p /etc/opendkim/keys/srv759970.hstgr.cloud
cd /etc/opendkim/keys/srv759970.hstgr.cloud
opendkim-genkey -s mail -d srv759970.hstgr.cloud
cat mail.txt  # Copier la clé publique
```

#### Enregistrement DMARC

**Type** : `TXT`
**Nom/Host** : `_dmarc`
**Valeur/Value** :
```
v=DMARC1; p=quarantine; rua=mailto:postmaster@srv759970.hstgr.cloud; pct=100
```
**TTL** : 3600

### 3. Vérification après propagation (1-48h)

#### Depuis Windows (PowerShell)

```powershell
# Vérifier SPF
nslookup -type=TXT srv759970.hstgr.cloud

# Vérifier DKIM
nslookup -type=TXT mail._domainkey.srv759970.hstgr.cloud

# Vérifier DMARC
nslookup -type=TXT _dmarc.srv759970.hstgr.cloud
```

#### Depuis le serveur (SSH)

```bash
ssh root@69.62.108.82

# Vérifier SPF
dig +short TXT srv759970.hstgr.cloud

# Vérifier DKIM
dig +short TXT mail._domainkey.srv759970.hstgr.cloud

# Vérifier DMARC
dig +short TXT _dmarc.srv759970.hstgr.cloud

# Tester la clé DKIM
opendkim-testkey -d srv759970.hstgr.cloud -s mail -vvv
```

**Résultat attendu** : `key OK`

---

## Outils de test en ligne

### MXToolbox - Test complet
https://mxtoolbox.com/SuperTool.aspx
- Entrer `srv759970.hstgr.cloud`
- Vérifier SPF, DKIM, DMARC

### Google Admin Toolbox - Test headers
https://toolbox.googleapps.com/apps/messageheader/
- Coller les headers d'un email reçu
- Voir le résultat d'authentification

### Mail Tester - Score spam
https://www.mail-tester.com/
- Envoyer un email à l'adresse fournie
- Voir le score /10

---

## Monitoring

### SendGrid Dashboard

- Statistiques d'envoi
- Taux de délivrabilité
- Bounces et spam reports

### Logs Postfix

```bash
tail -f /var/log/mail.log
```

### Logs WordPress

```bash
tail -50 /var/www/wordpress/wp-content/debug.log
```

---

## Troubleshooting

### DNS ne se propagent pas

1. Vérifier que les enregistrements sont bien ajoutés dans le panneau Hostinger
2. Attendre 24-48h (propagation mondiale)
3. Vider le cache DNS local :
   ```powershell
   ipconfig /flushdns
   ```

### DKIM échoue toujours

Regénérer la clé DKIM :
```bash
ssh root@69.62.108.82
cd /etc/opendkim/keys/srv759970.hstgr.cloud
rm mail.private mail.txt
opendkim-genkey -s mail -d srv759970.hstgr.cloud
cat mail.txt  # Copier la nouvelle clé publique
systemctl restart opendkim
```

Puis mettre à jour l'enregistrement DNS DKIM avec la nouvelle clé.

---

## Ressources

- [SendGrid Documentation](https://docs.sendgrid.com/)
- [Postfix Documentation](http://www.postfix.org/documentation.html)
- [Grafana Email Notifications](https://grafana.com/docs/grafana/latest/alerting/contact-points/)
- [Google App Passwords](https://myaccount.google.com/apppasswords)
- [WP Mail SMTP Documentation](https://wpmailsmtp.com/docs/)
- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)
