# ⚠️ TODO - Configuration DNS pour Email Server

## 🎯 Objectif

Configurer les enregistrements DNS SPF, DKIM et DMARC pour améliorer la délivrabilité des emails et éviter le spam.

---

## 📋 Étapes à suivre

### 1. Accéder au panneau DNS Hostinger

1. Aller sur https://hpanel.hostinger.com/
2. Sélectionner le VPS `srv759970.hstgr.cloud`
3. Cliquer sur **DNS Zone** ou **DNS Management**

---

### 2. Ajouter les 3 enregistrements DNS

#### 📌 Enregistrement SPF

**Type** : `TXT`
**Nom/Host** : `srv759970.hstgr.cloud` (ou `@` si c'est le domaine racine)
**Valeur/Value** :
```
v=spf1 ip4:69.62.108.82 a mx ~all
```
**TTL** : 3600 (ou laisser par défaut)

---

#### 📌 Enregistrement DKIM

**Type** : `TXT`
**Nom/Host** : `mail._domainkey.srv759970.hstgr.cloud` (ou `mail._domainkey`)
**Valeur/Value** :
```
v=DKIM1; h=sha256; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuTozVcay5Yf8yxuYF4XKhoMy9mNORQyIOt68Rl6SceWwTo4DnmXaN3N/2TZI5m9bJ2lN8A2FYENbMmoiG3DPD/2zyShvnRLuqwU941Lmgwix+61TtSpJ2wz5bDhlueylIFUxNwwgKdQ77xu2XYrfZTQeGwbQ9GOjknu9SoFK/eeTrXflgF4Tsvp5LSxo+gTu/plXtZnTterWlmrIZ9T1RRcRDPCSHiNXL2EOScAz2OrODzmjlatFaDkezwPIXAmJEKO5DxwCKCY+ALlbi8D0l/MkBtotz9RZZ8BKCPIyHt+LHQ0Lp7+ruD4sJKOKnnfihP6Qqz7rt31g0CDUJ2CsoQIDAQAB
```
**TTL** : 3600 (ou laisser par défaut)

**⚠️ Important** : Copier TOUTE la valeur en UNE SEULE ligne (sans espaces ni retours à la ligne)

---

#### 📌 Enregistrement DMARC

**Type** : `TXT`
**Nom/Host** : `_dmarc.srv759970.hstgr.cloud` (ou `_dmarc`)
**Valeur/Value** :
```
v=DMARC1; p=quarantine; rua=mailto:postmaster@srv759970.hstgr.cloud; pct=100
```
**TTL** : 3600 (ou laisser par défaut)

---

### 3. Sauvegarder et attendre la propagation

- Cliquer sur **Save** ou **Add Record**
- Attendre la propagation DNS : **15 minutes à 48h** (généralement 1-2h)

---

## ✅ Vérification après propagation

### Depuis Windows (PowerShell ou CMD)

```powershell
# Vérifier SPF
nslookup -type=TXT srv759970.hstgr.cloud

# Vérifier DKIM
nslookup -type=TXT mail._domainkey.srv759970.hstgr.cloud

# Vérifier DMARC
nslookup -type=TXT _dmarc.srv759970.hstgr.cloud
```

### Depuis le serveur (SSH)

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

**Résultat attendu** :
```
key OK
```

---

## 📧 Test d'envoi d'email après configuration

Une fois les DNS propagés, tester l'envoi vers un vrai email externe :

```bash
ssh root@69.62.108.82
echo "Test email avec DNS configurés" | mail -s "Test DNS" votre-email@gmail.com
```

Vérifier :
1. L'email arrive bien dans la boîte de réception (pas SPAM)
2. Dans Gmail : clic droit sur l'email → **Afficher l'original** → vérifier les headers :
   - `SPF: PASS`
   - `DKIM: PASS`
   - `DMARC: PASS`

---

## 🔍 Outils de test en ligne

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

## ❓ Si ça ne fonctionne pas

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

## 📚 Ressources

- **GUIDE_EMAIL.md** - Documentation complète du serveur email
- Postfix : http://www.postfix.org/
- OpenDKIM : http://www.opendkim.org/

---

**Créé le** : 2025-10-16
**À faire** : Dès que possible pour activer l'envoi d'emails externes

