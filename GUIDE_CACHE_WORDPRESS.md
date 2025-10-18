# Guide Cache Nginx pour WordPress

**Dernière mise à jour** : 18 octobre 2025
**Serveur** : srv759970.hstgr.cloud (69.62.108.82)
**Sites concernés** : clemence.srv759970.hstgr.cloud, solidarlink.srv759970.hstgr.cloud

---

## Objectif

Améliorer les performances des sites WordPress en mettant en cache les réponses HTTP au niveau du reverse proxy Nginx, réduisant ainsi la charge sur les containers WordPress et accélérant le temps de réponse pour les visiteurs.

**Bénéfices attendus** :
- ✅ Temps de chargement 2-3x plus rapide pour les pages mises en cache
- ✅ Réduction de la charge CPU/RAM sur les containers WordPress
- ✅ Meilleure expérience utilisateur
- ✅ Gestion automatique du cache (purge, invalidation)

---

## Architecture

```
Client HTTPS Request
     ↓
Nginx (Port 443) - SSL Termination + Basic Auth
     ↓
Proxy Cache Layer ← NOUVEAU !
     ↓
Auto-Start Proxy (Port 8890)
     ↓
WordPress Container (Port 9002 ou 9003)
```

Le cache intercepte les réponses des containers WordPress et les stocke sur disque. Les requêtes suivantes sont servies directement depuis le cache sans solliciter le container.

---

## Configuration

### 1. Zone de cache globale

**Fichier** : `/etc/nginx/snippets/wordpress-cache.conf`

```nginx
# WordPress Proxy Cache Configuration
proxy_cache_path /var/cache/nginx/wordpress levels=1:2 keys_zone=WORDPRESS:100m max_size=500m inactive=60m use_temp_path=off;
proxy_cache_key $scheme$request_method$host$request_uri;

# Bypass cache pour méthodes POST
map $request_method $skip_cache_method {
    default 0;
    POST    1;
}

# Bypass cache pour URIs admin WordPress
map $request_uri $skip_cache_uri {
    default 0;
    ~*wp-admin  1;
    ~*wp-login  1;
    ~*wp-cron   1;
    ~*xmlrpc    1;
}

# Bypass cache pour utilisateurs connectés
map $http_cookie $skip_cache_cookie {
    default 0;
    ~*wordpress_logged_in  1;
    ~*comment_author       1;
    ~*wp-postpass          1;
}

# Combinaison finale
map $skip_cache_method$skip_cache_uri$skip_cache_cookie $skip_cache {
    default 1;
    000     0;
}
```

**Paramètres** :
- `keys_zone=WORDPRESS:100m` : 100MB pour stocker les clés de cache (≈800k pages)
- `max_size=500m` : Taille maximale du cache sur disque (500MB)
- `inactive=60m` : Supprimer les entrées non accédées depuis 60 minutes
- `levels=1:2` : Structure de répertoires pour optimiser les accès disque

### 2. Inclusion dans nginx.conf

**Fichier** : `/etc/nginx/nginx.conf`

Ajouté dans le bloc `http {}` (ligne 61) :

```nginx
# WordPress cache configuration
include /etc/nginx/snippets/wordpress-cache.conf;
```

### 3. Configuration par site

#### Clémence

**Fichier** : `/etc/nginx/sites-available/clemence`

```nginx
location / {
    proxy_pass http://127.0.0.1:8890;

    # WordPress Proxy Cache
    proxy_cache WORDPRESS;
    proxy_cache_bypass $skip_cache;
    proxy_no_cache $skip_cache;
    proxy_cache_valid 200 60m;
    proxy_cache_valid 404 10m;
    proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
    proxy_cache_lock on;
    add_header X-Cache-Status $upstream_cache_status;

    # ... reste de la config proxy ...
}
```

#### SolidarLink

**Fichier** : `/etc/nginx/sites-available/solidarlink`

Configuration identique à clemence (directives `proxy_cache*` ajoutées).

---

## Directives importantes

### proxy_cache WORDPRESS

Active le cache en utilisant la zone "WORDPRESS" définie dans wordpress-cache.conf.

### proxy_cache_bypass $skip_cache

Ne **pas lire** depuis le cache si `$skip_cache` vaut 1 (admin, POST, logged in).

