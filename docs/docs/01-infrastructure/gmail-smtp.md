# 📧 Configuration Gmail SMTP pour WordPress

## 🎯 Objectif

Configurer WordPress pour envoyer des emails via Gmail SMTP au lieu du serveur Postfix local.

---

## 📋 Prérequis

1. Un compte Gmail (ex: `clemsfou@gmail.com`)
2. Validation en 2 étapes activée sur le compte Gmail
3. Un mot de passe d'application Gmail

---

## Étape 1 : Créer un mot de passe d'application Gmail

### 1.1 Activer la validation en 2 étapes (si pas déjà fait)

1. Aller sur https://myaccount.google.com/security
2. Dans "Connexion à Google", cliquer sur **Validation en 2 étapes**
3. Suivre les instructions pour activer

### 1.2 Générer un mot de passe d'application

1. Aller sur https://myaccount.google.com/apppasswords
2. Se connecter si demandé
3. Dans "Sélectionner une application", choisir **Autre (nom personnalisé)**
4. Entrer : `WordPress srv759970`
5. Cliquer sur **Générer**
6. **COPIER** le mot de passe de 16 caractères (format: `xxxx xxxx xxxx xxxx`)
7. ⚠️ **IMPORTANT** : Garder ce mot de passe, il ne sera affiché qu'une fois !

---

## Étape 2 : Configuration WordPress

### Option A : Via SSH (Recommandé)

```bash
ssh root@69.62.108.82

# Éditer wp-config.php
nano /var/www/wordpress/wp-config.php
```

**Remplacer la section WP Mail SMTP existante par** :

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
define( 'WPMS_SMTP_PASS', 'VOTRE_MOT_DE_PASSE_APPLICATION' );  // ⚠️ Remplacer par le mot de passe généré
define( 'WPMS_SMTP_AUTOTLS', true );
```

**Sauvegarder** : `Ctrl + O`, `Enter`, `Ctrl + X`

---

### Option B : Via le plugin WP Mail SMTP (Interface)

1. Aller sur https://wordpress.srv759970.hstgr.cloud/clemence/wp-admin/
2. Se connecter avec :
   - **User** : `admin`
   - **Password** : `TempPass2025!`
3. Menu : **WP Mail SMTP** → **Settings**
4. Configurer :
   - **From Email** : `clemsfou@gmail.com`
   - **From Name** : `Clémence - RH Diversité & Inclusion`
   - **Mailer** : Sélectionner **Gmail**
5. Section **Gmail Settings** :
   - **Client ID** : (laisser vide si on utilise le mot de passe d'app)
6. OU utiliser **Other SMTP** :
   - **SMTP Host** : `smtp.gmail.com`
   - **SMTP Port** : `587`
   - **Encryption** : `TLS`
   - **Authentication** : Activé
   - **Username** : `clemsfou@gmail.com`
   - **Password** : `votre-mot-de-passe-application`
7. Cliquer sur **Save Settings**

---

## Étape 3 : Test d'envoi

### Via WordPress Admin

1. Dans WP Mail SMTP → **Email Test**
2. Entrer une adresse email de test
3. Cliquer sur **Send Email**
4. Vérifier la réception

### Via SSH

```bash
ssh root@69.62.108.82
wp --path=/var/www/wordpress --url=wordpress.srv759970.hstgr.cloud/clemence eval 'wp_mail("votre-email@example.com", "Test Gmail SMTP", "Email envoyé via Gmail SMTP depuis WordPress.");' --allow-root
```

Vérifier :
- L'email arrive bien
- L'expéditeur est `clemsfou@gmail.com`
- Pas de spam

---

## ✅ Vérification

### Logs WordPress

```bash
ssh root@69.62.108.82
tail -50 /var/www/wordpress/wp-content/debug.log
```

### Logs serveur (optionnel)

```bash
tail -50 /var/log/mail.log
```

Avec Gmail SMTP, les emails ne passent plus par Postfix local, donc les logs Postfix seront vides.

---

## 🔒 Sécurité

### Protéger le mot de passe dans wp-config.php

Le fichier `wp-config.php` n'est **pas accessible via le web** par défaut (Nginx le bloque), donc le mot de passe est en sécurité.

Vérifier les permissions :
```bash
ssh root@69.62.108.82
ls -la /var/www/wordpress/wp-config.php
```

**Résultat attendu** :
```
-rw-r--r-- 1 www-data www-data ... wp-config.php
```

---

## 🚨 Limites Gmail

### Quotas d'envoi

- **Comptes Gmail gratuits** : 500 emails/jour
- **Google Workspace** : 2000 emails/jour

Si dépassement → compte bloqué temporairement (24h).

### Solutions si quota dépassé

1. **Utiliser Postfix local** (déjà installé) pour les notifications internes
2. **Utiliser SendGrid/Mailgun** pour les volumes élevés
3. **Passer à Google Workspace** pour un quota supérieur

---

## 🔄 Revenir à Postfix local

Si besoin de revenir au serveur Postfix local :

```bash
ssh root@69.62.108.82
nano /var/www/wordpress/wp-config.php
```

Remplacer par :
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

---

## 📚 Ressources

- [Google App Passwords](https://myaccount.google.com/apppasswords)
- [WP Mail SMTP Documentation](https://wpmailsmtp.com/docs/)
- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)

---

**Créé le** : 2025-10-16

