# Guide Configuration Email - srv759970.hstgr.cloud

## Vue d'ensemble

Ce guide documente la configuration complète du serveur email sur srv759970.hstgr.cloud utilisant **Postfix** comme serveur SMTP et **OpenDKIM** pour l'authentification des messages.

**Version**: 1.0
**Date**: 2025-10-16
**Système**: Ubuntu 24.04.2 LTS

---

## Architecture

```
┌─────────────────┐
│   WordPress     │
│   Applications  │
└────────┬────────┘
         │ Port 25 (local)
         ▼
┌─────────────────┐
│   Postfix       │ ◄─── OpenDKIM (signature DKIM)
│   SMTP Server   │
└────────┬────────┘
         │ Port 25 (SMTP)
         │ Port 587 (Submission)
         ▼
    Internet

```

---

## Composants installés

| Composant | Version | Rôle |
|-----------|---------|------|
| **Postfix** | 3.8.6-1build2 | Serveur SMTP pour envoi d'emails |
| **OpenDKIM** | 2.11.0~beta2 | Signature DKIM des messages sortants |
| **mailutils** | 1:3.17-1.1build3 | Utilitaires de test (commande `mail`) |
| **WP Mail SMTP** | 4.6.0 | Plugin WordPress pour configuration SMTP |

---

## Configuration Postfix

### Fichiers de configuration

**`/etc/postfix/main.cf`**
```ini
# Serveur et domaines
myhostname = srv759970.hstgr.cloud
myorigin = srv759970.hstgr.cloud
mydestination = $myhostname, localhost.$mydomain, localhost

# Réseau
inet_interfaces = all
inet_protocols = ipv4
mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128

# TLS/SSL (Let's Encrypt)
smtpd_tls_cert_file = /etc/letsencrypt/live/wordpress.srv759970.hstgr.cloud/fullchain.pem
smtpd_tls_key_file = /etc/letsencrypt/live/wordpress.srv759970.hstgr.cloud/privkey.pem
smtp_tls_cert_file = /etc/letsencrypt/live/wordpress.srv759970.hstgr.cloud/fullchain.pem
smtp_tls_key_file = /etc/letsencrypt/live/wordpress.srv759970.hstgr.cloud/privkey.pem
smtpd_tls_security_level = may
smtp_tls_security_level = may
smtp_tls_loglevel = 1
smtpd_tls_loglevel = 1

# Sécurité
smtpd_relay_restrictions = permit_mynetworks, reject_unauth_destination
smtpd_sasl_auth_enable = no
disable_vrfy_command = yes
smtpd_helo_required = yes

# OpenDKIM Milter integration
milter_default_action = accept
milter_protocol = 6
smtpd_milters = local:/opendkim/opendkim.sock
non_smtpd_milters = local:/opendkim/opendkim.sock

# Mailbox
home_mailbox = Maildir/
```

**`/etc/postfix/master.cf`** (ajout pour port 587)
```ini
# Submission port for applications (WordPress, etc.)
submission inet n       -       y       -       -       smtpd
  -o syslog_name=postfix/submission
  -o smtpd_tls_security_level=may
  -o smtpd_sasl_auth_enable=no
  -o smtpd_relay_restrictions=permit_mynetworks,reject
  -o milter_macro_daemon_name=ORIGINATING
```

### Ports en écoute

| Port | Service | Usage |
|------|---------|-------|
| **25** | SMTP | Réception d'emails (local) |
| **587** | Submission | Envoi depuis applications |

Vérification :
```bash
ss -tlnp | grep -E ':(25|587)'
```

---

## Configuration OpenDKIM

### Structure des répertoires

```
/etc/opendkim/
├── opendkim.conf          # Configuration principale
├── TrustedHosts           # Hôtes de confiance
├── KeyTable               # Table des clés DKIM
├── SigningTable           # Table des signatures (regex)
└── keys/
    └── srv759970.hstgr.cloud/
        ├── mail.private   # Clé privée DKIM (600 root:root)
        └── mail.txt       # Clé publique DNS
```

### Fichier `/etc/opendkim.conf`