### proxy_no_cache $skip_cache

Ne **pas écrire** dans le cache si `$skip_cache` vaut 1.

### proxy_cache_valid

- `proxy_cache_valid 200 60m` : Cache les réponses 200 OK pendant 60 minutes
- `proxy_cache_valid 404 10m` : Cache les 404 pendant 10 minutes seulement

### proxy_cache_use_stale

En cas d'erreur du backend (502, 503, timeout), servir une version **stale** (périmée) du cache plutôt qu'une erreur. Très important pour la disponibilité !

### proxy_cache_lock

Si plusieurs requêtes demandent la même ressource absente du cache, **une seule** va au backend, les autres attendent. Évite le "cache stampede".

### add_header X-Cache-Status

Ajoute un header HTTP indiquant le statut du cache :
- `MISS` : Pas en cache, récupéré depuis le backend
- `HIT` : Servi depuis le cache
- `BYPASS` : Cache ignoré (admin, POST, logged in)
- `STALE` : Version périmée servie suite à erreur backend
- `UPDATING` : Mise à jour en cours, version stale servie temporairement
- `REVALIDATED` : Cache validé avec backend (304 Not Modified)

---

## Quand le cache est-il utilisé ?

### ✅ Pages mises en cache

- Pages publiques (homepage, articles, pages statiques)
- Archives (catégories, tags, dates)
- Flux RSS
- Réponses JSON API publiques

**Conditions** :
- Méthode HTTP : `GET` ou `HEAD`
- Pas de cookie `wordpress_logged_in`
- Pas d'URL contenant `wp-admin`, `wp-login`, `wp-cron`

### ❌ Pages NON mises en cache

- Toutes les requêtes `POST` (formulaires, commentaires)
- URLs contenant `wp-admin`, `wp-login.php`, `wp-cron.php`, `xmlrpc.php`
- Utilisateurs connectés (cookie `wordpress_logged_in` présent)
- Auteurs de commentaires (cookie `comment_author`)
- Pages protégées par mot de passe (`wp-postpass` cookie)

---

## Vérification et monitoring

### Vérifier que le cache fonctionne

```bash
# Depuis le serveur
curl -I https://clemence.srv759970.hstgr.cloud/ -k | grep X-Cache-Status
# Devrait afficher : X-Cache-Status: MISS (première requête)

# Deuxième requête
curl -I https://clemence.srv759970.hstgr.cloud/ -k | grep X-Cache-Status
# Devrait afficher : X-Cache-Status: HIT (deuxième requête)
```

**Note** : Basic Auth requis pour clemence, utiliser `-u user:password`.

### Statistiques du cache

```bash
# Taille actuelle du cache
du -sh /var/cache/nginx/wordpress/

# Nombre de fichiers en cache
find /var/cache/nginx/wordpress/ -type f | wc -l

# Fichiers les plus récents (dernières entrées)
find /var/cache/nginx/wordpress/ -type f -mmin -10
```

### Logs

Les logs Nginx access montrent les requêtes :

```bash
# Voir les requêtes avec statut cache
tail -f /var/log/nginx/clemence-access.log
tail -f /var/log/nginx/solidarlink-access.log
```

L'en-tête `X-Cache-Status` est visible dans les logs si configuré dans le format de log (actuellement format par défaut, ne le montre pas).

---

## Gestion du cache

### Purger tout le cache

```bash
# Supprimer tous les fichiers de cache
sudo rm -rf /var/cache/nginx/wordpress/*

# Ou recréer le répertoire avec bonnes permissions
sudo rm -rf /var/cache/nginx/wordpress
sudo mkdir -p /var/cache/nginx/wordpress
sudo chown www-data:www-data /var/cache/nginx/wordpress
```

### Purger le cache d'un site spécifique

Le cache utilise une clé basée sur `$scheme$request_method$host$request_uri`, donc les deux sites ont des clés différentes. Cependant, ils partagent le même répertoire `/var/cache/nginx/wordpress/`.

**Solution manuelle** : Supprimer tout et laisser se reconstruire (WordPress met à jour rarement).

**Solution avancée** : Utiliser un plugin WordPress comme "Nginx Helper" qui envoie des purges au cache via des requêtes PURGE HTTP (nécessite configuration supplémentaire).

### Recharger la configuration

