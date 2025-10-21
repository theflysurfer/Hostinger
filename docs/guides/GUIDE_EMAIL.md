# Configuration Email

## Vue d'ensemble

Guide pour la configuration de l'envoi d'emails depuis le serveur srv759970.hstgr.cloud.

## SMTP Configuration

### Options disponibles

1. **SMTP Relay externe** (recommandé)
   - SendGrid
   - Mailgun
   - Amazon SES
   - SMTP2GO

2. **SMTP local** (plus complexe)
   - Postfix
   - Exim4

## Configuration avec SendGrid (Recommandé)

### 1. Créer un compte SendGrid

1. Aller sur [sendgrid.com](https://sendgrid.com)
2. Créer un compte gratuit (100 emails/jour)
3. Créer une API Key dans Settings > API Keys

### 2. Configuration Docker

```yaml
# Dans docker-compose.yml
environment:
  - SMTP_HOST=smtp.sendgrid.net
  - SMTP_PORT=587
  - SMTP_USER=apikey
  - SMTP_PASSWORD=<your_sendgrid_api_key>
  - SMTP_FROM=noreply@srv759970.hstgr.cloud
```

### 3. Test d'envoi

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

## Alertes Grafana par Email

### Configuration dans Grafana

1. Aller dans Alerting > Contact points
2. Créer un nouveau contact point:
   - Type: Email
   - Addresses: julien@julienfernandez.xyz
   - SMTP Host: smtp.sendgrid.net:587
   - Username: apikey
   - Password: <api_key>
   - From: grafana@srv759970.hstgr.cloud

### Exemple d'alerte

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

## Configuration Postfix (Alternative)

### Installation

```bash
apt-get install -y postfix mailutils
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

## SPF et DKIM

Pour améliorer la délivrabilité, configurer les enregistrements DNS:

### SPF Record

```
Type: TXT
Name: @
Value: v=spf1 include:sendgrid.net ~all
```

### DKIM

Configuré automatiquement par SendGrid.

## Monitoring des Emails

### SendGrid Dashboard

- Statistiques d'envoi
- Taux de délivrabilité
- Bounces et spam reports

### Logs Postfix

```bash
tail -f /var/log/mail.log
```

## Ressources

- [SendGrid Documentation](https://docs.sendgrid.com/)
- [Postfix Documentation](http://www.postfix.org/documentation.html)
- [Grafana Email Notifications](https://grafana.com/docs/grafana/latest/alerting/contact-points/)