```ini
# OpenDKIM simplified configuration
Syslog                  yes
UMask                   002
Socket                  local:/var/spool/postfix/opendkim/opendkim.sock
PidFile                 /run/opendkim/opendkim.pid

Canonicalization        relaxed/simple
Mode                    sv
SubDomains              yes

AutoRestart             yes
AutoRestartRate         10/1M

ExternalIgnoreList      /etc/opendkim/TrustedHosts
InternalHosts           /etc/opendkim/TrustedHosts
KeyTable                /etc/opendkim/KeyTable
SigningTable            refile:/etc/opendkim/SigningTable
LogWhy                  yes
```

### Fichier `/etc/opendkim/TrustedHosts`

```
127.0.0.1
localhost
srv759970.hstgr.cloud
*.srv759970.hstgr.cloud
69.62.108.82
```

### Fichier `/etc/opendkim/KeyTable`

```
mail._domainkey.srv759970.hstgr.cloud srv759970.hstgr.cloud:mail:/etc/opendkim/keys/srv759970.hstgr.cloud/mail.private
```

### Fichier `/etc/opendkim/SigningTable`

```
root@srv759970.hstgr.cloud mail._domainkey.srv759970.hstgr.cloud
wordpress@srv759970.hstgr.cloud mail._domainkey.srv759970.hstgr.cloud
noreply@srv759970.hstgr.cloud mail._domainkey.srv759970.hstgr.cloud
/.*@srv759970\.hstgr\.cloud$/ mail._domainkey.srv759970.hstgr.cloud
/.*@.*\.srv759970\.hstgr\.cloud$/ mail._domainkey.srv759970.hstgr.cloud
```

### Permissions critiques

```bash
# Répertoires et fichiers OpenDKIM
chown -R root:root /etc/opendkim
chmod 755 /etc/opendkim
chmod 755 /etc/opendkim/keys
chmod 755 /etc/opendkim/keys/srv759970.hstgr.cloud
chmod 600 /etc/opendkim/keys/srv759970.hstgr.cloud/mail.private

# Socket Unix pour Postfix
mkdir -p /var/spool/postfix/opendkim
chown opendkim:postfix /var/spool/postfix/opendkim
chmod 750 /var/spool/postfix/opendkim

# PID directory
mkdir -p /run/opendkim
chown opendkim:opendkim /run/opendkim
chmod 755 /run/opendkim

# Ajouter postfix au groupe opendkim
usermod -a -G opendkim postfix
```

### Service systemd override

Fichier `/etc/systemd/system/opendkim.service.d/override.conf`:

```ini
[Service]
ExecStartPost=/bin/sh -c 'sleep 1; chown opendkim:postfix /var/spool/postfix/opendkim/opendkim.sock; chmod 660 /var/spool/postfix/opendkim/opendkim.sock'
```

Appliquer :
```bash
systemctl daemon-reload
systemctl restart opendkim
```

---

## Configuration DNS (SPF, DKIM, DMARC)

### Enregistrement SPF

**Type**: TXT
**Nom**: `srv759970.hstgr.cloud`
**Valeur**:
```
v=spf1 ip4:69.62.108.82 a mx ~all
```

### Enregistrement DKIM

**Type**: TXT
**Nom**: `mail._domainkey.srv759970.hstgr.cloud`
**Valeur** (voir `/etc/opendkim/keys/srv759970.hstgr.cloud/mail.txt`):
```
v=DKIM1; h=sha256; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuTozVcay5Yf8yxuYF4XKhoMy9mNORQyIOt68Rl6SceWwTo4DnmXaN3N/2TZI5m9bJ2lN8A2FYENbMmoiG3DPD/2zyShvnRLuqwU941Lmgwix+61TtSpJ2wz5bDhlueylIFUxNwwgKdQ77xu2XYrfZTQeGwbQ9GOjknu9SoFK/eeTrXflgF4Tsvp5LSxo+gTu/plXtZnTterWlmrIZ9T1RRcRDPCSHiNXL2EOScAz2OrODzmjlatFaDkezwPIXAmJEKO5DxwCKCY+ALlbi8D0l/MkBtotz9RZZ8BKCPIyHt+LHQ0Lp7+ruD4sJKOKnnfihP6Qqz7rt31g0CDUJ2CsoQIDAQAB
```