Après modification des fichiers de configuration :

```bash
# Tester la syntaxe
sudo nginx -t

# Recharger (sans downtime)
sudo systemctl reload nginx

# Redémarrer (si problème)
sudo systemctl restart nginx
```

---

## Tuning et optimisation

### Augmenter la taille du cache

Si 500MB ne suffit pas :

```nginx
# Dans /etc/nginx/snippets/wordpress-cache.conf
proxy_cache_path /var/cache/nginx/wordpress levels=1:2 keys_zone=WORDPRESS:200m max_size=2g inactive=120m use_temp_path=off;
```

- `keys_zone=200m` : 200MB de clés (≈1.6M pages)
- `max_size=2g` : 2GB de cache disque
- `inactive=120m` : Garder les entrées 2 heures

**Puis** :

```bash
sudo systemctl reload nginx
```

### Ajuster la durée de cache

Pour cacher plus longtemps les pages :

```nginx
# Dans les vhosts clemence et solidarlink
proxy_cache_valid 200 120m;  # 2 heures au lieu de 60min
proxy_cache_valid 404 30m;   # 30min pour 404
```

### Exclure des URIs supplémentaires

Si certaines pages dynamiques sont mises en cache par erreur :

```nginx
# Dans /etc/nginx/snippets/wordpress-cache.conf
map $request_uri $skip_cache_uri {
    default 0;
    ~*wp-admin  1;
    ~*wp-login  1;
    ~*wp-cron   1;
    ~*xmlrpc    1;
    ~*/cart     1;  # Panier WooCommerce
    ~*/checkout 1;  # Page de paiement
    ~*/my-account 1; # Compte utilisateur
}
```

### Cache conditionnel par query string

Actuellement, toute query string crée une clé de cache unique. Pour ignorer certains paramètres :

```nginx
# Clé de cache sans query string inutiles
proxy_cache_key "$scheme$request_method$host$uri$is_args$filtered_args";
```

(Nécessite configuration avancée avec `map` pour filtrer les args).

---

## Troubleshooting

### Cache ne semble pas fonctionner

**Vérifications** :

1. **Header X-Cache-Status présent ?**
   ```bash
   curl -I https://clemence.srv759970.hstgr.cloud/ -k | grep X-Cache
   ```

   Si absent → Configuration proxy_cache non appliquée, vérifier vhost et reload nginx.

2. **Toujours MISS ou BYPASS ?**
   - MISS : Normal première requête, deuxième devrait être HIT
   - BYPASS : Vérifier que vous n'êtes pas logué (cookies), pas de POST, pas d'URL admin

3. **Répertoire cache vide ?**
   ```bash
   ls /var/cache/nginx/wordpress/
   ```

   Si vide → Vérifier permissions (doit être `www-data:www-data`).

4. **Erreurs dans logs Nginx ?**
   ```bash
   tail -50 /var/log/nginx/error.log | grep cache
   ```

### Réponses stale servies trop souvent

Si `X-Cache-Status: STALE` apparaît fréquemment, le backend a des problèmes. Vérifier :

```bash
# Logs containers WordPress
docker logs -f wordpress-clemence
docker logs -f wordpress-solidarlink

# Logs auto-start
journalctl -u docker-autostart -f
```

### Espace disque plein

Le cache est limité à 500MB (`max_size=500m`), mais si le disque se remplit :

```bash
# Vérifier espace disque
df -h /var/cache

# Purger manuellement
sudo rm -rf /var/cache/nginx/wordpress/*
```

### Cache invalide après mise à jour WordPress

Après mise à jour de contenu WordPress, le cache peut servir des anciennes versions.

**Solution 1 : Attendre expiration** (60min par défaut)

**Solution 2 : Purge manuelle**
```bash
sudo rm -rf /var/cache/nginx/wordpress/*
```

**Solution 3 : Plugin WordPress** (Nginx Helper) pour purge automatique lors de publications.

---

## Performance attendue

### Avant cache (proxy direct)

- **Première requête** : 500-1000ms (démarrage container via auto-start)
- **Requêtes suivantes** : 200-400ms (container chaud)
- **RAM container** : 150-300MB

### Après cache

- **Première requête (MISS)** : Identique (500-1000ms)
- **Requêtes suivantes (HIT)** : **50-100ms** (depuis Nginx cache)
- **RAM économisée** : Container peut s'arrêter plus vite (auto-start idle)

