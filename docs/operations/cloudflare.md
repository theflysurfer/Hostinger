# Guide Configuration Cloudflare - srv759970.hstgr.cloud

## 🎯 Objectifs

- ✅ Protéger les sites en dev avec Cloudflare Access (Zero Trust)
- ✅ Activer le CDN et cache pour améliorer les performances
- ✅ Configurer le firewall WAF pour bloquer les menaces
- ✅ Garder les APIs accessibles mais sécurisées

---

## 📋 Prérequis

- Compte Cloudflare (gratuit) : https://dash.cloudflare.com/sign-up
- Accès aux DNS du domaine `srv759970.hstgr.cloud` (Hostinger)
- 15-20 minutes

---

## Étape 1 : Ajouter le site à Cloudflare

### 1.1 Créer un compte Cloudflare

1. Aller sur https://dash.cloudflare.com/sign-up
2. S'inscrire avec ton email (julien.fernandez.work@gmail.com)
3. Vérifier l'email

### 1.2 Ajouter le domaine

1. Dans le dashboard Cloudflare, cliquer **Add a Site**
2. Entrer : `srv759970.hstgr.cloud`
3. Sélectionner le plan **Free** ($0/mois)
4. Cliquer **Continue**

### 1.3 Scanner les DNS existants

Cloudflare va scanner automatiquement tous les enregistrements DNS actuels.

**Vérifier que tous les sous-domaines sont détectés** :
- `dashboard.srv759970.hstgr.cloud`
- `wordpress.srv759970.hstgr.cloud`
- `cristina.srv759970.hstgr.cloud`
- `clemence.srv759970.hstgr.cloud`
- `sharepoint.srv759970.hstgr.cloud`
- `whisper.srv759970.hstgr.cloud`
- `tika.srv759970.hstgr.cloud`
- `portal.srv759970.hstgr.cloud`
- `ollama.srv759970.hstgr.cloud`
- Etc.

Si un sous-domaine manque, l'ajouter manuellement :
- **Type** : `A`
- **Name** : `sous-domaine` (ex: `dashboard`)
- **IPv4 address** : `69.62.108.82`
- **Proxy status** : 🟠 **Proxied** (cloud orange activé)

Cliquer **Continue**

---

## Étape 2 : Changer les nameservers chez Hostinger

### 2.1 Récupérer les nameservers Cloudflare

Cloudflare affiche 2 nameservers, exemple :
```
aisha.ns.cloudflare.com
baker.ns.cloudflare.com
```

**Copier ces 2 nameservers**

### 2.2 Modifier chez Hostinger

1. Aller sur https://hpanel.hostinger.com/
2. Sélectionner le VPS `srv759970.hstgr.cloud`
3. Menu **DNS / Name Servers**
4. Cliquer **Change Nameservers**
5. Sélectionner **Custom nameservers**
6. Entrer les 2 nameservers Cloudflare
7. Cliquer **Change Nameservers**

### 2.3 Vérifier la propagation

⏱️ **Délai** : 5 minutes à 24h (généralement 15-30 min)

Vérifier avec :
```bash
nslookup -type=NS srv759970.hstgr.cloud
```

**Résultat attendu** : Les nameservers Cloudflare

Une fois propagé, Cloudflare affichera **Active** avec une coche verte ✅

---

## Étape 3 : Configuration SSL/TLS

### 3.1 Mode SSL