**Remarque** : Supprimer les sauts de ligne et parenthèses pour le panneau DNS réel.

### Enregistrement DMARC

**Type**: TXT
**Nom**: `_dmarc.srv759970.hstgr.cloud`
**Valeur**:
```
v=DMARC1; p=quarantine; rua=mailto:postmaster@srv759970.hstgr.cloud; pct=100
```

### Vérification DNS

```bash
# Vérifier SPF
dig +short TXT srv759970.hstgr.cloud

# Vérifier DKIM
dig +short TXT mail._domainkey.srv759970.hstgr.cloud

# Vérifier DMARC
dig +short TXT _dmarc.srv759970.hstgr.cloud
```

---

## Configuration WordPress

### Plugin WP Mail SMTP

**Installation** :
```bash
wp plugin install wp-mail-smtp --activate --allow-root
```

### Configuration dans `wp-config.php`

Ajouter à la fin de `/var/www/wordpress/wp-config.php` :

```php
// WP Mail SMTP configuration for local Postfix
define( 'WPMS_ON', true );
define( 'WPMS_MAIL_FROM', 'noreply@srv759970.hstgr.cloud' );
define( 'WPMS_MAIL_FROM_NAME', 'Clémence - RH Diversité & Inclusion' );
define( 'WPMS_MAILER', 'smtp' );
define( 'WPMS_SMTP_HOST', 'localhost' );
define( 'WPMS_SMTP_PORT', 25 );
define( 'WPMS_SSL', '' );
define( 'WPMS_SMTP_AUTH', false );
define( 'WPMS_SMTP_AUTOTLS', false );
```

### Test depuis WordPress

```bash
wp eval 'wp_mail("votre-email@example.com", "Test WordPress", "Ceci est un test.");' --allow-root
```

---

## Tests et Diagnostics

### Test 1 : Envoi email local

```bash
echo "Test email from Postfix" | mail -s "Test Subject" root@localhost
tail -20 /var/log/mail.log
```

**Attendu** : `status=sent (delivered to maildir)`

### Test 2 : Vérifier OpenDKIM

```bash
systemctl status opendkim
tail -20 /var/log/mail.log | grep opendkim
```

**Attendu** : Pas d'erreurs "error loading key" ou "Permission denied"

### Test 3 : Vérifier signature DKIM

```bash
echo "DKIM test" | mail -s "DKIM Test" root@localhost
sleep 2
tail -20 /var/log/mail.log | grep -E "(DKIM|signed|opendkim)"
```

**Attendu** : Logs indiquant `mail._domainkey.srv759970.hstgr.cloud: DKIM-Signature field added`

### Test 4 : Tester clé DKIM publique

```bash
opendkim-testkey -d srv759970.hstgr.cloud -s mail -vvv
```

**Attendu** : `key OK` (après configuration DNS)

### Test 5 : Vérifier ports SMTP

```bash
ss -tlnp | grep -E ':(25|587)'
```

**Attendu** :
```
LISTEN 0 100 0.0.0.0:25   users:(("master",pid=XXX))
LISTEN 0 100 0.0.0.0:587  users:(("master",pid=XXX))
```

---

## Dépannage

### Problème : "Permission denied" pour socket OpenDKIM

**Symptôme** :
```
postfix/cleanup: warning: connect to Milter service local:/opendkim/opendkim.sock: Permission denied
```

**Solution** :
```bash
chown opendkim:postfix /var/spool/postfix/opendkim/opendkim.sock
chmod 660 /var/spool/postfix/opendkim/opendkim.sock
systemctl restart postfix
```

### Problème : "no signing table match"

**Symptôme** :
```
opendkim: no signing table match for 'user@domain'
```

**Solution** :
Vérifier `/etc/opendkim/SigningTable` et ajouter l'adresse email ou utiliser regex :
```bash
echo "/.*@srv759970\.hstgr\.cloud$/ mail._domainkey.srv759970.hstgr.cloud" >> /etc/opendkim/SigningTable
systemctl restart opendkim
```

### Problème : "key data is not secure"

**Symptôme** :
```
opendkim: key data is not secure: /etc/opendkim is writeable
```

**Solution** :
```bash
chown -R root:root /etc/opendkim
chmod 755 /etc/opendkim
chmod 600 /etc/opendkim/keys/*/mail.private
systemctl restart opendkim
```