**Gain net** : 5-10x plus rapide pour pages en cache, réduction significative de la charge backend.

---

## Sécurité

### Considérations

1. **Pas de cache pour contenu sensible** : Les règles `$skip_cache` excluent déjà les zones admin et utilisateurs connectés.

2. **Cache partagé** : Les deux sites (clemence + solidarlink) utilisent la même zone de cache, mais les clés incluent `$host`, donc pas de collision.

3. **Headers de sécurité préservés** : Le cache transmet les headers SSL/TLS et Security headers du backend.

4. **Basic Auth avant cache** : Le basic auth Nginx s'applique **avant** le cache, donc pas de bypass possible.

### Risques potentiels

- ❌ **Cache poisoning** : Si un attaquant injecte des headers malicieux, ils peuvent être cachés. Risque faible avec configuration actuelle.
- ❌ **Données personnelles** : Vérifier que les pages cachées ne contiennent pas de données spécifiques utilisateur.
- ❌ **Stale content** : Pages périmées servies en cas d'erreur backend (voulu pour disponibilité).

---

## Compatibilité

### Plugins WordPress

**Compatible** :
- ✅ Yoast SEO
- ✅ WooCommerce (avec exclusions `/cart`, `/checkout` si ajoutées)
- ✅ Contact Form 7
- ✅ Elementor (pages statiques)

**Peut nécessiter ajustements** :
- ⚠️ Plugins de cache WordPress (W3 Total Cache, WP Super Cache) : Désactiver ou coordonner
- ⚠️ Plugins e-commerce : Exclure panier, checkout, account pages
- ⚠️ Plugins de personnalisation dynamique : Peuvent être affectés

**Recommandation** : Désactiver les plugins de cache WordPress (inutiles avec cache Nginx).

### Auto-Start System

Le cache Nginx fonctionne **en amont** de l'auto-start, donc :

- ✅ Les requêtes HIT ne déclenchent PAS le démarrage des containers
- ✅ Les containers peuvent rester arrêtés plus longtemps (économie RAM)
- ✅ Les requêtes MISS déclenchent l'auto-start normalement

**Synergie parfaite** : Cache réduit le nombre de démarrages containers, auto-start réduit l'utilisation RAM totale.

---

## Métriques de succès

### Phase de test (1 semaine)

- [ ] X-Cache-Status HIT visible dans headers
- [ ] Temps de réponse moyen < 100ms pour pages en cache
- [ ] Taux de HIT > 70% sur trafic total
- [ ] Aucune plainte utilisateurs (pages périmées, erreurs)
- [ ] Taille cache < 500MB (limite non atteinte)

### Production (1 mois)

- [ ] Réduction 50% temps de démarrage containers (moins sollicités)
- [ ] Réduction 30% RAM moyenne utilisée (containers idle plus souvent)
- [ ] Temps de réponse moyen global < 200ms
- [ ] Zéro erreur de cache (stale content acceptable uniquement en erreur)

---

## Références

- **Nginx Proxy Cache** : https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_cache
- **WordPress Nginx** : https://www.nginx.com/resources/wiki/start/topics/recipes/wordpress/
- **Cache Key Optimization** : https://www.nginx.com/blog/nginx-caching-guide/

---

## Historique des modifications

| Date       | Action                                      | Par          |
|------------|---------------------------------------------|--------------|
| 2025-10-18 | Configuration initiale cache proxy WordPress| Claude Code  |
| 2025-10-18 | Ajout zones de cache globales               | Claude Code  |
| 2025-10-18 | Activation cache clemence + solidarlink     | Claude Code  |
| 2025-10-18 | Documentation complète créée                | Claude Code  |

---

## TODO

- [ ] Tester cache depuis Windows avec credentials basic auth
- [ ] Monitorer taux HIT/MISS pendant 1 semaine
- [ ] Évaluer besoin plugin WordPress Nginx Helper pour purge automatique
- [ ] Documenter procédure purge cache dans scripts maintenance
- [ ] Ajouter métriques cache au dashboard auto-start (futur)

---

**Version** : 1.0
**Auteur** : Claude Code + Julien
**Prochaine revue** : Après 1 semaine de production
