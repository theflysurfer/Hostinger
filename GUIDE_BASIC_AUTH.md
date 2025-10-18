# Guide d'utilisation - Basic Auth sur srv759970.hstgr.cloud

## 🔒 Protection activée

Tous les sites et APIs sur `srv759970.hstgr.cloud` sont maintenant protégés par **HTTP Basic Authentication**.

---

## 🔑 Identifiants

**Username** : `julien`
**Password** : `DevAccess2025`

---

## 🌐 Accès via Navigateur Web

### Tous les sites protégés :
- https://clemence.srv759970.hstgr.cloud
- https://cristina.srv759970.hstgr.cloud
- https://wordpress.srv759970.hstgr.cloud
- https://admin.cristina.srv759970.hstgr.cloud (Strapi)
- https://dashboard.srv759970.hstgr.cloud
- https://sharepoint.srv759970.hstgr.cloud
- https://portal.srv759970.hstgr.cloud
- https://whisper.srv759970.hstgr.cloud
- https://tika.srv759970.hstgr.cloud

### Comment se connecter :

1. Ouvrir l'URL dans le navigateur
2. Une popup apparaît demandant login/password
3. Entrer :
   - **Nom d'utilisateur** : `julien`
   - **Mot de passe** : `DevAccess2025`
4. Cliquer **OK** ou **Se connecter**

Le navigateur mémorise les credentials pour la session.

---

## 🔧 Accès API via Code

Toutes les APIs nécessitent maintenant l'authentification Basic Auth.

### Python (requests)

```python
import requests

# Méthode 1 : auth parameter (recommandée)
response = requests.get(
    'https://whisper.srv759970.hstgr.cloud/docs',
    auth=('julien', 'DevAccess2025')
)

# Méthode 2 : headers manuels
import base64
credentials = base64.b64encode(b'julien:DevAccess2025').decode('utf-8')
headers = {'Authorization': f'Basic {credentials}'}
response = requests.get(
    'https://whisper.srv759970.hstgr.cloud/docs',
    headers=headers
)

# Exemple Whisper API (transcription)
with open('audio.mp3', 'rb') as audio_file:
    response = requests.post(
        'https://whisper.srv759970.hstgr.cloud/v1/audio/transcriptions',
        auth=('julien', 'DevAccess2025'),
        files={'file': audio_file},
        data={'model': 'base'}
    )
    print(response.json())

# Exemple Tika API (extraction document)
with open('document.pdf', 'rb') as doc:
    response = requests.put(
        'https://tika.srv759970.hstgr.cloud/tika',
        auth=('julien', 'DevAccess2025'),
        data=doc,
        headers={'Accept': 'text/plain'}
    )
    print(response.text)

# Exemple Ollama API (génération texte)
response = requests.post(
    'http://69.62.108.82:11435/api/generate',
    auth=('julien', 'DevAccess2025'),
    json={
        'model': 'qwen2.5:3b',
        'prompt': 'Explique-moi la diversité en entreprise',
        'stream': False
    }
)
print(response.json()['response'])
```

### JavaScript / Node.js (fetch)

```javascript
// Méthode 1 : Basic Auth dans l'URL (simple mais visible)
fetch('https://julien:DevAccess2025@whisper.srv759970.hstgr.cloud/docs')
    .then(res => res.json())
    .then(data => console.log(data));

// Méthode 2 : Headers manuels (recommandée)
const credentials = btoa('julien:DevAccess2025');
fetch('https://whisper.srv759970.hstgr.cloud/docs', {
    headers: {
        'Authorization': `Basic ${credentials}`
    }
})
.then(res => res.json())
.then(data => console.log(data));

// Exemple Whisper API
const formData = new FormData();
formData.append('file', audioBlob, 'audio.mp3');
formData.append('model', 'base');

fetch('https://whisper.srv759970.hstgr.cloud/v1/audio/transcriptions', {
    method: 'POST',
    headers: {
        'Authorization': `Basic ${btoa('julien:DevAccess2025')}`
    },
    body: formData
})
.then(res => res.json())
.then(data => console.log(data.text));

// Exemple Tika API
fetch('https://tika.srv759970.hstgr.cloud/tika', {
    method: 'PUT',
    headers: {
        'Authorization': `Basic ${btoa('julien:DevAccess2025')}`,
        'Accept': 'text/plain'
    },
    body: pdfFile
})
.then(res => res.text())
.then(text => console.log(text));
```

### cURL (Terminal/Bash)

```bash
# Méthode 1 : -u flag (recommandée)
curl -u julien:DevAccess2025 https://clemence.srv759970.hstgr.cloud

# Méthode 2 : URL avec credentials
curl https://julien:DevAccess2025@clemence.srv759970.hstgr.cloud

# Méthode 3 : Header manuel
curl -H "Authorization: Basic anVsaWVuOkRldkFjY2VzczIwMjU=" https://clemence.srv759970.hstgr.cloud

# Exemple Whisper API
curl -u julien:DevAccess2025 \
  -X POST https://whisper.srv759970.hstgr.cloud/v1/audio/transcriptions \
  -F file=@audio.mp3 \
  -F model=base

# Exemple Tika API
curl -u julien:DevAccess2025 \
  -X PUT https://tika.srv759970.hstgr.cloud/tika \
  -H "Accept: text/plain" \
  --data-binary @document.pdf

# Exemple Ollama API
curl -u julien:DevAccess2025 \
  http://69.62.108.82:11435/api/generate \
  -d '{
    "model": "qwen2.5:3b",
    "prompt": "Hello world",
    "stream": false
  }'
```