### Problème : Emails non livrés

**Vérifier les logs** :
```bash
tail -50 /var/log/mail.log
journalctl -xeu postfix.service
```

**Vérifier la queue Postfix** :
```bash
postqueue -p
```

**Flush la queue** :
```bash
postqueue -f
```

---

## Commandes utiles

### Gestion des services

```bash
# Redémarrer Postfix
systemctl restart postfix

# Recharger la configuration Postfix
systemctl reload postfix

# Redémarrer OpenDKIM
systemctl restart opendkim

# Voir les logs en temps réel
tail -f /var/log/mail.log
```

### Postfix

```bash
# Voir la configuration actuelle
postconf | grep -E '^(myhostname|mydestination|mynetworks)'

# Modifier une option
postconf -e 'parameter=value'

# Tester la configuration
postfix check

# Voir la queue
mailq
postqueue -p

# Supprimer un message de la queue
postsuper -d MESSAGE_ID
```

### OpenDKIM

```bash
# Générer une nouvelle clé DKIM
cd /etc/opendkim/keys/srv759970.hstgr.cloud
opendkim-genkey -s mail -d srv759970.hstgr.cloud

# Tester la clé DNS
opendkim-testkey -d srv759970.hstgr.cloud -s mail -vvv

# Voir la clé publique
cat /etc/opendkim/keys/srv759970.hstgr.cloud/mail.txt
```

---

## Sécurité et Bonnes Pratiques

### ✅ Recommandations

1. **Firewall** : Ouvrir uniquement les ports nécessaires
   ```bash
   ufw allow 25/tcp   # SMTP
   ufw allow 587/tcp  # Submission
   ```

2. **Reverse DNS** : Configurer un enregistrement PTR pour `69.62.108.82` → `srv759970.hstgr.cloud`

3. **Monitoring** : Surveiller les logs régulièrement
   ```bash
   tail -f /var/log/mail.log | grep -E '(reject|error|warning)'
   ```

4. **Rate Limiting** : Limiter l'envoi d'emails pour éviter le spam
   ```ini
   # Dans /etc/postfix/main.cf
   smtpd_client_connection_rate_limit = 10
   ```

5. **Backup des clés** : Sauvegarder `/etc/opendkim/keys/`
   ```bash
   tar -czf /root/backups/opendkim-keys-$(date +%Y%m%d).tar.gz /etc/opendkim/keys/
   ```

### ⚠️ Points d'attention

- **DKIM** : La signature DKIM nécessite la configuration DNS complète
- **Delivery** : Sans SPF/DKIM/DMARC, les emails peuvent être marqués comme spam
- **Certificats SSL** : Renouveler automatiquement avec certbot
- **Logs** : Rotation automatique via logrotate (déjà configuré)

---

## Intégration avec d'autres applications

### Pour d'autres applications Node.js/Python/PHP

Utiliser `localhost:25` ou `localhost:587` sans authentification :

**Exemple Node.js (nodemailer)** :
```javascript
const nodemailer = require('nodemailer');
const transporter = nodemailer.createTransport({
  host: 'localhost',
  port: 25,
  secure: false,
  tls: { rejectUnauthorized: false }
});
```

**Exemple Python (smtplib)** :
```python
import smtplib
server = smtplib.SMTP('localhost', 25)
server.sendmail('noreply@srv759970.hstgr.cloud', 'dest@example.com', 'Message')
server.quit()
```

---

## Historique des modifications

| Date | Version | Changements |
|------|---------|-------------|
| 2025-10-16 | 1.0 | Configuration initiale Postfix + OpenDKIM + WordPress |

---

## Ressources

- [Postfix Documentation](http://www.postfix.org/documentation.html)
- [OpenDKIM Documentation](http://www.opendkim.org/docs.html)
- [SPF Record Syntax](https://www.rfc-editor.org/rfc/rfc7208)
- [DKIM RFC](https://www.rfc-editor.org/rfc/rfc6376)
- [DMARC RFC](https://www.rfc-editor.org/rfc/rfc7489)

---

**Maintenu par** : Julien Fernandez
**Contact** : Via GitHub Issues