1. Dans Cloudflare Dashboard → **SSL/TLS**
2. Sélectionner le mode : **Full (strict)**
   - ✅ Cloudflare ↔️ Serveur : SSL validé (Let's Encrypt)
   - ✅ Client ↔️ Cloudflare : SSL Cloudflare

3. Activer **Always Use HTTPS**
4. Activer **Automatic HTTPS Rewrites**

### 3.2 Edge Certificates

Dans **SSL/TLS** → **Edge Certificates** :
- ✅ Activer **Always Use HTTPS**
- ✅ Activer **HTTP Strict Transport Security (HSTS)** (optionnel, mais recommandé)
  - Max Age: `6 months`
  - Include subdomains: ✅
  - Preload: ✅ (si tu es sûr)

---

## Étape 4 : Activer le CDN et optimisations

### 4.1 Speed optimizations

Dans **Speed** → **Optimization** :

✅ **Auto Minify** :
- JavaScript
- CSS
- HTML

✅ **Brotli** : Activé

✅ **Early Hints** : Activé

✅ **Rocket Loader** : ⚠️ Désactivé (peut casser certains JS)

### 4.2 Caching

Dans **Caching** → **Configuration** :

**Caching Level** : `Standard`

**Browser Cache TTL** : `4 hours` (ou `1 day` pour prod)

**Always Online** : ✅ Activé (cache de secours si serveur down)

---

## Étape 5 : Protéger les sites en DEV avec Cloudflare Access (Zero Trust)

### 5.1 Activer Cloudflare Access

1. Dans le menu de gauche → **Zero Trust**
2. Si premier usage, créer une "team" : `julien-dev` (ou autre nom)
3. Menu **Access** → **Applications**

### 5.2 Créer une application pour les sites DEV

**Pour chaque site à protéger** (Clémence, Cristina, WordPress) :

1. Cliquer **Add an application**
2. Sélectionner **Self-hosted**
3. Configuration :

   **Application Configuration** :
   - **Application name** : `Clémence Site (DEV)`
   - **Session Duration** : `24 hours`
   - **Application domain** :
     - Subdomain : `clemence`
     - Domain : `srv759970.hstgr.cloud`
   - **Accept all available identity providers** : ✅

4. Cliquer **Next**

   **Add policies** :
   - **Policy name** : `Allow Julien & Team`
   - **Action** : `Allow`
   - **Include** :
     - Selector : `Emails`
     - Value : `julien.fernandez.work@gmail.com, clemsfou@gmail.com`

   Ou utiliser **Email domain** :
     - Value : `gmail.com` (si tu veux autoriser tous les @gmail.com)

5. Cliquer **Next** → **Add application**

**Répéter pour** :
- `wordpress.srv759970.hstgr.cloud`
- `cristina.srv759970.hstgr.cloud`
- `admin.cristina.srv759970.hstgr.cloud` (Strapi)

### 5.3 Tester l'accès

1. Ouvrir https://clemence.srv759970.hstgr.cloud
2. **Cloudflare Access login page** apparaît
3. Entrer ton email → Recevoir un code par email → Entrer le code
4. Accès au site ✅

---

## Étape 6 : Sécuriser les APIs avec Firewall Rules

Pour les APIs (Whisper, Tika, Ollama) et outils (Portal, Portainer), on ne veut pas bloquer totalement, mais ajouter une protection.

### Option A : IP Allowlist (si IP fixe)

1. **Security** → **WAF** → **Custom rules**
2. Cliquer **Create rule**
3. Configuration :
   - **Rule name** : `Allow only my IP for APIs`
   - **Field** : `IP Source Address`
   - **Operator** : `does not equal`
   - **Value** : `VOTRE_IP_PUBLIQUE` (trouver avec https://ifconfig.me)
   - **Then** : `Block`

4. Appliquer uniquement à certains sous-domaines :
   - **Field** : `Hostname`
   - **Operator** : `equals`
   - **Value** : `portal.srv759970.hstgr.cloud`

   Répéter avec OR pour chaque API.

### Option B : Secret Header (si IP dynamique)

1. **Security** → **WAF** → **Custom rules**
2. Cliquer **Create rule**
3. Configuration :
   - **Rule name** : `Require secret header for APIs`
   - **Field** : `HTTP Header`
   - **Header name** : `X-Access-Key`
   - **Operator** : `does not equal`
   - **Value** : `MonSecretSuper2025!`
   - **Then** : `Block`

4. Pour accéder à l'API, ajouter le header dans les requêtes :
   ```bash
   curl -H "X-Access-Key: MonSecretSuper2025!" https://whisper.srv759970.hstgr.cloud/docs
   ```

### Option C : Laisser public avec Rate Limiting

1. **Security** → **WAF** → **Rate limiting rules**
2. Créer une règle :
   - **If incoming requests match** : Hostname = `*.srv759970.hstgr.cloud`
   - **Rate** : `100 requests per 10 seconds`
   - **Then** : `Block` for `10 minutes`

Protection contre le spam/DDoS, mais accès public.

---

## Étape 7 : Configuration DNS avancée (Email)

Si tu as déjà configuré SPF/DKIM/DMARC (voir TODO_CONFIG_DNS_EMAIL.md), vérifier dans Cloudflare :

1. **DNS** → **Records**
2. Vérifier que les enregistrements existent :
   - **SPF** : `v=spf1 ip4:69.62.108.82 a mx ~all`
   - **DKIM** : `mail._domainkey` → (clé publique)
   - **DMARC** : `_dmarc` → politique

⚠️ **Important** : Les enregistrements email doivent avoir **Proxy status** = ☁️ **DNS Only** (gris, pas orange)

---

## Étape 8 : Monitoring et Analytics

### 8.1 Activer Analytics

1. **Analytics & Logs** → **Web Analytics**
2. Activer **Web Analytics**
3. Ajouter le tag sur le site (ou laisser auto-inject)

### 8.2 Security Events

1. **Security** → **Events**
2. Voir toutes les requêtes bloquées/autorisées
3. Analyser les menaces

### 8.3 Alertes

1. **Notifications**
2. Configurer des alertes :
   - **Rate Limiting** triggered
   - **SSL/TLS certificate expiring**
   - **Cloudflare Access** login failures

---

## ✅ Vérifications finales

### Test 1 : SSL fonctionne

```bash
curl -I https://clemence.srv759970.hstgr.cloud
```

**Attendu** : `HTTP/2 200` avec header `cf-ray` (preuve que Cloudflare est actif)

### Test 2 : Cloudflare Access fonctionne

1. Ouvrir un navigateur en navigation privée
2. Aller sur https://clemence.srv759970.hstgr.cloud
3. **Attendu** : Page de login Cloudflare Access

### Test 3 : CDN cache fonctionne

```bash
curl -I https://cristina.srv759970.hstgr.cloud
```

**Attendu** : Header `cf-cache-status: HIT` (après 2ème requête)

### Test 4 : Firewall bloque

Si tu as créé une règle IP :
1. Utiliser un VPN ou mobile data (autre IP)
2. Accéder à https://portal.srv759970.hstgr.cloud
3. **Attendu** : Erreur 1020 ou 1010 (blocked by Cloudflare)

---

## 🔄 Désactiver temporairement Cloudflare

Si besoin de contourner Cloudflare (debug) :

### Option 1 : Désactiver le proxy (par sous-domaine)
1. **DNS** → **Records**
2. Cliquer sur le cloud orange 🟠 → Devient gris ☁️ (DNS Only)
3. Le trafic passe direct au serveur

### Option 2 : Mode Development (global)
1. **Caching** → **Configuration**
2. Activer **Development Mode** (3 heures)
3. Cache et protection désactivés temporairement

---

## 📊 Résumé de la configuration

| Service | Protection | Accès |
|---------|-----------|-------|
| **Clémence Site** | Cloudflare Access | Login email obligatoire |
| **WordPress** | Cloudflare Access | Login email obligatoire |
| **Cristina Site** | Cloudflare Access | Login email obligatoire |
| **Strapi Admin** | Cloudflare Access | Login email obligatoire |
| **Portal/APIs** | Firewall Rules ou Public | IP whitelist ou Rate Limit |
| **Monitoring** | Firewall Rules ou Public | IP whitelist ou Rate Limit |

---

## 🚀 Avantages obtenus

✅ **Sécurité** :
- Sites dev protégés par authentification
- WAF bloque attaques automatiques
- Rate limiting anti-DDoS

✅ **Performance** :
- CDN global (cache statique)
- Compression Brotli
- HTTP/3 et optimisations auto

✅ **Monitoring** :
- Analytics détaillés
- Logs de sécurité
- Alertes en temps réel

✅ **Gratuit** :
- Plan Free largement suffisant
- Pas de limite de bande passante

---

## 📚 Ressources

- **Cloudflare Dashboard** : https://dash.cloudflare.com/
- **Zero Trust Access** : https://dash.cloudflare.com/zero-trust
- **Documentation** : https://developers.cloudflare.com/

---

**Temps estimé** : 30 minutes pour tout configurer

**Prochaine étape** : Créer un compte Cloudflare et ajouter le domaine !