### PHP

```php
<?php
// Méthode 1 : file_get_contents avec context
$auth = base64_encode('julien:DevAccess2025');
$context = stream_context_create([
    'http' => [
        'header' => "Authorization: Basic $auth"
    ]
]);
$response = file_get_contents('https://clemence.srv759970.hstgr.cloud', false, $context);

// Méthode 2 : cURL
$ch = curl_init('https://whisper.srv759970.hstgr.cloud/docs');
curl_setopt($ch, CURLOPT_USERPWD, 'julien:DevAccess2025');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);

// Exemple Whisper API
$ch = curl_init('https://whisper.srv759970.hstgr.cloud/v1/audio/transcriptions');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_USERPWD, 'julien:DevAccess2025');
curl_setopt($ch, CURLOPT_POSTFIELDS, [
    'file' => new CURLFile('audio.mp3'),
    'model' => 'base'
]);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$result = curl_exec($ch);
curl_close($ch);
?>
```

---

## 🔧 Ajouter/Modifier des utilisateurs

### Ajouter un nouvel utilisateur

```bash
ssh root@69.62.108.82
htpasswd -b /etc/nginx/.htpasswd clemence ClemPass2025
systemctl reload nginx
```

### Changer le mot de passe d'un utilisateur existant

```bash
ssh root@69.62.108.82
htpasswd -b /etc/nginx/.htpasswd julien NouveauMotDePasse
systemctl reload nginx
```

### Lister tous les utilisateurs

```bash
ssh root@69.62.108.82
cat /etc/nginx/.htpasswd
```

### Supprimer un utilisateur

```bash
ssh root@69.62.108.82
htpasswd -D /etc/nginx/.htpasswd username
systemctl reload nginx
```

---

## 🚫 Désactiver l'authentification (si besoin)

### Pour un site spécifique

```bash
ssh root@69.62.108.82

# Supprimer la ligne auth_basic du site
sed -i '/include snippets\/basic-auth.conf/d' /etc/nginx/sites-available/clemence

# Recharger Nginx
systemctl reload nginx
```

### Pour tous les sites

```bash
ssh root@69.62.108.82

# Supprimer toutes les références
for site in clemence cristina dashboard portal sharepoint strapi tika whisper wordpress; do
  sed -i '/include snippets\/basic-auth.conf/d' /etc/nginx/sites-available/$site
done

# Recharger Nginx
systemctl reload nginx
```

---

## 🔍 Debugging

### Tester si l'auth fonctionne

```bash
# Sans credentials (devrait retourner 401)
curl -I https://clemence.srv759970.hstgr.cloud

# Avec credentials (devrait retourner 200)
curl -I -u julien:DevAccess2025 https://clemence.srv759970.hstgr.cloud
```

### Voir les logs d'authentification

```bash
ssh root@69.62.108.82
tail -f /var/log/nginx/clemence-error.log
```

### Vérifier le fichier de mots de passe

```bash
ssh root@69.62.108.82
cat /etc/nginx/.htpasswd
# Devrait afficher : julien:$apr1$...
```

---

## 📊 Monitoring des accès

### Voir qui accède aux sites

```bash
ssh root@69.62.108.82

# Logs de tous les accès
tail -f /var/log/nginx/clemence-access.log

# Filtrer par username (julien)
tail -f /var/log/nginx/clemence-access.log | grep julien

# Compter les accès par IP
awk '{print $1}' /var/log/nginx/clemence-access.log | sort | uniq -c | sort -rn
```

### Logs d'erreurs d'authentification

```bash
ssh root@69.62.108.82
grep "401" /var/log/nginx/clemence-error.log
```

---

## ⚠️ Notes importantes

### Sécurité

- ⚠️ **Basic Auth envoie le mot de passe encodé en Base64** (facilement décodable)
- ✅ **Toujours utiliser HTTPS** pour chiffrer la transmission
- ✅ Les credentials sont valides uniquement en HTTPS sur ce serveur
- ✅ Le navigateur mémorise les credentials (cookies de session)

### Limites

- **Pas de gestion fine des permissions** : Tous les users ont accès à tout
- **Pas de rotation automatique** : Changer le mot de passe manuellement
- **Pas d'audit détaillé** : Logs basiques seulement

### Pour la production

Pour un environnement de production, considérer :
- **Cloudflare Access** (Zero Trust) : Login par email, plus sécurisé
- **OAuth2 / JWT** : Authentification moderne avec tokens
- **VPN** (Tailscale/WireGuard) : Accès réseau sécurisé

---

## 🔄 Migration vers Cloudflare (plus tard)

Si tu veux migrer vers Cloudflare Access plus tard :

1. Configurer Cloudflare selon **GUIDE_CLOUDFLARE_SETUP.md**
2. Désactiver Basic Auth une fois Cloudflare actif
3. Les APIs fonctionneront avec Service Tokens Cloudflare

---

## 📚 Ressources

- **Nginx Basic Auth Docs** : http://nginx.org/en/docs/http/ngx_http_auth_basic_module.html
- **htpasswd Docs** : https://httpd.apache.org/docs/current/programs/htpasswd.html

---

**Créé le** : 2025-10-16
**Identifiants actuels** : `julien` / `DevAccess2025`

